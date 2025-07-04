"""Redis checkpoint persistence for LangGraph state management."""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import asyncio
from dataclasses import asdict

from src.orchestration.state import ConversationState


class RedisCheckpointSaver:
    """Redis-based checkpoint saver for conversation state persistence."""
    
    def __init__(self, redis_client=None):
        """Initialize with Redis client."""
        self.redis_client = redis_client
        self.checkpoint_prefix = "checkpoint:"
        self.checkpoint_ttl = 7 * 24 * 3600  # 7 days in seconds
    
    async def save_checkpoint(self, state: ConversationState) -> str:
        """Save conversation state as checkpoint to Redis.
        
        Args:
            state: ConversationState to save
            
        Returns:
            checkpoint_id: Unique identifier for the saved checkpoint
        """
        # Generate checkpoint ID with timestamp including microseconds
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        checkpoint_id = f"{self.checkpoint_prefix}{state.conversation_id}:{timestamp}"
        
        # Serialize state to JSON
        state_data = self._serialize_state(state)
        serialized_data = json.dumps(state_data, indent=None)
        
        # Save to Redis with TTL
        await self.redis_client.set(
            checkpoint_id, 
            serialized_data,
            ex=self.checkpoint_ttl
        )
        
        return checkpoint_id
    
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[ConversationState]:
        """Load conversation state from checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            ConversationState or None if not found
        """
        # Get serialized data from Redis
        serialized_data = await self.redis_client.get(checkpoint_id)
        
        if serialized_data is None:
            return None
        
        # Deserialize state data
        state_data = json.loads(serialized_data)
        
        # Reconstruct ConversationState
        state = self._deserialize_state(state_data)
        
        return state
    
    async def checkpoint_exists(self, checkpoint_id: str) -> bool:
        """Check if checkpoint exists in Redis.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            True if checkpoint exists, False otherwise
        """
        return await self.redis_client.exists(checkpoint_id) > 0
    
    async def list_checkpoints(self, conversation_id: str) -> List[str]:
        """List all checkpoints for a conversation.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            List of checkpoint IDs
        """
        pattern = f"{self.checkpoint_prefix}{conversation_id}:*"
        
        # Scan for matching keys
        cursor = 0
        checkpoints = []
        
        while True:
            cursor, keys = await self.redis_client.scan(
                cursor=cursor,
                match=pattern,
                count=100
            )
            checkpoints.extend(keys)
            
            if cursor == 0:
                break
        
        # Sort by timestamp (newest first)
        checkpoints.sort(reverse=True)
        
        return checkpoints
    
    async def cleanup_old_checkpoints(self, max_age_hours: int = 168) -> int:
        """Clean up old checkpoints beyond max age.
        
        Args:
            max_age_hours: Maximum age in hours (default: 168 = 7 days)
            
        Returns:
            Number of checkpoints deleted
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cutoff_timestamp = cutoff_time.strftime("%Y%m%d_%H%M%S")
        
        # Scan for all checkpoint keys
        cursor = 0
        old_keys = []
        
        while True:
            cursor, keys = await self.redis_client.scan(
                cursor=cursor,
                match=f"{self.checkpoint_prefix}*",
                count=100
            )
            
            # Filter keys by timestamp
            for key in keys:
                try:
                    # Extract timestamp from key
                    timestamp_part = key.split(":")[-1]
                    if timestamp_part < cutoff_timestamp:
                        old_keys.append(key)
                except (IndexError, ValueError):
                    # Skip malformed keys
                    continue
            
            if cursor == 0:
                break
        
        # Delete old checkpoints
        deleted_count = 0
        if old_keys:
            for key in old_keys:
                await self.redis_client.delete(key)
                deleted_count += 1
        
        return deleted_count
    
    def _serialize_state(self, state: ConversationState) -> Dict[str, Any]:
        """Serialize ConversationState to dictionary.
        
        Args:
            state: ConversationState to serialize
            
        Returns:
            Serialized state dictionary
        """
        return {
            "conversation_id": state.conversation_id,
            "messages": state.messages,
            "conversation_state": state.conversation_state,
            "morning_challenge": state.morning_challenge,
            "morning_value": state.morning_value,
            "evaluations": state.evaluations,
            "satisfaction_scores": state.satisfaction_scores,
            "performance_metrics": state.performance_metrics,
            "decision_path": state.decision_path,
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat()
        }
    
    def _deserialize_state(self, state_data: Dict[str, Any]) -> ConversationState:
        """Deserialize dictionary to ConversationState.
        
        Args:
            state_data: Serialized state dictionary
            
        Returns:
            ConversationState instance
        """
        # Parse timestamps
        created_at = datetime.fromisoformat(state_data["created_at"])
        updated_at = datetime.fromisoformat(state_data["updated_at"])
        
        # Create ConversationState instance
        state = ConversationState(
            conversation_id=state_data["conversation_id"],
            messages=state_data["messages"],
            conversation_state=state_data["conversation_state"],
            morning_challenge=state_data["morning_challenge"],
            morning_value=state_data["morning_value"],
            evaluations=state_data["evaluations"],
            satisfaction_scores=state_data["satisfaction_scores"],
            performance_metrics=state_data["performance_metrics"],
            decision_path=state_data["decision_path"],
            created_at=created_at,
            updated_at=updated_at
        )
        
        return state
    
    async def get_latest_checkpoint(self, conversation_id: str) -> Optional[str]:
        """Get the latest checkpoint ID for a conversation.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Latest checkpoint ID or None if none found
        """
        checkpoints = await self.list_checkpoints(conversation_id)
        
        if not checkpoints:
            return None
        
        return checkpoints[0]  # Already sorted newest first
    
    async def resume_conversation(self, conversation_id: str) -> Optional[ConversationState]:
        """Resume conversation from latest checkpoint.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            ConversationState or None if no checkpoint found
        """
        latest_checkpoint = await self.get_latest_checkpoint(conversation_id)
        
        if latest_checkpoint is None:
            return None
        
        return await self.load_checkpoint(latest_checkpoint)
    
    async def create_checkpoint_version(self, state: ConversationState) -> str:
        """Create a new versioned checkpoint.
        
        Args:
            state: ConversationState to version
            
        Returns:
            New checkpoint ID
        """
        # Always create new checkpoint with current timestamp
        return await self.save_checkpoint(state)
    
    async def get_checkpoint_metadata(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint metadata without loading full state.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Metadata dictionary or None if not found
        """
        serialized_data = await self.redis_client.get(checkpoint_id)
        
        if serialized_data is None:
            return None
        
        state_data = json.loads(serialized_data)
        
        # Return lightweight metadata
        return {
            "conversation_id": state_data["conversation_id"],
            "conversation_state": state_data["conversation_state"],
            "message_count": len(state_data["messages"]),
            "evaluation_count": len(state_data["evaluations"]),
            "satisfaction_score": (
                sum(state_data["satisfaction_scores"]) / len(state_data["satisfaction_scores"])
                if state_data["satisfaction_scores"] else 0.0
            ),
            "decision_path": state_data["decision_path"],
            "created_at": state_data["created_at"],
            "updated_at": state_data["updated_at"]
        }
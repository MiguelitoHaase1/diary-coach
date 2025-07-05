"""Cloud Checkpoint Manager for Session 6.5 - Persistent conversation memory."""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import hashlib

from src.orchestration.context_state import ContextState


logger = logging.getLogger(__name__)


class CloudCheckpointManager:
    """Manages persistent conversation memory using LangGraph checkpoints."""
    
    def __init__(self, privacy_mode: bool = False, max_history_length: int = 50):
        """Initialize checkpoint manager.
        
        Args:
            privacy_mode: Enable privacy controls for sensitive content
            max_history_length: Maximum number of messages to keep in detailed history
        """
        self.privacy_mode = privacy_mode
        self.max_history_length = max_history_length
        self.checkpoints = {}  # In-memory storage for testing (would be Redis/DB in production)
        self.versions = {}  # Track checkpoint versions
        
        # Sensitive topic keywords for privacy detection
        self.sensitive_keywords = [
            "personal", "private", "confidential", "manager issues", 
            "conflict", "hr", "lawsuit", "discrimination", "harassment"
        ]
    
    async def save_checkpoint(self, thread_id: str, state: ContextState, version: Optional[int] = None) -> str:
        """Save conversation state to checkpoint storage."""
        try:
            # Apply privacy controls if enabled
            if self.privacy_mode:
                state = await self.apply_privacy_controls(state)
            
            # Summarize if conversation is too long
            if len(state.messages) > self.max_history_length:
                state = await self.summarize_for_checkpoint(state)
            
            # Create checkpoint data
            checkpoint_data = {
                "state": self._serialize_state(state),
                "timestamp": datetime.now().isoformat(),
                "thread_id": thread_id,
                "version": version or self._get_next_version(thread_id)
            }
            
            # Store checkpoint
            checkpoint_id = f"{thread_id}:{checkpoint_data['version']}"
            self.checkpoints[checkpoint_id] = checkpoint_data
            
            # Track versions
            if thread_id not in self.versions:
                self.versions[thread_id] = []
            self.versions[thread_id].append(checkpoint_data['version'])
            
            logger.info(f"Checkpoint saved: {checkpoint_id}")
            return checkpoint_id
            
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
            raise
    
    async def load_checkpoint(self, thread_id: str, version: Optional[int] = None) -> Optional[ContextState]:
        """Load conversation state from checkpoint storage."""
        try:
            # Get latest version if none specified
            if version is None:
                version = self._get_latest_version(thread_id)
                if version is None:
                    return None
            
            checkpoint_id = f"{thread_id}:{version}"
            if checkpoint_id not in self.checkpoints:
                return None
            
            checkpoint_data = self.checkpoints[checkpoint_id]
            state = self._deserialize_state(checkpoint_data["state"])
            
            # Convert messages to conversation history
            state.conversation_history = await self._extract_conversation_history(state)
            
            # Track that memory was loaded
            if not state.context_usage:
                state.context_usage = {}
            state.context_usage["memory_loaded"] = True
            state.context_usage["checkpoint_version"] = version
            
            logger.info(f"Checkpoint loaded: {checkpoint_id}")
            return state
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return None
    
    async def summarize_for_checkpoint(self, state: ContextState) -> ContextState:
        """Summarize long conversations for efficient checkpoint storage."""
        if len(state.messages) <= self.max_history_length:
            return state
        
        # Extract key topics and insights from conversation
        conversation_summary = await self._extract_conversation_insights(state.messages)
        
        # Keep only recent messages in detail
        recent_messages = state.messages[-self.max_history_length:]
        
        # Create summarized state
        summarized_state = ContextState(
            messages=recent_messages,
            conversation_id=state.conversation_id,
            context_enabled=state.context_enabled,
            todo_context=state.todo_context,
            document_context=state.document_context,
            conversation_history=conversation_summary,
            context_relevance=state.context_relevance,
            context_usage=state.context_usage or {},
            decision_path=state.decision_path,
            coach_response=state.coach_response
        )
        
        # Track summarization
        summarized_state.context_usage["summarized_messages"] = len(state.messages)
        summarized_state.context_usage["kept_recent_messages"] = len(recent_messages)
        
        return summarized_state
    
    async def score_memory_relevance(self, memories: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Score relevance of conversation memories to current query."""
        scored_memories = []
        
        query_words = set(query.lower().split())
        
        for memory in memories:
            # Calculate relevance score based on keyword overlap
            topic_words = set(memory.get("topic", "").lower().split())
            insights_words = set(memory.get("insights", "").lower().split())
            
            # Score based on word overlap  
            topic_overlap = len(query_words.intersection(topic_words))
            insights_overlap = len(query_words.intersection(insights_words))
            
            # Weight topic matches higher than insight matches
            relevance_score = (topic_overlap * 0.7) + (insights_overlap * 0.3)
            
            # Boost score for exact topic matches
            if memory.get("topic", "").lower() in query.lower():
                relevance_score += 0.5
            
            # Normalize by query length but keep meaningful scores
            if len(query_words) > 0:
                relevance_score = min(relevance_score / len(query_words) + 0.2, 1.0)  # Add baseline score
            
            # Add recency bonus (more recent memories get slight boost)
            try:
                memory_date = datetime.fromisoformat(memory.get("date", "2020-01-01"))
                days_ago = (datetime.now() - memory_date).days
                recency_bonus = max(0, (30 - days_ago) / 30 * 0.1)  # Up to 0.1 bonus for recent
                relevance_score += recency_bonus
            except:
                pass
            
            scored_memory = {
                **memory,
                "relevance_score": min(relevance_score, 1.0)
            }
            scored_memories.append(scored_memory)
        
        # Sort by relevance score (highest first)
        scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_memories
    
    async def apply_privacy_controls(self, state: ContextState) -> ContextState:
        """Apply privacy controls to sensitive conversation content."""
        if not self.privacy_mode:
            return state
        
        sensitive_detected = False
        filtered_messages = []
        
        for message in state.messages:
            content = message.get("content", "").lower()
            
            # Check for sensitive keywords
            is_sensitive = any(keyword in content for keyword in self.sensitive_keywords)
            
            if is_sensitive:
                sensitive_detected = True
                # Anonymize or flag sensitive content
                filtered_message = {
                    **message,
                    "content": "[SENSITIVE CONTENT - PRIVACY PROTECTED]",
                    "original_flagged": True
                }
                filtered_messages.append(filtered_message)
            else:
                filtered_messages.append(message)
        
        # Create privacy-controlled state
        filtered_state = ContextState(
            messages=filtered_messages,
            conversation_id=state.conversation_id,
            context_enabled=state.context_enabled,
            todo_context=state.todo_context,
            document_context=state.document_context,
            conversation_history=state.conversation_history,
            context_relevance=state.context_relevance,
            context_usage=state.context_usage or {},
            decision_path=state.decision_path,
            coach_response=state.coach_response
        )
        
        # Track privacy application
        filtered_state.context_usage["privacy_applied"] = sensitive_detected
        if sensitive_detected:
            filtered_state.context_usage["sensitive_topics_detected"] = True
        
        return filtered_state
    
    async def list_checkpoint_versions(self, thread_id: str) -> List[int]:
        """List all checkpoint versions for a thread."""
        return self.versions.get(thread_id, [])
    
    async def cleanup_old_checkpoints(self, thread_id: str, keep_latest: int = 5) -> int:
        """Clean up old checkpoint versions, keeping only the latest N."""
        versions = self.versions.get(thread_id, [])
        if len(versions) <= keep_latest:
            return 0
        
        # Sort versions and identify old ones to remove
        sorted_versions = sorted(versions, reverse=True)
        versions_to_remove = sorted_versions[keep_latest:]
        
        removed_count = 0
        for version in versions_to_remove:
            checkpoint_id = f"{thread_id}:{version}"
            if checkpoint_id in self.checkpoints:
                del self.checkpoints[checkpoint_id]
                removed_count += 1
        
        # Update version tracking
        self.versions[thread_id] = sorted_versions[:keep_latest]
        
        logger.info(f"Cleaned up {removed_count} old checkpoints for thread {thread_id}")
        return removed_count
    
    def _get_next_version(self, thread_id: str) -> int:
        """Get the next version number for a thread."""
        versions = self.versions.get(thread_id, [])
        return max(versions) + 1 if versions else 1
    
    def _get_latest_version(self, thread_id: str) -> Optional[int]:
        """Get the latest version number for a thread."""
        versions = self.versions.get(thread_id, [])
        return max(versions) if versions else None
    
    def _serialize_state(self, state: ContextState) -> Dict[str, Any]:
        """Serialize ContextState to dictionary."""
        return {
            "messages": state.messages,
            "conversation_id": state.conversation_id,
            "context_enabled": state.context_enabled,
            "todo_context": state.todo_context,
            "document_context": state.document_context,
            "conversation_history": state.conversation_history,
            "context_relevance": state.context_relevance,
            "context_usage": state.context_usage,
            "decision_path": state.decision_path,
            "coach_response": state.coach_response
        }
    
    def _deserialize_state(self, data: Dict[str, Any]) -> ContextState:
        """Deserialize dictionary to ContextState."""
        return ContextState(
            messages=data.get("messages", []),
            conversation_id=data.get("conversation_id", ""),
            context_enabled=data.get("context_enabled", True),
            todo_context=data.get("todo_context"),
            document_context=data.get("document_context"),
            conversation_history=data.get("conversation_history"),
            context_relevance=data.get("context_relevance", {}),
            context_usage=data.get("context_usage", {}),
            decision_path=data.get("decision_path", []),
            coach_response=data.get("coach_response")
        )
    
    async def _extract_conversation_history(self, state: ContextState) -> List[Dict[str, Any]]:
        """Extract conversation history summary from state."""
        if not state.messages:
            return []
        
        # Group messages by conversation topics
        history_items = []
        
        # Simple approach: create one history item per conversation
        user_messages = [msg for msg in state.messages if msg.get("type") == "user"]
        if user_messages:
            # Extract main topic from first user message
            first_message = user_messages[0]
            topic = self._extract_topic_from_message(first_message.get("content", ""))
            
            # Create history item
            history_item = {
                "date": first_message.get("timestamp", datetime.now().isoformat())[:10],  # Just date
                "topic": topic,
                "insights": f"Discussed {topic} with coaching focus",
                "message_count": len(state.messages)
            }
            history_items.append(history_item)
        
        return history_items
    
    async def _extract_conversation_insights(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract key insights from a long conversation."""
        # Simple extraction - in production this could use LLM summarization
        insights = []
        
        # Group messages by rough topics
        user_messages = [msg for msg in messages if msg.get("type") == "user"]
        
        for i, msg in enumerate(user_messages):
            if i % 10 == 0:  # Every 10th message as a rough topic break
                topic = self._extract_topic_from_message(msg.get("content", ""))
                insight = {
                    "date": msg.get("timestamp", datetime.now().isoformat())[:10],
                    "topic": topic,
                    "insights": f"Discussion about {topic}",
                    "message_index": i
                }
                insights.append(insight)
        
        return insights
    
    def _extract_topic_from_message(self, content: str) -> str:
        """Extract main topic from message content."""
        # Simple keyword-based topic extraction
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["delegate", "delegation", "delegating"]):
            return "delegation"
        elif any(word in content_lower for word in ["priority", "prioritize", "important"]):
            return "prioritization"
        elif any(word in content_lower for word in ["team", "communication", "meeting"]):
            return "team communication"
        elif any(word in content_lower for word in ["strategy", "strategic", "planning"]):
            return "strategic planning"
        elif any(word in content_lower for word in ["goal", "goals", "objective"]):
            return "goal setting"
        else:
            # Extract first meaningful word
            words = content.split()
            meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
            return meaningful_words[0] if meaningful_words else "general discussion"
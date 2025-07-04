"""Tests for Redis checkpoint persistence."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

from src.orchestration.state import ConversationState
from src.orchestration.checkpoint_persistence import RedisCheckpointSaver
from src.events.schemas import UserMessage, AgentResponse


class TestRedisCheckpointPersistence:
    """Test Redis checkpoint persistence functionality."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = Mock()
        mock.get = AsyncMock()
        mock.set = AsyncMock()
        mock.exists = AsyncMock()
        mock.delete = AsyncMock()
        mock.scan = AsyncMock()
        return mock

    @pytest.fixture
    def checkpoint_saver(self, mock_redis):
        """Create checkpoint saver with mock Redis."""
        return RedisCheckpointSaver(redis_client=mock_redis)

    @pytest.fixture
    def sample_state(self):
        """Create sample conversation state."""
        state = ConversationState(conversation_id="test_conv_123")
        
        # Add a user message
        user_msg = UserMessage(
            content="Good morning, I want to work on my project today",
            user_id="user123",
            timestamp=datetime.now(),
            conversation_id="test_conv_123"
        )
        state.add_message(user_msg)
        
        # Add an agent response
        agent_response = AgentResponse(
            content="What's the most important outcome you want to achieve?",
            agent_name="DiaryCoach",
            response_to=user_msg.message_id,
            conversation_id="test_conv_123"
        )
        state.add_response(agent_response)
        
        # Add some evaluation data
        state.add_evaluation({
            "analyzer": "SpecificityPush",
            "score": 8.5,
            "feedback": "Good challenge to specificity"
        })
        
        state.add_satisfaction_score(7.8)
        state.add_decision("coach")
        state.add_decision("evaluator")
        
        return state

    @pytest.mark.asyncio
    async def test_save_checkpoint(self, checkpoint_saver, sample_state, mock_redis):
        """Test saving a checkpoint to Redis."""
        # Mock Redis set operation
        mock_redis.set.return_value = True
        
        # Save checkpoint
        checkpoint_id = await checkpoint_saver.save_checkpoint(sample_state)
        
        # Verify checkpoint ID format
        assert checkpoint_id.startswith("checkpoint:")
        assert sample_state.conversation_id in checkpoint_id
        
        # Verify Redis set was called
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        
        # Verify the key format
        assert call_args[0][0] == checkpoint_id
        
        # Verify the stored data can be deserialized
        stored_data = json.loads(call_args[0][1])
        assert stored_data["conversation_id"] == "test_conv_123"
        assert len(stored_data["messages"]) == 2
        assert len(stored_data["evaluations"]) == 1
        assert stored_data["satisfaction_scores"] == [7.8]
        assert stored_data["decision_path"] == ["coach", "evaluator"]

    @pytest.mark.asyncio
    async def test_load_checkpoint(self, checkpoint_saver, sample_state, mock_redis):
        """Test loading a checkpoint from Redis."""
        # Prepare serialized state data
        state_data = {
            "conversation_id": sample_state.conversation_id,
            "messages": sample_state.messages,
            "conversation_state": sample_state.conversation_state,
            "morning_challenge": sample_state.morning_challenge,
            "morning_value": sample_state.morning_value,
            "evaluations": sample_state.evaluations,
            "satisfaction_scores": sample_state.satisfaction_scores,
            "performance_metrics": sample_state.performance_metrics,
            "decision_path": sample_state.decision_path,
            "created_at": sample_state.created_at.isoformat(),
            "updated_at": sample_state.updated_at.isoformat()
        }
        
        # Mock Redis get operation
        mock_redis.get.return_value = json.dumps(state_data)
        
        # Load checkpoint
        checkpoint_id = "checkpoint:test_conv_123:20250704_1200"
        loaded_state = await checkpoint_saver.load_checkpoint(checkpoint_id)
        
        # Verify loaded state
        assert loaded_state is not None
        assert loaded_state.conversation_id == sample_state.conversation_id
        assert len(loaded_state.messages) == len(sample_state.messages)
        assert loaded_state.messages[0]["content"] == "Good morning, I want to work on my project today"
        assert loaded_state.messages[1]["content"] == "What's the most important outcome you want to achieve?"
        assert len(loaded_state.evaluations) == 1
        assert loaded_state.satisfaction_scores == [7.8]
        assert loaded_state.decision_path == ["coach", "evaluator"]
        
        # Verify Redis get was called
        mock_redis.get.assert_called_once_with(checkpoint_id)

    @pytest.mark.asyncio
    async def test_load_nonexistent_checkpoint(self, checkpoint_saver, mock_redis):
        """Test loading a non-existent checkpoint."""
        # Mock Redis get returns None
        mock_redis.get.return_value = None
        
        # Try to load non-existent checkpoint
        checkpoint_id = "checkpoint:nonexistent:20250704_1200"
        loaded_state = await checkpoint_saver.load_checkpoint(checkpoint_id)
        
        # Should return None
        assert loaded_state is None
        
        # Verify Redis get was called
        mock_redis.get.assert_called_once_with(checkpoint_id)

    @pytest.mark.asyncio
    async def test_conversation_resume(self, checkpoint_saver, sample_state, mock_redis):
        """Test conversation resume from checkpoint."""
        # Mock successful save
        mock_redis.set.return_value = True
        
        # Save initial state
        checkpoint_id = await checkpoint_saver.save_checkpoint(sample_state)
        
        # Prepare serialized state for loading
        state_data = {
            "conversation_id": sample_state.conversation_id,
            "messages": sample_state.messages,
            "conversation_state": sample_state.conversation_state,
            "morning_challenge": sample_state.morning_challenge,
            "morning_value": sample_state.morning_value,
            "evaluations": sample_state.evaluations,
            "satisfaction_scores": sample_state.satisfaction_scores,
            "performance_metrics": sample_state.performance_metrics,
            "decision_path": sample_state.decision_path,
            "created_at": sample_state.created_at.isoformat(),
            "updated_at": sample_state.updated_at.isoformat()
        }
        
        # Mock Redis get operation
        mock_redis.get.return_value = json.dumps(state_data)
        
        # Load checkpoint
        resumed_state = await checkpoint_saver.load_checkpoint(checkpoint_id)
        
        # Add new message to resumed state
        new_msg = UserMessage(
            content="I want to focus on the most important task",
            user_id="user123",
            timestamp=datetime.now(),
            conversation_id="test_conv_123"
        )
        resumed_state.add_message(new_msg)
        
        # Verify conversation history includes original message
        user_messages = resumed_state.get_user_messages()
        assert len(user_messages) == 2
        assert user_messages[0]["content"] == "Good morning, I want to work on my project today"
        assert user_messages[1]["content"] == "I want to focus on the most important task"

    @pytest.mark.asyncio
    async def test_checkpoint_versioning(self, checkpoint_saver, sample_state, mock_redis):
        """Test checkpoint versioning with timestamps."""
        # Mock Redis set operation
        mock_redis.set.return_value = True
        
        # Save multiple checkpoints
        checkpoint1 = await checkpoint_saver.save_checkpoint(sample_state)
        
        # Add more data to state and wait briefly to ensure different timestamp
        sample_state.add_satisfaction_score(8.2)
        await asyncio.sleep(0.001)  # 1ms delay to ensure different timestamp
        checkpoint2 = await checkpoint_saver.save_checkpoint(sample_state)
        
        # Verify different checkpoint IDs
        assert checkpoint1 != checkpoint2
        
        # Both should contain conversation ID
        assert sample_state.conversation_id in checkpoint1
        assert sample_state.conversation_id in checkpoint2
        
        # Verify Redis set was called twice
        assert mock_redis.set.call_count == 2

    @pytest.mark.asyncio
    async def test_checkpoint_cleanup(self, checkpoint_saver, mock_redis):
        """Test cleanup of old checkpoints."""
        # Mock Redis scan operation
        old_keys = [
            "checkpoint:conv1:20250701_1000",
            "checkpoint:conv2:20250701_1100",
            "checkpoint:conv3:20250701_1200"
        ]
        mock_redis.scan.return_value = (0, old_keys)
        mock_redis.delete.return_value = len(old_keys)
        
        # Run cleanup
        deleted_count = await checkpoint_saver.cleanup_old_checkpoints(max_age_hours=24)
        
        # Verify cleanup was called
        mock_redis.scan.assert_called_once()
        assert deleted_count == 3
        
        # Verify delete was called for each key
        expected_calls = [unittest.mock.call(key) for key in old_keys]
        mock_redis.delete.assert_has_calls(expected_calls, any_order=True)

    @pytest.mark.asyncio
    async def test_checkpoint_serialization_integrity(self, checkpoint_saver, sample_state, mock_redis):
        """Test that checkpoint serialization preserves data integrity."""
        # Mock Redis operations
        mock_redis.set.return_value = True
        
        # Save checkpoint
        checkpoint_id = await checkpoint_saver.save_checkpoint(sample_state)
        
        # Get the serialized data that was saved
        call_args = mock_redis.set.call_args
        serialized_data = call_args[0][1]
        
        # Deserialize and verify all fields
        deserialized = json.loads(serialized_data)
        
        # Check core fields
        assert deserialized["conversation_id"] == sample_state.conversation_id
        assert deserialized["conversation_state"] == sample_state.conversation_state
        assert deserialized["morning_challenge"] == sample_state.morning_challenge
        assert deserialized["morning_value"] == sample_state.morning_value
        
        # Check arrays
        assert len(deserialized["messages"]) == len(sample_state.messages)
        assert len(deserialized["evaluations"]) == len(sample_state.evaluations)
        assert deserialized["satisfaction_scores"] == sample_state.satisfaction_scores
        assert deserialized["decision_path"] == sample_state.decision_path
        
        # Check timestamps are ISO format strings
        assert isinstance(deserialized["created_at"], str)
        assert isinstance(deserialized["updated_at"], str)
        
        # Verify datetime parsing works
        datetime.fromisoformat(deserialized["created_at"])
        datetime.fromisoformat(deserialized["updated_at"])

    @pytest.mark.asyncio
    async def test_checkpoint_error_handling(self, checkpoint_saver, sample_state, mock_redis):
        """Test error handling in checkpoint operations."""
        # Test save error
        mock_redis.set.side_effect = Exception("Redis connection error")
        
        with pytest.raises(Exception) as exc_info:
            await checkpoint_saver.save_checkpoint(sample_state)
        
        assert "Redis connection error" in str(exc_info.value)
        
        # Test load error
        mock_redis.get.side_effect = Exception("Redis connection error")
        
        with pytest.raises(Exception) as exc_info:
            await checkpoint_saver.load_checkpoint("checkpoint:test:123")
        
        assert "Redis connection error" in str(exc_info.value)


import unittest.mock
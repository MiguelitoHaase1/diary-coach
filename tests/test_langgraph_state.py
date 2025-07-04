"""Test LangGraph state schema for conversation + evaluation data."""

import pytest
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.events.schemas import UserMessage, AgentResponse
from src.orchestration.state import ConversationState


@pytest.mark.asyncio
async def test_conversation_state_schema():
    """State must track conversation, metrics, and decisions."""
    state = ConversationState(conversation_id="test_conv")
    
    # Test initial state
    assert state.conversation_id == "test_conv"
    assert state.conversation_state == "general"
    assert state.get_message_count() == 0
    assert state.get_satisfaction_score() == 0.0
    assert state.get_decision_path() == []
    
    # Test adding messages
    user_msg = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conv"
    )
    state.add_message(user_msg)
    assert state.get_message_count() == 1
    assert state.get_user_messages()[0]["content"] == "good morning"
    
    # Test adding responses
    agent_response = AgentResponse(
        agent_name="coach",
        content="Good morning Michael!",
        response_to=user_msg.message_id,
        conversation_id="test_conv"
    )
    state.add_response(agent_response)
    assert state.get_message_count() == 2
    assert state.get_agent_responses()[0]["content"] == "Good morning Michael!"
    
    # Test adding evaluations
    eval_result = {
        "satisfaction": 8.5,
        "effectiveness": 7.8,
        "engagement": 9.2
    }
    state.add_evaluation(eval_result)
    assert len(state.evaluations) == 1
    assert state.evaluations[0]["satisfaction"] == 8.5
    
    # Test satisfaction scoring
    state.add_satisfaction_score(8.5)
    state.add_satisfaction_score(7.8)
    assert state.get_satisfaction_score() == 8.15
    
    # Test decision tracking
    state.add_decision("coach")
    state.add_decision("evaluator")
    state.add_decision("output")
    assert state.get_decision_path() == ["coach", "evaluator", "output"]


@pytest.mark.asyncio
async def test_state_morning_tracking():
    """State should track morning-specific elements."""
    state = ConversationState(conversation_id="morning_conv")
    
    # Test conversation state updates
    state.update_conversation_state("morning")
    assert state.conversation_state == "morning"
    
    # Test morning challenge tracking
    state.set_morning_challenge("Organize my files")
    assert state.morning_challenge == "Organize my files"
    
    # Test morning value tracking
    state.set_morning_value("Clarity and focus")
    assert state.morning_value == "Clarity and focus"


@pytest.mark.asyncio
async def test_state_metrics_tracking():
    """State should track performance metrics."""
    state = ConversationState(conversation_id="metrics_conv")
    
    # Test performance metrics
    metrics = {
        "response_time": 1.2,
        "token_usage": 145,
        "cost": 0.0023
    }
    state.update_performance_metrics(metrics)
    assert state.performance_metrics["response_time"] == 1.2
    assert state.performance_metrics["token_usage"] == 145
    assert state.performance_metrics["cost"] == 0.0023
    
    # Test additional metrics
    more_metrics = {
        "response_time": 0.8,  # Should update
        "quality_score": 9.1   # Should add
    }
    state.update_performance_metrics(more_metrics)
    assert state.performance_metrics["response_time"] == 0.8
    assert state.performance_metrics["quality_score"] == 9.1
    assert state.performance_metrics["token_usage"] == 145  # Should remain


@pytest.mark.asyncio
async def test_state_timestamp_tracking():
    """State should track creation and update times."""
    state = ConversationState(conversation_id="time_conv")
    
    original_created = state.created_at
    original_updated = state.updated_at
    
    # Adding data should update the timestamp
    import time
    time.sleep(0.01)  # Small delay to ensure timestamp change
    
    state.add_satisfaction_score(8.0)
    assert state.updated_at > original_updated
    assert state.created_at == original_created  # Should not change


@pytest.mark.asyncio
async def test_state_message_filtering():
    """State should filter messages by type."""
    state = ConversationState(conversation_id="filter_conv")
    
    # Add multiple messages
    user_msg1 = UserMessage(
        user_id="test_user",
        content="Hello",
        timestamp=datetime.now(),
        conversation_id="filter_conv"
    )
    state.add_message(user_msg1)
    
    agent_resp1 = AgentResponse(
        agent_name="coach",
        content="Hi there!",
        response_to=user_msg1.message_id,
        conversation_id="filter_conv"
    )
    state.add_response(agent_resp1)
    
    user_msg2 = UserMessage(
        user_id="test_user",
        content="How are you?",
        timestamp=datetime.now(),
        conversation_id="filter_conv"
    )
    state.add_message(user_msg2)
    
    # Test filtering
    user_messages = state.get_user_messages()
    agent_responses = state.get_agent_responses()
    
    assert len(user_messages) == 2
    assert len(agent_responses) == 1
    assert user_messages[0]["content"] == "Hello"
    assert user_messages[1]["content"] == "How are you?"
    assert agent_responses[0]["content"] == "Hi there!"
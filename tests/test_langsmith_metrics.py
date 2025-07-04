"""Test LangSmith integration with custom metrics."""

import pytest
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock
import os

from src.orchestration.state import ConversationState
from src.orchestration.langsmith_tracker import LangSmithTracker
from src.events.schemas import UserMessage


class MockLangSmithContext:
    """Mock context manager for capturing LangSmith events."""
    
    def __init__(self):
        self.tracker = LangSmithTracker()
        self.custom_metrics = {}
        self.metadata = {}
        self.agent_communications = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def track_custom_metric(self, name: str, value: Any):
        """Track a custom metric."""
        self.custom_metrics[name] = value
    
    def track_metadata(self, metadata: Dict[str, Any]):
        """Track metadata."""
        self.metadata.update(metadata)
    
    def track_agent_communication(self, agent_name: str, input_data: Any, output_data: Any):
        """Track agent communication."""
        self.agent_communications.append({
            "agent_name": agent_name,
            "input": input_data,
            "output": output_data
        })


def capture_langsmith_events():
    """Mock function to capture LangSmith events."""
    return MockLangSmithContext()


@pytest.mark.asyncio
async def test_custom_satisfaction_tracking():
    """User satisfaction must be tracked in LangSmith."""
    tracker = LangSmithTracker()
    
    # Track satisfaction with context
    await tracker.track_user_satisfaction(8.5, {"session_type": "morning"})
    
    # Verify tracking
    metrics = tracker.get_custom_metrics()
    metadata = tracker.get_metadata()
    
    assert "user_satisfaction" in metrics
    assert metrics["user_satisfaction"] == 8.5
    assert metadata["session_type"] == "morning"


@pytest.mark.asyncio
async def test_conversation_flow_tracking():
    """Conversation flow must be tracked in LangSmith."""
    tracker = LangSmithTracker()
    
    # Track conversation flow
    decisions = ["coach", "evaluator", "output"]
    await tracker.track_conversation_flow(decisions)
    
    # Verify tracking
    metadata = tracker.get_metadata()
    assert "conversation_flow" in metadata
    assert metadata["conversation_flow"] == decisions


@pytest.mark.asyncio
async def test_agent_communication_tracking():
    """Agent communications must be tracked."""
    tracker = LangSmithTracker()
    
    # Track multiple agent communications
    await tracker.track_agent_communication(
        "coach",
        {"message": "good morning"},
        {"response": "Good morning Michael!"}
    )
    
    await tracker.track_agent_communication(
        "evaluator",
        {"conversation": "morning session"},
        {"score": 8.5}
    )
    
    # Verify tracking
    communications = tracker.get_agent_communications()
    assert len(communications) == 2
    assert communications[0]["agent_name"] == "coach"
    assert communications[1]["agent_name"] == "evaluator"


@pytest.mark.asyncio
async def test_conversation_lifecycle_tracking():
    """Full conversation lifecycle must be tracked."""
    tracker = LangSmithTracker()
    
    # Create test conversation state
    state = ConversationState(conversation_id="test_conv")
    msg = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conv"
    )
    state.add_message(msg)
    state.add_satisfaction_score(8.5)
    state.add_decision("coach")
    state.add_decision("evaluator")
    
    # Track conversation lifecycle
    run_id = await tracker.track_conversation_start(state)
    assert run_id is not None
    assert run_id.startswith("run_test_conv")
    
    await tracker.end_conversation(state, {"total_cost": 0.023})
    
    # Verify tracking
    events = tracker.get_all_events()
    assert len(events) == 2
    assert events[0]["type"] == "conversation_start"
    assert events[1]["type"] == "conversation_end"
    assert events[1]["satisfaction_score"] == 8.5
    assert events[1]["decision_path"] == ["coach", "evaluator"]


@pytest.mark.asyncio
async def test_performance_metrics_tracking():
    """Performance metrics must be tracked."""
    tracker = LangSmithTracker()
    
    # Track various performance metrics
    await tracker.track_performance_metrics({
        "response_time_ms": 1200,
        "token_usage": 145,
        "cost_usd": 0.0023
    })
    
    # Track additional metrics
    await tracker.track_performance_metrics({
        "quality_score": 9.1,
        "response_time_ms": 800  # Should update existing
    })
    
    # Verify tracking
    metrics = tracker.get_custom_metrics()
    assert metrics["response_time_ms"] == 800  # Updated
    assert metrics["token_usage"] == 145
    assert metrics["cost_usd"] == 0.0023
    assert metrics["quality_score"] == 9.1


@pytest.mark.asyncio
async def test_langsmith_integration_mock():
    """Test LangSmith integration with mock client."""
    
    async with capture_langsmith_events() as events:
        # Simulate conversation processing
        events.track_custom_metric("user_satisfaction", 8.5)
        events.track_metadata({"conversation_flow": ["coach", "evaluator"]})
        events.track_agent_communication("coach", "input", "output")
        events.track_agent_communication("evaluator", "input", "output")
    
    # Verify events were captured
    assert "user_satisfaction" in events.custom_metrics
    assert events.custom_metrics["user_satisfaction"] == 8.5
    assert "conversation_flow" in events.metadata
    assert len(events.agent_communications) == 2


@pytest.mark.asyncio
async def test_langsmith_tracker_initialization():
    """LangSmith tracker should initialize correctly."""
    tracker = LangSmithTracker("test-project")
    
    assert tracker.project_name == "test-project"
    assert tracker.events == []
    assert tracker.custom_metrics == {}
    assert tracker.metadata == {}
    assert tracker.agent_communications == []


@pytest.mark.asyncio
async def test_conversation_state_integration():
    """LangSmith should integrate with ConversationState."""
    tracker = LangSmithTracker()
    
    # Create conversation state with various data
    state = ConversationState(conversation_id="integration_test")
    
    # Add messages
    msg1 = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="integration_test"
    )
    state.add_message(msg1)
    
    # Add evaluations and metrics
    state.add_evaluation({"satisfaction": 8.5})
    state.add_satisfaction_score(8.5)
    state.add_decision("coach")
    state.update_performance_metrics({"cost": 0.0023})
    
    # Track with LangSmith
    run_id = await tracker.track_conversation_start(state)
    await tracker.track_user_satisfaction(state.get_satisfaction_score())
    await tracker.track_conversation_flow(state.get_decision_path())
    await tracker.end_conversation(state)
    
    # Verify integration
    events = tracker.get_all_events()
    metrics = tracker.get_custom_metrics()
    
    assert len(events) == 2
    assert events[0]["conversation_id"] == "integration_test"
    assert metrics["user_satisfaction"] == 8.5
    assert events[1]["decision_path"] == ["coach"]
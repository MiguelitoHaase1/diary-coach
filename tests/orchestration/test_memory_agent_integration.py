"""Test Memory Agent integration with multi-agent system."""

import pytest
import json
import os
import tempfile

from src.agents.memory_agent import MemoryAgent
from src.orchestration.multi_agent_state import MultiAgentState
from src.agents.base import AgentRequest


@pytest.fixture
def test_conversations_dir():
    """Create test conversations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test conversation
        conv = {
            "conversation_id": "test_conv_1",
            "timestamp": "2024-01-15T09:00:00",
            "messages": [
                {
                    "type": "user",
                    "content": "I need help with delegation strategies",
                    "timestamp": "2024-01-15T09:00:00"
                },
                {
                    "type": "agent",
                    "content": "What specific aspects of delegation challenge you?",
                    "timestamp": "2024-01-15T09:00:30"
                },
                {
                    "type": "user",
                    "content": "I struggle with letting go of control",
                    "timestamp": "2024-01-15T09:01:00"
                }
            ]
        }

        filepath = os.path.join(temp_dir, "conversation_1.json")
        with open(filepath, 'w') as f:
            json.dump(conv, f)

        yield temp_dir


@pytest.mark.asyncio
async def test_memory_agent_handles_coach_request(test_conversations_dir):
    """Test Memory Agent handles requests from coach."""
    agent = MemoryAgent(conversations_dir=test_conversations_dir)
    await agent.initialize()

    # Simulate request from coach
    request = AgentRequest(
        from_agent="coach",
        to_agent="memory",
        query="Find relevant past conversations about: delegation",
        context={"conversation_id": "current_conv"}
    )

    response = await agent.handle_request(request)

    assert response.agent_name == "memory"
    assert not response.error

    result = json.loads(response.content)
    assert result["total_found"] > 0
    assert "delegation" in str(result["results"])


@pytest.mark.asyncio
async def test_memory_agent_state_integration(test_conversations_dir):
    """Test Memory Agent updates multi-agent state correctly."""
    agent = MemoryAgent(conversations_dir=test_conversations_dir)
    await agent.initialize()

    # Create multi-agent state
    state = MultiAgentState(conversation_id="test")
    state.activate_agent("memory")

    # Add request to state
    request = AgentRequest(
        from_agent="coach",
        to_agent="memory",
        query="What are the patterns in our conversations?",
        context={"conversation_id": "test"}
    )
    state.add_pending_request(request)

    # Process request
    response = await agent.handle_request(request)

    # Complete request in state
    state.complete_request(request.request_id, response)

    # Check state was updated
    assert "memory" in state.agent_responses
    assert len(state.agent_responses["memory"]) == 1
    assert len(state.pending_requests) == 0


@pytest.mark.asyncio
async def test_memory_context_in_state(test_conversations_dir):
    """Test Memory Agent context can be stored in state."""
    agent = MemoryAgent(conversations_dir=test_conversations_dir)
    await agent.initialize()

    state = MultiAgentState(conversation_id="test")

    # Get memory summary
    request = AgentRequest(
        from_agent="coach",
        to_agent="memory",
        query="Give me a summary",
        context={}
    )

    response = await agent.handle_request(request)
    memory_data = json.loads(response.content)

    # Store in state
    state.set_memory_context(memory_data)

    # Verify it's accessible
    all_context = state.get_all_context()
    assert all_context["memory"] is not None
    assert "total_conversations" in all_context["memory"]


@pytest.mark.asyncio
async def test_memory_agent_with_empty_history():
    """Test Memory Agent handles empty history gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        agent = MemoryAgent(conversations_dir=temp_dir)
        await agent.initialize()

        request = AgentRequest(
            from_agent="coach",
            to_agent="memory",
            query="remember when we discussed productivity?",
            context={}
        )

        response = await agent.handle_request(request)

        # Should handle gracefully
        assert response.agent_name == "memory"
        assert not response.error

        result = json.loads(response.content)
        assert result["total_found"] == 0

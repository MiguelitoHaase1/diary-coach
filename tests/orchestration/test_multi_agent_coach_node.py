"""Test multi-agent coach node functionality."""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.events.schemas import UserMessage
from src.orchestration.multi_agent_state import MultiAgentState
from src.orchestration.multi_agent_coach_node import MultiAgentCoachNode
from src.agents.coach_agent import DiaryCoach


@pytest.mark.asyncio
async def test_coach_analyzes_agent_needs():
    """Coach should identify when other agents are needed."""

    class MockLLMService:
        async def generate_response(self, messages, system_prompt,
                                    max_tokens=200, temperature=0.7):
            return "Let me help you recall that conversation."

    coach_node = MultiAgentCoachNode(DiaryCoach(MockLLMService()))
    state = MultiAgentState(conversation_id="test")

    # Add a message that needs memory agent
    msg = UserMessage(
        user_id="test_user",
        content="Remember when we discussed productivity last week?",
        timestamp=datetime.now(),
        conversation_id="test"
    )
    state.add_message(msg)

    # Process
    new_state = await coach_node.process(state)

    # Should have created a request to memory agent
    assert len(new_state.pending_requests) == 1
    request = new_state.pending_requests[0]
    assert request.to_agent == "memory"
    assert "past conversations" in request.query

    # Should have sent a message to memory agent
    memory_messages = [
        m for m in new_state.agent_messages if m.to_agent == "memory"
    ]
    assert len(memory_messages) == 1


@pytest.mark.asyncio
async def test_coach_requests_multiple_agents():
    """Coach should request help from multiple agents when needed."""

    class MockLLMService:
        async def generate_response(self, messages, system_prompt,
                                    max_tokens=200, temperature=0.7):
            return "Let's explore your values and current priorities."

    coach_node = MultiAgentCoachNode(DiaryCoach(MockLLMService()))
    state = MultiAgentState(conversation_id="test")

    # Add a message that needs multiple agents
    msg = UserMessage(
        user_id="test_user",
        content="What should I prioritize today based on my core values?",
        timestamp=datetime.now(),
        conversation_id="test"
    )
    state.add_message(msg)

    # Process
    new_state = await coach_node.process(state)

    # Should have created requests to both MCP and personal content agents
    assert len(new_state.pending_requests) == 2
    requested_agents = [r.to_agent for r in new_state.pending_requests]
    assert "mcp" in requested_agents
    assert "personal_content" in requested_agents


@pytest.mark.asyncio
async def test_stage_transition():
    """Test automatic stage transition when problem is identified."""

    class MockLLMService:
        async def generate_response(self, messages, system_prompt,
                                    max_tokens=200, temperature=0.7):
            return "That's a great challenge to tackle!"

    # Mock morning time
    mock_morning_time = datetime.now().replace(hour=8, minute=0)

    with patch('src.agents.coach_agent.datetime') as mock_dt:
        mock_dt.now.return_value = mock_morning_time

        coach_node = MultiAgentCoachNode(DiaryCoach(MockLLMService()))
        state = MultiAgentState(conversation_id="test")

        # Activate coach
        state.activate_agent("coach")
        state.activate_agent("memory")
        state.activate_agent("mcp")

        # Message 1: Good morning
        msg1 = UserMessage(
            user_id="test_user",
            content="Good morning",
            timestamp=mock_morning_time,
            conversation_id="test"
        )
        state.add_message(msg1)
        state = await coach_node.process(state)

        # Should still be in stage 1
        assert state.current_stage == 1

        # Message 2: Define challenge
        msg2 = UserMessage(
            user_id="test_user",
            content="I need to organize my project files",
            timestamp=mock_morning_time,
            conversation_id="test"
        )
        state.add_message(msg2)
        state = await coach_node.process(state)

        # Still stage 1 (only 2 messages)
        assert state.current_stage == 1

        # Message 3: More depth
        msg3 = UserMessage(
            user_id="test_user",
            content="The clutter is affecting my focus",
            timestamp=mock_morning_time,
            conversation_id="test"
        )
        state.add_message(msg3)
        state = await coach_node.process(state)

        # Should transition to stage 2
        assert state.current_stage == 2
        assert state.stage_metadata["reason"] == "problem_clarity_achieved"

        # Should have broadcast the transition
        broadcasts = [
            m for m in state.agent_messages if m.message_type == "broadcast"
        ]
        assert len(broadcasts) > 0


@pytest.mark.asyncio
async def test_coach_state_tracking():
    """Test that coach node properly tracks internal state."""

    class MockLLMService:
        async def generate_response(self, messages, system_prompt,
                                    max_tokens=200, temperature=0.7):
            return "Good morning! What's on your mind today?"

    # Mock morning time
    mock_morning_time = datetime.now().replace(hour=8, minute=0)

    with patch('src.agents.coach_agent.datetime') as mock_dt:
        mock_dt.now.return_value = mock_morning_time

        coach_node = MultiAgentCoachNode(DiaryCoach(MockLLMService()))
        state = MultiAgentState(conversation_id="test")

        # Process morning message
        msg = UserMessage(
            user_id="test_user",
            content="Good morning",
            timestamp=mock_morning_time,
            conversation_id="test"
        )
        state.add_message(msg)
        state = await coach_node.process(state)

        # Check agent state was updated
        coach_state = state.get_agent_state("coach")
        assert coach_state["conversation_state"] == "morning"
        assert coach_state["message_count"] == 2  # User + assistant

        # Get coach state directly
        direct_state = await coach_node.get_coach_state()
        assert direct_state["conversation_state"] == "morning"


@pytest.mark.asyncio
async def test_multi_agent_state_compatibility():
    """Test that MultiAgentState works with existing coach functionality."""

    class MockLLMService:
        async def generate_response(self, messages, system_prompt,
                                    max_tokens=200, temperature=0.7):
            return "Hello! How can I help you today?"

    coach_node = MultiAgentCoachNode(DiaryCoach(MockLLMService()))
    state = MultiAgentState(conversation_id="test")

    # Test basic message processing
    msg = UserMessage(
        user_id="test_user",
        content="Hello",
        timestamp=datetime.now(),
        conversation_id="test"
    )
    state.add_message(msg)
    state = await coach_node.process(state)

    # Should have response
    responses = state.get_agent_responses()
    assert len(responses) == 1
    assert responses[0]["content"] == "Hello! How can I help you today?"

    # Decision tracking should work
    assert "coach" in state.get_decision_path()

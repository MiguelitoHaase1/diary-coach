"""Test Coach Node implementation as LangGraph wrapper."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.events.schemas import UserMessage, AgentResponse
from src.orchestration.state import ConversationState
from src.orchestration.coach_node import CoachNode
from src.agents.coach_agent import DiaryCoach
from src.services.llm_service import AnthropicService


@pytest.mark.asyncio
async def test_coach_node_preserves_behavior():
    """LangGraph coach must match event-bus coach exactly."""
    
    # Create mock LLM service to avoid API calls
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            return "Good morning Michael! What dragon are you most excited to slay today?"
    
    # Create coaches
    event_bus_coach = DiaryCoach(MockLLMService())
    coach_node = CoachNode(DiaryCoach(MockLLMService()))
    
    # Create test message
    test_message = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conv"
    )
    
    # Process through event-bus coach
    event_response = await event_bus_coach.process_message(test_message)
    
    # Process through LangGraph coach node
    state = ConversationState(conversation_id="test_conv")
    state.add_message(test_message)
    updated_state = await coach_node.process(state)
    
    # Get the response from state
    agent_responses = updated_state.get_agent_responses()
    assert len(agent_responses) == 1
    graph_response = agent_responses[0]
    
    # Compare responses
    assert graph_response["content"] == event_response.content
    assert graph_response["agent_name"] == event_response.agent_name
    
    # Check state updates
    assert updated_state.conversation_state == "morning"
    assert "coach" in updated_state.get_decision_path()


@pytest.mark.asyncio
async def test_coach_node_state_management():
    """Coach node should properly manage conversation state."""
    
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            if "value" in messages[-1]["content"].lower():
                return "That's a powerful value to champion!"
            return "Tell me more about what that means to you."
    
    coach_node = CoachNode(DiaryCoach(MockLLMService()))
    
    # Create initial state
    state = ConversationState(conversation_id="test_conv")
    
    # First message - good morning
    msg1 = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conv"
    )
    state.add_message(msg1)
    
    # Process first message
    state = await coach_node.process(state)
    assert state.conversation_state == "morning"
    assert len(state.get_agent_responses()) == 1
    
    # Second message - challenge
    msg2 = UserMessage(
        user_id="test_user",
        content="I need to organize my files",
        timestamp=datetime.now(),
        conversation_id="test_conv"
    )
    state.add_message(msg2)
    
    # Process second message
    state = await coach_node.process(state)
    assert len(state.get_agent_responses()) == 2
    
    # Third message - value
    msg3 = UserMessage(
        user_id="test_user",
        content="I want to fight for clarity",
        timestamp=datetime.now(),
        conversation_id="test_conv"
    )
    state.add_message(msg3)
    
    # Process third message
    state = await coach_node.process(state)
    assert len(state.get_agent_responses()) == 3
    assert state.morning_value == "I want to fight for clarity"


@pytest.mark.asyncio
async def test_coach_node_error_handling():
    """Coach node should handle errors gracefully."""
    
    class FailingLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            raise Exception("API Error")
    
    coach_node = CoachNode(DiaryCoach(FailingLLMService()))
    
    # Create state with message
    state = ConversationState(conversation_id="test_conv")
    msg = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conv"
    )
    state.add_message(msg)
    
    # Process should handle error gracefully
    with pytest.raises(Exception):
        await coach_node.process(state)


@pytest.mark.asyncio
async def test_coach_node_empty_state():
    """Coach node should handle empty conversation state."""
    
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            return "How can I help you today?"
    
    coach_node = CoachNode(DiaryCoach(MockLLMService()))
    
    # Create empty state
    state = ConversationState(conversation_id="test_conv")
    
    # Process empty state
    result_state = await coach_node.process(state)
    
    # Should return unchanged state
    assert result_state == state
    assert len(result_state.get_agent_responses()) == 0
    assert len(result_state.get_user_messages()) == 0


@pytest.mark.asyncio
async def test_coach_node_internal_state_access():
    """Coach node should provide access to internal coach state."""
    
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            return "Good morning Michael!"
    
    coach_node = CoachNode(DiaryCoach(MockLLMService()))
    
    # Process a message
    state = ConversationState(conversation_id="test_conv")
    msg = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conv"
    )
    state.add_message(msg)
    
    await coach_node.process(state)
    
    # Get internal coach state
    coach_state = await coach_node.get_coach_state()
    assert coach_state["conversation_state"] == "morning"
    assert coach_state["message_count"] >= 2
    assert "morning_challenge" in coach_state
    assert "morning_value" in coach_state
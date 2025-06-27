"""Test event schema definitions"""
from src.events.schemas import UserMessage, AgentResponse
from datetime import datetime


def test_user_message_schema():
    """User messages must have required fields"""
    msg = UserMessage(
        user_id="test_user",
        content="I want to be more productive",
        timestamp=datetime.now()
    )
    assert msg.user_id == "test_user"
    assert msg.conversation_id is not None  # Auto-generated


def test_agent_response_schema():
    """Agent responses must have required fields"""
    response = AgentResponse(
        agent_name="test_coach",
        content="Let's explore your productivity goals",
        response_to="msg_123"
    )
    assert response.agent_name == "test_coach"
    assert response.content == "Let's explore your productivity goals"
    assert response.response_to == "msg_123"
    assert response.timestamp is not None  # Auto-generated
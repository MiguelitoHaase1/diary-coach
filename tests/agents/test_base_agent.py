import pytest
from datetime import datetime
from src.agents.base import BaseAgent
from src.events.schemas import UserMessage, AgentResponse


@pytest.mark.asyncio
async def test_base_agent_responds_to_message():
    """Agents should respond to user messages with relevant content"""
    agent = BaseAgent(name="test_coach")
    
    user_msg = UserMessage(
        user_id="test_user",
        content="I want to set goals for today",
        timestamp=datetime.now()
    )
    
    response = await agent.process_message(user_msg)
    
    assert isinstance(response, AgentResponse)
    assert response.agent_name == "test_coach"
    assert len(response.content) > 0
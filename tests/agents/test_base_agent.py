import pytest
from datetime import datetime
from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse
from src.events.schemas import UserMessage, AgentResponse as LegacyAgentResponse


class MockTestAgent(BaseAgent):
    """Concrete test implementation of BaseAgent."""
    
    async def initialize(self):
        """Initialize the test agent."""
        self.is_initialized = True
    
    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle a test request."""
        return AgentResponse(
            agent_name=self.name,
            content="Test response",
            metadata={},
            request_id=request.request_id,
            timestamp=datetime.now()
        )


@pytest.mark.asyncio
async def test_base_agent_responds_to_message():
    """Agents should respond to user messages with relevant content"""
    agent = MockTestAgent(name="test_coach", capabilities=[AgentCapability.CONVERSATION])
    
    user_msg = UserMessage(
        user_id="test_user",
        content="I want to set goals for today",
        timestamp=datetime.now()
    )
    
    response = await agent.process_message(user_msg)
    
    assert isinstance(response, LegacyAgentResponse)
    assert response.agent_name == "test_coach"
    assert len(response.content) > 0
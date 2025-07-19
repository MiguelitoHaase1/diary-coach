"""Simplified tests for Coach Agent using new API."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from src.agents.coach_agent import DiaryCoach
from src.agents.base import AgentRequest
from src.services.llm_service import AnthropicService


class TestDiaryCoachSimple:
    """Simplified test suite for DiaryCoach agent."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service for testing."""
        mock_service = AsyncMock(spec=AnthropicService)
        return mock_service

    @pytest.fixture
    def coach(self, mock_llm_service):
        """Create a DiaryCoach instance with mocked LLM service."""
        return DiaryCoach(llm_service=mock_llm_service)

    @pytest.mark.asyncio
    async def test_conversation_state_tracking(self, coach, mock_llm_service):
        """Test that coach maintains conversation state."""
        mock_llm_service.generate_response.side_effect = [
            "Good morning Michael! What challenge are you ready to tackle today?",
            "That sounds meaningful. What core value do you want to fight for today?",
            "Great choice. How does that value feel in your body right now?"
        ]
        
        # First message should set morning state
        response1 = await coach.handle_request(AgentRequest(
            from_agent="test",
            to_agent="coach",
            query="good morning",
            context={"user_id": "michael", "timestamp": datetime.now().isoformat()}
        ))
        
        # Check state changed to morning if it's morning time
        if coach._is_morning_time():
            assert coach.conversation_state == "morning"
        else:
            assert coach.conversation_state == "general"
        
        # Challenge response
        response2 = await coach.handle_request(AgentRequest(
            from_agent="test",
            to_agent="coach",
            query="My challenge is to set better boundaries",
            context={"user_id": "michael", "timestamp": datetime.now().isoformat()}
        ))
        
        assert len(coach.message_history) == 4  # 2 user + 2 assistant messages
        
        # Value response
        response3 = await coach.handle_request(AgentRequest(
            from_agent="test",
            to_agent="coach",
            query="My core value is integrity",
            context={"user_id": "michael", "timestamp": datetime.now().isoformat()}
        ))
        
        # Verify we have all 6 messages in history
        assert len(coach.message_history) == 6  # 3 user + 3 assistant messages
        assert response3.agent_name == "coach"
        assert response3.content is not None
"""Tests for Coach Agent implementation."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from src.agents.coach_agent import DiaryCoach
from src.events.schemas import UserMessage, AgentResponse
from src.services.llm_service import AnthropicService


class TestDiaryCoach:
    """Test suite for DiaryCoach agent."""

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
    async def test_morning_greeting_format(self, coach, mock_llm_service):
        """Test morning greeting includes name and single question about challenge."""
        # Mock the LLM response
        mock_llm_service.generate_response.return_value = (
            "Good morning Michael! What's the one challenge you're ready to tackle today that could shift everything?"
        )
        
        user_message = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
        response = await coach.process_message(user_message)
        
        # Must include name and single question
        assert "Good morning Michael!" in response.content
        assert response.content.count("?") == 1
        assert "challenge" in response.content.lower()

    @pytest.mark.asyncio
    async def test_evening_greeting_format(self, coach, mock_llm_service):
        """Test evening greeting references morning context."""
        # Set up morning context first
        mock_llm_service.generate_response.side_effect = [
            "Good morning Michael! What's the one challenge you're ready to tackle today?",
            "Being present sounds important. What core value do you want to fight for today?",
            "Good evening Michael! How did being more present with your family actually unfold today?"
        ]
        
        # Morning conversation
        morning_message = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
        await coach.process_message(morning_message)
        
        challenge_message = UserMessage(content="I want to be more present with my family", user_id="michael", timestamp=datetime.now())
        await coach.process_message(challenge_message)
        
        # Evening should reference morning
        evening_message = UserMessage(content="good evening", user_id="michael", timestamp=datetime.now())
        response = await coach.process_message(evening_message)
        
        assert "Good evening Michael!" in response.content
        # Should reference morning discussion
        assert "present" in response.content.lower() or "family" in response.content.lower()

    @pytest.mark.asyncio
    async def test_coach_style_no_bullets(self, coach, mock_llm_service):
        """Test coach responses follow style constraints."""
        mock_llm_service.generate_response.return_value = (
            "That's an interesting perspective. What feels most alive about that idea right now?"
        )
        
        user_message = UserMessage(content="What should I focus on?", user_id="michael", timestamp=datetime.now())
        response = await coach.process_message(user_message)
        
        # Style validation
        assert "•" not in response.content
        assert not response.content.strip().startswith("-")
        assert len(response.content.split("\n")) <= 6  # Max 6 lines

    @pytest.mark.asyncio
    async def test_conversation_state_tracking(self, coach, mock_llm_service):
        """Test that coach maintains conversation state."""
        mock_llm_service.generate_response.side_effect = [
            "Good morning Michael! What challenge are you ready to tackle today?",
            "That sounds meaningful. What core value do you want to fight for today?",
            "Great choice. How does that value feel in your body right now?"
        ]
        
        # First message should set morning state
        morning_msg = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
        await coach.process_message(morning_msg)
        assert coach.conversation_state == "morning"
        
        # Challenge response
        challenge_msg = UserMessage(content="I need to set better boundaries", user_id="michael", timestamp=datetime.now())
        await coach.process_message(challenge_msg)
        assert coach.morning_challenge == "I need to set better boundaries"
        
        # Value response
        value_msg = UserMessage(content="I want to fight for my integrity", user_id="michael", timestamp=datetime.now())
        response = await coach.process_message(value_msg)
        assert coach.morning_value == "I want to fight for my integrity"

    @pytest.mark.asyncio
    async def test_system_prompt_integration(self, coach, mock_llm_service):
        """Test that coach uses the proper system prompt."""
        mock_llm_service.generate_response.return_value = "Good morning Michael!"
        
        user_message = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
        await coach.process_message(user_message)
        
        # Verify the system prompt was used
        call_args = mock_llm_service.generate_response.call_args
        assert call_args[1]["system_prompt"] is not None
        system_prompt = call_args[1]["system_prompt"]
        
        # Should contain key elements from the prompt
        assert "Daily Transformation Diary Coach" in system_prompt
        assert "Good morning Michael!" in system_prompt
        assert "Good evening Michael!" in system_prompt
        assert "core value" in system_prompt

    @pytest.mark.asyncio
    async def test_message_history_maintenance(self, coach, mock_llm_service):
        """Test that coach maintains message history for context."""
        mock_llm_service.generate_response.side_effect = [
            "Good morning Michael! What's your challenge today?",
            "I understand. What value do you want to fight for?"
        ]
        
        # Send two messages
        msg1 = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
        await coach.process_message(msg1)
        
        msg2 = UserMessage(content="I'm struggling with focus", user_id="michael", timestamp=datetime.now())
        await coach.process_message(msg2)
        
        # Should have message history
        assert len(coach.message_history) == 4  # 2 user + 2 assistant messages
        assert coach.message_history[0]["role"] == "user"
        assert coach.message_history[0]["content"] == "good morning"
        assert coach.message_history[1]["role"] == "assistant"
        assert coach.message_history[2]["role"] == "user"
        assert coach.message_history[2]["content"] == "I'm struggling with focus"

    @pytest.mark.asyncio
    async def test_value_question_timing(self, coach, mock_llm_service):
        """Test that value question appears after challenge discussion."""
        mock_llm_service.generate_response.side_effect = [
            "Good morning Michael! What challenge are you ready to tackle?",
            "That's significant. Tell me more about what makes this challenging.",
            "I hear you. What core value do you want to fight for today? Tell me a bit more about it."
        ]
        
        # Morning greeting
        await coach.process_message(UserMessage(content="good morning", user_id="michael", timestamp=datetime.now()))
        
        # Challenge identification
        await coach.process_message(UserMessage(content="I need to have a difficult conversation", user_id="michael", timestamp=datetime.now()))
        
        # Further exploration should eventually lead to value question
        response = await coach.process_message(UserMessage(content="I'm worried about how they'll react", user_id="michael", timestamp=datetime.now()))
        
        # Should ask about values at some point
        all_calls = mock_llm_service.generate_response.call_args_list
        all_text = ""
        for call in all_calls:
            if call.kwargs and "messages" in call.kwargs:
                all_text += str(call.kwargs["messages"])
        assert "value" in all_text.lower() or "fight for" in all_text.lower()
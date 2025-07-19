"""Tests for Morning Coach specific functionality."""

import pytest
from datetime import datetime, time
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.coach_agent import DiaryCoach
from src.events.schemas import UserMessage, AgentResponse
from src.services.llm_service import AnthropicService


class TestMorningCoach:
    """Test suite for Morning Coach specific behaviors."""

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
    async def test_morning_coach_challenges_problem_selection(self, coach, mock_llm_service):
        """Morning coach should question if this is really today's biggest problem."""
        # Set up morning time
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 9, 30)  # 9:30 AM
            
            mock_llm_service.generate_response.side_effect = [
                "Good morning, Michael! What dragon are you most excited to slay today?",
                "Hmm, is organizing files really the biggest lever you could pull today?"
            ]
            
            # Morning greeting 
            morning_msg = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
            response1 = await coach.process_message(morning_msg)
            
            # User states initial problem
            problem_msg = UserMessage(content="I need to organize my files", user_id="michael", timestamp=datetime.now())
            response2 = await coach.process_message(problem_msg)
            
            # Check that coach challenges the problem selection
            assert "really" in response2.content.lower() or "biggest" in response2.content.lower()
            
    @pytest.mark.asyncio
    async def test_morning_coach_uses_creative_greeting(self, coach, mock_llm_service):
        """Coach should use witty creative format for opening question."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 8, 15)  # 8:15 AM
            
            mock_llm_service.generate_response.return_value = (
                "Good morning, Michael! What mountain are you most pumped to climb today?"
            )
            
            user_message = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
            response = await coach.process_message(user_message)
            
            # Should include name
            assert "Good morning, Michael!" in response.content
            
            # Should use creative/witty language (metaphors, vivid imagery)
            creative_words = ["mountain", "climb", "dragon", "slay", "adventure", "challenge", "tackle", "shift"]
            has_creative_language = any(word in response.content.lower() for word in creative_words)
            assert has_creative_language
            
    @pytest.mark.asyncio 
    async def test_morning_coach_asks_about_core_value(self, coach, mock_llm_service):
        """After problem is energizing, coach asks about core value to fight for."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 9, 0)  # 9:00 AM
            
            mock_llm_service.generate_response.side_effect = [
                "Good morning, Michael! What's the one thing you're most fired up to tackle today?",
                "That sounds meaningful! What core value do you want to fight for today?"
            ]
            
            # Morning greeting
            morning_msg = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
            await coach.process_message(morning_msg)
            
            # User states energizing problem
            problem_msg = UserMessage(content="I want to have that difficult conversation with my team about our direction", user_id="michael", timestamp=datetime.now())
            response = await coach.process_message(problem_msg)
            
            # Should ask about core value
            assert "core value" in response.content.lower()
            assert "fight for" in response.content.lower()
            
    @pytest.mark.asyncio
    async def test_morning_coach_detects_morning_time(self, coach, mock_llm_service):
        """Coach should detect morning time and use morning-specific prompts."""
        with patch('src.agents.coach_agent.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 7, 45)  # 7:45 AM
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            mock_llm_service.generate_response.return_value = (
                "Good morning, Michael! What adventure awaits you today?"
            )
            
            user_message = UserMessage(content="good morning", user_id="michael", timestamp=datetime.now())
            response = await coach.process_message(user_message)
            
            # Verify morning-specific system prompt was used
            call_args = mock_llm_service.generate_response.call_args
            system_prompt = call_args[1]["system_prompt"]
            
            # Should contain morning-specific elements
            morning_indicators = [
                "Morning Ritual Protocol",
                "What feels like the most important problem to solve today?",
                "find problem"
            ]
            
            # At least one morning indicator should be present
            has_morning_content = any(indicator in system_prompt for indicator in morning_indicators)
            assert has_morning_content
            
    @pytest.mark.asyncio
    async def test_evening_coach_maintains_original_behavior(self, coach, mock_llm_service):
        """Coach should still use original prompts for evening conversations."""
        with patch('src.agents.coach_agent.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 19, 30)  # 7:30 PM
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            mock_llm_service.generate_response.return_value = (
                "Good evening Michael! How did that challenge from this morning actually unfold?"
            )
            
            user_message = UserMessage(content="good evening", user_id="michael", timestamp=datetime.now())
            response = await coach.process_message(user_message)
            
            # Verify standard system prompt was used (not morning-specific)
            call_args = mock_llm_service.generate_response.call_args
            system_prompt = call_args[1]["system_prompt"]
            
            # Should NOT contain morning-specific elements in evening
            assert "Morning Ritual Protocol" not in system_prompt
            # Should still have base coaching prompt
            assert "Daily Transformation Diary Coach" in system_prompt
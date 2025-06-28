"""Tests for CLI interface."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.interface.cli import DiaryCoachCLI
from src.agents.coach_agent import DiaryCoach
from src.events.bus import EventBus
from src.events.schemas import UserMessage, AgentResponse


class TestDiaryCoachCLI:
    """Test suite for DiaryCoachCLI."""

    @pytest.fixture
    def mock_coach(self):
        """Create a mock coach for testing."""
        coach = AsyncMock(spec=DiaryCoach)
        coach.llm_service = MagicMock()
        coach.llm_service.session_cost = 0.0024
        return coach

    @pytest.fixture
    def mock_event_bus(self):
        """Create a mock event bus for testing."""
        return AsyncMock(spec=EventBus)

    @pytest.fixture
    def cli(self, mock_coach, mock_event_bus):
        """Create a CLI instance with mocked dependencies."""
        return DiaryCoachCLI(coach=mock_coach, event_bus=mock_event_bus)

    @pytest.mark.asyncio
    async def test_cli_processes_input(self, cli, mock_coach):
        """Test CLI processes user input and returns response."""
        # Mock coach response
        mock_response = AgentResponse(
            agent_name="diary_coach",
            content="Good morning Michael! What's your challenge today?",
            response_to="test_msg_id"
        )
        mock_coach.process_message.return_value = mock_response
        
        # Process input
        response = await cli.process_input("good morning")
        
        assert response is not None
        assert isinstance(response, str)
        assert response == "Good morning Michael! What's your challenge today?"

    @pytest.mark.asyncio
    async def test_cli_maintains_session(self, cli, mock_coach):
        """Test CLI maintains conversation context across exchanges."""
        # Mock multiple responses
        responses = [
            AgentResponse(
                agent_name="diary_coach", 
                content="Good morning Michael! What challenge are you ready to tackle?",
                response_to="msg1"
            ),
            AgentResponse(
                agent_name="diary_coach",
                content="Being patient sounds meaningful. What core value drives that?",
                response_to="msg2"
            )
        ]
        mock_coach.process_message.side_effect = responses
        
        # Multiple exchanges
        response1 = await cli.process_input("good morning")
        response2 = await cli.process_input("I want to be more patient")
        
        # Verify responses
        assert "Good morning Michael!" in response1
        assert "patient" in response2.lower() or "meaningful" in response2.lower()
        
        # Verify coach was called twice
        assert mock_coach.process_message.call_count == 2

    @pytest.mark.asyncio
    async def test_cli_handles_exit_commands(self, cli):
        """Test CLI recognizes exit commands."""
        # Test various exit commands
        exit_commands = ["exit", "quit", "EXIT", "QUIT"]
        
        for cmd in exit_commands:
            result = await cli.process_input(cmd)
            assert result is None  # Should return None for exit

    @pytest.mark.asyncio
    async def test_cli_displays_cost_info(self, cli, mock_coach):
        """Test CLI includes cost information."""
        mock_response = AgentResponse(
            agent_name="diary_coach",
            content="Hello Michael!",
            response_to="test_msg"
        )
        mock_coach.process_message.return_value = mock_response
        mock_coach.llm_service.session_cost = 0.0034
        
        # Process input and check cost tracking
        await cli.process_input("hello")
        
        # Verify cost is accessible
        assert cli.get_session_cost() == 0.0034

    @pytest.mark.asyncio
    async def test_cli_handles_coach_errors(self, cli, mock_coach):
        """Test CLI handles coach errors gracefully."""
        # Mock coach to raise an error
        mock_coach.process_message.side_effect = Exception("API Error")
        
        # Should not crash on error
        response = await cli.process_input("good morning")
        
        # Should return error message
        assert response is not None
        assert "error" in response.lower() or "try again" in response.lower()

    @pytest.mark.asyncio 
    async def test_cli_user_message_creation(self, cli, mock_coach):
        """Test CLI creates proper UserMessage objects."""
        mock_response = AgentResponse(
            agent_name="diary_coach",
            content="Hello!",
            response_to="test_msg"
        )
        mock_coach.process_message.return_value = mock_response
        
        await cli.process_input("test message")
        
        # Verify UserMessage was created correctly
        call_args = mock_coach.process_message.call_args[0][0]
        assert isinstance(call_args, UserMessage)
        assert call_args.content == "test message"
        assert call_args.user_id == "michael"
        assert isinstance(call_args.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_cli_async_input_loop_exit(self, cli):
        """Test async input loop handles exit gracefully."""
        # Mock input to return exit command
        with patch('builtins.input', return_value='exit'):
            # This should not hang or crash
            result = await cli.process_input("exit")
            assert result is None
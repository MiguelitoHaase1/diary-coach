"""Quick smoke tests to verify core functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import os

# Set env var before imports
os.environ["DISABLE_MULTI_AGENT"] = "true"

from src.interface.multi_agent_cli import MultiAgentCLI
from src.agents.base import AgentRequest


@pytest.mark.smoke
class TestSmoke:
    """Fast smoke tests for core functionality."""
    
    @pytest.fixture
    def mock_cli(self):
        """Create a CLI with all dependencies mocked."""
        cli = MultiAgentCLI()
        
        # Mock LLM to return instantly
        mock_llm = MagicMock()
        mock_llm.generate_response = AsyncMock(return_value="Test response")
        cli.coach.llm_service = mock_llm
        
        # Mock eval command to return instantly
        mock_eval_result = MagicMock()
        mock_eval_result.overall_score = 8.5
        cli.eval_command.run_comprehensive_eval = AsyncMock(return_value=mock_eval_result)
        cli.eval_command.save_report = AsyncMock()
        cli.eval_command.format_report = MagicMock(return_value="Mock report")
        
        # Mock deep thoughts generator
        cli.deep_thoughts_generator.generate_deep_thoughts = AsyncMock(
            return_value="Mock deep thoughts"
        )
        
        return cli
    
    @pytest.mark.asyncio
    async def test_cli_initializes(self, mock_cli):
        """Test that CLI initializes without errors."""
        assert mock_cli.coach is not None
        assert mock_cli.multi_agent_enabled is False
    
    @pytest.mark.asyncio
    async def test_coach_responds_to_message(self, mock_cli):
        """Test basic message processing."""
        response = await mock_cli.process_input("Hello")
        assert response is not None
        assert "Test response" in response
    
    @pytest.mark.asyncio
    async def test_coach_handles_stop_command(self, mock_cli):
        """Test stop command handling."""
        # Add a message first
        await mock_cli.process_input("Hello")
        # Now stop - returns empty string and prints to stdout
        response = await mock_cli.process_input("stop")
        assert response == ""  # Stop command returns empty string
    
    @pytest.mark.asyncio
    async def test_coach_agent_request(self, mock_cli):
        """Test agent request handling."""
        request = AgentRequest(
            from_agent="test",
            to_agent="coach",
            query="Test query",
            context={"user_id": "test"}
        )
        
        response = await mock_cli.coach.handle_request(request)
        assert response.content == "Test response"
    
    def test_single_vs_multi_agent_mode(self):
        """Test mode switching via environment variable."""
        # Single agent mode
        os.environ["DISABLE_MULTI_AGENT"] = "true"
        cli1 = MultiAgentCLI()
        assert cli1.multi_agent_enabled is False
        
        # Multi agent mode  
        os.environ["DISABLE_MULTI_AGENT"] = "false"
        cli2 = MultiAgentCLI()
        assert cli2.multi_agent_enabled is True
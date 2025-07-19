"""Tests for multi-agent CLI interface."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.interface.multi_agent_cli import MultiAgentCLI


class TestMultiAgentCLI:
    """Test multi-agent CLI initialization and basic functionality."""
    
    @patch('src.interface.multi_agent_cli.LLMFactory')
    @patch('src.interface.multi_agent_cli.EventBus')
    def test_cli_initialization(self, mock_event_bus, mock_llm_factory):
        """Test that MultiAgentCLI initializes correctly."""
        # Mock the LLM service
        mock_llm_service = MagicMock()
        mock_llm_factory.create_cheap_service.return_value = mock_llm_service
        
        # Mock EventBus
        mock_event_bus.return_value = MagicMock()
        
        # Create CLI - should not raise errors
        cli = MultiAgentCLI()
        
        # Verify components were created
        assert cli.coach is not None
        assert cli.memory_agent is not None
        assert cli.personal_content_agent is not None
        assert cli.mcp_agent is not None
        
        # Verify LLM factory was called correctly
        mock_llm_factory.create_cheap_service.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that agents are initialized when running."""
        with patch('src.interface.multi_agent_cli.LLMFactory') as mock_llm_factory:
            # Mock the LLM service
            mock_llm_service = MagicMock()
            mock_llm_factory.create_cheap_service.return_value = mock_llm_service
            
            # Create CLI
            cli = MultiAgentCLI()
            
            # Mock agent initialization
            cli.memory_agent.initialize = AsyncMock()
            cli.personal_content_agent.initialize = AsyncMock()
            cli.mcp_agent.initialize = AsyncMock()
            cli.coach.initialize = AsyncMock()
            
            # Call initialize agents
            await cli._initialize_agents()
            
            # Verify all agents were initialized
            cli.memory_agent.initialize.assert_called_once()
            cli.personal_content_agent.initialize.assert_called_once()
            cli.mcp_agent.initialize.assert_called_once()
            cli.coach.initialize.assert_called_once()
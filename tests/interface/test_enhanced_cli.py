"""Tests for enhanced CLI with evaluation capabilities."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import asyncio

from src.interface.enhanced_cli import EnhancedCLI
from src.agents.coach_agent import DiaryCoach
from src.events.bus import EventBus


class TestEnhancedCLI:
    """Test enhanced CLI with evaluation mode."""
    
    @pytest.fixture
    async def mock_coach(self):
        """Mock diary coach for testing."""
        coach = Mock(spec=DiaryCoach)
        coach.process_message = AsyncMock()
        coach.llm_service = Mock()
        coach.llm_service.session_cost = 0.0234
        return coach
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus for testing."""
        return Mock(spec=EventBus)
    
    @pytest.fixture
    async def enhanced_cli(self, mock_coach, mock_event_bus):
        """Enhanced CLI instance for testing."""
        cli = EnhancedCLI(mock_coach, mock_event_bus)
        return cli
    
    @pytest.mark.asyncio
    async def test_cli_evaluation_mode(self, enhanced_cli):
        """Test CLI generates evaluation report on stop command."""
        # Mock responses
        response1 = Mock()
        response1.content = "Good morning Michael! What's the one challenge you're ready to tackle today?"
        response1.timestamp = datetime.now()
        
        response2 = Mock()
        response2.content = "That sounds like an important priority. What specific outcome would make you feel like you've succeeded with the roadmap today?"
        response2.timestamp = datetime.now()
        
        enhanced_cli.coach.process_message.side_effect = [response1, response2]
        
        # Simulate conversation
        result1 = await enhanced_cli.process_input("good morning")
        assert result1 is not None
        
        result2 = await enhanced_cli.process_input("I need to finish my product roadmap")
        assert result2 is not None
        
        # Process stop command - should trigger evaluation
        with patch('builtins.print') as mock_print:
            result3 = await enhanced_cli.process_input("stop")
            assert result3 is None  # Stop returns None
            
            # Should display evaluation report
            printed_output = ' '.join([str(call) for call in mock_print.call_args_list])
            assert "Conversation Evaluation" in printed_output
            assert "Total Cost:" in printed_output
            assert "Coaching Effectiveness:" in printed_output
            assert "Response Speed:" in printed_output
            assert "Add notes" in printed_output
    
    @pytest.mark.asyncio
    async def test_performance_tracking(self, enhanced_cli):
        """Test that response times are tracked."""
        # Mock a response
        response = Mock()
        response.content = "Test response"
        response.timestamp = datetime.now()
        enhanced_cli.coach.process_message.return_value = response
        
        # Process a message
        await enhanced_cli.process_input("test message")
        
        # Should have tracked at least one response time
        assert len(enhanced_cli.performance_tracker.response_times) == 1
        assert enhanced_cli.performance_tracker.response_times[0] > 0
    
    @pytest.mark.asyncio
    async def test_report_command(self, enhanced_cli):
        """Test report command generates evaluation report."""
        # Add some conversation history
        enhanced_cli.conversation_history = [
            {"role": "user", "content": "good morning", "timestamp": datetime.now()},
            {"role": "assistant", "content": "Good morning Michael!", "timestamp": datetime.now()}
        ]
        
        with patch('builtins.print') as mock_print:
            result = await enhanced_cli.process_input("report")
            assert result is not None
            
            # Should display evaluation report
            printed_output = ' '.join([str(call) for call in mock_print.call_args_list])
            assert "Evaluation Report" in printed_output
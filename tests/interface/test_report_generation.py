"""Tests for report generation flow in enhanced CLI."""

import pytest
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from src.interface.enhanced_cli import EnhancedCLI
from src.agents.coach_agent import DiaryCoach
from src.events.bus import EventBus
from src.evaluation.reporting.reporter import EvaluationReport


class TestReportGeneration:
    """Test comprehensive report generation workflow."""
    
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
        # Add some conversation history
        cli.conversation_history = [
            {"role": "user", "content": "I want to be more productive", "timestamp": datetime.now()},
            {"role": "assistant", "content": "What specific productivity challenge are you facing?", "timestamp": datetime.now()},
            {"role": "user", "content": "I waste too much time on emails", "timestamp": datetime.now()},
            {"role": "assistant", "content": "Can you commit to checking emails only twice daily this week?", "timestamp": datetime.now()},
        ]
        return cli
    
    @pytest.fixture
    def temp_docs_dir(self):
        """Create temporary docs/prototype directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs" / "prototype"
            docs_dir.mkdir(parents=True)
            yield docs_dir
    
    @pytest.mark.asyncio
    async def test_stop_command_variations(self, enhanced_cli):
        """Test that various stop command variations trigger evaluation."""
        stop_commands = [
            "stop", "stop here", "end conversation", "go to report",
            "generate report", "evaluate", "evaluation", "finish",
            "end session", "wrap up", "that's enough"
        ]
        
        for command in stop_commands:
            with patch.object(enhanced_cli, '_handle_stop_command') as mock_handle:
                result = await enhanced_cli.process_input(command)
                mock_handle.assert_called_once()
                assert result is not None
                assert "Light evaluation report generated" in result
                mock_handle.reset_mock()
    
    @pytest.mark.asyncio
    async def test_deep_report_command_variations(self, enhanced_cli):
        """Test that various deep report command variations work."""
        deep_commands = [
            "deep report", "detailed report", "enhanced report",
            "deep analysis", "full report", "comprehensive report"
        ]
        
        for command in deep_commands:
            with patch.object(enhanced_cli, '_handle_deep_report_command') as mock_handle:
                result = await enhanced_cli.process_input(command)
                mock_handle.assert_called_once()
                assert result is not None
                assert "Deep evaluation report generated" in result
                mock_handle.reset_mock()
    
    @pytest.mark.asyncio
    async def test_light_report_generation_creates_file(self, enhanced_cli, temp_docs_dir):
        """Test that light report actually creates markdown file."""
        # Mock the docs/prototype directory path
        with patch('src.interface.enhanced_cli.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 6, 29, 14, 30, 45)
            mock_datetime.strftime = datetime.strftime
            
            # Mock file writing
            with patch('builtins.open', create=True) as mock_open, \
                 patch('os.makedirs') as mock_makedirs, \
                 patch.object(enhanced_cli, '_get_input', return_value="Test notes"):
                
                # Mock the evaluation report
                mock_eval = Mock(spec=EvaluationReport)
                mock_eval.save_as_markdown = Mock()
                mock_eval.overall_score = 0.75
                mock_eval.behavioral_scores = [
                    Mock(analyzer_name="ActionOrientation", value=0.8),
                    Mock(analyzer_name="SpecificityPush", value=0.7)
                ]
                
                with patch.object(enhanced_cli.evaluation_reporter, 'generate_light_report', return_value=mock_eval):
                    # Call the stop command
                    result = await enhanced_cli.process_input("stop")
                    
                    # Verify the result
                    assert result is not None
                    assert "Light evaluation report generated" in result
                    
                    # Verify report was generated and saved
                    mock_eval.save_as_markdown.assert_called_once()
                    expected_path = "docs/prototype/eval_20250629_143045.md"
                    mock_eval.save_as_markdown.assert_called_with(expected_path)
                    
                    # Verify the evaluation report was assigned
                    assert enhanced_cli.current_eval == mock_eval
                    assert hasattr(enhanced_cli.current_eval, 'report_file_path')
                    assert enhanced_cli.current_eval.report_file_path == expected_path
    
    @pytest.mark.asyncio
    async def test_deep_report_upgrades_existing_file(self, enhanced_cli):
        """Test that deep report upgrades existing light report file."""
        # Set up existing evaluation with file path
        mock_existing_eval = Mock(spec=EvaluationReport)
        mock_existing_eval.report_file_path = "docs/prototype/eval_20250629_143045.md"
        mock_existing_eval.user_notes = "Initial notes"
        enhanced_cli.current_eval = mock_existing_eval
        
        # Mock the deep evaluation
        mock_deep_eval = Mock(spec=EvaluationReport)
        mock_deep_eval.save_as_markdown = Mock()
        
        with patch.object(enhanced_cli, '_get_input', return_value="skip"), \
             patch.object(enhanced_cli.evaluation_reporter, 'generate_deep_report', return_value=mock_deep_eval):
            
            result = await enhanced_cli.process_input("deep report")
            
            # Verify deep report was generated
            assert result is not None
            assert "Deep evaluation report generated" in result
            
            # Verify the deep report was saved to same file (upgrade)
            enhanced_cli.evaluation_reporter.generate_deep_report.assert_called_once()
            call_args = enhanced_cli.evaluation_reporter.generate_deep_report.call_args
            assert call_args[1]['user_notes'] == "Initial notes"  # Used existing notes
    
    @pytest.mark.asyncio
    async def test_deep_report_without_existing_report_shows_error(self, enhanced_cli):
        """Test that deep report without existing report shows appropriate error."""
        # Clear any existing evaluation
        enhanced_cli.current_eval = None
        
        with patch('builtins.print') as mock_print:
            result = await enhanced_cli.process_input("deep report")
            
            # Should show error message
            mock_print.assert_called_with("No existing report found. Please run 'stop' command first.")
    
    @pytest.mark.asyncio
    async def test_full_workflow_stop_then_deep_report(self, enhanced_cli):
        """Test complete workflow: stop -> deep report."""
        # Mock light evaluation
        mock_light_eval = Mock(spec=EvaluationReport)
        mock_light_eval.save_as_markdown = Mock()
        mock_light_eval.overall_score = 0.75
        mock_light_eval.behavioral_scores = []
        mock_light_eval.report_file_path = "docs/prototype/eval_test.md"
        mock_light_eval.user_notes = "Initial notes"
        
        # Mock deep evaluation
        mock_deep_eval = Mock(spec=EvaluationReport)
        mock_deep_eval.save_as_markdown = Mock()
        
        with patch.object(enhanced_cli, '_get_input', side_effect=["Initial notes", "skip"]), \
             patch.object(enhanced_cli.evaluation_reporter, 'generate_light_report', return_value=mock_light_eval), \
             patch.object(enhanced_cli.evaluation_reporter, 'generate_deep_report', return_value=mock_deep_eval):
            
            # Step 1: Stop command generates light report
            stop_result = await enhanced_cli.process_input("stop")
            assert stop_result is not None
            assert "Light evaluation report generated" in stop_result
            assert enhanced_cli.current_eval == mock_light_eval
            
            # Step 2: Deep report upgrades existing report
            deep_result = await enhanced_cli.process_input("deep report")
            assert deep_result is not None
            assert "Deep evaluation report generated" in deep_result
            assert enhanced_cli.current_eval == mock_deep_eval
            
            # Verify both reports were saved
            mock_light_eval.save_as_markdown.assert_called_once()
            mock_deep_eval.save_as_markdown.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_light_report_generation(self, enhanced_cli):
        """Test error handling when light report generation fails."""
        with patch.object(enhanced_cli, '_get_input', return_value="Test notes"), \
             patch.object(enhanced_cli.evaluation_reporter, 'generate_light_report', side_effect=Exception("Test error")), \
             patch.object(enhanced_cli, '_generate_simple_evaluation') as mock_fallback, \
             patch('builtins.print') as mock_print:
            
            result = await enhanced_cli.process_input("stop")
            
            # Should fall back to simple evaluation
            mock_fallback.assert_called_once()
            mock_print.assert_any_call("Error generating evaluation: Test error")
    
    @pytest.mark.asyncio
    async def test_report_content_includes_conversation_transcript(self, enhanced_cli):
        """Test that generated reports include conversation transcript."""
        # Create a real EvaluationReport to test markdown generation
        from src.evaluation.reporting.reporter import EvaluationReport
        
        conversation_metadata = {
            "report_id": 1,
            "messages": enhanced_cli.conversation_history,
            "persona_type": "Real User",
            "scenario": "CLI Session",
            "breakthrough_achieved": False,
            "final_resistance_level": 0.5
        }
        
        eval_report = EvaluationReport(
            timestamp=datetime.now(),
            conversation_metadata=conversation_metadata,
            response_times_ms=[500, 750],
            percentile_80=750,
            responses_under_1s_percentage=0.5,
            behavioral_scores=[],
            overall_score=0.75,
            user_notes="Test user notes",
            ai_reflection="Test AI reflection"
        )
        
        # Generate markdown and check content
        markdown = eval_report.to_markdown()
        
        # Should include conversation transcript
        assert "## Conversation Transcript" in markdown
        assert "**User**: I want to be more productive" in markdown
        assert "**Coach**: What specific productivity challenge are you facing?" in markdown
        assert "**User**: I waste too much time on emails" in markdown
        assert "**Coach**: Can you commit to checking emails only twice daily this week?" in markdown
    
    @pytest.mark.asyncio
    async def test_exit_commands_still_work(self, enhanced_cli):
        """Test that exit commands still properly exit."""
        exit_commands = ["exit", "quit"]
        
        for command in exit_commands:
            result = await enhanced_cli.process_input(command)
            assert result is None  # Should return None to exit CLI
    
    @pytest.mark.asyncio
    async def test_evaluation_reporter_generate_deep_report_method_exists(self):
        """Test that the generate_deep_report method exists and can be called."""
        from src.evaluation.reporting.reporter import EvaluationReporter
        from src.evaluation.generator import GeneratedConversation
        from src.evaluation.analyzers.base import BaseAnalyzer, AnalysisScore
        
        # Create a mock conversation
        conversation = GeneratedConversation(
            messages=[
                {"role": "user", "content": "I want to be more productive"},
                {"role": "assistant", "content": "What specific productivity challenge are you facing?"},
                {"role": "user", "content": "I waste too much time on emails"},
                {"role": "assistant", "content": "Can you commit to checking emails only twice daily this week?"}
            ],
            persona_type="Real User",
            scenario="CLI Session",
            timestamp=datetime.now(),
            breakthrough_achieved=False,
            final_resistance_level=0.5
        )
        
        # Create mock analyzers
        mock_analyzer = Mock(spec=BaseAnalyzer)
        mock_analyzer.name = "TestAnalyzer"
        mock_analyzer.analyze = AsyncMock(return_value=AnalysisScore(
            value=0.8,
            reasoning="Test reasoning",
            analyzer_name="TestAnalyzer"
        ))
        
        # Create reporter and test method exists
        reporter = EvaluationReporter()
        assert hasattr(reporter, 'generate_deep_report'), "generate_deep_report method should exist"
        
        # Test method can be called (mock the LLM service to avoid API calls)
        with patch.object(reporter, 'opus_service') as mock_opus:
            mock_opus.generate_response = AsyncMock(return_value="Test AI reflection")
            
            result = await reporter.generate_deep_report(
                conversation=conversation,
                user_notes="Test notes",
                analyzers=[mock_analyzer],
                performance_data={"response_times_ms": [500, 750], "percentile_80": 750, "responses_under_1s_percentage": 0.5}
            )
            
            # Verify result
            assert result is not None
            assert hasattr(result, 'ai_reflection')
            assert hasattr(result, 'behavioral_scores')
            assert hasattr(result, 'overall_score')
            assert result.user_notes == "Test notes"
            
            # Verify the analyzer was called
            mock_analyzer.analyze.assert_called_once()
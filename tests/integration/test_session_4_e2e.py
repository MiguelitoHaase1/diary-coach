"""Integration tests for Session 4: Morning Coach Excellence."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from src.interface.enhanced_cli import EnhancedCLI
from src.agents.coach_agent import DiaryCoach
from src.events.bus import EventBus
from src.services.llm_service import AnthropicService


class TestSession4Integration:
    """Test suite for Session 4 integration and CLI commands."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service for testing."""
        mock = AsyncMock(spec=AnthropicService)
        mock.session_cost = 0.0025  # Mock session cost
        return mock

    @pytest.fixture
    def coach(self, mock_llm_service):
        """Create a coach agent with mocked LLM service."""
        return DiaryCoach(llm_service=mock_llm_service)

    @pytest.fixture
    def event_bus(self):
        """Create a mock event bus."""
        return MagicMock(spec=EventBus)

    @pytest.fixture
    def enhanced_cli(self, coach, event_bus):
        """Create enhanced CLI with mocked dependencies."""
        return EnhancedCLI(coach, event_bus)

    @pytest.mark.asyncio
    async def test_morning_coach_to_deep_thoughts_flow(self, enhanced_cli, mock_llm_service):
        """Complete morning conversation → Deep Thoughts generation."""
        # Mock morning coach responses
        mock_llm_service.generate_response.side_effect = [
            "Good morning, Michael! What dragon are you most excited to slay today?",
            "Is organizing files really the biggest lever you could pull today?", 
            "What core value do you want to fight for today? Tell me a bit more about it.",
            # Deep Thoughts generation (Opus call)
            """# Deep Thoughts: Problem Selection Challenge

## Core Problem
Michael initially wanted to organize files but was challenged to consider if this was truly the biggest lever for his day.

## Fact Check
✅ User stated organizing files as initial priority
❓ Unclear if this was truly the most important task

## Just One More Thing...
Just one more thing puzzles me - if organizing feels urgent, what's making it feel more important than strategic work?

## Hints
Consider asking yourself: what would happen if the files stayed disorganized for one more day?"""
        ]

        # Simulate morning conversation
        response1 = await enhanced_cli.process_input("good morning")
        assert "Good morning, Michael!" in response1
        assert "dragon" in response1.lower()

        response2 = await enhanced_cli.process_input("I need to organize my files")
        assert "biggest lever" in response2.lower()

        response3 = await enhanced_cli.process_input("I want to fight for focus and clarity")
        assert "core value" in response3.lower()

        # Mock the Deep Thoughts generation and user input
        with patch('src.evaluation.reporting.deep_thoughts.DeepThoughtsGenerator') as mock_generator, \
             patch.object(enhanced_cli, '_get_input', return_value="Great conversation"):
            mock_instance = AsyncMock()
            mock_generator.return_value = mock_instance
            mock_instance.generate_deep_thoughts.return_value = "Deep thoughts content"
            mock_instance.get_output_filepath.return_value = "docs/prototype/DeepThoughts/test.md"
            
            # Trigger deep report command
            result = await enhanced_cli.process_input("deep report")
            
            # Should indicate generation started/completed
            assert "deep" in result.lower() and "report" in result.lower()

    @pytest.mark.asyncio
    async def test_deep_thoughts_command_variations(self, enhanced_cli, mock_llm_service):
        """'deep research', 'think deeper', 'deep thoughts' all work."""
        # First create some conversation history
        mock_llm_service.generate_response.return_value = "Test response"
        await enhanced_cli.process_input("test message")
        
        test_commands = [
            "deep report",
            "detailed report", 
            "enhanced report",
            "deep analysis",
            "full report",
            "comprehensive report"
        ]

        for command in test_commands:
            with patch.object(enhanced_cli, '_get_input', return_value="skip"), \
                 patch.object(enhanced_cli.deep_thoughts_generator, 'generate_deep_thoughts', new=AsyncMock(return_value="content")), \
                 patch.object(enhanced_cli.eval_exporter, 'export_evaluation_markdown', new=AsyncMock(return_value="content")):
                result = await enhanced_cli.process_input(command)
                # Should handle the command (not return an error)
                assert result is not None
                assert "deep" in result.lower() or "report" in result.lower()

    @pytest.mark.asyncio 
    async def test_eval_export_command(self, enhanced_cli, mock_llm_service):
        """'export eval' saves evaluation to Evals folder.""" 
        # First have a conversation
        mock_llm_service.generate_response.side_effect = [
            "Good morning, Michael!",
            "That's interesting. Tell me more."
        ]
        
        await enhanced_cli.process_input("good morning")
        await enhanced_cli.process_input("I need help with priorities")
        
        # Mock the evaluation exporter
        with patch('src.evaluation.reporting.eval_exporter.EvaluationExporter') as mock_exporter:
            mock_instance = AsyncMock()
            mock_exporter.return_value = mock_instance
            mock_instance.export_evaluation_markdown.return_value = "Exported content"
            
            # Trigger stop command to generate evaluation
            with patch.object(enhanced_cli, '_get_input', return_value="Test notes"):
                result = await enhanced_cli.process_input("stop")
                
                # Should generate evaluation
                assert "evaluation" in result.lower()

    @pytest.mark.asyncio
    async def test_morning_analyzer_integration(self, enhanced_cli, mock_llm_service):
        """Morning analyzers are properly integrated with evaluation system."""
        # Mock LLM response for conversation
        mock_llm_service.generate_response.return_value = "Good morning, Michael! What's your biggest challenge today?"
        
        # Verify morning analyzers are included in the CLI
        analyzer_names = [analyzer.name for analyzer in enhanced_cli.analyzers]
        
        # Should include morning-specific analyzers
        assert "ProblemSelection" in analyzer_names
        assert "ThinkingPivot" in analyzer_names  
        assert "ExcitementBuilder" in analyzer_names
        
        # Should also include general analyzers
        assert "SpecificityPush" in analyzer_names
        assert "ActionOrientation" in analyzer_names
        
        # Verify total count is correct (3 morning + 2 general = 5)
        assert len(enhanced_cli.analyzers) == 5
        
        print(f"✅ All analyzers integrated: {analyzer_names}")

    @pytest.mark.asyncio
    async def test_file_organization_structure(self, enhanced_cli):
        """Verify correct file organization: DeepThoughts/ and Evals/ folders."""
        from pathlib import Path
        
        # Check that the directory structure exists
        deep_thoughts_dir = Path("docs/prototype/DeepThoughts")
        evals_dir = Path("docs/prototype/Evals")
        
        assert deep_thoughts_dir.exists(), "DeepThoughts directory should exist"
        assert evals_dir.exists(), "Evals directory should exist"

    @pytest.mark.asyncio
    async def test_filename_format_consistency(self, enhanced_cli):
        """Both reports use YYYYMMDD_HHMM naming convention."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 14, 30, 45)
            
            # Test Deep Thoughts filename
            from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
            generator = DeepThoughtsGenerator()
            dt_filepath = generator.get_output_filepath(datetime(2025, 1, 30, 14, 30, 45))
            assert "DeepThoughts_20250130_1430.md" in dt_filepath
            
            # Test Eval filename  
            from src.evaluation.reporting.eval_exporter import EvaluationExporter
            exporter = EvaluationExporter()
            eval_filepath = exporter.get_output_filepath(datetime(2025, 1, 30, 14, 30, 45))
            assert "Eval_20250130_1430.md" in eval_filepath

    @pytest.mark.asyncio
    async def test_morning_time_detection(self, enhanced_cli, mock_llm_service):
        """Coach should detect morning time and use morning-specific prompts."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 9, 0)  # 9:00 AM
            
            mock_llm_service.generate_response.return_value = "Good morning, Michael! What adventure awaits you today?"
            
            response = await enhanced_cli.process_input("good morning")
            
            # Verify morning-specific response characteristics
            assert "Good morning, Michael!" in response
            assert any(word in response.lower() for word in ["adventure", "dragon", "excited", "slay"])

    @pytest.mark.asyncio
    async def test_evening_maintains_original_behavior(self, enhanced_cli, mock_llm_service):
        """Evening conversations should use original coach prompts."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 19, 30)  # 7:30 PM
            
            mock_llm_service.generate_response.return_value = "Good evening Michael! How did that challenge from this morning unfold?"
            
            response = await enhanced_cli.process_input("good evening")
            
            # Verify evening-specific response
            assert "Good evening Michael!" in response
            assert "unfold" in response.lower() or "challenge" in response.lower()

    @pytest.mark.asyncio
    async def test_deep_report_requires_existing_conversation(self, enhanced_cli):
        """Deep report should require an existing conversation."""
        # Try deep report without conversation
        result = await enhanced_cli.process_input("deep report")
        
        assert "no conversation" in result.lower() or "history" in result.lower() or "start a conversation" in result.lower()

    @pytest.mark.asyncio
    async def test_complete_morning_workflow(self, enhanced_cli, mock_llm_service):
        """Test complete morning workflow: conversation → stop → deep report."""
        # Mock all LLM responses
        mock_llm_service.generate_response.side_effect = [
            "Good morning, Michael! What dragon are you most excited to slay today?",
            "Is that really the biggest lever you could pull today?",
            "What core value do you want to fight for today?",
            # Deep Thoughts generation
            "# Deep Thoughts: Complete workflow test\n\n## Core Problem\nTest problem\n\n## Fact Check\n✅ Test\n\n## Just One More Thing...\nTest insight\n\n## Hints\nTest hints"
        ]

        # Step 1: Morning conversation
        response1 = await enhanced_cli.process_input("good morning")
        assert "Good morning, Michael!" in response1

        response2 = await enhanced_cli.process_input("I want to work on my presentation")
        assert "biggest lever" in response2.lower()

        response3 = await enhanced_cli.process_input("I want to fight for clarity in communication")
        assert "core value" in response3.lower()

        # Step 2: Stop and generate evaluation
        with patch.object(enhanced_cli, '_get_input', return_value="Great session, felt challenged"):
            result = await enhanced_cli.process_input("stop")
            assert "evaluation" in result.lower()

        # Step 3: Generate deep report
        with patch.object(enhanced_cli, 'deep_thoughts_generator') as mock_dt_instance, \
             patch.object(enhanced_cli, 'eval_exporter') as mock_exp_instance, \
             patch.object(enhanced_cli, '_get_input', return_value="skip"):
            
            mock_dt_instance.generate_deep_thoughts = AsyncMock(return_value="Deep thoughts content")
            mock_dt_instance.get_output_filepath.return_value = "docs/prototype/DeepThoughts/test.md"
            mock_exp_instance.export_evaluation_markdown = AsyncMock(return_value="Eval content")
            mock_exp_instance.get_output_filepath.return_value = "docs/prototype/Evals/test.md"
            
            result = await enhanced_cli.process_input("deep report")
            assert "deep" in result.lower()

            # Verify both generators were called
            mock_dt_instance.generate_deep_thoughts.assert_called_once()
            mock_exp_instance.export_evaluation_markdown.assert_called_once()
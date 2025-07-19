"""Integration tests for Session 4: Morning Coach Excellence."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from src.interface.multi_agent_cli import MultiAgentCLI
import os


class TestSession4Integration:
    """Test suite for Session 4 integration and CLI commands."""

    @pytest.fixture
    def cli(self):
        """Create a multi-agent CLI for testing."""
        # Set environment to disable multi-agent for simpler testing
        os.environ["DISABLE_MULTI_AGENT"] = "true"
        
        # Create CLI
        cli = MultiAgentCLI()
        
        # Mock the LLM service
        mock_llm = AsyncMock()
        mock_llm.session_cost = 0.0025
        cli.coach.llm_service = mock_llm
        
        return cli


    @pytest.mark.asyncio
    async def test_morning_coach_to_deep_thoughts_flow(self, cli):
        """Complete morning conversation → Deep Thoughts generation."""
        # Mock morning coach responses
        cli.coach.llm_service.generate_response.side_effect = [
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
        response1 = await cli.process_input("good morning")
        assert "Good morning, Michael!" in response1
        assert "dragon" in response1.lower()

        response2 = await cli.process_input("I need to organize my files")
        assert "biggest lever" in response2.lower()

        response3 = await cli.process_input("I want to fight for focus and clarity")
        assert "core value" in response3.lower()

        # Mock the Deep Thoughts generation and user input
        with patch('src.evaluation.reporting.deep_thoughts.DeepThoughtsGenerator') as mock_generator, \
             patch('builtins.input', return_value="Great conversation"):
            mock_instance = AsyncMock()
            mock_generator.return_value = mock_instance
            mock_instance.generate_deep_thoughts.return_value = "Deep thoughts content"
            mock_instance.get_output_filepath.return_value = "docs/prototype/DeepThoughts/test.md"
            
            # Trigger deep report command
            result = await cli.process_input("deep report")
            
            # Should indicate generation started/completed
            assert "deep" in result.lower() and "report" in result.lower()

    @pytest.mark.asyncio
    async def test_deep_thoughts_command_variations(self, cli):
        """'deep research', 'think deeper', 'deep thoughts' all work."""
        # First create some conversation history
        cli.coach.llm_service.generate_response.return_value = "Test response"
        await cli.process_input("test message")
        
        test_commands = [
            "deep report",
            "detailed report", 
            "enhanced report",
            "deep analysis",
            "full report",
            "comprehensive report"
        ]

        for command in test_commands:
            with patch('builtins.input', return_value="skip"), \
                 patch.object(cli.deep_thoughts_generator, 'generate_deep_thoughts', new=AsyncMock(return_value="content")), \
                 patch.object(cli.deep_thoughts_generator, 'generate_deep_thoughts', new=AsyncMock(return_value="content")):
                result = await cli.process_input(command)
                # Should handle the command (not return an error)
                assert result is not None
                assert "deep" in result.lower() or "report" in result.lower()

    @pytest.mark.asyncio 
    async def test_deep_thoughts_generation(self, cli):
        """Deep thoughts generation after conversation.""" 
        # First have a conversation
        cli.coach.llm_service.generate_response.side_effect = [
            "Good morning, Michael!",
            "That's interesting. Tell me more."
        ]
        
        await cli.process_input("good morning")
        await cli.process_input("I need help with priorities")
        
        # Mock the deep thoughts generator
        with patch.object(cli.deep_thoughts_generator, 'generate_deep_thoughts', new=AsyncMock(return_value="Deep thoughts content")):
            # Trigger stop command to generate evaluation
            with patch('builtins.input', return_value="Test notes"):
                result = await cli.process_input("stop")
                
                # Should generate evaluation
                assert "evaluation" in result.lower()

    # @pytest.mark.asyncio
    # async def test_morning_analyzer_integration(self, cli):
    #     """Morning analyzers are properly integrated with evaluation system."""
    #     # This test is for the old 7-analyzer system that was removed in Session 7
    #     # The new system uses 5 criteria integrated into Deep Thoughts
    #     pass

    @pytest.mark.asyncio
    async def test_file_organization_structure(self, cli):
        """Verify correct file organization: DeepThoughts/ and Evals/ folders."""
        from pathlib import Path
        
        # Check that the directory structure exists
        deep_thoughts_dir = Path("docs/prototype/DeepThoughts")
        evals_dir = Path("docs/prototype/Evals")
        
        assert deep_thoughts_dir.exists(), "DeepThoughts directory should exist"
        assert evals_dir.exists(), "Evals directory should exist"

    @pytest.mark.asyncio
    async def test_filename_format_consistency(self, cli):
        """Both reports use YYYYMMDD_HHMM naming convention."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 14, 30, 45)
            
            # Test Deep Thoughts filename
            from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
            generator = DeepThoughtsGenerator()
            dt_filepath = generator.get_output_filepath(datetime(2025, 1, 30, 14, 30, 45))
            assert "DeepThoughts_20250130_1430.md" in dt_filepath
            
            # No longer test Eval filename since eval_exporter is deprecated

    @pytest.mark.asyncio
    async def test_morning_time_detection(self, cli):
        """Coach should detect morning time and use morning-specific prompts."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 9, 0)  # 9:00 AM
            
            cli.coach.llm_service.generate_response.return_value = "Good morning, Michael! What adventure awaits you today?"
            
            response = await cli.process_input("good morning")
            
            # Verify morning-specific response characteristics
            assert "Good morning, Michael!" in response
            assert any(word in response.lower() for word in ["adventure", "dragon", "excited", "slay"])

    @pytest.mark.asyncio
    async def test_evening_maintains_original_behavior(self, cli):
        """Evening conversations should use original coach prompts."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 19, 30)  # 7:30 PM
            
            cli.coach.llm_service.generate_response.return_value = "Good evening Michael! How did that challenge from this morning unfold?"
            
            response = await cli.process_input("good evening")
            
            # Verify evening-specific response
            assert "Good evening Michael!" in response
            assert "unfold" in response.lower() or "challenge" in response.lower()

    @pytest.mark.asyncio
    async def test_deep_report_requires_existing_conversation(self, cli):
        """Deep report should require an existing conversation."""
        # Try deep report without conversation
        result = await cli.process_input("deep report")
        
        assert "no conversation" in result.lower() or "history" in result.lower() or "start a conversation" in result.lower()

    @pytest.mark.asyncio
    async def test_complete_morning_workflow(self, cli):
        """Test complete morning workflow: conversation → stop → deep report."""
        # Mock all LLM responses
        cli.coach.llm_service.generate_response.side_effect = [
            "Good morning, Michael! What dragon are you most excited to slay today?",
            "Is that really the biggest lever you could pull today?",
            "What core value do you want to fight for today?",
            # Deep Thoughts generation
            "# Deep Thoughts: Complete workflow test\n\n## Core Problem\nTest problem\n\n## Fact Check\n✅ Test\n\n## Just One More Thing...\nTest insight\n\n## Hints\nTest hints"
        ]

        # Step 1: Morning conversation
        response1 = await cli.process_input("good morning")
        assert "Good morning, Michael!" in response1

        response2 = await cli.process_input("I want to work on my presentation")
        assert "biggest lever" in response2.lower()

        response3 = await cli.process_input("I want to fight for clarity in communication")
        assert "core value" in response3.lower()

        # Step 2: Stop and generate evaluation
        with patch('builtins.input', return_value="Great session, felt challenged"):
            result = await cli.process_input("stop")
            assert "evaluation" in result.lower()

        # Step 3: Generate deep report
        with patch.object(cli, 'deep_thoughts_generator') as mock_dt_instance, \
             patch('builtins.input', return_value="skip"):
            
            mock_dt_instance.generate_deep_thoughts = AsyncMock(return_value="Deep thoughts content")
            mock_dt_instance.get_output_filepath.return_value = "docs/prototype/DeepThoughts/test.md"
            
            result = await cli.process_input("deep report")
            assert "deep" in result.lower()

            # Verify deep thoughts generator was called
            mock_dt_instance.generate_deep_thoughts.assert_called_once()
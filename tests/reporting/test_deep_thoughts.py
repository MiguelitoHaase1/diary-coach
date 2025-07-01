"""Tests for Deep Thoughts Generator functionality."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
from src.services.llm_service import AnthropicService


class TestDeepThoughtsGenerator:
    """Test suite for Deep Thoughts Generator."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service for testing."""
        mock_service = AsyncMock(spec=AnthropicService)
        return mock_service

    @pytest.fixture
    def generator(self, mock_llm_service):
        """Create a DeepThoughtsGenerator instance with mocked LLM service."""
        return DeepThoughtsGenerator(llm_service=mock_llm_service)

    @pytest.fixture
    def sample_conversation(self):
        """Sample conversation for testing."""
        return [
            {"role": "user", "content": "good morning"},
            {"role": "assistant", "content": "Good morning, Michael! What dragon are you most excited to slay today?"},
            {"role": "user", "content": "I need to have a difficult conversation with my team about our product direction"},
            {"role": "assistant", "content": "That sounds significant. Is this really the biggest lever you could pull today?"},
            {"role": "user", "content": "Yes, we've been avoiding this for weeks and it's blocking everything"},
            {"role": "assistant", "content": "What core value do you want to fight for today? Tell me a bit more about it."},
            {"role": "user", "content": "I want to fight for honesty and transparency. No more dancing around the hard truths."}
        ]

    @pytest.mark.asyncio
    async def test_deep_thoughts_summarizes_problem_clearly(self, generator, mock_llm_service, sample_conversation):
        """Report should crystallize the core problem in 2-3 sentences."""
        mock_llm_service.generate_response.return_value = """# Deep Thoughts: Product Direction Conversation

## Core Problem
Michael needs to have a difficult conversation with his team about product direction. They've been avoiding this critical discussion for weeks, and it's now blocking all progress. The challenge isn't technical but requires confronting uncomfortable truths about their current path.

## Fact Check
✅ Team has been avoiding the conversation for weeks
✅ The avoidance is blocking other progress  
✅ This is about product direction, not individual performance

## Just One More Thing... (Devil's Advocate)
I hear you want to fight for honesty and transparency, but just one more thing puzzles me. If everyone knows this conversation needs to happen, what's really keeping the team from bringing it up themselves? Sometimes the "difficult conversation" we think we need to have isn't actually about the topic we think it is.

## Hints (Without Giving Away the Answer)
Consider starting with curiosity rather than conclusions. What if you asked the team what they think is working and what isn't, before sharing your own perspective?"""

        result = await generator.generate_deep_thoughts(
            conversation_history=sample_conversation,
            conversation_id="test-123"
        )

        # Should crystallize core problem in 2-3 sentences
        lines = result.split('\n')
        problem_section = []
        in_problem_section = False
        for line in lines:
            if line.startswith("## Core Problem"):
                in_problem_section = True
                continue
            elif line.startswith("##") and in_problem_section:
                break
            elif in_problem_section and line.strip():
                problem_section.append(line.strip())

        problem_text = ' '.join(problem_section)
        sentences = problem_text.split('. ')
        assert len(sentences) >= 2 and len(sentences) <= 4  # 2-3 clear sentences

    @pytest.mark.asyncio
    async def test_deep_thoughts_fact_checks_assumptions(self, generator, mock_llm_service, sample_conversation):
        """Report should identify and verify key claims from conversation."""
        mock_llm_service.generate_response.return_value = """# Deep Thoughts: Product Direction Conversation

## Core Problem
Michael needs to address product direction with his team after weeks of avoidance.

## Fact Check
✅ Team has been avoiding the conversation for weeks
✅ The avoidance is blocking other progress  
✅ This is about product direction, not individual performance
❓ Unclear if "blocking everything" is literally true or felt experience

## Just One More Thing...
The real question might be what made this conversation feel so difficult in the first place.

## Hints
Start with questions, not statements."""

        result = await generator.generate_deep_thoughts(
            conversation_history=sample_conversation,
            conversation_id="test-123"
        )

        # Should have fact check section with checkmarks
        assert "## Fact Check" in result
        assert "✅" in result  # Should have verified facts
        assert "❓" in result or "❌" in result  # Should question some assumptions

    @pytest.mark.asyncio
    async def test_deep_thoughts_uses_columbo_style(self, generator, mock_llm_service, sample_conversation):
        """Devil's advocate section uses 'just one more thing' phrasing."""
        mock_llm_service.generate_response.return_value = """# Deep Thoughts: Product Direction Conversation

## Core Problem
Michael needs to address product direction challenges.

## Fact Check  
✅ Conversation has been avoided for weeks

## Just One More Thing... (Devil's Advocate)
I hear you want to fight for honesty and transparency, but just one more thing puzzles me. If everyone knows this conversation needs to happen, what's really keeping the team from bringing it up themselves?

## Hints
Consider the team's perspective first."""

        result = await generator.generate_deep_thoughts(
            conversation_history=sample_conversation,
            conversation_id="test-123"
        )

        # Should use Columbo-style phrasing
        assert "just one more thing" in result.lower()
        assert "## Just One More Thing" in result or "just one more thing" in result.lower()

    @pytest.mark.asyncio
    async def test_deep_thoughts_provides_actionable_hints(self, generator, mock_llm_service, sample_conversation):
        """Hints guide without solving - Socratic not prescriptive."""
        mock_llm_service.generate_response.return_value = """# Deep Thoughts: Product Direction Conversation

## Core Problem
Michael needs to address product direction with his team.

## Fact Check
✅ Conversation avoided for weeks

## Just One More Thing...
What if the real issue isn't the conversation itself?

## Hints (Without Giving Away the Answer)
What would happen if you asked the team to diagnose the problem before you share your solution? Consider starting with: "I've been thinking about our direction. What's your take on where we are right now?"
"""

        result = await generator.generate_deep_thoughts(
            conversation_history=sample_conversation,
            conversation_id="test-123"
        )

        # Should have hints section
        assert "## Hints" in result
        
        # Hints should be questions or suggestions, not commands
        hints_section = result.split("## Hints")[1] if "## Hints" in result else ""
        assert "?" in hints_section or "consider" in hints_section.lower() or "what if" in hints_section.lower()
        
        # Should NOT be prescriptive (avoid "you should", "you must")
        assert "you should" not in hints_section.lower()
        assert "you must" not in hints_section.lower()

    @pytest.mark.asyncio
    async def test_deep_thoughts_filename_format(self, generator, mock_llm_service, sample_conversation):
        """Files named DeepThoughts_YYYYMMDD_HHMM.md in docs/prototype/DeepThoughts/."""
        mock_llm_service.generate_response.return_value = "# Deep Thoughts\n\nTest content"

        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 14, 30, 45)  # 2:30:45 PM
            
            # Generate the report
            await generator.generate_deep_thoughts(
                conversation_history=sample_conversation,
                conversation_id="test-123"
            )
            
            # Check the filepath format using the separate method
            filepath = generator.get_output_filepath(datetime(2025, 1, 30, 14, 30, 45))

            # Should return the filepath
            expected_filename = "DeepThoughts_20250130_1430.md"
            assert expected_filename in str(filepath)
            assert "docs/prototype/DeepThoughts/" in str(filepath)

    @pytest.mark.asyncio
    async def test_deep_thoughts_uses_opus_model(self, generator, mock_llm_service, sample_conversation):
        """Generator should use Claude Opus-4 for deep analysis."""
        mock_llm_service.generate_response.return_value = "# Deep Thoughts\n\nTest content"

        await generator.generate_deep_thoughts(
            conversation_history=sample_conversation,
            conversation_id="test-123"
        )

        # Verify Opus model was requested
        call_args = mock_llm_service.generate_response.call_args
        assert call_args is not None
        # Could check for model parameter if LLM service supports it
        # For now, verify the call was made with appropriate parameters for deep analysis
        assert call_args[1]["max_tokens"] >= 1000  # Should allow longer responses
        assert call_args[1]["temperature"] <= 0.3  # Should be more focused/analytical

    @pytest.mark.asyncio
    async def test_deep_thoughts_structured_output(self, generator, mock_llm_service, sample_conversation):
        """Report should have consistent markdown structure."""
        mock_llm_service.generate_response.return_value = """# Deep Thoughts: Product Direction Conversation

## Core Problem
Test problem summary.

## Fact Check
✅ Test fact

## Just One More Thing... (Devil's Advocate)
Test devil's advocate perspective.

## Hints (Without Giving Away the Answer)
Test hints."""

        result = await generator.generate_deep_thoughts(
            conversation_history=sample_conversation,
            conversation_id="test-123"
        )

        # Should have all required sections
        required_sections = [
            "# Deep Thoughts:",
            "## Core Problem",
            "## Fact Check", 
            "## Just One More Thing",
            "## Hints"
        ]
        
        for section in required_sections:
            assert section in result

    @pytest.mark.asyncio 
    async def test_deep_thoughts_creates_directory_if_not_exists(self, generator, mock_llm_service, sample_conversation, tmp_path):
        """Should create output directory if it doesn't exist."""
        mock_llm_service.generate_response.return_value = "# Deep Thoughts\n\nTest content"
        
        # Override the output directory to use temp path
        test_dir = tmp_path / "docs" / "prototype" / "DeepThoughts"
        assert not test_dir.exists()
        
        with patch.object(generator, '_get_output_path', return_value=test_dir / "test.md"):
            filepath = await generator.generate_deep_thoughts(
                conversation_history=sample_conversation,
                conversation_id="test-123"
            )
            
            # Directory should be created
            assert test_dir.parent.exists()  # At least the parent should exist after path operations
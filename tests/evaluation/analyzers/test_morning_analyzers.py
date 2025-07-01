"""Tests for morning-specific behavioral analyzers."""

import pytest
import json
from unittest.mock import AsyncMock
from src.evaluation.analyzers.morning import (
    ProblemSelectionAnalyzer,
    ThinkingPivotAnalyzer, 
    ExcitementBuilderAnalyzer
)
from src.services.llm_service import AnthropicService


class TestProblemSelectionAnalyzer:
    """Test suite for Problem Selection Analyzer."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service for testing."""
        return AsyncMock(spec=AnthropicService)

    @pytest.fixture
    def analyzer(self, mock_llm_service):
        """Create analyzer instance with mocked LLM service."""
        return ProblemSelectionAnalyzer(llm_service=mock_llm_service)

    @pytest.mark.asyncio
    async def test_problem_selection_analyzer_challenges_weak_choice(self, analyzer, mock_llm_service):
        """Should detect when coach challenges a weak problem selection."""
        # Mock LLM response for strong challenging
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.9,
            "reasoning": "Coach directly questions if organizing files is really the biggest lever today"
        })

        coach_response = "Is organizing your files really the biggest lever you could pull today?"
        context = ["User: I need to organize my files today"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.9
        assert "biggest lever" in score.reasoning
        assert score.analyzer_name == "ProblemSelection"

    @pytest.mark.asyncio
    async def test_problem_selection_analyzer_accepts_without_challenge(self, analyzer, mock_llm_service):
        """Should detect when coach accepts problem without challenging."""
        # Mock LLM response for weak challenging
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.2,
            "reasoning": "Coach accepts the stated problem without questioning if it's truly the most important"
        })

        coach_response = "That sounds like a good plan. How will you approach organizing those files?"
        context = ["User: I need to organize my files today"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.2
        assert "without questioning" in score.reasoning

    @pytest.mark.asyncio
    async def test_problem_selection_analyzer_prompts_for_priorities(self, analyzer, mock_llm_service):
        """Should detect when coach helps user examine priorities."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.8,
            "reasoning": "Coach guides user to consider what's most important rather than accepting first stated problem"
        })

        coach_response = "Before we dive into that, what's the single most important thing you could tackle today that would shift everything?"
        context = ["User: I need to catch up on emails"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.8
        assert "most important" in score.reasoning


class TestThinkingPivotAnalyzer:
    """Test suite for Thinking Pivot Analyzer."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service for testing."""
        return AsyncMock(spec=AnthropicService)

    @pytest.fixture
    def analyzer(self, mock_llm_service):
        """Create analyzer instance with mocked LLM service."""
        return ThinkingPivotAnalyzer(llm_service=mock_llm_service)

    @pytest.mark.asyncio
    async def test_thinking_pivot_analyzer_detects_reframing(self, analyzer, mock_llm_service):
        """Should detect when coach helps user reframe their thinking."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.9,
            "reasoning": "Coach offers powerful reframe from 'difficult conversation' to 'opportunity for alignment'"
        })

        coach_response = "What if this isn't a difficult conversation but an opportunity for alignment?"
        context = ["User: I need to have a difficult conversation with my team"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.9
        assert "reframe" in score.reasoning.lower()
        assert score.analyzer_name == "ThinkingPivot"

    @pytest.mark.asyncio
    async def test_thinking_pivot_analyzer_detects_perspective_shift(self, analyzer, mock_llm_service):
        """Should detect when coach creates perspective shifts."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.8,
            "reasoning": "Coach invites user to consider the root cause rather than staying with surface symptoms"
        })

        coach_response = "What if the real knot isn't time management but energy management?"
        context = ["User: I can't seem to manage my time effectively"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.8
        assert "root cause" in score.reasoning

    @pytest.mark.asyncio
    async def test_thinking_pivot_analyzer_no_reframing(self, analyzer, mock_llm_service):
        """Should detect when coach misses reframing opportunities."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.3,
            "reasoning": "Coach asks standard follow-up without challenging the framing or offering new perspective"
        })

        coach_response = "Tell me more about that conversation. What specifically concerns you?"
        context = ["User: I need to have a difficult conversation"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.3
        assert "without challenging" in score.reasoning


class TestExcitementBuilderAnalyzer:
    """Test suite for Excitement Builder Analyzer."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service for testing."""
        return AsyncMock(spec=AnthropicService)

    @pytest.fixture
    def analyzer(self, mock_llm_service):
        """Create analyzer instance with mocked LLM service."""
        return ExcitementBuilderAnalyzer(llm_service=mock_llm_service)

    @pytest.mark.asyncio
    async def test_excitement_builder_increases_energy(self, analyzer, mock_llm_service):
        """Should detect when coach builds energy and motivation."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.9,
            "reasoning": "Coach uses vivid, energizing language that transforms anxiety into adventure"
        })

        coach_response = "That sounds like an adventure! What's most exciting about the possibility of this breakthrough?"
        context = ["User: I'm nervous about this big presentation"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.9
        assert "energizing" in score.reasoning
        assert score.analyzer_name == "ExcitementBuilder"

    @pytest.mark.asyncio
    async def test_excitement_builder_detects_motivation_increase(self, analyzer, mock_llm_service):
        """Should detect when coach helps user feel eager rather than anxious."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.8,
            "reasoning": "Coach shifts focus from fear to opportunity, building genuine enthusiasm"
        })

        coach_response = "I can hear your passion for this! What happens when you picture yourself nailing this?"
        context = ["User: I'm worried about failing at this new project"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.8
        assert "enthusiasm" in score.reasoning

    @pytest.mark.asyncio
    async def test_excitement_builder_misses_energy_opportunity(self, analyzer, mock_llm_service):
        """Should detect when coach misses opportunities to build excitement."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.2,
            "reasoning": "Coach stays in problem-focused mode without building energy or motivation"
        })

        coach_response = "What are the specific challenges you're facing with this project?"
        context = ["User: I'm excited about this new opportunity but also nervous"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.2
        assert "without building energy" in score.reasoning

    @pytest.mark.asyncio
    async def test_excitement_builder_uses_vivid_language(self, analyzer, mock_llm_service):
        """Should detect when coach uses vivid, motivating language."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "score": 0.8,
            "reasoning": "Coach uses adventure metaphor to make the work feel motivating and alive"
        })

        coach_response = "What dragon are you most fired up to slay today?"
        context = ["User: good morning"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.8
        assert "adventure" in score.reasoning

    @pytest.mark.asyncio
    async def test_analyzer_fallback_behavior(self, analyzer, mock_llm_service):
        """Should handle LLM failures gracefully."""
        # Mock LLM failure
        mock_llm_service.generate_response.side_effect = Exception("Network error")

        coach_response = "What's your biggest challenge today?"
        context = ["User: good morning"]

        score = await analyzer.analyze(coach_response, context)

        assert score.value == 0.5
        assert "Analysis failed" in score.reasoning
        assert score.analyzer_name == "ExcitementBuilder"
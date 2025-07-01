"""Tests for Deep Thoughts quality evaluation."""

import pytest
import json
from unittest.mock import AsyncMock
from src.evaluation.deep_thoughts_evaluator import DeepThoughtsQualityEvaluator
from src.services.llm_service import AnthropicService


class TestDeepThoughtsQualityEvaluator:
    """Test suite for Deep Thoughts Quality Evaluator."""

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service for testing."""
        return AsyncMock(spec=AnthropicService)

    @pytest.fixture
    def evaluator(self, mock_llm_service):
        """Create evaluator instance with mocked LLM service."""
        return DeepThoughtsQualityEvaluator(llm_service=mock_llm_service)

    @pytest.fixture
    def sample_deep_thoughts_report(self):
        """Sample Deep Thoughts report for testing."""
        return """# Deep Thoughts: Product Direction Conversation

## Core Problem
Michael needs to have a difficult conversation with his team about product direction. They've been avoiding this critical discussion for weeks, and it's now blocking all progress.

## Fact Check
✅ Team has been avoiding the conversation for weeks
✅ The avoidance is blocking other progress  
❓ Unclear if "blocking everything" is literally true or felt experience

## Just One More Thing... (Devil's Advocate)
I hear you want to fight for honesty and transparency, but just one more thing puzzles me. If everyone knows this conversation needs to happen, what's really keeping the team from bringing it up themselves? Sometimes the "difficult conversation" we think we need to have isn't actually about the topic we think it is.

## Hints (Without Giving Away the Answer)
Consider starting with curiosity rather than conclusions. What if you asked the team what they think is working and what isn't, before sharing your own perspective?"""

    @pytest.fixture
    def sample_conversation_history(self):
        """Sample conversation history that generated the report."""
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
    async def test_deep_thoughts_conciseness(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Report should be scannable in under 2 minutes."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "conciseness_score": 0.8,
            "reasoning": "Report is well-structured and scannable, clocking in at about 90 seconds reading time"
        })

        score = await evaluator.evaluate_conciseness(sample_deep_thoughts_report, sample_conversation_history)

        assert score.value == 0.8
        assert "scannable" in score.reasoning
        assert score.analyzer_name == "DeepThoughtsConciseness"

    @pytest.mark.asyncio
    async def test_deep_thoughts_devil_advocate_quality(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Columbo section should feel insightful not annoying."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "devil_advocate_score": 0.9,
            "reasoning": "Columbo section offers genuine insight about underlying team dynamics while maintaining supportive tone"
        })

        score = await evaluator.evaluate_devil_advocate_quality(sample_deep_thoughts_report, sample_conversation_history)

        assert score.value == 0.9
        assert "supportive" in score.reasoning
        assert score.analyzer_name == "DeepThoughtsDevilAdvocate"

    @pytest.mark.asyncio
    async def test_deep_thoughts_rereadability(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Report should offer new value on second reading."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "rereadability_score": 0.8,
            "reasoning": "Report has depth that reveals new insights on rereading, especially the devil's advocate section"
        })

        score = await evaluator.evaluate_rereadability(sample_deep_thoughts_report, sample_conversation_history)

        assert score.value == 0.8
        assert "new insights" in score.reasoning
        assert score.analyzer_name == "DeepThoughtsRereadability"

    @pytest.mark.asyncio
    async def test_deep_thoughts_hint_quality(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Hints should guide without prescribing."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "hint_quality_score": 0.8,
            "reasoning": "Hints use Socratic questioning and guide thinking without solving the problem"
        })

        score = await evaluator.evaluate_hint_quality(sample_deep_thoughts_report, sample_conversation_history)

        assert score.value == 0.8
        assert "Socratic" in score.reasoning
        assert score.analyzer_name == "DeepThoughtsHintQuality"

    @pytest.mark.asyncio
    async def test_deep_thoughts_fact_check_accuracy(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Fact check section should accurately verify claims from conversation."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "fact_accuracy_score": 0.9,
            "reasoning": "Fact check accurately identifies verifiable claims and appropriately questions hyperbolic statements"
        })

        score = await evaluator.evaluate_fact_check_accuracy(sample_deep_thoughts_report, sample_conversation_history)

        assert score.value == 0.9
        assert "accurately identifies" in score.reasoning
        assert score.analyzer_name == "DeepThoughtsFactAccuracy"

    @pytest.mark.asyncio
    async def test_deep_thoughts_overall_usefulness(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Report should feel genuinely useful and worth saving."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "usefulness_score": 0.8,
            "reasoning": "Report provides breakthrough insights that user would want to reference throughout the day"
        })

        score = await evaluator.evaluate_overall_usefulness(sample_deep_thoughts_report, sample_conversation_history)

        assert score.value == 0.8
        assert "breakthrough insights" in score.reasoning
        assert score.analyzer_name == "DeepThoughtsUsefulness"

    @pytest.mark.asyncio
    async def test_evaluate_all_metrics(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Should evaluate all quality metrics and return comprehensive results."""
        # Mock responses for all metrics
        mock_llm_service.generate_response.side_effect = [
            json.dumps({"conciseness_score": 0.8, "reasoning": "Scannable and well-structured"}),
            json.dumps({"devil_advocate_score": 0.9, "reasoning": "Insightful Columbo-style questioning"}),
            json.dumps({"rereadability_score": 0.7, "reasoning": "Good depth for rereading"}),
            json.dumps({"hint_quality_score": 0.8, "reasoning": "Socratic hints without prescribing"}),
            json.dumps({"fact_accuracy_score": 0.9, "reasoning": "Accurate fact verification"}),
            json.dumps({"usefulness_score": 0.8, "reasoning": "Genuinely useful insights"})
        ]

        results = await evaluator.evaluate_all_metrics(sample_deep_thoughts_report, sample_conversation_history)

        assert len(results) == 6
        metric_names = [result.analyzer_name for result in results]
        
        expected_metrics = [
            "DeepThoughtsConciseness",
            "DeepThoughtsDevilAdvocate", 
            "DeepThoughtsRereadability",
            "DeepThoughtsHintQuality",
            "DeepThoughtsFactAccuracy",
            "DeepThoughtsUsefulness"
        ]
        
        for expected_metric in expected_metrics:
            assert expected_metric in metric_names

    @pytest.mark.asyncio
    async def test_poor_quality_report_detection(self, evaluator, mock_llm_service, sample_conversation_history):
        """Should detect poor quality reports and give low scores."""
        poor_report = """# Deep Thoughts: Basic Report

## Core Problem
User has a problem.

## Fact Check
✅ Problem exists

## Just One More Thing...
Maybe think about it more.

## Hints
Try harder."""

        mock_llm_service.generate_response.return_value = json.dumps({
            "conciseness_score": 0.2,
            "reasoning": "Report lacks depth and insight, feels generic and unhelpful"
        })

        score = await evaluator.evaluate_conciseness(poor_report, sample_conversation_history)

        assert score.value == 0.2
        assert "lacks depth" in score.reasoning

    @pytest.mark.asyncio
    async def test_evaluator_handles_llm_failures(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Should handle LLM failures gracefully with fallback scores."""
        # Mock LLM failure
        mock_llm_service.generate_response.side_effect = Exception("Network error")

        score = await evaluator.evaluate_conciseness(sample_deep_thoughts_report, sample_conversation_history)

        assert score.value == 0.5  # Fallback score
        assert "Evaluation failed" in score.reasoning
        assert score.analyzer_name == "DeepThoughtsConciseness"

    @pytest.mark.asyncio
    async def test_evaluator_uses_appropriate_model_parameters(self, evaluator, mock_llm_service, sample_deep_thoughts_report, sample_conversation_history):
        """Should use appropriate parameters for analytical evaluation."""
        mock_llm_service.generate_response.return_value = json.dumps({
            "conciseness_score": 0.8,
            "reasoning": "Well-structured report"
        })

        await evaluator.evaluate_conciseness(sample_deep_thoughts_report, sample_conversation_history)

        # Verify LLM was called with appropriate parameters
        call_args = mock_llm_service.generate_response.call_args
        assert call_args[1]["max_tokens"] >= 300  # Should allow detailed analysis
        assert call_args[1]["temperature"] <= 0.2  # Should be analytical, not creative
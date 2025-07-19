"""Simple tests for the 5 new LangSmith evaluators."""

import pytest
from unittest.mock import Mock, AsyncMock
import json

from src.evaluation.langsmith_evaluators import (
    ProblemDefinitionEvaluator,
    CruxRecognitionEvaluator,
    TodayAccomplishmentEvaluator,
    MultiplePathsEvaluator,
    CoreBeliefsEvaluator,
    EVALUATOR_REGISTRY,
    get_all_evaluators,
    get_evaluator
)


@pytest.fixture
def mock_llm_service():
    """Mock LLM service that returns valid scores."""
    service = Mock()
    service.generate_response = AsyncMock(return_value=json.dumps({
        "score": 0.8,
        "reasoning": "Good coaching response"
    }))
    return service


class TestEvaluatorRegistry:
    """Test the evaluator registry and factory functions."""
    
    def test_registry_has_five_evaluators(self):
        """Verify registry contains exactly 5 evaluators."""
        assert len(EVALUATOR_REGISTRY) == 5
        assert "problem_definition" in EVALUATOR_REGISTRY
        assert "crux_recognition" in EVALUATOR_REGISTRY
        assert "today_accomplishment" in EVALUATOR_REGISTRY
        assert "multiple_paths" in EVALUATOR_REGISTRY
        assert "core_beliefs" in EVALUATOR_REGISTRY
    
    def test_get_all_evaluators_returns_five(self):
        """Verify get_all_evaluators returns 5 instances."""
        evaluators = get_all_evaluators()
        assert len(evaluators) == 5
        
    def test_get_evaluator_by_name(self):
        """Test retrieving specific evaluators by name."""
        evaluator = get_evaluator("problem_definition")
        assert isinstance(evaluator, ProblemDefinitionEvaluator)
        
        evaluator = get_evaluator("core_beliefs")
        assert isinstance(evaluator, CoreBeliefsEvaluator)
        
    def test_get_evaluator_invalid_name_raises(self):
        """Test that invalid names raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_evaluator("invalid_name")
        assert "Unknown evaluator" in str(exc_info.value)


class TestEvaluatorFunctionality:
    """Test basic functionality of each evaluator."""
    
    def test_all_evaluators_have_required_methods(self):
        """Verify all evaluators have the required interface."""
        evaluators = get_all_evaluators()
        
        for evaluator in evaluators:
            assert hasattr(evaluator, 'evaluate_run')
            assert hasattr(evaluator, 'aevaluate_run')
            assert hasattr(evaluator, '_build_eval_prompt')
            assert hasattr(evaluator, 'key')
    
    def test_evaluator_prompts_contain_criteria(self):
        """Verify each evaluator's prompt contains its criterion."""
        conversation = [
            {"role": "user", "content": "I have a problem."},
            {"role": "assistant", "content": "Tell me more."}
        ]
        response = "Tell me more about your problem."
        
        # Test each evaluator
        evaluator = ProblemDefinitionEvaluator()
        prompt = evaluator._build_eval_prompt(conversation, response)
        assert "Define biggest problem" in prompt
        
        evaluator = CruxRecognitionEvaluator()
        prompt = evaluator._build_eval_prompt(conversation, response)
        assert "key constraint" in prompt
        
        evaluator = TodayAccomplishmentEvaluator()
        prompt = evaluator._build_eval_prompt(conversation, response)
        assert "accomplish today" in prompt
        
        evaluator = MultiplePathsEvaluator()
        prompt = evaluator._build_eval_prompt(conversation, response)
        assert "multiple viable" in prompt
        
        evaluator = CoreBeliefsEvaluator()
        prompt = evaluator._build_eval_prompt(conversation, response)
        assert "core beliefs" in prompt
"""
Tests for LangSmith evaluator wrappers.

Tests the integration between our coaching evaluation templates and LangSmith's
RunEvaluator framework.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from langsmith.schemas import Run, Example

from src.evaluation.langsmith_evaluators import (
    ProblemSignificanceEvaluator,
    TaskConcretizationEvaluator, 
    SolutionDiversityEvaluator,
    CruxIdentificationEvaluator,
    CruxSolutionEvaluator,
    BeliefSystemEvaluator,
    NonDirectiveStyleEvaluator,
    EVALUATOR_REGISTRY,
    get_all_evaluators,
    get_evaluator
)


def create_mock_run(messages: list, response: str) -> Run:
    """Create a mock Run object for testing."""
    run = Mock(spec=Run)
    run.inputs = {"messages": messages}
    run.outputs = {"response": response}
    return run


@pytest.fixture
def mock_llm_service():
    """Mock LLM service that returns valid JSON responses."""
    service = Mock()
    service.generate_response = AsyncMock(return_value=json.dumps({
        "score": 4,
        "reasoning": "Good coaching response with strong questioning",
        "strengths": ["Uses open-ended questions", "Explores deeper meaning"],
        "improvements": ["Could probe more on emotional significance"]
    }))
    return service


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing."""
    return [
        {"role": "user", "content": "I'm having conflicts with my team at work."},
        {"role": "assistant", "content": "Tell me more about these conflicts."},
        {"role": "user", "content": "They never listen to my ideas in meetings."}
    ]


@pytest.fixture
def sample_coach_response():
    """Sample coach response for evaluation."""
    return "This team conflict seems important to you. Help me understand - what makes this particularly significant right now? What would happen if these conflicts continued unresolved?"


class TestProblemSignificanceEvaluator:
    """Test Problem Significance evaluation wrapper."""
    
    def test_evaluate_run_success(self, mock_llm_service, sample_conversation, sample_coach_response):
        """Test successful evaluation run."""
        evaluator = ProblemSignificanceEvaluator(llm_service=mock_llm_service)
        run = create_mock_run(sample_conversation, sample_coach_response)
        
        result = evaluator.evaluate_run(run)
        
        assert 0 <= result["score"] <= 1  # Normalized score
        assert result["score"] == 0.8  # 4/5 = 0.8
        assert "reasoning" in result
        assert "feedback" in result
        assert "strengths" in result["feedback"]
        assert "improvements" in result["feedback"]
        
        # Verify LLM was called with proper prompt
        mock_llm_service.generate_response.assert_called_once()
        prompt_arg = mock_llm_service.generate_response.call_args[0][0]
        assert "Problem Significance Assessment" in prompt_arg
        assert sample_coach_response in prompt_arg
    
    def test_evaluate_run_with_llm_error(self, sample_conversation, sample_coach_response):
        """Test evaluation run when LLM service fails."""
        mock_llm_service = Mock()
        mock_llm_service.generate_response = AsyncMock(side_effect=Exception("API Error"))
        
        evaluator = ProblemSignificanceEvaluator(llm_service=mock_llm_service)
        run = create_mock_run(sample_conversation, sample_coach_response)
        
        result = evaluator.evaluate_run(run)
        
        assert result["score"] == 0.0
        assert "Evaluation failed: API Error" in result["reasoning"]
        assert result["feedback"]["improvements"] == ["Evaluation system error"]
    
    def test_build_eval_prompt_contains_required_elements(self, sample_conversation, sample_coach_response, mock_llm_service):
        """Test that evaluation prompt contains all required elements."""
        evaluator = ProblemSignificanceEvaluator(llm_service=mock_llm_service)
        client_statement = "I'm having conflicts with my team at work."
        
        prompt = evaluator._build_eval_prompt(sample_conversation, sample_coach_response, client_statement)
        
        # Check key sections are present
        assert "Problem Significance Assessment" in prompt
        assert "Criteria" in prompt
        assert "Rating Rubric" in prompt
        assert "Conversation Context" in prompt
        assert "Coach Response to Evaluate" in prompt
        assert "Client Statement" in prompt
        assert sample_coach_response in prompt
        assert client_statement in prompt
    
    def test_format_conversation_history(self, sample_conversation, mock_llm_service):
        """Test conversation history formatting."""
        evaluator = ProblemSignificanceEvaluator(llm_service=mock_llm_service)
        
        formatted = evaluator._format_conversation_history(sample_conversation)
        
        assert "Client: I'm having conflicts with my team at work." in formatted
        assert "Coach: Tell me more about these conflicts." in formatted
        assert "Client: They never listen to my ideas in meetings." in formatted


class TestTaskConcretizationEvaluator:
    """Test Task Concretization evaluation wrapper."""
    
    def test_evaluate_run_success(self, mock_llm_service):
        """Test successful task concretization evaluation."""
        evaluator = TaskConcretizationEvaluator(llm_service=mock_llm_service)
        
        conversation = [
            {"role": "user", "content": "I want to be a better leader."},
            {"role": "assistant", "content": "What specific behaviors would show better leadership?"}
        ]
        
        run = create_mock_run(conversation, "What specific behaviors would show better leadership?")
        result = evaluator.evaluate_run(run)
        
        assert 0 <= result["score"] <= 1
        assert "reasoning" in result
        
        # Verify correct template is used
        prompt_arg = mock_llm_service.generate_response.call_args[0][0]
        assert "Task Concretization" in prompt_arg
        assert "Specificity Enhancement" in prompt_arg


class TestSolutionDiversityEvaluator:
    """Test Solution Diversity evaluation wrapper."""
    
    def test_build_eval_prompt_contains_solution_criteria(self, mock_llm_service):
        """Test that solution diversity prompt contains creativity criteria."""
        evaluator = SolutionDiversityEvaluator(llm_service=mock_llm_service)
        
        conversation = [{"role": "user", "content": "I need better team communication."}]
        response = "What are different ways you could approach this?"
        client_statement = "I need better team communication."
        
        prompt = evaluator._build_eval_prompt(conversation, response, client_statement)
        
        assert "Solution Diversity" in prompt
        assert "Option Generation" in prompt
        assert "Creative Exploration" in prompt
        assert "Brainstorming Support" in prompt


class TestCruxIdentificationEvaluator:
    """Test Crux Identification evaluation wrapper."""
    
    def test_build_eval_prompt_contains_root_cause_criteria(self, mock_llm_service):
        """Test that crux identification prompt contains root cause analysis criteria."""
        evaluator = CruxIdentificationEvaluator(llm_service=mock_llm_service)
        
        conversation = [{"role": "user", "content": "I keep missing deadlines."}]
        response = "What's the common thread in these deadline issues?"
        client_statement = "I keep missing deadlines."
        
        prompt = evaluator._build_eval_prompt(conversation, response, client_statement)
        
        assert "Crux Identification" in prompt
        assert "Root Cause Exploration" in prompt
        assert "Leverage Point Recognition" in prompt
        assert "Systems Thinking" in prompt


class TestCruxSolutionEvaluator:
    """Test Crux Solution evaluation wrapper."""
    
    def test_build_eval_prompt_contains_strategic_focus(self, mock_llm_service):
        """Test that crux solution prompt contains strategic solution criteria."""
        evaluator = CruxSolutionEvaluator(llm_service=mock_llm_service)
        
        conversation = [{"role": "user", "content": "We identified avoidance as the core issue."}]
        response = "What would addressing this avoidance pattern look like?"
        client_statement = "We identified avoidance as the core issue."
        
        prompt = evaluator._build_eval_prompt(conversation, response, client_statement)
        
        assert "Crux Solution Exploration" in prompt
        assert "Target Alignment" in prompt
        assert "Strategic Focus" in prompt
        assert "Implementation Viability" in prompt


class TestBeliefSystemEvaluator:
    """Test Belief System evaluation wrapper."""
    
    def test_build_eval_prompt_contains_belief_criteria(self, mock_llm_service):
        """Test that belief system prompt contains belief work criteria."""
        evaluator = BeliefSystemEvaluator(llm_service=mock_llm_service)
        
        conversation = [{"role": "user", "content": "I don't think I'm leadership material."}]
        response = "What experiences shaped this belief about yourself?"
        client_statement = "I don't think I'm leadership material."
        
        prompt = evaluator._build_eval_prompt(conversation, response, client_statement)
        
        assert "Belief System Integration" in prompt
        assert "Belief Identification" in prompt
        assert "Assumption Examination" in prompt
        assert "Perspective Expansion" in prompt


class TestNonDirectiveStyleEvaluator:
    """Test Non-Directive Style evaluation wrapper."""
    
    def test_build_eval_prompt_contains_non_directive_criteria(self, mock_llm_service):
        """Test that non-directive prompt contains coaching methodology criteria."""
        evaluator = NonDirectiveStyleEvaluator(llm_service=mock_llm_service)
        
        conversation = [{"role": "user", "content": "I'm not sure what to do."}]
        response = "What options are you considering? What feels most aligned?"
        client_statement = "I'm not sure what to do."
        
        prompt = evaluator._build_eval_prompt(conversation, response, client_statement)
        
        assert "Non-Directive Coaching Style" in prompt
        assert "Question vs. Advice Ratio" in prompt
        assert "Client Autonomy Support" in prompt
        assert "Self-Discovery Facilitation" in prompt


class TestEvaluatorRegistry:
    """Test evaluator registry and factory functions."""
    
    def test_evaluator_registry_contains_all_evaluators(self):
        """Test that registry contains all 7 evaluators."""
        expected_evaluators = {
            "problem_significance",
            "task_concretization", 
            "solution_diversity",
            "crux_identification",
            "crux_solution",
            "belief_system",
            "non_directive_style"
        }
        
        assert set(EVALUATOR_REGISTRY.keys()) == expected_evaluators
    
    @patch('src.evaluation.langsmith_evaluators.LLMFactory.create_service')
    def test_get_all_evaluators_returns_seven_instances(self, mock_create_service):
        """Test that get_all_evaluators returns 7 evaluator instances."""
        mock_create_service.return_value = Mock()
        evaluators = get_all_evaluators()
        
        assert len(evaluators) == 7
        assert all(hasattr(eval, "evaluate_run") for eval in evaluators)
        assert all(hasattr(eval, "_build_eval_prompt") for eval in evaluators)
    
    @patch('src.evaluation.langsmith_evaluators.LLMFactory.create_service')
    def test_get_evaluator_by_name(self, mock_create_service):
        """Test getting specific evaluator by name."""
        mock_create_service.return_value = Mock()
        evaluator = get_evaluator("problem_significance")
        
        assert isinstance(evaluator, ProblemSignificanceEvaluator)
        assert hasattr(evaluator, "evaluate_run")
    
    def test_get_evaluator_unknown_name_raises_error(self):
        """Test that unknown evaluator name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown evaluator: unknown"):
            get_evaluator("unknown")


class TestJSONOutputParsing:
    """Test JSON output parsing and error handling."""
    
    def test_evaluate_run_with_invalid_json(self, sample_conversation, sample_coach_response):
        """Test evaluation when LLM returns invalid JSON."""
        mock_llm_service = Mock()
        mock_llm_service.generate_response = AsyncMock(return_value="Invalid JSON response")
        
        evaluator = ProblemSignificanceEvaluator(llm_service=mock_llm_service)
        run = create_mock_run(sample_conversation, sample_coach_response)
        
        result = evaluator.evaluate_run(run)
        
        assert result["score"] == 0.0
        assert "Evaluation failed" in result["reasoning"]
    
    def test_evaluate_run_normalizes_score_correctly(self, sample_conversation, sample_coach_response):
        """Test that scores are properly normalized from 1-5 to 0-1 scale."""
        test_cases = [
            (1, 0.2), (2, 0.4), (3, 0.6), (4, 0.8), (5, 1.0)
        ]
        
        for input_score, expected_normalized in test_cases:
            mock_llm_service = Mock()
            mock_llm_service.generate_response = AsyncMock(return_value=json.dumps({
                "score": input_score,
                "reasoning": "Test reasoning",
                "strengths": ["Test strength"],
                "improvements": ["Test improvement"]
            }))
            
            evaluator = ProblemSignificanceEvaluator(llm_service=mock_llm_service)
            run = create_mock_run(sample_conversation, sample_coach_response)
            
            result = evaluator.evaluate_run(run)
            
            assert result["score"] == expected_normalized
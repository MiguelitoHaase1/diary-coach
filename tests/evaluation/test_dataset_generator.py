"""
Tests for the evaluation dataset generator.

Tests the generation of targeted conversation examples for coaching evaluation.
"""

import pytest
from src.evaluation.dataset_generator import (
    EvalDatasetGenerator,
    ConversationExample,
    get_dataset_summary
)


@pytest.fixture
def generator():
    """Create a dataset generator instance."""
    return EvalDatasetGenerator()


class TestConversationExample:
    """Test the ConversationExample dataclass."""
    
    def test_conversation_example_creation(self):
        """Test creating a conversation example."""
        example = ConversationExample(
            scenario_name="test_scenario",
            context="Test context",
            client_opening="I have a problem",
            good_coach_response="Tell me more about that",
            poor_coach_response="Here's what you should do",
            evaluation_dimension="test_dimension",
            expected_good_score=0.8,
            expected_poor_score=0.3
        )
        
        assert example.scenario_name == "test_scenario"
        assert example.context == "Test context"
        assert example.evaluation_dimension == "test_dimension"
        assert example.expected_good_score == 0.8
        assert example.expected_poor_score == 0.3


class TestProblemSignificanceExamples:
    """Test problem significance example generation."""
    
    def test_generates_multiple_examples(self, generator):
        """Test that multiple problem significance examples are generated."""
        examples = generator.generate_problem_significance_examples()
        
        assert len(examples) >= 3
        assert all(ex.evaluation_dimension == "problem_significance" for ex in examples)
    
    def test_examples_have_required_fields(self, generator):
        """Test that all examples have required fields."""
        examples = generator.generate_problem_significance_examples()
        
        for example in examples:
            assert example.scenario_name
            assert example.context
            assert example.client_opening
            assert example.good_coach_response
            assert example.poor_coach_response
            assert example.evaluation_dimension == "problem_significance"
            assert 0 <= example.expected_good_score <= 1
            assert 0 <= example.expected_poor_score <= 1
            assert example.expected_good_score > example.expected_poor_score
    
    def test_good_responses_explore_significance(self, generator):
        """Test that good responses explore problem significance."""
        examples = generator.generate_problem_significance_examples()
        
        for example in examples:
            good_response = example.good_coach_response.lower()
            # Good responses should contain significance-related questions
            assert any(keyword in good_response for keyword in [
                "what would happen", "impact", "ripple effect", "consequence",
                "importance", "priority", "significant", "core", "matter"
            ])
    
    def test_poor_responses_lack_significance_exploration(self, generator):
        """Test that poor responses don't explore significance properly."""
        examples = generator.generate_problem_significance_examples()
        
        for example in examples:
            poor_response = example.poor_coach_response.lower()
            # Poor responses should be more directive or surface-level
            assert len(poor_response) < len(example.good_coach_response)


class TestTaskConcretizationExamples:
    """Test task concretization example generation."""
    
    def test_generates_multiple_examples(self, generator):
        """Test that multiple task concretization examples are generated."""
        examples = generator.generate_task_concretization_examples()
        
        assert len(examples) >= 3
        assert all(ex.evaluation_dimension == "task_concretization" for ex in examples)
    
    def test_good_responses_push_for_specificity(self, generator):
        """Test that good responses push for concrete, specific details."""
        examples = generator.generate_task_concretization_examples()
        
        for example in examples:
            good_response = example.good_coach_response.lower()
            # Good responses should contain specificity-related questions
            assert any(keyword in good_response for keyword in [
                "specific", "how would", "what would", "measure", "notice",
                "concrete", "exactly", "precisely", "define"
            ])


class TestSolutionDiversityExamples:
    """Test solution diversity example generation."""
    
    def test_generates_multiple_examples(self, generator):
        """Test that multiple solution diversity examples are generated."""
        examples = generator.generate_solution_diversity_examples()
        
        assert len(examples) >= 3
        assert all(ex.evaluation_dimension == "solution_diversity" for ex in examples)
    
    def test_good_responses_encourage_multiple_options(self, generator):
        """Test that good responses encourage diverse solution generation."""
        examples = generator.generate_solution_diversity_examples()
        
        for example in examples:
            good_response = example.good_coach_response.lower()
            # Good responses should encourage multiple options
            assert any(keyword in good_response for keyword in [
                "different ways", "all possibilities", "options", "alternatives",
                "brainstorm", "unconventional", "creative", "various"
            ])


class TestCruxIdentificationExamples:
    """Test crux identification example generation."""
    
    def test_generates_multiple_examples(self, generator):
        """Test that multiple crux identification examples are generated."""
        examples = generator.generate_crux_identification_examples()
        
        assert len(examples) >= 3
        assert all(ex.evaluation_dimension == "crux_identification" for ex in examples)
    
    def test_good_responses_explore_root_causes(self, generator):
        """Test that good responses explore underlying patterns and causes."""
        examples = generator.generate_crux_identification_examples()
        
        for example in examples:
            good_response = example.good_coach_response.lower()
            # Good responses should explore deeper patterns
            assert any(keyword in good_response for keyword in [
                "pattern", "root", "underlying", "common thread", "deeper",
                "core", "system", "fundamental", "central"
            ])


class TestCruxSolutionExamples:
    """Test crux solution example generation."""
    
    def test_generates_multiple_examples(self, generator):
        """Test that multiple crux solution examples are generated."""
        examples = generator.generate_crux_solution_examples()
        
        assert len(examples) >= 3
        assert all(ex.evaluation_dimension == "crux_solution" for ex in examples)
    
    def test_good_responses_target_core_issues(self, generator):
        """Test that good responses target core issues with comprehensive solutions."""
        examples = generator.generate_crux_solution_examples()
        
        for example in examples:
            good_response = example.good_coach_response.lower()
            # Good responses should target fundamental change
            assert any(keyword in good_response for keyword in [
                "fundamental", "transform", "core", "root", "comprehensive",
                "shift", "ripple", "central", "address"
            ])


class TestBeliefSystemExamples:
    """Test belief system example generation."""
    
    def test_generates_multiple_examples(self, generator):
        """Test that multiple belief system examples are generated."""
        examples = generator.generate_belief_system_examples()
        
        assert len(examples) >= 3
        assert all(ex.evaluation_dimension == "belief_system" for ex in examples)
    
    def test_good_responses_explore_beliefs(self, generator):
        """Test that good responses explore underlying beliefs and assumptions."""
        examples = generator.generate_belief_system_examples()
        
        for example in examples:
            good_response = example.good_coach_response.lower()
            # Good responses should explore beliefs
            assert any(keyword in good_response for keyword in [
                "belief", "assume", "what would you need to believe",
                "shaped", "view", "perspective", "meaning"
            ])


class TestNonDirectiveExamples:
    """Test non-directive style example generation."""
    
    def test_generates_multiple_examples(self, generator):
        """Test that multiple non-directive examples are generated."""
        examples = generator.generate_non_directive_examples()
        
        assert len(examples) >= 3
        assert all(ex.evaluation_dimension == "non_directive_style" for ex in examples)
    
    def test_good_responses_use_questions_not_advice(self, generator):
        """Test that good responses use questions rather than giving advice."""
        examples = generator.generate_non_directive_examples()
        
        for example in examples:
            good_response = example.good_coach_response
            poor_response = example.poor_coach_response
            
            # Count question marks in responses
            good_questions = good_response.count("?")
            poor_questions = poor_response.count("?")
            
            assert good_questions > poor_questions
            assert good_questions >= 2  # Should have multiple questions
    
    def test_poor_responses_give_directive_advice(self, generator):
        """Test that poor responses give directive advice."""
        examples = generator.generate_non_directive_examples()
        
        for example in examples:
            poor_response = example.poor_coach_response.lower()
            # Poor responses should contain directive language
            assert any(keyword in poor_response for keyword in [
                "you should", "you need to", "i think you", "you have to",
                "the best approach", "you must"
            ])


class TestGenerateAllExamples:
    """Test generation of all examples across dimensions."""
    
    def test_generates_examples_for_all_dimensions(self, generator):
        """Test that all 7 evaluation dimensions are covered."""
        examples = generator.generate_all_examples()
        
        dimensions_covered = set(ex.evaluation_dimension for ex in examples)
        expected_dimensions = {
            "problem_significance",
            "task_concretization", 
            "solution_diversity",
            "crux_identification",
            "crux_solution",
            "belief_system",
            "non_directive_style"
        }
        
        assert dimensions_covered == expected_dimensions
    
    def test_total_example_count(self, generator):
        """Test that adequate number of examples are generated."""
        examples = generator.generate_all_examples()
        
        # Should have at least 3 examples per dimension
        assert len(examples) >= 21  # 7 dimensions * 3 examples each
        assert len(examples) <= 35  # Upper bound for reasonable dataset size
    
    def test_balanced_coverage_across_dimensions(self, generator):
        """Test that coverage is balanced across dimensions."""
        examples = generator.generate_all_examples()
        
        dimension_counts = {}
        for example in examples:
            dim = example.evaluation_dimension
            dimension_counts[dim] = dimension_counts.get(dim, 0) + 1
        
        # Each dimension should have similar number of examples
        counts = list(dimension_counts.values())
        min_count = min(counts)
        max_count = max(counts)
        
        # No dimension should have more than 2x the examples of any other
        assert max_count <= min_count * 2


class TestLangSmithFormatting:
    """Test formatting examples for LangSmith dataset upload."""
    
    def test_format_for_langsmith_doubles_entries(self, generator):
        """Test that LangSmith formatting creates good + poor entries for each example."""
        examples = generator.generate_problem_significance_examples()
        langsmith_examples = generator.format_for_langsmith(examples)
        
        # Should create 2 LangSmith entries for each conversation example
        assert len(langsmith_examples) == len(examples) * 2
    
    def test_langsmith_format_structure(self, generator):
        """Test that LangSmith examples have correct structure."""
        examples = generator.generate_problem_significance_examples()[:1]  # Just test one
        langsmith_examples = generator.format_for_langsmith(examples)
        
        for ls_example in langsmith_examples:
            assert "inputs" in ls_example
            assert "outputs" in ls_example
            assert "metadata" in ls_example
            
            # Check inputs structure
            assert "messages" in ls_example["inputs"]
            assert "scenario" in ls_example["inputs"]
            assert "context" in ls_example["inputs"]
            assert "evaluation_dimension" in ls_example["inputs"]
            
            # Check outputs structure
            assert "response" in ls_example["outputs"]
            
            # Check metadata structure
            assert "response_type" in ls_example["metadata"]
            assert "expected_score" in ls_example["metadata"]
            assert "evaluation_dimension" in ls_example["metadata"]
            assert "scenario_name" in ls_example["metadata"]
    
    def test_langsmith_good_and_poor_responses(self, generator):
        """Test that LangSmith formatting includes both good and poor responses."""
        examples = generator.generate_problem_significance_examples()[:1]
        langsmith_examples = generator.format_for_langsmith(examples)
        
        response_types = [ex["metadata"]["response_type"] for ex in langsmith_examples]
        assert "good" in response_types
        assert "poor" in response_types


class TestDatasetSummary:
    """Test dataset summary generation."""
    
    def test_get_dataset_summary(self, generator):
        """Test dataset summary calculation."""
        examples = generator.generate_all_examples()
        summary = get_dataset_summary(examples)
        
        assert "total_examples" in summary
        assert "total_langsmith_entries" in summary
        assert "dimensions" in summary
        assert "coverage" in summary
        
        assert summary["total_examples"] == len(examples)
        assert summary["total_langsmith_entries"] == len(examples) * 2
        assert len(summary["dimensions"]) == 7  # All 7 evaluation dimensions
    
    def test_coverage_breakdown(self, generator):
        """Test that coverage breakdown is accurate."""
        examples = generator.generate_all_examples()
        summary = get_dataset_summary(examples)
        
        coverage = summary["coverage"]
        total_from_coverage = sum(coverage.values())
        
        assert total_from_coverage == summary["total_examples"]
        
        # Each dimension should have at least some examples
        for dimension, count in coverage.items():
            assert count > 0
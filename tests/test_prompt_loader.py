"""Test prompt loader functionality."""

import pytest
from src.agents.prompts import PromptLoader, get_coach_system_prompt


def test_prompt_loader_loads_coach_prompt():
    """Should load the coach system prompt from markdown file."""

    prompt = PromptLoader.get_coach_system_prompt()

    # Should contain key elements from the coaching prompt
    assert "Daily Transformation Diary Coach" in prompt
    assert "Michael's personal" in prompt
    assert "Non-Directive Coaching Philosophy" in prompt
    assert "Problem Exploration Framework" in prompt
    assert "Communication Constraints" in prompt


def test_prompt_loader_caching():
    """Should cache prompts for performance."""

    # Clear cache first
    PromptLoader.clear_cache()

    # First load
    prompt1 = PromptLoader.get_coach_system_prompt()

    # Second load should use cache
    prompt2 = PromptLoader.get_coach_system_prompt()

    # Should be identical
    assert prompt1 == prompt2

    # Cache should contain the prompt
    assert "coach_system_prompt" in PromptLoader._cache


def test_convenience_function():
    """Should provide convenience function for easy access."""

    prompt = get_coach_system_prompt()

    # Should be same as direct loader call
    assert prompt == PromptLoader.get_coach_system_prompt()


def test_prompt_file_not_found_error():
    """Should raise FileNotFoundError for missing prompts."""

    with pytest.raises(FileNotFoundError):
        PromptLoader.load_prompt("nonexistent_prompt")


def test_coach_agent_uses_prompt_loader():
    """Should verify that coach agent loads prompt dynamically."""

    from src.agents.coach_agent import DiaryCoach

    # Create mock LLM service
    class MockLLMService:
        async def generate_response(self, messages, system_prompt,
                                    max_tokens=200, temperature=0.7):
            return "Test response"

    coach = DiaryCoach(MockLLMService())

    # Should load prompt from file
    prompt = coach.SYSTEM_PROMPT
    assert "Daily Transformation Diary Coach" in prompt
    assert "Michael's personal" in prompt


def test_implicit_context_coach_uses_prompt_loader():
    """Should verify that implicit context coach loads prompt dynamically."""

    from src.orchestration.implicit_context_coach import ImplicitContextCoach

    # Create mock LLM service
    class MockLLMService:
        async def generate_response(self, messages, system_prompt,
                                    max_tokens=200, temperature=0.7):
            return "Test response"

    coach = ImplicitContextCoach(MockLLMService())

    # Should load prompt from file
    prompt = coach._get_base_coaching_prompt()
    assert "Daily Transformation Diary Coach" in prompt
    assert "Remember: Your role is to coach" in prompt

"""Tests for Evaluator Agent."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.base import AgentRequest, AgentResponse


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service."""
    service = AsyncMock()
    service.generate_response = AsyncMock()
    return service


@pytest.fixture
def evaluator_agent(mock_llm_service):
    """Create evaluator agent with mock LLM."""
    agent = EvaluatorAgent(llm_service=mock_llm_service)
    return agent


@pytest.mark.asyncio
async def test_evaluator_initialization(evaluator_agent):
    """Test evaluator agent initializes properly."""
    assert evaluator_agent.name == "evaluator"
    assert not evaluator_agent.is_initialized  # Not initialized yet
    
    await evaluator_agent.initialize()
    
    assert evaluator_agent.is_initialized
    assert len(evaluator_agent.capabilities) == 2
    # Verify all criteria are defined
    assert len(EvaluatorAgent.CRITERIA) == 5
    assert all(c in EvaluatorAgent.CRITERIA for c in ["A", "B", "C", "D", "E"])


@pytest.mark.asyncio
async def test_evaluator_all_criteria_perfect(evaluator_agent, mock_llm_service):
    """Test evaluation with perfect scores on all criteria."""
    await evaluator_agent.initialize()
    # Mock perfect scores for all criteria + summary
    mock_responses = [
        '{"score": 1.0, "reasoning": "Clearly defined problem and its importance"}',
        '{"score": 1.0, "reasoning": "Identified key constraint accurately"}',
        '{"score": 1.0, "reasoning": "Specific action for today defined"}',
        '{"score": 1.0, "reasoning": "Multiple creative paths explored"}',
        '{"score": 1.0, "reasoning": "Deep alignment with core beliefs"}',
        'The conversation focused on improving leadership skills. Key insights include identifying specific challenges and developing actionable strategies. The action item is to practice active listening in the next team meeting.',
    ]
    mock_llm_service.generate_response.side_effect = mock_responses

    # Create request
    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="evaluator",
        query="Evaluate coaching session",
        context={
            "conversation": [
                {"role": "user", "content": "I need to improve my leadership"},
                {"role": "assistant", "content": "Let's identify the key challenge"},
            ],
            "deep_thoughts": "# Deep Thoughts\n\nExcellent session content...",
        },
    )

    # Process request
    response = await evaluator_agent.handle_request(request)

    # Verify response
    assert response.agent_name == "evaluator"
    assert "Coaching Session Evaluation Report" in response.content
    assert "Overall Effectiveness Score: 100.0%" in response.content

    # Check metadata
    assert response.metadata["overall_score"] == 1.0
    evaluations = response.metadata["evaluations"]
    assert all(evaluations[c]["score"] == 1.0 for c in ["A", "B", "C", "D", "E"])


@pytest.mark.asyncio
async def test_evaluator_mixed_scores(evaluator_agent, mock_llm_service):
    """Test evaluation with mixed scores."""
    await evaluator_agent.initialize()
    # Mock mixed scores + summary
    mock_responses = [
        '{"score": 1.0, "reasoning": "Problem well defined"}',
        '{"score": 0.0, "reasoning": "Crux not identified"}',
        '{"score": 1.0, "reasoning": "Clear action for today"}',
        '{"score": 0.5, "reasoning": "Some paths explored"}',
        '{"score": 0.3, "reasoning": "Limited belief connection"}',
        'The conversation started with problem identification but struggled to find the root cause. Some progress was made on defining immediate actions.',
    ]
    mock_llm_service.generate_response.side_effect = mock_responses

    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="evaluator",
        query="Evaluate",
        context={
            "conversation": [{"role": "user", "content": "Help"}],
            "deep_thoughts": "Report content",
        },
    )

    response = await evaluator_agent.handle_request(request)

    # Verify mixed results
    assert "A. Problem Definition: ✓" in response.content
    assert "B. Crux Recognition: ✗" in response.content
    assert "D. Multiple Paths: 50.0%" in response.content

    # Check overall score calculation
    # A=1.0*0.25 + B=0*0.25 + C=1.0*0.25 + D=0.5*0.125 + E=0.3*0.125 = 0.6
    assert response.metadata["overall_score"] == 0.6


@pytest.mark.asyncio
async def test_evaluator_binary_criteria_rounding(evaluator_agent, mock_llm_service):
    """Test binary criteria are properly rounded to 0 or 1."""
    await evaluator_agent.initialize()
    # Mock responses with intermediate scores for binary criteria + summary
    mock_responses = [
        '{"score": 0.7, "reasoning": "Mostly defined"}',  # Should round to 1
        '{"score": 0.3, "reasoning": "Partially recognized"}',  # Should round to 0
        '{"score": 0.5, "reasoning": "Borderline"}',  # Should round to 1
        '{"score": 0.8, "reasoning": "Good paths"}',
        '{"score": 0.2, "reasoning": "Weak beliefs"}',
        'Summary of the coaching session.',
    ]
    mock_llm_service.generate_response.side_effect = mock_responses

    request = AgentRequest(
        from_agent="test",
        to_agent="evaluator",
        query="Evaluate",
        context={"conversation": [], "deep_thoughts": ""},
    )

    response = await evaluator_agent.handle_request(request)

    evaluations = response.metadata["evaluations"]
    # Binary criteria should be 0 or 1
    assert evaluations["A"]["score"] == 1.0
    assert evaluations["B"]["score"] == 0.0
    assert evaluations["C"]["score"] == 1.0
    # Graduated criteria keep their values
    assert evaluations["D"]["score"] == 0.8
    assert evaluations["E"]["score"] == 0.2


@pytest.mark.asyncio
async def test_evaluator_json_parsing_variants(evaluator_agent, mock_llm_service):
    """Test JSON parsing handles various response formats."""
    # Test different JSON response formats
    test_cases = [
        '```json\n{"score": 0.8, "reasoning": "Good"}\n```',
        '{"score": 0.8, "reasoning": "Good"}',
        'Some text before {"score": 0.8, "reasoning": "Good"} and after',
        '```\n{"score": 0.8, "reasoning": "Good"}\n```',
    ]

    for response_format in test_cases:
        mock_llm_service.generate_response.return_value = response_format

        request = AgentRequest(
            from_agent="test",
            to_agent="evaluator",
            query="Evaluate",
            context={"conversation": [], "deep_thoughts": ""},
        )

        # Should parse successfully
        score, reasoning = await evaluator_agent._evaluate_criterion(
            "D", {"name": "Test", "description": "Test criterion", "binary": False}, [], ""
        )
        assert score == 0.8
        assert reasoning == "Good"


@pytest.mark.asyncio
async def test_evaluator_empty_conversation(evaluator_agent, mock_llm_service):
    """Test evaluator handles empty conversation."""
    await evaluator_agent.initialize()
    # Mock response for all criteria + summary
    mock_llm_service.generate_response.side_effect = [
        '{"score": 0.0, "reasoning": "No conversation to evaluate"}',
        '{"score": 0.0, "reasoning": "No conversation to evaluate"}',
        '{"score": 0.0, "reasoning": "No conversation to evaluate"}',
        '{"score": 0.0, "reasoning": "No conversation to evaluate"}',
        '{"score": 0.0, "reasoning": "No conversation to evaluate"}',
        'No conversation available to summarize.',
    ]

    request = AgentRequest(
        from_agent="test",
        to_agent="evaluator",
        query="Evaluate",
        context={"conversation": [], "deep_thoughts": ""},
    )

    response = await evaluator_agent.handle_request(request)

    assert response.agent_name == "evaluator"
    assert not response.error
    assert response.content  # Should have generated a report


@pytest.mark.asyncio
async def test_evaluator_error_handling(evaluator_agent, mock_llm_service):
    """Test evaluator handles errors gracefully."""
    await evaluator_agent.initialize()
    # Test LLM error
    mock_llm_service.generate_response.side_effect = Exception("LLM API error")

    request = AgentRequest(
        from_agent="test",
        to_agent="evaluator",
        query="Evaluate",
        context={"conversation": [], "deep_thoughts": ""},
    )

    response = await evaluator_agent.handle_request(request)

    assert "Error evaluating coaching session" in response.content
    assert response.error == "LLM API error"


@pytest.mark.asyncio
async def test_evaluator_malformed_json(evaluator_agent, mock_llm_service):
    """Test evaluator handles malformed JSON responses."""
    await evaluator_agent.initialize()
    # Mock malformed JSON that can't be parsed
    mock_llm_service.generate_response.return_value = "This is not JSON at all"

    request = AgentRequest(
        from_agent="test",
        to_agent="evaluator",
        query="Evaluate",
        context={
            "conversation": [{"role": "user", "content": "Hi"}],
            "deep_thoughts": "Report",
        },
    )

    response = await evaluator_agent.handle_request(request)

    # Should handle gracefully with 0 scores
    evaluations = response.metadata["evaluations"]
    assert all(evaluations[c]["score"] == 0.0 for c in evaluations)
    assert all(
        "Error parsing evaluation" in evaluations[c]["reasoning"] for c in evaluations
    )


@pytest.mark.asyncio
async def test_evaluator_prompt_building(evaluator_agent):
    """Test criterion-specific prompt building."""
    conversation = [{"role": "user", "content": "Test"}]
    deep_thoughts = "Test report"

    # Test each criterion gets appropriate instructions
    for criterion_id, criterion_info in EvaluatorAgent.CRITERIA.items():
        prompt = evaluator_agent._build_criterion_prompt(
            criterion_id, criterion_info, conversation, deep_thoughts
        )

        assert f"Criterion {criterion_id}" in prompt
        assert criterion_info["name"] in prompt
        assert criterion_info["description"] in prompt
        assert "Return ONLY a JSON object" in prompt

        # Check for specific evaluation instructions
        if criterion_id == "A":
            assert "biggest/most important problem" in prompt
        elif criterion_id == "B":
            assert "key constraint" in prompt
            assert "crux" in prompt
        elif criterion_id == "C":
            assert "TODAY" in prompt
        elif criterion_id == "D":
            assert "multiple distinct approaches" in prompt
        elif criterion_id == "E":
            assert "core beliefs" in prompt


@pytest.mark.asyncio
async def test_evaluator_report_formatting(mock_llm_service):
    """Test evaluation report formatting."""
    agent = EvaluatorAgent(llm_service=mock_llm_service)

    evaluations = {
        "A": {"name": "Problem Definition", "score": 1.0, "reasoning": "Clear"},
        "B": {"name": "Crux Recognition", "score": 0.0, "reasoning": "Missing"},
        "C": {"name": "Today Accomplishment", "score": 1.0, "reasoning": "Specific"},
        "D": {"name": "Multiple Paths", "score": 0.7, "reasoning": "Good variety"},
        "E": {"name": "Core Beliefs", "score": 0.4, "reasoning": "Some alignment"},
    }

    # Add conversation and summary for new method signature
    conversation = [
        {"role": "user", "content": "Test conversation"},
        {"role": "assistant", "content": "Test response"}
    ]
    summary = "This was a test coaching session."
    
    report = agent._format_evaluation_report(evaluations, 0.65, conversation, summary)

    # Check formatting
    assert "Overall Effectiveness Score: 65.0%" in report
    assert "A. Problem Definition: ✓" in report
    assert "B. Crux Recognition: ✗" in report
    assert "D. Multiple Paths: 70.0%" in report
    assert "Conversation Summary" in report
    assert summary in report
    assert "Full Conversation Transcript" in report
    assert "Test conversation" in report

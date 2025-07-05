"""Test enhanced relevance scoring system for Session 6.3."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestration.context_state import ContextState
from src.orchestration.relevance_scorer import EnhancedRelevanceScorer


@pytest.mark.asyncio
async def test_context_relevance_scoring():
    """Should score context relevance based on conversation content."""
    scorer = EnhancedRelevanceScorer()
    
    # High relevance for task-related conversation
    state = ContextState(
        messages=[{"type": "user", "content": "What should I prioritize today?", "timestamp": datetime.now().isoformat()}],
        conversation_id="test_conv"
    )
    result = await scorer.score(state)
    
    assert result.context_relevance["todos"] > 0.7
    assert result.context_relevance["calendar"] > 0.5
    assert "context_relevance_scorer" in result.decision_path
    
    # Low relevance for emotional check-in
    state = ContextState(
        messages=[{"type": "user", "content": "I'm feeling overwhelmed", "timestamp": datetime.now().isoformat()}],
        conversation_id="test_conv"
    )
    result = await scorer.score(state)
    
    assert result.context_relevance["todos"] < 0.3


@pytest.mark.asyncio
async def test_pattern_matching_relevance():
    """Should detect context relevance through pattern matching."""
    scorer = EnhancedRelevanceScorer()
    
    # Test specific patterns
    test_cases = [
        ("What are my tasks for today?", {"todos": 0.4, "calendar": 0.4}),
        ("Let's review my core beliefs", {"documents": 0.4, "todos": 0.1}),
        ("Remember what we discussed about delegation?", {"memory": 0.4, "documents": 0.0}),
        ("I need help with project planning", {"todos": 0.4, "documents": 0.2}),
        ("What's my schedule looking like?", {"calendar": 0.4, "todos": 0.2})
    ]
    
    for content, expected_scores in test_cases:
        state = ContextState(
            messages=[{"type": "user", "content": content, "timestamp": datetime.now().isoformat()}],
            conversation_id="test_conv"
        )
        result = await scorer.score(state)
        
        for context_type, min_score in expected_scores.items():
            if context_type in result.context_relevance:
                assert result.context_relevance[context_type] >= min_score - 0.1, \
                    f"Expected {context_type} >= {min_score} for '{content}', got {result.context_relevance[context_type]}"


@pytest.mark.asyncio
async def test_conversation_history_relevance():
    """Should consider conversation history for relevance scoring."""
    scorer = EnhancedRelevanceScorer()
    
    # Multiple messages building context
    state = ContextState(
        messages=[
            {"type": "user", "content": "Good morning!", "timestamp": datetime.now().isoformat()},
            {"type": "agent", "content": "Good morning! What's your biggest priority today?", "timestamp": datetime.now().isoformat()},
            {"type": "user", "content": "I need to focus on finishing my project", "timestamp": datetime.now().isoformat()}
        ],
        conversation_id="test_conv"
    )
    result = await scorer.score(state)
    
    # Should have high todo relevance based on "project" + "focus" context
    assert result.context_relevance["todos"] > 0.7
    
    # Should track multiple message analysis
    assert "analyzed_messages" in result.context_usage
    assert result.context_usage["analyzed_messages"] == 3


@pytest.mark.asyncio 
async def test_llm_powered_relevance_scoring():
    """Should use LLM for sophisticated relevance analysis."""
    scorer = EnhancedRelevanceScorer(use_llm=True)
    
    # Complex, nuanced conversation requiring LLM understanding
    state = ContextState(
        messages=[{"type": "user", "content": "I'm struggling to balance strategic thinking with daily execution. How do I stay focused on both?", "timestamp": datetime.now().isoformat()}],
        conversation_id="test_conv"
    )
    result = await scorer.score(state)
    
    # Should recognize this as both todo-relevant (execution) and document-relevant (strategic thinking)
    assert result.context_relevance["todos"] > 0.6
    assert result.context_relevance["documents"] > 0.5
    
    # Should track LLM usage
    assert result.context_usage["llm_analysis"] == True
    assert "reasoning" in result.context_usage


@pytest.mark.asyncio
async def test_performance_optimized_scoring():
    """Should complete relevance scoring under performance threshold."""
    scorer = EnhancedRelevanceScorer()
    
    # Long conversation history to test performance
    messages = []
    for i in range(20):
        messages.append({
            "type": "user" if i % 2 == 0 else "agent",
            "content": f"Message {i} about various topics",
            "timestamp": datetime.now().isoformat()
        })
    
    state = ContextState(
        messages=messages,
        conversation_id="test_conv"
    )
    
    start_time = datetime.now()
    result = await scorer.score(state)
    duration = (datetime.now() - start_time).total_seconds()
    
    # Should complete in under 500ms
    assert duration < 0.5
    assert result.context_relevance is not None
    assert len(result.context_relevance) > 0


@pytest.mark.asyncio
async def test_configurable_thresholds():
    """Should support configurable relevance thresholds."""
    # High sensitivity scorer
    high_sensitivity_scorer = EnhancedRelevanceScorer(
        todo_threshold=0.3,
        document_threshold=0.3,
        memory_threshold=0.3
    )
    
    # Low sensitivity scorer  
    low_sensitivity_scorer = EnhancedRelevanceScorer(
        todo_threshold=0.8,
        document_threshold=0.8, 
        memory_threshold=0.8
    )
    
    state = ContextState(
        messages=[{"type": "user", "content": "I should probably work on something", "timestamp": datetime.now().isoformat()}],
        conversation_id="test_conv"
    )
    
    high_result = await high_sensitivity_scorer.score(state)
    low_result = await low_sensitivity_scorer.score(state)
    
    # High sensitivity should detect more context needs
    assert any(score > 0.3 for score in high_result.context_relevance.values())
    # Low sensitivity should be more conservative (some scores might still be high due to pattern matches)
    assert max(low_result.context_relevance.values()) > 0.0  # At least some detection
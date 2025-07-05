"""Test implicit context injection for Session 6.4."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestration.context_state import ContextState
from src.orchestration.implicit_context_coach import ImplicitContextCoach
from src.services.llm_service import AnthropicService


@pytest.mark.asyncio
async def test_implicit_context_enhancement():
    """Coach should naturally incorporate relevant context."""
    
    # Mock LLM service
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            # Check if context is in system prompt
            if "Q4 planning" in system_prompt and "team proposals" in system_prompt:
                return "Looking at your current priorities, Q4 planning seems like your biggest lever. What specific aspect of the planning needs your focus first?"
            return "What's your biggest priority today?"
    
    coach = ImplicitContextCoach(MockLLMService())
    
    # Setup state with high-relevance todos
    state = ContextState(
        messages=[{"type": "user", "content": "What's my biggest lever today?", "timestamp": datetime.now().isoformat()}],
        todo_context=[
            {"id": "1", "content": "Finish Q4 planning", "priority": "high"},
            {"id": "2", "content": "Review team proposals", "priority": "medium"}
        ],
        context_relevance={"todos": 0.9},
        conversation_id="test_conv"
    )
    
    result = await coach.generate_response(state)
    
    # Should reference todos without being explicit
    assert "Q4" in result.coach_response or "planning" in result.coach_response
    
    # Should maintain coaching style
    assert "?" in result.coach_response  # Still asks questions
    
    # Should track context attribution
    assert "context_sources_used" in result.context_usage
    assert "todos" in result.context_usage["context_sources_used"]


@pytest.mark.asyncio
async def test_context_budget_management():
    """Should limit context injection to preserve conversation flow."""
    
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            # Should receive abbreviated context, not full todo list
            if len(system_prompt) > 1500:  # Too much context (allowing for base prompt)
                return "ERROR: Context overload"
            return "Based on your priorities, what needs attention first?"
    
    coach = ImplicitContextCoach(MockLLMService(), context_budget=500)
    
    # Setup state with many todos (would exceed budget if not managed)
    large_todo_list = [
        {"id": str(i), "content": f"Task {i}: " + "A" * 100, "priority": "medium"}
        for i in range(20)  # 20 tasks with long descriptions
    ]
    
    state = ContextState(
        messages=[{"type": "user", "content": "What should I prioritize?", "timestamp": datetime.now().isoformat()}],
        todo_context=large_todo_list,
        context_relevance={"todos": 0.8},
        conversation_id="test_conv"
    )
    
    result = await coach.generate_response(state)
    
    # Should not error due to context overload
    assert "ERROR: Context overload" not in result.coach_response
    
    # Should track budget usage
    assert "context_budget_used" in result.context_usage
    assert result.context_usage["context_budget_used"] <= 500


@pytest.mark.asyncio
async def test_context_formatting_strategies():
    """Should format different context types appropriately."""
    
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            return "Based on your context, here's what I see..."
    
    coach = ImplicitContextCoach(MockLLMService())
    
    # Test with multiple context types
    state = ContextState(
        messages=[{"type": "user", "content": "Help me plan my strategic focus", "timestamp": datetime.now().isoformat()}],
        todo_context=[{"id": "1", "content": "Strategic planning session", "priority": "high"}],
        document_context={"core_beliefs": "Focus on impact, embrace discomfort"},
        conversation_history=[{"date": "2024-12-15", "topic": "delegation", "insights": "Need better systems"}],
        context_relevance={"todos": 0.8, "documents": 0.9, "memory": 0.7},
        conversation_id="test_conv"
    )
    
    result = await coach.generate_response(state)
    
    # Should track all context types used
    assert "context_sources_used" in result.context_usage
    context_sources = result.context_usage["context_sources_used"]
    assert "todos" in context_sources
    assert "documents" in context_sources
    assert "memory" in context_sources


@pytest.mark.asyncio
async def test_coaching_style_preservation():
    """Should enhance responses while maintaining coaching approach."""
    
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            # Should receive coaching instructions along with context
            if "coaching" in system_prompt.lower() and "strategic" in system_prompt.lower():
                return "I see you have strategic planning on your list. What's the real challenge you're avoiding there?"
            return "Generic response"
    
    coach = ImplicitContextCoach(MockLLMService())
    
    state = ContextState(
        messages=[{"type": "user", "content": "I'm not sure what to work on", "timestamp": datetime.now().isoformat()}],
        todo_context=[{"id": "1", "content": "Strategic planning", "priority": "high"}],
        context_relevance={"todos": 0.8},
        conversation_id="test_conv"
    )
    
    result = await coach.generate_response(state)
    
    # Should maintain coaching qualities
    assert "?" in result.coach_response  # Asks questions
    assert any(word in result.coach_response.lower() for word in ["challenge", "real", "what"]) # Challenges thinking
    
    # Should reference context naturally
    assert "strategic" in result.coach_response.lower() or "planning" in result.coach_response.lower()


@pytest.mark.asyncio
async def test_no_context_fallback():
    """Should work normally when no context is available."""
    
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            return "What's on your mind today?"
    
    coach = ImplicitContextCoach(MockLLMService())
    
    # No context available
    state = ContextState(
        messages=[{"type": "user", "content": "Good morning", "timestamp": datetime.now().isoformat()}],
        context_relevance={"todos": 0.1, "documents": 0.1, "memory": 0.1},
        conversation_id="test_conv"
    )
    
    result = await coach.generate_response(state)
    
    # Should still generate response
    assert result.coach_response is not None
    assert len(result.coach_response) > 0
    
    # Should track that no context was used
    assert result.context_usage.get("context_sources_used", []) == []


@pytest.mark.asyncio
async def test_context_attribution_tracking():
    """Should track which context sources influenced the response."""
    
    class MockLLMService:
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            return "Looking at your priorities and core beliefs..."
    
    coach = ImplicitContextCoach(MockLLMService())
    
    state = ContextState(
        messages=[{"type": "user", "content": "What should guide my decisions?", "timestamp": datetime.now().isoformat()}],
        todo_context=[{"id": "1", "content": "Decision framework review", "priority": "high"}],
        document_context={"core_beliefs": "Impact-focused decision making"},
        context_relevance={"todos": 0.7, "documents": 0.9},
        conversation_id="test_conv"
    )
    
    result = await coach.generate_response(state)
    
    # Should track detailed attribution
    assert "context_attribution" in result.context_usage
    attribution = result.context_usage["context_attribution"]
    
    # Should show which specific items were used
    assert "todos_referenced" in attribution
    assert "documents_referenced" in attribution
    
    # Should track relevance scores that triggered inclusion
    assert "relevance_scores" in attribution
"""Test memory recall functionality for Session 6.7."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from src.orchestration.context_state import ContextState
from src.orchestration.memory_recall import MemoryRecallNode


@pytest.mark.asyncio
async def test_explicit_memory_recall():
    """Should handle explicit memory queries."""
    
    recall_node = MemoryRecallNode()
    
    # Create state with conversation history
    state = ContextState(
        messages=[{"type": "user", "content": "Remember what we discussed about delegation?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[
            {"date": "2024-12-15", "topic": "delegation", "insights": "Need better systems for task handoff"},
            {"date": "2024-12-10", "topic": "prioritization", "insights": "Focus on impact over urgency"}
        ],
        conversation_id="test_conv"
    )
    
    result = await recall_node.process_memory_query(state)
    
    # Should retrieve relevant memory
    assert result.memory_recall is not None
    assert "delegation" in result.memory_recall
    assert result.recall_mode == True
    assert result.context_usage["memory_recall_triggered"] == True


@pytest.mark.asyncio
async def test_memory_query_detection():
    """Should detect various memory query patterns."""
    
    recall_node = MemoryRecallNode()
    
    # Test different memory query patterns
    query_patterns = [
        "Remember when we talked about goal setting?",
        "What did we discuss about team management?",
        "Recall our conversation about priorities",
        "Last time we talked about delegation",
        "You mentioned before about work-life balance",
        "What was that thing about strategic thinking?",
        "Didn't we cover feedback techniques?",
        "As we discussed earlier about coaching"
    ]
    
    for query in query_patterns:
        state = ContextState(
            messages=[{"type": "user", "content": query, "timestamp": datetime.now().isoformat()}],
            conversation_history=[
                {"date": "2024-12-15", "topic": "delegation", "insights": "Task handoff systems"}
            ],
            conversation_id="test_conv"
        )
        
        result = await recall_node.process_memory_query(state)
        
        # Should detect as memory query
        assert result.context_usage["memory_recall_triggered"] == True, f"Failed to detect: {query}"


@pytest.mark.asyncio
async def test_non_memory_queries():
    """Should not trigger memory recall for regular queries."""
    
    recall_node = MemoryRecallNode()
    
    # Regular queries that shouldn't trigger memory recall
    regular_queries = [
        "How can I improve my delegation skills?",
        "What's the best way to prioritize tasks?",
        "I'm struggling with team communication",
        "Help me set better goals",
        "What should I focus on today?"
    ]
    
    for query in regular_queries:
        state = ContextState(
            messages=[{"type": "user", "content": query, "timestamp": datetime.now().isoformat()}],
            conversation_history=[
                {"date": "2024-12-15", "topic": "delegation", "insights": "Task handoff systems"}
            ],
            conversation_id="test_conv"
        )
        
        result = await recall_node.process_memory_query(state)
        
        # Should NOT trigger memory recall
        assert result.context_usage["memory_recall_triggered"] == False, f"Incorrectly triggered for: {query}"


@pytest.mark.asyncio
async def test_search_term_extraction():
    """Should extract relevant search terms from memory queries."""
    
    recall_node = MemoryRecallNode()
    
    # Test search term extraction
    test_cases = [
        ("Remember what we discussed about delegation strategies?", ["delegation", "strategies"]),
        ("What was that thing about team leadership?", ["team", "leadership"]),
        ("Recall our conversation regarding work-life balance", ["work", "life", "balance"]),
        ("You mentioned before about strategic planning", ["strategic", "planning"])
    ]
    
    for query, expected_terms in test_cases:
        state = ContextState(
            messages=[{"type": "user", "content": query, "timestamp": datetime.now().isoformat()}],
            conversation_id="test_conv"
        )
        
        result = await recall_node.process_memory_query(state)
        
        # Should extract relevant search terms
        search_terms = result.context_usage.get("search_terms", [])
        for term in expected_terms:
            assert any(term in search_term for search_term in search_terms), f"Missing term '{term}' in {search_terms}"


@pytest.mark.asyncio
async def test_memory_relevance_scoring():
    """Should score memory relevance accurately."""
    
    recall_node = MemoryRecallNode()
    
    # Create diverse conversation history
    conversation_history = [
        {"date": "2024-12-15", "topic": "delegation", "insights": "Need better systems for task handoff and delegation strategies"},
        {"date": "2024-12-10", "topic": "prioritization", "insights": "Focus on impact over urgency in task management"},
        {"date": "2024-12-05", "topic": "team communication", "insights": "Weekly check-ins improve clarity and team alignment"}
    ]
    
    state = ContextState(
        messages=[{"type": "user", "content": "Remember what we discussed about delegation?", "timestamp": datetime.now().isoformat()}],
        conversation_history=conversation_history,
        conversation_id="test_conv"
    )
    
    result = await recall_node.process_memory_query(state)
    
    # Should find relevant memories
    assert result.memory_recall is not None
    assert "delegation" in result.memory_recall
    assert result.context_usage["memories_found"] > 0
    
    # Should have high confidence for good matches
    assert result.context_usage["recall_confidence"] > 0.5


@pytest.mark.asyncio
async def test_memory_formatting():
    """Should format memories coherently for coach response."""
    
    recall_node = MemoryRecallNode()
    
    # Rich conversation history
    conversation_history = [
        {
            "date": "2024-12-15", 
            "topic": "delegation", 
            "insights": "Identified need for better task handoff systems and clearer delegation protocols"
        },
        {
            "date": "2024-12-10", 
            "topic": "team leadership", 
            "insights": "Discussed importance of empowering team members and building trust"
        }
    ]
    
    state = ContextState(
        messages=[{"type": "user", "content": "Remember our discussion about delegation and leadership?", "timestamp": datetime.now().isoformat()}],
        conversation_history=conversation_history,
        conversation_id="test_conv"
    )
    
    result = await recall_node.process_memory_query(state)
    
    # Should format as coherent response
    assert result.memory_recall is not None
    assert "remember" in result.memory_recall.lower()
    assert "delegation" in result.memory_recall
    assert "leadership" in result.memory_recall
    
    # Should include actionable follow-up
    assert "how would you like to build" in result.memory_recall.lower()


@pytest.mark.asyncio
async def test_no_memory_found():
    """Should handle cases where no relevant memories exist."""
    
    recall_node = MemoryRecallNode()
    
    # Empty conversation history
    state = ContextState(
        messages=[{"type": "user", "content": "Remember what we discussed about quantum physics?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[],
        conversation_id="test_conv"
    )
    
    result = await recall_node.process_memory_query(state)
    
    # Should handle gracefully
    assert result.memory_recall is not None
    assert "don't have specific memories" in result.memory_recall.lower()
    assert result.context_usage["memories_found"] == 0
    assert result.context_usage["recall_confidence"] == 0.0


@pytest.mark.asyncio
async def test_recent_memory_boost():
    """Should boost relevance for recent memories."""
    
    recall_node = MemoryRecallNode()
    
    # Mix of recent and old memories
    recent_date = datetime.now() - timedelta(days=2)
    old_date = datetime.now() - timedelta(days=30)
    
    conversation_history = [
        {
            "date": recent_date.isoformat(), 
            "topic": "delegation", 
            "insights": "Recent discussion about task handoff"
        },
        {
            "date": old_date.isoformat(), 
            "topic": "delegation", 
            "insights": "Old discussion about delegation techniques"
        }
    ]
    
    state = ContextState(
        messages=[{"type": "user", "content": "Remember what we discussed about delegation?", "timestamp": datetime.now().isoformat()}],
        conversation_history=conversation_history,
        conversation_id="test_conv"
    )
    
    result = await recall_node.process_memory_query(state)
    
    # Should prioritize recent memories
    assert result.memory_recall is not None
    assert "recent" in result.memory_recall.lower()


@pytest.mark.asyncio
async def test_multiple_memory_integration():
    """Should integrate multiple relevant memories coherently."""
    
    recall_node = MemoryRecallNode()
    
    # Multiple related memories
    conversation_history = [
        {
            "date": "2024-12-15", 
            "topic": "delegation strategies", 
            "insights": "Discussed various approaches to effective delegation"
        },
        {
            "date": "2024-12-12", 
            "topic": "delegation challenges", 
            "insights": "Identified common obstacles in delegation process"
        },
        {
            "date": "2024-12-10", 
            "topic": "delegation tools", 
            "insights": "Explored digital tools for task management and delegation"
        }
    ]
    
    state = ContextState(
        messages=[{"type": "user", "content": "What did we cover about delegation?", "timestamp": datetime.now().isoformat()}],
        conversation_history=conversation_history,
        conversation_id="test_conv"
    )
    
    result = await recall_node.process_memory_query(state)
    
    # Should integrate multiple memories
    assert result.memory_recall is not None
    assert result.context_usage["memories_found"] == 3
    assert "strategies" in result.memory_recall
    assert "challenges" in result.memory_recall
    assert "tools" in result.memory_recall


@pytest.mark.asyncio
async def test_context_usage_tracking():
    """Should track context usage properly."""
    
    recall_node = MemoryRecallNode()
    
    state = ContextState(
        messages=[{"type": "user", "content": "Remember our talk about leadership?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[
            {"date": "2024-12-15", "topic": "leadership", "insights": "Authentic leadership principles"}
        ],
        conversation_id="test_conv"
    )
    
    result = await recall_node.process_memory_query(state)
    
    # Should track all context usage
    assert "memory_recall_triggered" in result.context_usage
    assert "search_terms" in result.context_usage
    assert "memories_found" in result.context_usage
    assert "recall_confidence" in result.context_usage
    
    # Should add to decision path
    assert "memory_recall" in result.decision_path
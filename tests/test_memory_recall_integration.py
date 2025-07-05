"""Test memory recall integration with other Session 6 components."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestration.context_state import ContextState
from src.orchestration.memory_recall import MemoryRecallNode
from src.orchestration.relevance_scorer import EnhancedRelevanceScorer
from src.orchestration.document_loader import MarkdownDocumentLoader


@pytest.mark.asyncio
async def test_memory_recall_with_relevance_scoring():
    """Should work with the enhanced relevance scorer."""
    
    # Create components
    scorer = EnhancedRelevanceScorer()
    memory_recall = MemoryRecallNode()
    
    # Initial state
    state = ContextState(
        messages=[{"type": "user", "content": "Remember what we discussed about delegation?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[
            {"date": "2024-12-15", "topic": "delegation", "insights": "Need better systems for task handoff"}
        ],
        conversation_id="test_conv"
    )
    
    # First, score relevance
    scored_state = await scorer.score(state)
    
    # Then, process memory recall
    final_state = await memory_recall.process_memory_query(scored_state)
    
    # Should have both scoring and recall results
    assert final_state.context_relevance is not None
    assert final_state.memory_recall is not None
    assert final_state.recall_mode == True
    assert "delegation" in final_state.memory_recall


@pytest.mark.asyncio 
async def test_memory_recall_bypass_context_fetching():
    """Should skip regular context fetching when memory recall is triggered."""
    
    memory_recall = MemoryRecallNode()
    
    state = ContextState(
        messages=[{"type": "user", "content": "Do you remember our conversation about leadership?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[
            {"date": "2024-12-15", "topic": "leadership", "insights": "Authentic leadership matters"}
        ],
        conversation_id="test_conv",
        context_relevance={"todos": 0.8, "documents": 0.9, "memory": 0.7}  # High relevance scores
    )
    
    result = await memory_recall.process_memory_query(state)
    
    # Memory recall should be triggered
    assert result.context_usage["memory_recall_triggered"] == True
    assert result.recall_mode == True
    assert "leadership" in result.memory_recall
    
    # Should indicate that normal context fetching can be bypassed
    assert "memory_recall" in result.decision_path


@pytest.mark.asyncio
async def test_memory_recall_with_document_context():
    """Should work alongside document context when both are relevant."""
    
    memory_recall = MemoryRecallNode()
    document_loader = MarkdownDocumentLoader("/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory")
    
    # Query that could trigger both memory recall and document loading
    state = ContextState(
        messages=[{"type": "user", "content": "Remember our core beliefs discussion?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[
            {"date": "2024-12-15", "topic": "core beliefs", "insights": "Values guide decision-making"}
        ],
        conversation_id="test_conv",
        context_relevance={"documents": 0.9}  # High document relevance
    )
    
    # Process memory recall first
    recall_result = await memory_recall.process_memory_query(state)
    
    # Then load documents
    final_result = await document_loader.load_documents(recall_result)
    
    # Should have both memory recall and document context
    assert final_result.memory_recall is not None
    assert final_result.document_context is not None
    assert "core beliefs" in final_result.memory_recall.lower()
    assert "Core_beliefs" in final_result.document_context


@pytest.mark.asyncio
async def test_regular_query_flow_unchanged():
    """Should not interfere with regular coaching queries."""
    
    memory_recall = MemoryRecallNode()
    
    # Regular coaching query
    state = ContextState(
        messages=[{"type": "user", "content": "I'm struggling with delegation today. Can you help?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[
            {"date": "2024-12-15", "topic": "delegation", "insights": "Task handoff systems"}
        ],
        conversation_id="test_conv"
    )
    
    result = await memory_recall.process_memory_query(state)
    
    # Should NOT trigger memory recall
    assert result.context_usage["memory_recall_triggered"] == False
    assert result.recall_mode == False
    assert result.memory_recall is None
    
    # Should proceed with normal flow
    assert "memory_recall" not in result.decision_path


@pytest.mark.asyncio
async def test_context_usage_tracking_integration():
    """Should properly track context usage across components."""
    
    memory_recall = MemoryRecallNode()
    
    # Start with some existing context usage
    state = ContextState(
        messages=[{"type": "user", "content": "What did we cover about team management?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[
            {"date": "2024-12-15", "topic": "team management", "insights": "Clear communication channels"}
        ],
        conversation_id="test_conv",
        context_usage={"previous_component": "already_processed"}
    )
    
    result = await memory_recall.process_memory_query(state)
    
    # Should preserve existing context usage and add its own
    assert result.context_usage["previous_component"] == "already_processed"
    assert result.context_usage["memory_recall_triggered"] == True
    assert "search_terms" in result.context_usage
    assert "memories_found" in result.context_usage
    assert "recall_confidence" in result.context_usage


@pytest.mark.asyncio
async def test_decision_path_tracking():
    """Should properly track decision path for debugging."""
    
    memory_recall = MemoryRecallNode()
    
    state = ContextState(
        messages=[{"type": "user", "content": "Recall our discussion about strategic planning", "timestamp": datetime.now().isoformat()}],
        conversation_history=[
            {"date": "2024-12-15", "topic": "strategic planning", "insights": "Long-term vision clarity"}
        ],
        conversation_id="test_conv",
        decision_path=["context_scorer", "relevance_scorer"]
    )
    
    result = await memory_recall.process_memory_query(state)
    
    # Should preserve existing decision path and add its own
    assert "context_scorer" in result.decision_path
    assert "relevance_scorer" in result.decision_path
    assert "memory_recall" in result.decision_path
    
    # Should be last in the path
    assert result.decision_path[-1] == "memory_recall"


@pytest.mark.asyncio
async def test_edge_case_empty_conversation_history():
    """Should handle edge case where conversation history is empty."""
    
    memory_recall = MemoryRecallNode()
    
    state = ContextState(
        messages=[{"type": "user", "content": "Remember what we talked about last week?", "timestamp": datetime.now().isoformat()}],
        conversation_history=[],  # Empty history
        conversation_id="test_conv"
    )
    
    result = await memory_recall.process_memory_query(state)
    
    # Should still trigger memory recall but handle gracefully
    assert result.context_usage["memory_recall_triggered"] == True
    assert result.context_usage["memories_found"] == 0
    assert result.context_usage["recall_confidence"] == 0.0
    
    # Should provide helpful response
    assert "don't have specific memories" in result.memory_recall.lower()


@pytest.mark.asyncio
async def test_high_confidence_memory_recall():
    """Should have high confidence for strong memory matches."""
    
    memory_recall = MemoryRecallNode()
    
    # Rich conversation history with strong matches
    conversation_history = [
        {
            "date": "2024-12-15", 
            "topic": "delegation strategies", 
            "insights": "Systematic approach to delegating tasks with clear expectations and follow-up"
        },
        {
            "date": "2024-12-12", 
            "topic": "delegation frameworks", 
            "insights": "Using RACI matrices and delegation templates for clarity"
        }
    ]
    
    state = ContextState(
        messages=[{"type": "user", "content": "Remember our detailed discussion about delegation strategies?", "timestamp": datetime.now().isoformat()}],
        conversation_history=conversation_history,
        conversation_id="test_conv"
    )
    
    result = await memory_recall.process_memory_query(state)
    
    # Should have high confidence and good results
    assert result.context_usage["recall_confidence"] > 0.7
    assert result.context_usage["memories_found"] >= 2
    assert "delegation" in result.memory_recall
    assert "strategies" in result.memory_recall
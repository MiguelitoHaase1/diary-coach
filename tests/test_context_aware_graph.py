"""Test context-aware graph structure for Session 6."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.events.schemas import UserMessage, AgentResponse
from src.orchestration.state import ConversationState
from src.orchestration.context_graph import create_context_aware_graph


@pytest.mark.asyncio
async def test_context_aware_graph_structure():
    """Graph should have context nodes that can be conditionally executed."""
    graph = create_context_aware_graph()
    
    # Graph should have new context nodes
    assert "todo_context" in graph.nodes
    assert "document_context" in graph.nodes
    assert "conversation_memory" in graph.nodes
    
    # Should have relevance scoring node
    assert "context_relevance_scorer" in graph.nodes
    
    # Should maintain existing coach functionality
    result = await graph.ainvoke({
        "messages": [{"type": "user", "content": "Good morning!", "timestamp": datetime.now().isoformat()}],
        "context_enabled": True,
        "conversation_id": "test_conv"
    })
    assert result["coach_response"] is not None


@pytest.mark.asyncio
async def test_context_node_conditional_execution():
    """Context nodes should only execute when relevance score exceeds threshold."""
    graph = create_context_aware_graph()
    
    # Low relevance scenario - should skip context nodes
    result = await graph.ainvoke({
        "messages": [{"type": "user", "content": "I'm feeling overwhelmed", "timestamp": datetime.now().isoformat()}],
        "context_enabled": True,
        "conversation_id": "test_conv"
    })
    
    # Should have relevance scores
    assert "context_relevance" in result
    assert "todos" in result["context_relevance"]
    assert "documents" in result["context_relevance"]
    assert "memory" in result["context_relevance"]
    
    # Should have decision tracking
    assert "decision_path" in result
    assert "context_relevance_scorer" in result["decision_path"]


@pytest.mark.asyncio
async def test_context_state_channels():
    """Graph should have dedicated state channels for context data."""
    graph = create_context_aware_graph()
    
    # High relevance scenario
    result = await graph.ainvoke({
        "messages": [{"type": "user", "content": "What should I prioritize today?", "timestamp": datetime.now().isoformat()}],
        "context_enabled": True,
        "conversation_id": "test_conv"
    })
    
    # Should have context data channels
    assert "todo_context" in result
    assert "document_context" in result  
    assert "conversation_history" in result
    assert "context_usage" in result
    
    # Should track which context sources were used
    assert isinstance(result["context_usage"], dict)


@pytest.mark.asyncio
async def test_context_disabled_fallback():
    """Graph should work normally when context is disabled."""
    graph = create_context_aware_graph()
    
    # Context disabled
    result = await graph.ainvoke({
        "messages": [{"type": "user", "content": "Good morning!", "timestamp": datetime.now().isoformat()}],
        "context_enabled": False,
        "conversation_id": "test_conv"
    })
    
    # Should still have coach response
    assert result["coach_response"] is not None
    
    # Should skip context nodes
    assert "todo_context" not in result or result["todo_context"] is None
    assert "document_context" not in result or result["document_context"] is None
    assert "conversation_history" not in result or result["conversation_history"] is None
"""Test MCP Todo Integration for Session 6.2."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestration.context_state import ContextState
from src.orchestration.mcp_todo_node import MCPTodoNode


@pytest.mark.asyncio
async def test_mcp_todo_context_node():
    """MCP node should fetch relevant todos based on conversation."""
    state = ContextState(
        messages=[{"type": "user", "content": "I need to work on the API integration today", "timestamp": datetime.now().isoformat()}],
        context_relevance={"todos": 0.8},
        conversation_id="test_conv"
    )
    
    todo_node = MCPTodoNode()
    result = await todo_node.fetch_todos(state)
    
    # Should fetch todos when relevance is high
    assert result.todo_context is not None
    assert len(result.todo_context) > 0
    assert "API" in str(result.todo_context).upper()
    
    # Should track context usage
    assert result.context_usage["todos_fetched"] == True


@pytest.mark.asyncio
async def test_mcp_todo_low_relevance():
    """MCP node should skip fetching when relevance is low."""
    state = ContextState(
        messages=[{"type": "user", "content": "I'm feeling overwhelmed", "timestamp": datetime.now().isoformat()}],
        context_relevance={"todos": 0.2},
        conversation_id="test_conv"
    )
    
    todo_node = MCPTodoNode()
    result = await todo_node.fetch_todos(state)
    
    # Should not fetch todos when relevance is low
    assert result.context_usage["todos_fetched"] == False


@pytest.mark.asyncio
async def test_mcp_todo_filtering():
    """MCP node should filter todos based on conversation context."""
    state = ContextState(
        messages=[{"type": "user", "content": "What should I prioritize for the meeting prep?", "timestamp": datetime.now().isoformat()}],
        context_relevance={"todos": 0.9},
        conversation_id="test_conv"
    )
    
    todo_node = MCPTodoNode()
    result = await todo_node.fetch_todos(state)
    
    # Should fetch todos and attempt content filtering
    assert result.todo_context is not None
    assert result.context_usage["todos_fetched"] == True
    
    # Should track filter attempts
    assert "filter_applied" in result.context_usage


@pytest.mark.asyncio
async def test_mcp_todo_error_handling():
    """MCP node should handle connection errors gracefully."""
    state = ContextState(
        messages=[{"type": "user", "content": "What should I do today?", "timestamp": datetime.now().isoformat()}],
        context_relevance={"todos": 0.9},
        conversation_id="test_conv"
    )
    
    # Create node with failing connection
    todo_node = MCPTodoNode(mock_error=True)
    result = await todo_node.fetch_todos(state)
    
    # Should handle error gracefully
    assert result.context_usage["todos_fetched"] == False
    assert "error" in result.context_usage
    assert result.todo_context is None


@pytest.mark.asyncio
async def test_mcp_todo_empty_response():
    """MCP node should handle empty todo lists gracefully."""
    state = ContextState(
        messages=[{"type": "user", "content": "What's my biggest priority?", "timestamp": datetime.now().isoformat()}],
        context_relevance={"todos": 0.8},
        conversation_id="test_conv"
    )
    
    # Create node with empty response
    todo_node = MCPTodoNode(mock_empty=True)
    result = await todo_node.fetch_todos(state)
    
    # Should handle empty response
    assert result.context_usage["todos_fetched"] == True
    assert result.todo_context == []
    assert "empty_response" in result.context_usage
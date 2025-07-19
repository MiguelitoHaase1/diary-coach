"""Tests for MCP Agent."""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.agents.mcp_agent import MCPAgent
from src.agents.base import AgentRequest, AgentCapability
from src.orchestration.context_state import ContextState


@pytest.fixture
def mock_mcp_node():
    """Create a mock MCP node."""
    node = Mock()
    node.get_mcp_status = AsyncMock()
    node.fetch_todos = AsyncMock()
    return node


@pytest.fixture
def mock_todos():
    """Create mock todo data."""
    return [
        {
            "id": "1",
            "content": "Finish Q4 planning",
            "priority": "high",
            "due_date": datetime.now().date().isoformat(),
            "project": "Work",
            "labels": ["planning", "quarterly"]
        },
        {
            "id": "2",
            "content": "Review team proposals",
            "priority": "medium",
            "due_date": None,
            "project": "Work",
            "labels": ["review"]
        },
        {
            "id": "3",
            "content": "Buy groceries",
            "priority": "low",
            "due_date": None,
            "project": "Personal",
            "labels": ["errands"]
        }
    ]


@pytest.mark.asyncio
async def test_mcp_agent_initialization_connected(mock_mcp_node):
    """Test agent initialization with successful connection."""
    mock_mcp_node.get_mcp_status.return_value = {
        "connected": True,
        "total_todos": 15,
        "last_sync": datetime.now().isoformat()
    }
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    
    assert agent.name == "mcp"
    assert AgentCapability.TASK_MANAGEMENT in agent.capabilities
    assert not agent.is_initialized
    
    await agent.initialize()
    
    assert agent.is_initialized
    assert agent.connection_status["connected"] is True
    assert agent.connection_status["total_todos"] == 15


@pytest.mark.asyncio
async def test_mcp_agent_initialization_disconnected(mock_mcp_node):
    """Test agent initialization with failed connection."""
    mock_mcp_node.get_mcp_status.return_value = {
        "connected": False,
        "error": "No TODOIST_API_TOKEN provided"
    }
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    
    await agent.initialize()
    
    assert agent.is_initialized  # Still initialized
    assert agent.connection_status["connected"] is False
    assert "No TODOIST_API_TOKEN" in agent.connection_status["error"]


@pytest.mark.asyncio
async def test_get_connection_status(mock_mcp_node):
    """Test getting connection status."""
    mock_mcp_node.get_mcp_status.return_value = {
        "connected": True,
        "total_todos": 10,
        "last_sync": "2025-01-15T10:00:00"
    }
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    await agent.initialize()
    
    request = AgentRequest(
        from_agent="coach",
        to_agent="mcp",
        query="What's the MCP connection status?",
        context={}
    )
    
    response = await agent.handle_request(request)
    
    assert response.agent_name == "mcp"
    assert not response.error
    assert "TODOIST CONNECTION: Active" in response.content
    assert "Total Tasks: 10" in response.content
    assert response.metadata["connected"] is True


@pytest.mark.asyncio
async def test_get_tasks_today_filter(mock_mcp_node, mock_todos):
    """Test getting tasks with today filter."""
    # Mock the fetch_todos to return a state with todos
    mock_state = ContextState()
    mock_state.todo_context = [mock_todos[0]]  # Only today's task
    mock_state.context_usage = {"todos_fetched": True}
    mock_mcp_node.fetch_todos.return_value = mock_state
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    agent.connection_status = {"connected": True}
    
    request = AgentRequest(
        from_agent="coach",
        to_agent="mcp",
        query="What tasks are due today?",
        context={}
    )
    
    response = await agent.handle_request(request)
    
    assert "CURRENT TASKS:" in response.content
    assert "🔴 [DUE TODAY] Finish Q4 planning" in response.content
    assert "Due Today: 1" in response.content
    assert response.metadata["tasks_found"] == 1
    
    # Verify fetch was called with today filter
    mock_mcp_node.fetch_todos.assert_called_once()
    call_args = mock_mcp_node.fetch_todos.call_args
    assert call_args[0][1] == "today"  # date_filter argument


@pytest.mark.asyncio
async def test_get_relevant_tasks(mock_mcp_node, mock_todos):
    """Test getting tasks based on context."""
    mock_state = ContextState()
    mock_state.todo_context = mock_todos[:2]  # First two tasks
    mock_state.context_usage = {"todos_fetched": True}
    mock_mcp_node.fetch_todos.return_value = mock_state
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    agent.connection_status = {"connected": True}
    
    request = AgentRequest(
        from_agent="coach",
        to_agent="mcp",
        query="What should I work on related to planning?",
        context={"conversation_id": "test123"}
    )
    
    response = await agent.handle_request(request)
    
    assert "CURRENT TASKS:" in response.content
    assert "Finish Q4 planning" in response.content
    assert "Review team proposals" in response.content
    assert "TASK SUMMARY:" in response.content
    assert response.metadata["tasks_shown"] == 2


@pytest.mark.asyncio
async def test_no_tasks_found(mock_mcp_node):
    """Test response when no tasks are found."""
    mock_state = ContextState()
    mock_state.todo_context = None
    mock_state.context_usage = {"todos_fetched": False}
    mock_mcp_node.fetch_todos.return_value = mock_state
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    
    request = AgentRequest(
        from_agent="coach",
        to_agent="mcp",
        query="Any tasks?",
        context={}
    )
    
    response = await agent.handle_request(request)
    
    assert "No" in response.content
    assert response.metadata.get("todos_fetched") is False


@pytest.mark.asyncio
async def test_task_formatting(mock_mcp_node, mock_todos):
    """Test proper task formatting with priorities and metadata."""
    mock_state = ContextState()
    mock_state.todo_context = mock_todos
    mock_state.context_usage = {"todos_fetched": True}
    mock_mcp_node.fetch_todos.return_value = mock_state
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    agent.connection_status = {"connected": True}
    
    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="mcp",
        query="Show all tasks",
        context={}
    )
    
    response = await agent.handle_request(request)
    
    # Check formatting
    assert "🔴 [DUE TODAY] Finish Q4 planning" in response.content  # Due today takes precedence
    assert "[Medium Priority]" in response.content
    assert "Project: Work" in response.content
    # Due date is not shown for tasks due today
    
    # Low priority task should not have priority marker
    assert "Buy groceries" in response.content
    assert "[Low Priority] Buy groceries" not in response.content
    
    # Check metadata
    assert response.metadata["high_priority_count"] == 0  # Due today takes precedence
    assert response.metadata["due_today_count"] == 1
    assert response.metadata["tasks_shown"] == 3


@pytest.mark.asyncio
async def test_error_handling(mock_mcp_node):
    """Test error handling during task fetch."""
    mock_mcp_node.fetch_todos.side_effect = Exception("MCP connection failed")
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    
    request = AgentRequest(
        from_agent="coach",
        to_agent="mcp",
        query="What are my tasks?",
        context={}
    )
    
    response = await agent.handle_request(request)
    
    assert response.error == "MCP connection failed"
    assert "Unable to access task information" in response.content
    assert response.metadata["error"] == "MCP connection failed"


@pytest.mark.asyncio
async def test_overdue_filter(mock_mcp_node):
    """Test getting overdue tasks."""
    mock_state = ContextState()
    mock_state.todo_context = []
    mock_state.context_usage = {"todos_fetched": True}
    mock_mcp_node.fetch_todos.return_value = mock_state
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    
    request = AgentRequest(
        from_agent="coach",
        to_agent="mcp",
        query="Show me overdue tasks",
        context={}
    )
    
    response = await agent.handle_request(request)
    
    # Verify fetch was called with overdue filter
    mock_mcp_node.fetch_todos.assert_called_once()
    call_args = mock_mcp_node.fetch_todos.call_args
    assert call_args[0][1] == "overdue"


@pytest.mark.asyncio
async def test_task_limit_to_five(mock_mcp_node):
    """Test that only top 5 tasks are shown."""
    # Create 10 mock tasks
    many_todos = [
        {
            "id": str(i),
            "content": f"Task {i}",
            "priority": "medium",
            "project": "Test"
        }
        for i in range(10)
    ]
    
    mock_state = ContextState()
    mock_state.todo_context = many_todos
    mock_state.context_usage = {"todos_fetched": True}
    mock_mcp_node.fetch_todos.return_value = mock_state
    
    agent = MCPAgent()
    agent.mcp_node = mock_mcp_node
    agent.connection_status = {"connected": True}
    
    request = AgentRequest(
        from_agent="coach",
        to_agent="mcp",
        query="Show all tasks",
        context={}
    )
    
    response = await agent.handle_request(request)
    
    # Count task lines (start with "- ")
    task_lines = [line for line in response.content.split("\n") if line.startswith("- ")]
    assert len(task_lines) == 5
    
    assert response.metadata["tasks_found"] == 10
    assert response.metadata["tasks_shown"] == 5
    assert "Total: 10 tasks" in response.content
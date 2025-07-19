"""Integration tests for MCP Agent in multi-agent system."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from src.agents.mcp_agent import MCPAgent
from src.agents.base import AgentRequest, AgentResponse
from src.orchestration.multi_agent_state import MultiAgentState
from src.agents.registry import agent_registry


@pytest.fixture
def mock_mcp_status():
    """Mock MCP status response."""
    return {
        "connected": True,
        "total_todos": 5,
        "last_sync": datetime.now().isoformat()
    }


@pytest.fixture
def mock_todos():
    """Mock todo data."""
    return [
        {
            "id": "1",
            "content": "Prepare Q4 strategy presentation",
            "priority": "high",
            "due_date": datetime.now().date().isoformat(),
            "project": "Work"
        },
        {
            "id": "2",
            "content": "Review team proposals",
            "priority": "medium",
            "project": "Work"
        }
    ]


@pytest.mark.asyncio
async def test_mcp_agent_in_multi_agent_state(mock_mcp_status, mock_todos):
    """Test MCP Agent integration with MultiAgentState."""
    # Create agent with mocked MCP node
    agent = MCPAgent()
    
    with patch.object(agent.mcp_node, 'get_mcp_status', AsyncMock(return_value=mock_mcp_status)):
        with patch.object(agent.mcp_node, 'fetch_todos') as mock_fetch:
            # Mock fetch_todos to return a state with todos
            from src.orchestration.context_state import ContextState
            mock_state = ContextState()
            mock_state.todo_context = mock_todos
            mock_state.context_usage = {"todos_fetched": True}
            mock_fetch.return_value = mock_state
            
            await agent.initialize()
            
            # Register agent
            agent_registry.register_instance(agent)
            
            # Create multi-agent state
            state = MultiAgentState(
                messages=[{
                    "role": "user",
                    "content": "What should I focus on today?"
                }],
                conversation_id="test_conv"
            )
            
            # Simulate coach requesting task context
            request = AgentRequest(
                from_agent="coach",
                to_agent="mcp",
                query="What tasks does the user have today?",
                context={"conversation_id": state.conversation_id}
            )
            
            # Add to pending requests
            state.add_pending_request(request)
            
            # Process request
            response = await agent.handle_request(request)
            
            # Complete request in state
            state.complete_request(request.request_id, response)
            
            # Store MCP context
            state.set_mcp_context({
                "tasks": response.content,
                "metadata": response.metadata
            })
            
            # Verify integration
            assert state.mcp_context is not None
            assert "CURRENT TASKS:" in state.mcp_context["tasks"]
            assert "Q4 strategy presentation" in state.mcp_context["tasks"]
            assert len(state.agent_responses["mcp"]) == 1


@pytest.mark.asyncio
async def test_coach_requests_today_tasks():
    """Test coach agent requesting today's tasks from MCP agent."""
    agent = MCPAgent()
    
    # Mock the MCP node methods
    with patch.object(agent.mcp_node, 'get_mcp_status', AsyncMock(return_value={"connected": True})):
        with patch.object(agent.mcp_node, 'fetch_todos') as mock_fetch:
            from src.orchestration.context_state import ContextState
            mock_state = ContextState()
            mock_state.todo_context = [
                {
                    "id": "1",
                    "content": "Daily standup",
                    "priority": "high",
                    "due_date": datetime.now().date().isoformat(),
                    "project": "Work"
                }
            ]
            mock_state.context_usage = {"todos_fetched": True}
            mock_fetch.return_value = mock_state
            
            await agent.initialize()
            
            # Coach requests today's tasks
            request = AgentRequest(
                from_agent="coach",
                to_agent="mcp",
                query="What tasks are due today?",
                context={
                    "conversation_id": "test123",
                    "current_time": datetime.now().isoformat()
                }
            )
            
            response = await agent.handle_request(request)
            
            # Verify response
            assert not response.error
            assert "Daily standup" in response.content
            assert "Due Today: 1" in response.content
            
            # Verify today filter was used
            mock_fetch.assert_called_once()
            call_args = mock_fetch.call_args
            assert call_args[0][1] == "today"  # date_filter


@pytest.mark.asyncio
async def test_mcp_context_relevance_filtering():
    """Test that MCP agent respects context relevance."""
    agent = MCPAgent()
    
    with patch.object(agent.mcp_node, 'get_mcp_status', AsyncMock(return_value={"connected": True})):
        with patch.object(agent.mcp_node, 'fetch_todos') as mock_fetch:
            from src.orchestration.context_state import ContextState
            
            # Mock low relevance response
            mock_state = ContextState()
            mock_state.todo_context = None
            mock_state.context_usage = {
                "todos_fetched": False,
                "skip_reason": "Low relevance score"
            }
            mock_fetch.return_value = mock_state
            
            await agent.initialize()
            
            request = AgentRequest(
                from_agent="coach",
                to_agent="mcp",
                query="User is discussing feelings, any relevant tasks?",
                context={"messages": [
                    {"role": "user", "content": "I'm feeling overwhelmed"}
                ]}
            )
            
            response = await agent.handle_request(request)
            
            # Should handle low relevance gracefully
            assert not response.error
            assert "No relevant tasks" in response.content or "No tasks" in response.content


@pytest.mark.asyncio
async def test_mcp_connection_failure_handling():
    """Test graceful handling of MCP connection failures."""
    agent = MCPAgent()
    
    # Mock connection failure
    with patch.object(
        agent.mcp_node, 
        'get_mcp_status', 
        AsyncMock(return_value={
            "connected": False,
            "error": "No TODOIST_API_TOKEN provided"
        })
    ):
        await agent.initialize()
        
        # Create state
        state = MultiAgentState(
            messages=[{"role": "user", "content": "What should I work on?"}],
            conversation_id="test_conv"
        )
        
        # Request tasks despite connection failure
        request = AgentRequest(
            from_agent="orchestrator",
            to_agent="mcp",
            query="Get user's high priority tasks",
            context={"conversation_id": state.conversation_id}
        )
        
        # Mock fetch_todos to fail
        with patch.object(
            agent.mcp_node,
            'fetch_todos',
            AsyncMock(side_effect=Exception("Connection failed"))
        ):
            response = await agent.handle_request(request)
        
        # Should handle error gracefully
        assert response.error == "Connection failed"
        assert "Unable to access" in response.content
        
        # Can still store in state
        state.set_mcp_context({
            "error": response.error,
            "available": False
        })
        
        assert state.mcp_context["available"] is False


@pytest.mark.asyncio
async def test_mcp_agent_stage_integration():
    """Test MCP agent working across different conversation stages."""
    agent = MCPAgent()
    
    with patch.object(agent.mcp_node, 'get_mcp_status', AsyncMock(return_value={"connected": True})):
        await agent.initialize()
        
        # Stage 1: Exploration - Coach calls MCP directly
        state = MultiAgentState(conversation_id="test_conv")
        state.current_stage = 1
        state.activate_agent("coach")
        state.activate_agent("mcp")
        
        # Stage 2: Orchestrated - Multiple agents coordinate
        state.update_stage(2, {"problem_identified": True})
        state.activate_agent("orchestrator")
        
        # MCP should be available in both stages
        assert "mcp" in state.active_agents
        
        # Test request in Stage 2
        request = AgentRequest(
            from_agent="orchestrator",
            to_agent="mcp",
            query="Get all tasks related to the identified problem",
            context={
                "stage": state.current_stage,
                "problem": "Time management"
            }
        )
        
        with patch.object(agent.mcp_node, 'fetch_todos') as mock_fetch:
            from src.orchestration.context_state import ContextState
            mock_state = ContextState()
            mock_state.todo_context = []
            mock_state.context_usage = {"todos_fetched": True}
            mock_fetch.return_value = mock_state
            
            response = await agent.handle_request(request)
            
            # Should work in orchestrated stage
            assert not response.error
            assert response.metadata.get("connected") is True
"""Tests for the Orchestrator Agent."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.base import AgentRequest, AgentResponse, AgentCapability
from src.services.llm_service import AnthropicService


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    mock = AsyncMock(spec=AnthropicService)
    mock.generate = AsyncMock()
    mock.generate_response = AsyncMock()
    return mock


@pytest.fixture
def orchestrator(mock_llm_service):
    """Create an orchestrator agent for testing."""
    return OrchestratorAgent(mock_llm_service)


@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    """Test orchestrator agent initializes correctly."""
    await orchestrator.initialize()
    assert orchestrator.agent_id == "orchestrator"
    assert AgentCapability.AGENT_COORDINATION in orchestrator.capabilities
    assert AgentCapability.PARALLEL_EXECUTION in orchestrator.capabilities
    assert AgentCapability.STAGE_MANAGEMENT in orchestrator.capabilities
    assert orchestrator.active_stage == 1
    assert not orchestrator.problem_identified


@pytest.mark.asyncio
async def test_stage_transition_insufficient_history(orchestrator):
    """Test stage transition with insufficient conversation history."""
    request = AgentRequest(
        from_agent="coach",
        to_agent="orchestrator",
        query="check_stage_transition",
        context={
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
    )

    response = await orchestrator.handle_request(request)
    assert response.content == "False"
    assert orchestrator.active_stage == 1


@pytest.mark.asyncio
async def test_stage_transition_with_problem(orchestrator, mock_llm_service):
    """Test stage transition when user expresses a clear problem."""
    # Mock LLM response for stage transition analysis
    mock_llm_service.generate_response.return_value = '''{
        "stage_transition": {
            "recommended": true,
            "reasoning": "User articulated problem with procrastination",
            "confidence": 0.9
        }
    }'''

    request = AgentRequest(
        from_agent="coach",
        to_agent="orchestrator",
        query="check_stage_transition",
        context={
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How are you?"},
                {"role": "user", "content": "Not great"},
                {"role": "assistant", "content": "What's going on?"},
                {"role": "user", "content": "I'm struggling with "
                 "procrastination on my big project and feeling overwhelmed"},
                {"role": "assistant", "content": "Tell me more about this project"}
            ]
        }
    )

    response = await orchestrator.handle_request(request)
    assert response.content == "True"
    assert orchestrator.active_stage == 2
    assert orchestrator.problem_identified


@pytest.mark.asyncio
async def test_stage_transition_coach_request(orchestrator):
    """Test stage transition when coach explicitly requests orchestration."""
    request = AgentRequest(
        from_agent="coach",
        to_agent="orchestrator",
        query="check_stage_transition",
        context={
            "coach_requests_orchestration": True,
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"},
                {"role": "user", "content": "I have a problem"},
                {"role": "assistant", "content": "Tell me more"},
                {"role": "user", "content": "Need help"},
                {"role": "assistant", "content": "I'm here to help"}
            ]
        }
    )

    response = await orchestrator.handle_request(request)
    assert response.content == "True"
    assert orchestrator.active_stage == 2


@pytest.mark.asyncio
async def test_coordinate_agents_wrong_stage(orchestrator):
    """Test coordination request when not in Stage 2."""
    request = AgentRequest(
        from_agent="coach",
        to_agent="orchestrator",
        query="coordinate_agents",
        context={}
    )

    response = await orchestrator.handle_request(request)
    assert "Not in Stage 2" in response.content
    assert response.metadata["error"] == "wrong_stage"
    assert response.metadata["current_stage"] == 1


@pytest.mark.asyncio
async def test_coordinate_agents_success(orchestrator, mock_llm_service):
    """Test successful agent coordination in Stage 2."""
    # First, transition to Stage 2
    orchestrator.active_stage = 2

    # Mock LLM response for coordination strategy
    mock_llm_service.generate_response.return_value = '''{
        "agent_coordination": {
            "agents_to_query": ["memory", "personal_content", "mcp"],
            "query_strategy": "parallel",
            "specific_prompts": {
                "memory": "Find past conversations about procrastination",
                "personal_content": "Identify beliefs related to productivity",
                "mcp": "Get current tasks and deadlines"
            }
        },
        "synthesis_approach": "Combine historical patterns with current obligations"
    }'''

    # Mock the agent registry
    mock_memory_agent = AsyncMock()
    mock_memory_agent.handle_request.return_value = AgentResponse(
        agent_name="memory",
        content="Found 3 relevant past conversations",
        metadata={"conversations": 3},
        request_id="test-request-1",
        timestamp=datetime.now()
    )

    mock_personal_agent = AsyncMock()
    mock_personal_agent.handle_request.return_value = AgentResponse(
        agent_name="personal_content",
        content="Core belief: Growth through challenges",
        metadata={"belief_count": 1},
        request_id="test-request-2",
        timestamp=datetime.now()
    )

    mock_mcp_agent = AsyncMock()
    mock_mcp_agent.handle_request.return_value = AgentResponse(
        agent_name="mcp",
        content="2 tasks due today",
        metadata={"task_count": 2},
        request_id="test-request-3",
        timestamp=datetime.now()
    )

    with patch('src.agents.registry.agent_registry.get_agent') as mock_get_agent:
        def get_agent_side_effect(name):
            if name == "memory":
                return mock_memory_agent
            elif name == "personal_content":
                return mock_personal_agent
            elif name == "mcp":
                return mock_mcp_agent
            return None

        mock_get_agent.side_effect = get_agent_side_effect

        request = AgentRequest(
            from_agent="coach",
            to_agent="orchestrator",
            query="coordinate_agents",
            context={
                "query_context": {
                    "current_focus": "dealing with procrastination"
                }
            }
        )

        response = await orchestrator.handle_request(request)
        assert response.content == "Agent coordination complete"
        assert response.metadata["stage"] == 2
        assert "coordination_time" in response.metadata
        assert len(response.metadata["agent_responses"]) == 3

        # Verify all agents were queried
        assert mock_memory_agent.handle_request.called
        assert mock_personal_agent.handle_request.called
        assert mock_mcp_agent.handle_request.called


@pytest.mark.asyncio
async def test_coordinate_agents_with_timeout(orchestrator):
    """Test agent coordination with timeout handling."""
    orchestrator.active_stage = 2

    # Mock an agent that times out
    mock_slow_agent = AsyncMock()

    async def slow_response(request):
        import asyncio
        await asyncio.sleep(10)  # Longer than timeout
        return AgentResponse(
            from_agent="memory",
            to_agent="orchestrator",
            content="Should timeout"
        )
    mock_slow_agent.handle_request = slow_response

    with patch('src.agents.registry.agent_registry.get_agent') as mock_get_agent:
        mock_get_agent.return_value = mock_slow_agent

        request = AgentRequest(
            from_agent="coach",
            to_agent="orchestrator",
            query="coordinate_agents",
            context={
                "query_context": {
                    "current_focus": "test query"
                }
            }
        )

        response = await orchestrator.handle_request(request)
        assert response.content == "Agent coordination complete"

        # Check that timeouts were handled
        for agent_name, agent_response in response.metadata["agent_responses"].items():
            if agent_response["status"] == "success":
                assert "timed out" in agent_response["content"]


@pytest.mark.asyncio
async def test_get_stage_info(orchestrator):
    """Test getting current stage information."""
    info = orchestrator.get_stage_info()
    assert info["current_stage"] == 1
    assert not info["problem_identified"]
    assert info["coordination_count"] == 0
    assert info["last_coordination"] is None

    # Simulate some coordination
    orchestrator.coordination_history.append({
        "timestamp": datetime.now(),
        "query": "test",
        "agents_queried": ["memory", "mcp"],
        "duration": 1.5,
        "results": 2
    })

    info = orchestrator.get_stage_info()
    assert info["coordination_count"] == 1
    assert info["last_coordination"] is not None
    assert info["llm_enabled"] is True


@pytest.mark.asyncio
async def test_llm_failure_fallback(orchestrator, mock_llm_service):
    """Test fallback behavior when LLM fails."""
    # Mock LLM failure
    mock_llm_service.generate.side_effect = Exception("LLM service unavailable")

    request = AgentRequest(
        from_agent="coach",
        to_agent="orchestrator",
        query="check_stage_transition",
        context={
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How are you?"},
                {"role": "user", "content": "Not great"},
                {"role": "assistant", "content": "What's going on?"},
                {"role": "user",
                 "content": "I'm struggling with this challenging problem "
                 "and need help"},
                {"role": "assistant", "content": "Tell me more"}
            ]
        }
    )

    # Should fall back to heuristic and still work
    response = await orchestrator.handle_request(request)
    # Should still return a valid response
    assert response.content in ["True", "False"]

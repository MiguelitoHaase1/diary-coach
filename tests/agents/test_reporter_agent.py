"""Tests for Reporter Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.agents.reporter_agent import ReporterAgent
from src.agents.base import AgentRequest, AgentResponse


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service."""
    service = AsyncMock()
    service.generate_response = AsyncMock()
    return service


@pytest.fixture
def reporter_agent(mock_llm_service):
    """Create reporter agent with mock LLM."""
    agent = ReporterAgent(llm_service=mock_llm_service)
    return agent


@pytest.mark.asyncio 
async def test_reporter_initialization(reporter_agent):
    """Test reporter agent initializes properly."""
    assert reporter_agent.name == "reporter"
    assert not reporter_agent.is_initialized  # Not initialized yet
    
    await reporter_agent.initialize()
    
    assert reporter_agent.is_initialized
    assert len(reporter_agent.capabilities) == 2


@pytest.mark.asyncio
async def test_reporter_basic_synthesis(reporter_agent, mock_llm_service):
    await reporter_agent.initialize()
    """Test basic Deep Thoughts synthesis."""
    # Mock LLM response
    mock_llm_service.generate_response.return_value = """# Deep Thoughts Report

## Today's Problem
The user is struggling with time management and feeling overwhelmed.

## Today's Concrete Crux
The key constraint is lack of clear priorities.

## Crux Solutions Deep Dive
1. Time-boxing critical tasks
2. Creating a priority matrix
3. Delegating non-essential work"""

    # Create request with conversation
    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="reporter",
        query="Generate Deep Thoughts report",
        context={
            "conversation": [
                {"role": "user", "content": "I'm feeling overwhelmed"},
                {"role": "assistant", "content": "Let's explore what's causing this"},
            ],
            "agent_contributions": {
                "memory": "Past patterns show productivity concerns",
                "personal_content": "Core belief: Focus on high-impact work",
            },
        },
    )

    # Process request
    response = await reporter_agent.handle_request(request)

    # Verify response
    assert response.agent_name == "reporter"
    assert "Deep Thoughts Report" in response.content
    assert response.metadata["report_type"] == "deep_thoughts"
    assert response.metadata["conversation_turns"] == 2
    assert "memory" in response.metadata["synthesized_agents"]


@pytest.mark.asyncio
async def test_reporter_without_evaluation(reporter_agent, mock_llm_service):
    """Test reporter generates report without evaluation."""
    await reporter_agent.initialize()
    # Mock LLM response
    mock_llm_service.generate_response.return_value = "# Deep Thoughts Report\n\nContent here..."

    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="reporter",
        query="Generate Deep Thoughts report",
        context={
            "conversation": [{"role": "user", "content": "Test"}],
            "agent_contributions": {},
        },
    )

    # Process request
    response = await reporter_agent.handle_request(request)

    # Verify report generated without evaluation
    assert "Deep Thoughts Report" in response.content
    assert "Coaching Session Evaluation" not in response.content
    assert response.metadata["report_type"] == "deep_thoughts"


@pytest.mark.asyncio
async def test_reporter_empty_conversation(reporter_agent, mock_llm_service):
    """Test reporter handles empty conversation gracefully."""
    await reporter_agent.initialize()
    mock_llm_service.generate_response.return_value = (
        "# Deep Thoughts Report\n\nNo conversation provided."
    )

    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="reporter",
        query="Generate report",
        context={"conversation": [], "agent_contributions": {}},
    )

    response = await reporter_agent.handle_request(request)

    assert response.agent_name == "reporter"
    assert response.content
    assert response.metadata["conversation_turns"] == 0


@pytest.mark.asyncio
async def test_reporter_complex_agent_contributions(reporter_agent, mock_llm_service):
    """Test reporter handles various agent contribution formats."""
    await reporter_agent.initialize()
    mock_llm_service.generate_response.return_value = (
        "# Deep Thoughts Report\n\nSynthesized content..."
    )

    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="reporter",
        query="Generate report",
        context={
            "conversation": [{"role": "user", "content": "Help"}],
            "agent_contributions": {
                "memory": "String contribution",
                "mcp": {"content": "Dict with content field", "tasks": 5},
                "personal_content": {"beliefs": ["Focus", "Growth"]},
                "orchestrator": None,  # Should handle None gracefully
            },
        },
    )

    response = await reporter_agent.handle_request(request)

    # Verify all agents are listed (except None)
    synthesized = response.metadata["synthesized_agents"]
    assert "memory" in synthesized
    assert "mcp" in synthesized
    assert "personal_content" in synthesized
    assert "orchestrator" in synthesized


@pytest.mark.asyncio
async def test_reporter_prompt_building(reporter_agent):
    """Test internal prompt building methods."""
    # Test conversation formatting
    conversation = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]
    formatted = reporter_agent._format_conversation(conversation)
    assert "**User**: Hello" in formatted
    assert "**Assistant**: Hi there" in formatted

    # Test agent contribution formatting
    agent_data = {
        "memory_agent": "Past insights",
        "mcp_agent": {"content": "Tasks from Todoist"},
    }
    formatted = reporter_agent._format_agent_contributions(agent_data)
    assert "### Memory Agent" in formatted
    assert "Past insights" in formatted
    assert "### Mcp Agent" in formatted
    assert "Tasks from Todoist" in formatted


@pytest.mark.asyncio
async def test_reporter_error_handling(reporter_agent, mock_llm_service):
    """Test reporter handles errors gracefully."""
    await reporter_agent.initialize()
    # Mock LLM error
    mock_llm_service.generate_response.side_effect = Exception("LLM API error")

    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="reporter",
        query="Generate report",
        context={"conversation": [], "agent_contributions": {}},
    )

    response = await reporter_agent.handle_request(request)

    assert response.agent_name == "reporter"
    assert "Error generating Deep Thoughts" in response.content
    assert response.error == "LLM API error"



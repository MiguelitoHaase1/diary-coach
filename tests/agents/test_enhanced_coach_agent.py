"""Tests for Enhanced Coach Agent with multi-agent capabilities."""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.agents.enhanced_coach_agent import EnhancedDiaryCoach
from src.agents.base import AgentRequest, AgentResponse
from src.events.schemas import UserMessage
from src.services.llm_service import AnthropicService
from src.agents.registry import agent_registry

@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = Mock(spec=AnthropicService)
    service.generate_response = AsyncMock()
    return service

@pytest.fixture
def mock_agents():
    """Create mock agents for testing."""
    # Mock Memory Agent
    memory_agent = Mock()
    memory_agent.name = "memory"
    memory_agent.handle_request = AsyncMock(return_value=AgentResponse(
        agent_name="memory",
        content="RELEVANT CONTEXT:\n- Last week you discussed time management challenges",
        metadata={"conversations_found": 1},
        request_id="test",
        timestamp=datetime.now()
    ))
    
    # Mock Personal Content Agent
    personal_agent = Mock()
    personal_agent.name = "personal_content"
    personal_agent.handle_request = AsyncMock(return_value=AgentResponse(
        agent_name="personal_content",
        content="RELEVANT CONTEXT:\n- Core belief: Focus on high-leverage activities",
        metadata={"documents_found": 1},
        request_id="test",
        timestamp=datetime.now()
    ))
    
    # Mock MCP Agent
    mcp_agent = Mock()
    mcp_agent.name = "mcp"
    mcp_agent.handle_request = AsyncMock(return_value=AgentResponse(
        agent_name="mcp",
        content="CURRENT TASKS:\n- [High Priority] Q4 planning (Due: Today)",
        metadata={"tasks_found": 1},
        request_id="test",
        timestamp=datetime.now()
    ))
    
    return {
        "memory": memory_agent,
        "personal_content": personal_agent,
        "mcp": mcp_agent
    }

@pytest.mark.asyncio
async def test_enhanced_coach_initialization(mock_llm_service):
    """Test enhanced coach initializes properly."""
    coach = EnhancedDiaryCoach(mock_llm_service)
    
    assert coach.name == "coach"
    assert coach.max_agent_calls_per_turn == 2
    assert len(coach.recent_agent_calls) == 0
    
    await coach.initialize()
    assert coach.is_initialized

@pytest.mark.asyncio
async def test_should_call_memory_agent(mock_llm_service):
    """Test memory agent trigger detection."""
    coach = EnhancedDiaryCoach(mock_llm_service)
    
    # Should trigger
    assert await coach._should_call_agent("memory", "Remember when we discussed this?")
    assert await coach._should_call_agent("memory", "Last time you mentioned something")
    
    # Should not trigger
    assert not await coach._should_call_agent("memory", "What should I do today?")
    
    # Should not trigger if recently called
    coach.recent_agent_calls.add("memory")
    assert not await coach._should_call_agent("memory", "Remember when we talked?")

@pytest.mark.asyncio
async def test_should_call_personal_content_agent(mock_llm_service):
    """Test personal content agent trigger detection."""
    coach = EnhancedDiaryCoach(mock_llm_service)
    
    # Should trigger
    assert await coach._should_call_agent("personal_content", "What are my core beliefs?")
    assert await coach._should_call_agent("personal_content", "This goes against my values")
    
    # Should not trigger
    assert not await coach._should_call_agent("personal_content", "What time is it?")

@pytest.mark.asyncio
async def test_should_call_mcp_agent(mock_llm_service):
    """Test MCP agent trigger detection."""
    coach = EnhancedDiaryCoach(mock_llm_service)
    
    # Should trigger
    assert await coach._should_call_agent("mcp", "What should I work on today?")
    assert await coach._should_call_agent("mcp", "What are my priorities?")
    assert await coach._should_call_agent("mcp", "Any important deadlines?")
    
    # Should not trigger
    assert not await coach._should_call_agent("mcp", "I'm feeling overwhelmed")

@pytest.mark.asyncio
async def test_enhance_prompt_with_context(mock_llm_service):
    """Test prompt enhancement with agent context."""
    coach = EnhancedDiaryCoach(mock_llm_service)
    
    base_prompt = "You are a coach."
    agent_context = {
        "memory": {
            "content": "Past conversation about goals",
            "metadata": {}
        },
        "mcp": {
            "content": "Current tasks list",
            "metadata": {}
        }
    }
    
    enhanced = coach._enhance_prompt_with_context(base_prompt, agent_context)
    
    assert "You are a coach." in enhanced
    assert "RELEVANT PAST CONVERSATIONS:" in enhanced
    assert "CURRENT TASKS:" in enhanced
    assert "Integrate this real data naturally" in enhanced

@pytest.mark.asyncio
async def test_recent_calls_cleared_periodically(mock_llm_service):
    """Test that recent agent calls are cleared periodically."""
    coach = EnhancedDiaryCoach(mock_llm_service)
    mock_llm_service.generate_response.return_value = "Response"
    
    # Add some recent calls
    coach.recent_agent_calls.add("memory")
    coach.recent_agent_calls.add("mcp")
    
    # Process 3 exchanges (6 messages total)
    for i in range(3):
        message = UserMessage(
            content=f"Message {i}",
            user_id="test",
            conversation_id="test123",
            message_id=f"msg{i}",
            timestamp=datetime.now()
        )
        await coach.process_message(message)
    
    # Recent calls should be cleared after 3 turns
    assert len(coach.recent_agent_calls) == 0

@pytest.mark.asyncio
async def test_no_agent_calls_for_emotional_content(mock_llm_service, mock_agents):
    """Test that agents aren't called for purely emotional content."""
    coach = EnhancedDiaryCoach(mock_llm_service)
    mock_llm_service.generate_response.return_value = "How does that feeling sit with you?"
    
    message = UserMessage(
        content="I'm feeling really overwhelmed and anxious",
        user_id="test",
        conversation_id="test123",
        message_id="msg1",
        timestamp=datetime.now()
    )
    
    response = await coach.process_message(message)
    
    # No agents should be called
    assert coach._last_response_metadata["agents_called"] == []
    assert coach._last_response_metadata["agent_calls_made"] == 0

@pytest.mark.asyncio
async def test_handle_request_conversion(mock_llm_service):
    """Test handling AgentRequest format."""
    coach = EnhancedDiaryCoach(mock_llm_service)
    mock_llm_service.generate_response.return_value = "What matters most about that?"
    
    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="coach",
        query="I need help with decision making",
        context={
            "conversation_id": "test123",
            "user_id": "michael"
        }
    )
    
    response = await coach.handle_request(request)
    
    assert response.agent_name == "coach"
    assert response.content == "What matters most about that?"
    assert not response.error
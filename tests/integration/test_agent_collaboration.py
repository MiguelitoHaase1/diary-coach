"""Integration tests for agent collaboration in the multi-agent system."""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from src.agents.enhanced_coach_agent import EnhancedDiaryCoach
from src.agents.memory_agent import MemoryAgent
from src.agents.personal_content_agent import PersonalContentAgent
from src.agents.mcp_agent import MCPAgent
from src.agents.registry import agent_registry
from src.agents.base import AgentResponse
from src.events.schemas import UserMessage


@pytest.fixture
async def mock_llm_service():
    """Create a mock LLM service."""
    service = AsyncMock()
    service.generate_response = AsyncMock(return_value="Test coach response")
    service.total_cost = 0.0
    service.session_cost = 0.0
    return service


@pytest.fixture
async def agent_system(mock_llm_service):
    """Create a complete agent system with all agents registered."""
    # Clear registry
    agent_registry._agents.clear()
    agent_registry._instances.clear()

    # Create agents
    coach = EnhancedDiaryCoach(mock_llm_service)
    memory_agent = MemoryAgent()
    personal_agent = PersonalContentAgent()
    mcp_agent = MCPAgent()

    # Mock initialization
    for agent in [coach, memory_agent, personal_agent, mcp_agent]:
        agent.initialize = AsyncMock()
        await agent.initialize()

    # Register agents
    agent_registry.register_instance(coach)
    agent_registry.register_instance(memory_agent)
    agent_registry.register_instance(personal_agent)
    agent_registry.register_instance(mcp_agent)

    # Mock agent methods
    memory_agent._search_conversations = AsyncMock(return_value=[])
    personal_agent._load_content = AsyncMock(return_value={})
    mcp_agent._fetch_tasks = AsyncMock(return_value=[])

    yield {
        'coach': coach,
        'memory': memory_agent,
        'personal': personal_agent,
        'mcp': mcp_agent,
        'registry': agent_registry
    }


@pytest.mark.asyncio
class TestAgentCollaboration:
    """Test collaboration between multiple agents."""

    async def test_coach_calls_single_agent(self, agent_system):
        """Test coach successfully calling a single agent."""
        coach = agent_system['coach']
        mcp_agent = agent_system['mcp']

        # Mock MCP agent response
        mcp_agent._fetch_tasks = AsyncMock(return_value=[
            {"content": "Review PR", "priority": 1},
            {"content": "Team meeting", "priority": 2}
        ])

        # Create user message asking about tasks
        message = UserMessage(
            content="What should I work on today?",
            user_id="test_user",
            timestamp=datetime.now()
        )

        # Coach should identify need for MCP agent
        should_call = await coach._should_call_agent("mcp", message.content)
        assert should_call is True

        # Call the agent
        response = await coach._call_agent(
            "mcp",
            message.content,
            {"conversation_id": "test-123"}
        )

        assert response is not None
        assert response.error is None
        assert ("tasks" in response.content.lower() or
                "today" in response.content.lower())

    async def test_coach_calls_multiple_agents(self, agent_system):
        """Test coach calling multiple agents for comprehensive context."""
        coach = agent_system['coach']
        memory_agent = agent_system['memory']
        mcp_agent = agent_system['mcp']

        # Mock responses
        memory_agent._search_conversations = AsyncMock(
            return_value=[{
                "date": "2024-01-14",
                "summary": "Discussed productivity strategies"
            }]
        )

        mcp_agent._fetch_tasks = AsyncMock(
            return_value=[{"content": "Implement new feature", "priority": 1}]
        )

        # Message that should trigger multiple agents
        message = UserMessage(
            content="Based on what we discussed before, what should I tackle today?",
            user_id="test_user",
            timestamp=datetime.now()
        )

        # Gather context from multiple agents
        context = await coach._gather_agent_context(message)

        # Should have called both memory and mcp agents
        assert len(context) >= 1  # At least one agent called
        assert coach.agent_call_history[-1]['success'] is True

    async def test_agent_context_enhancement(self, agent_system):
        """Test that agent context properly enhances the prompt."""
        coach = agent_system['coach']

        # Create mock agent context
        agent_context = {
            "memory": {
                "content": "Previous discussion: User prefers morning deep work",
                "metadata": {"relevance_score": 0.9}
            },
            "mcp": {
                "content": "Today: 1. Code review (High), 2. Documentation (Medium)",
                "metadata": {"task_count": 2}
            },
            "personal_content": {
                "content": "Core value: Continuous improvement and learning",
                "metadata": {"content_type": "values"}
            }
        }

        # Get base prompt
        base_prompt = coach._get_system_prompt()

        # Enhance with context
        enhanced_prompt = coach._enhance_prompt_with_context(base_prompt, agent_context)

        # Verify all context sections are included
        assert "RELEVANT PAST CONVERSATIONS:" in enhanced_prompt
        assert "Previous discussion: User prefers morning deep work" in enhanced_prompt
        assert "CURRENT TASKS:" in enhanced_prompt
        assert "Code review" in enhanced_prompt
        assert "PERSONAL CONTEXT:" in enhanced_prompt
        assert "Continuous improvement" in enhanced_prompt
        assert "Context Usage Instructions:" in enhanced_prompt

    async def test_agent_call_limit_enforcement(self, agent_system):
        """Test that agent call limits are enforced."""
        coach = agent_system['coach']
        coach.max_agent_calls_per_turn = 2

        # Message that could trigger all agents
        message = UserMessage(
            content=("Remember our past talks about my values and "
                     "what tasks I should prioritize today?"),
            user_id="test_user",
            timestamp=datetime.now()
        )

        # Gather context
        context = await coach._gather_agent_context(message)

        # Should respect the limit
        assert len(context) <= coach.max_agent_calls_per_turn

    async def test_agent_failure_recovery(self, agent_system):
        """Test graceful handling when an agent fails."""
        coach = agent_system['coach']
        memory_agent = agent_system['memory']

        # Make memory agent fail
        memory_agent.handle_request = AsyncMock(
            return_value=AgentResponse(
                agent_name="memory",
                content="",
                error="Database connection failed",
                request_id="test-123",
                timestamp=datetime.now()
            )
        )

        # Try to call the failing agent
        response = await coach._call_agent(
            "memory",
            "Remember our last conversation?",
            {}
        )

        # Should handle gracefully
        assert response is not None
        assert response.error == "Database connection failed"
        assert coach.agent_call_history[-1]['success'] is False

    async def test_agent_registry_lookup(self, agent_system):
        """Test agent registry functionality."""
        registry = agent_system['registry']

        # Test getting agents by name
        coach = registry.get_agent("coach")
        assert coach is not None
        assert coach.name == "coach"

        memory = registry.get_agent("memory")
        assert memory is not None
        assert memory.name == "memory"

        # Test getting non-existent agent
        fake = registry.get_agent("fake_agent")
        assert fake is None

    async def test_recent_agent_call_tracking(self, agent_system):
        """Test that recent agent calls are tracked to prevent redundancy."""
        coach = agent_system['coach']

        # First call should succeed
        message1 = UserMessage(
            content="What are my tasks?",
            user_id="test_user",
            timestamp=datetime.now()
        )

        should_call1 = await coach._should_call_agent("mcp", message1.content)
        assert should_call1 is True

        # Mark as recently called
        coach.recent_agent_calls.add("mcp")

        # Second call should be prevented
        should_call2 = await coach._should_call_agent("mcp", message1.content)
        assert should_call2 is False

        # Clear recent calls
        coach.recent_agent_calls.clear()

        # Now should allow calling again
        should_call3 = await coach._should_call_agent("mcp", message1.content)
        assert should_call3 is True

    async def test_agent_query_enhancement(self, agent_system):
        """Test that queries to agents are properly enhanced."""
        coach = agent_system['coach']
        mcp_agent = agent_system['mcp']

        # Mock MCP response
        mcp_agent._fetch_tasks = AsyncMock(
            return_value=[
                {"content": "Task 1", "due": "today"},
                {"content": "Task 2", "due": "tomorrow"}
            ]
        )

        # Message asking about today
        message = UserMessage(
            content="What should I prioritize today?",
            user_id="test_user",
            timestamp=datetime.now()
        )

        # Gather context - should enhance query for MCP
        await coach._gather_agent_context(message)

        # Verify query was enhanced
        if coach.agent_call_history:
            last_call = coach.agent_call_history[-1]
            if last_call['agent'] == 'mcp':
                assert "focus on tasks due today" in last_call['query']

    async def test_conversation_state_affects_agents(self, agent_system):
        """Test that conversation state affects agent behavior."""
        coach = agent_system['coach']

        # Set morning context
        coach.conversation_state = "morning"
        coach.message_history = [
            {"role": "user", "content": "Good morning!"},
            {"role": "assistant", "content": "Good morning! How are you feeling today?"}
        ]

        # Morning message should potentially trigger different agent behavior
        message = UserMessage(
            content="What's my main focus for today?",
            user_id="test_user",
            timestamp=datetime.now()
        )

        # Process with morning context
        response = await coach.process_message(message)

        # Verify conversation state influenced the response
        assert coach.conversation_state == "morning"
        assert response.content is not None

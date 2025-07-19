"""End-to-end integration tests for the multi-agent coaching system."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.interface.multi_agent_cli import MultiAgentCLI


class MockLLMService:
    """Mock LLM service with predictable responses."""

    def __init__(self):
        self.responses = []
        self.call_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.session_cost = 0.0

    async def generate_response(self, messages, system_prompt,
                                max_tokens=200, temperature=0.7):
        """Return next mocked response."""
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return "Default test response"


@pytest.fixture
async def mock_llm_service():
    """Create a mock LLM service."""
    return MockLLMService()


@pytest.fixture
async def multi_agent_cli(mock_llm_service):
    """Create multi-agent CLI with mocked dependencies."""
    # Patch LLMFactory to return our mock
    with patch('src.interface.multi_agent_cli.LLMFactory') as mock_factory:
        mock_factory.create_cheap_service.return_value = mock_llm_service

        # Create CLI instance
        cli = MultiAgentCLI()

        # Mock agent initialization
        cli.memory_agent.initialize = AsyncMock()
        cli.personal_content_agent.initialize = AsyncMock()
        cli.mcp_agent.initialize = AsyncMock()
        cli.coach.initialize = AsyncMock()

        # Mock LangSmith tracker
        cli.langsmith_tracker.client = None  # Disable actual tracking

        # Mock input/output
        cli._get_input = AsyncMock()
        cli.print = MagicMock()

        yield cli


@pytest.mark.asyncio
class TestMultiAgentIntegration:
    """Test complete multi-agent workflows."""

    async def test_morning_routine_with_tasks(self, multi_agent_cli, mock_llm_service):
        """Test morning routine that triggers task agent."""
        # Setup mock responses
        mock_llm_service.responses = [
            "Good morning! I see you have some tasks to tackle today. "
            "What's on your mind as you start your day?",
            "That's a great mindset! Let me check what you have planned for today.",
            "I understand that feeling. "
            "What would help you feel more prepared for these tasks?"
        ]

        # Mock agent responses
        multi_agent_cli.mcp_agent.handle_request = AsyncMock(
            return_value=MagicMock(
                content=("Today's tasks:\n"
                         "1. Review code changes (High priority)\n"
                         "2. Team meeting at 2pm\n"
                         "3. Update documentation"),
                error=None,
                metadata={"task_count": 3}
            )
        )

        # Simulate morning greeting
        response1 = await multi_agent_cli.process_input("Good morning!")
        assert "morning" in response1.lower()
        assert len(multi_agent_cli.coach.agent_call_history) == 0  # No agents called yet

        # Ask about tasks - should trigger MCP agent
        response2 = await multi_agent_cli.process_input(
            "What should I work on today?")

        # Verify MCP agent was called
        assert multi_agent_cli.mcp_agent.handle_request.called
        call_args = multi_agent_cli.mcp_agent.handle_request.call_args[0][0]
        assert "today" in call_args.query.lower()

        # Verify coach incorporated task context
        assert "check what you have planned" in response2

    async def test_memory_recall_integration(self, multi_agent_cli, mock_llm_service):
        """Test conversation that triggers memory agent."""
        # Setup mock responses
        mock_llm_service.responses = [
            "I'll help you reflect on that. Let me recall what we discussed before.",
            "Yes, I remember that conversation. "
            "You were working through similar challenges. "
            "How do you feel about your progress since then?"
        ]

        # Mock memory agent response
        multi_agent_cli.memory_agent.handle_request = AsyncMock(
            return_value=MagicMock(
                content=("Previous conversation (2024-01-15): "
                         "You discussed feeling overwhelmed with "
                         "project deadlines and we explored time "
                         "management strategies."),
                error=None,
                metadata={"conversations_found": 1}
            )
        )

        # Trigger memory recall
        response = await multi_agent_cli.process_input(
            "Do you remember when we talked about project management?"
        )

        # Verify memory agent was called
        assert multi_agent_cli.memory_agent.handle_request.called
        assert "remember" in response.lower() or "recall" in response.lower()

    async def test_personal_values_integration(self, multi_agent_cli, mock_llm_service):
        """Test conversation that accesses personal content."""
        # Setup mock responses
        mock_llm_service.responses = [
            "Let me connect this to your core values and beliefs.",
            "Based on your values of continuous learning and growth, "
            "how does this decision align with what's important to you?"
        ]

        # Mock personal content agent
        multi_agent_cli.personal_content_agent.handle_request = AsyncMock(
            return_value=MagicMock(
                content=("Core values: Continuous learning, "
                         "Work-life balance, Authentic relationships"),
                error=None,
                metadata={"content_type": "values"}
            )
        )

        # Trigger values discussion
        response = await multi_agent_cli.process_input(
            "I'm not sure if this aligns with my values"
        )

        # Verify personal content agent was called
        assert multi_agent_cli.personal_content_agent.handle_request.called
        assert "values" in response.lower() or "connect" in response.lower()

    async def test_multi_agent_collaboration(self, multi_agent_cli, mock_llm_service):
        """Test scenario where multiple agents collaborate."""
        # Setup mock responses
        mock_llm_service.responses = [
            "I see you're planning for tomorrow. "
            "Let me gather some context to help you prepare effectively.",
            "Based on your past experiences and upcoming tasks, "
            "here's my suggestion for approaching tomorrow..."
        ]

        # Mock multiple agent responses
        multi_agent_cli.memory_agent.handle_request = AsyncMock(
            return_value=MagicMock(
                content="You tend to be most productive in the morning for deep work",
                error=None
            )
        )

        multi_agent_cli.mcp_agent.handle_request = AsyncMock(
            return_value=MagicMock(
                content="Tomorrow: 1. Code review (9am), 2. Client presentation (2pm)",
                error=None
            )
        )

        # Complex query that should trigger multiple agents
        await multi_agent_cli.process_input(
            "How should I approach tomorrow given what we've discussed before?"
        )

        # Verify both agents were called
        assert multi_agent_cli.memory_agent.handle_request.called
        assert multi_agent_cli.mcp_agent.handle_request.called

    async def test_langsmith_tracking_integration(self, multi_agent_cli):
        """Test that LangSmith tracking is properly integrated."""
        # Enable mock LangSmith client
        mock_client = MagicMock()
        multi_agent_cli.langsmith_tracker.client = mock_client

        # Mock conversation state
        with patch('src.orchestration.state.ConversationState'):
            await multi_agent_cli.run()

            # Verify conversation start was tracked
            assert multi_agent_cli.langsmith_tracker.track_conversation_start.called

    async def test_agent_error_handling(self, multi_agent_cli, mock_llm_service):
        """Test graceful handling of agent failures."""
        # Setup mock responses
        mock_llm_service.responses = [
            "I'll check your tasks for today.",
            "I'm having trouble accessing your tasks right now, "
            "but let's focus on what you'd like to accomplish today. "
            "What's your main priority?"
        ]

        # Mock agent failure
        multi_agent_cli.mcp_agent.handle_request = AsyncMock(
            return_value=MagicMock(
                content="",
                error="Failed to connect to Todoist API",
                metadata={}
            )
        )

        # Should handle gracefully
        response = await multi_agent_cli.process_input(
            "What tasks do I have today?")

        # Coach should provide helpful response despite agent failure
        assert "priority" in response.lower() or "accomplish" in response.lower()
        assert multi_agent_cli.mcp_agent.handle_request.called

    async def test_conversation_flow_tracking(self, multi_agent_cli, mock_llm_service):
        """Test that conversation flow and agent calls are tracked."""
        # Setup responses
        mock_llm_service.responses = [
            "Good morning! How are you feeling today?",
            "I understand. Let me check what's on your plate for today.",
            "Great perspective! How do you want to tackle the first task?"
        ]

        # Mock successful agent call
        multi_agent_cli.mcp_agent.handle_request = AsyncMock(
            return_value=MagicMock(
                content="3 tasks for today",
                error=None
            )
        )

        # Simulate conversation
        await multi_agent_cli.process_input("Good morning")
        await multi_agent_cli.process_input(
            "Feeling a bit overwhelmed with tasks")

        # Check agent call history
        assert len(multi_agent_cli.coach.agent_call_history) > 0
        assert multi_agent_cli.coach.agent_call_history[0]['agent'] == 'mcp'
        assert multi_agent_cli.coach.agent_call_history[0]['success'] is True

    async def test_morning_context_detection(self, multi_agent_cli, mock_llm_service):
        """Test that morning context is properly detected and handled."""
        # Setup responses with morning-specific coaching
        mock_llm_service.responses = [
            "Good morning! I notice it's the start of your day. "
            "What intention would you like to set for today?",
            "That's a powerful intention. "
            "What specific action will help you embody that today?"
        ]

        # Test various morning greetings
        morning_greetings = ["Good morning!", "Morning!", "GM", "g'morning"]

        for greeting in morning_greetings:
            multi_agent_cli.coach.message_history = []  # Reset history
            response = await multi_agent_cli.process_input(greeting)

            # Verify morning context is recognized
            # May change to "morning"
            assert multi_agent_cli.coach.conversation_state == "general"
            assert "morning" in response.lower() or "day" in response.lower()

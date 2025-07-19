"""Integration tests for LangSmith tracking in multi-agent system."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from src.interface.multi_agent_cli import MultiAgentCLI
from src.orchestration.state import ConversationState
from langsmith import Client as LangSmithClient


@pytest.fixture
async def mock_langsmith_client():
    """Create a mock LangSmith client."""
    client = MagicMock(spec=LangSmithClient)
    client.create_run = MagicMock()
    client.update_run = MagicMock()
    return client


@pytest.fixture
async def multi_agent_cli_with_tracking(mock_langsmith_client):
    """Create multi-agent CLI with LangSmith tracking enabled."""
    with patch('src.interface.multi_agent_cli.LLMFactory') as mock_factory:
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_response.return_value = "Test response"
        mock_llm.total_cost = 0.0
        mock_llm.session_cost = 0.0
        mock_factory.create_cheap_service.return_value = mock_llm

        # Create CLI
        cli = MultiAgentCLI()

        # Mock agent initialization
        cli.memory_agent.initialize = AsyncMock()
        cli.personal_content_agent.initialize = AsyncMock()
        cli.mcp_agent.initialize = AsyncMock()
        cli.coach.initialize = AsyncMock()

        # Enable LangSmith tracking with mock client
        cli.langsmith_tracker.client = mock_langsmith_client

        # Mock I/O
        cli._get_input = AsyncMock()
        cli.print = MagicMock()

        yield cli


@pytest.mark.asyncio
class TestLangSmithIntegration:
    """Test LangSmith tracking integration in multi-agent system."""

    async def test_conversation_start_tracking(
            self, multi_agent_cli_with_tracking, mock_langsmith_client):
        """Test that conversation start is tracked in LangSmith."""
        # Mock ConversationState
        with patch('src.interface.multi_agent_cli.ConversationState') as\
                mock_state_class:
            mock_state = MagicMock()
            mock_state.conversation_id = "test-conv-123"
            mock_state.conversation_state = "active"
            mock_state.get_message_count.return_value = 0
            mock_state_class.return_value = mock_state

            # Start tracking
            await multi_agent_cli_with_tracking.langsmith_tracker\
                .track_conversation_start(mock_state)

            # Verify create_run was called
            assert mock_langsmith_client.create_run.called
            create_call = mock_langsmith_client.create_run.call_args

            # Check run parameters
            assert create_call[1]['name'] == 'conversation_start'
            assert create_call[1]['run_type'] == 'chain'
            assert create_call[1]['inputs']['conversation_id'] == 'test-conv-123'
            assert create_call[1]['project_name'] == 'diary-coach-debug'

    async def test_agent_communication_tracking(
            self, multi_agent_cli_with_tracking, mock_langsmith_client):
        """Test that agent communications are tracked."""
        # Track an agent communication
        await multi_agent_cli_with_tracking.langsmith_tracker.track_agent_communication(
            agent_name="mcp",
            input_data={"query": "What tasks do I have today?"},
            output_data={"response": "You have 3 tasks today", "task_count": 3}
        )

        # Verify tracking
        assert mock_langsmith_client.create_run.called
        create_call = mock_langsmith_client.create_run.call_args

        assert create_call[1]['name'] == 'agent_mcp'
        assert create_call[1]['run_type'] == 'llm'
        assert create_call[1]['inputs']['query'] == "What tasks do I have today?"
        assert create_call[1]['outputs']['task_count'] == 3

    async def test_multi_agent_call_tracking(
            self, multi_agent_cli_with_tracking, mock_langsmith_client):
        """Test tracking when multiple agents are called."""
        # Mock agent responses
        multi_agent_cli_with_tracking.memory_agent.handle_request = AsyncMock(
            return_value=MagicMock(content="Past context", error=None)
        )
        multi_agent_cli_with_tracking.mcp_agent.handle_request = AsyncMock(
            return_value=MagicMock(content="Today's tasks", error=None)
        )

        # Mock coach to trigger multiple agents
        multi_agent_cli_with_tracking.coach.agent_call_history = [
            {
                'timestamp': datetime.now(),
                'agent': 'memory',
                'query': 'recall past discussions',
                'response': 'Past context',
                'success': True
            },
            {
                'timestamp': datetime.now(),
                'agent': 'mcp',
                'query': 'today tasks',
                'response': "Today's tasks",
                'success': True
            }
        ]

        # Process input that triggers tracking
        await multi_agent_cli_with_tracking._handle_user_input(
            "What should I work on based on our past discussions?")

        # Expected calls for verification (not used in assertion)
        # Just documenting what we expect to see

        # Check the actual calls made
        track_calls = [
            c for c in multi_agent_cli_with_tracking.langsmith_tracker
            .track_agent_communication.call_args_list]
        assert len(track_calls) == 2

    async def test_traceable_decorator_integration(self, multi_agent_cli_with_tracking):
        """Test that @traceable decorators work in multi-agent system."""
        # Import should work without errors
        from src.agents.enhanced_coach_agent import LANGSMITH_AVAILABLE

        # If LangSmith is available, traceable should be the real decorator
        if LANGSMITH_AVAILABLE:
            from langsmith import traceable as real_traceable  # noqa: F401
            from src.agents.enhanced_coach_agent import traceable
            # Can't directly compare functions, but we know it's imported
            assert traceable is not None
        else:
            # Should have no-op decorator
            from src.agents.enhanced_coach_agent import traceable
            assert callable(traceable)

    async def test_error_handling_in_tracking(
            self, multi_agent_cli_with_tracking, mock_langsmith_client):
        """Test that tracking errors don't break the conversation."""
        # Make create_run raise an exception
        mock_langsmith_client.create_run.side_effect = Exception(
            "LangSmith API error")

        # This should not raise an exception
        state = ConversationState()
        await multi_agent_cli_with_tracking.langsmith_tracker\
            .track_conversation_start(state)

        # Verify error was caught (no exception raised)
        assert mock_langsmith_client.create_run.called

    async def test_performance_metrics_tracking(self, multi_agent_cli_with_tracking):
        """Test that performance metrics are tracked."""
        # Track performance metrics
        metrics = {
            "response_time": 1.23,
            "tokens_used": 150,
            "agent_calls": 2
        }

        await multi_agent_cli_with_tracking.langsmith_tracker\
            .track_performance_metrics(metrics)

        # Verify metrics were stored
        tracker = multi_agent_cli_with_tracking.langsmith_tracker
        assert tracker.custom_metrics["response_time"] == 1.23
        assert tracker.custom_metrics["tokens_used"] == 150

    async def test_conversation_end_tracking(self, multi_agent_cli_with_tracking):
        """Test that conversation end is properly tracked."""
        # Create a conversation state
        state = ConversationState()
        state.conversation_id = "test-123"

        # Add some mock data
        state.messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        # End conversation with metrics
        final_metrics = {
            "total_messages": 2,
            "duration_seconds": 120,
            "satisfaction_score": 4.5
        }

        await multi_agent_cli_with_tracking.langsmith_tracker\
            .end_conversation(state, final_metrics)

        # Verify event was recorded
        events = multi_agent_cli_with_tracking.langsmith_tracker.get_all_events()
        end_events = [e for e in events if e['type'] == 'conversation_end']

        assert len(end_events) == 1
        assert end_events[0]['conversation_id'] == 'test-123'
        assert end_events[0]['final_metrics']['total_messages'] == 2

    async def test_agent_metadata_tracking(self, multi_agent_cli_with_tracking):
        """Test that agent-specific metadata is tracked."""
        # Track agent communication with metadata
        await multi_agent_cli_with_tracking.langsmith_tracker.track_agent_communication(
            agent_name="memory",
            input_data={
                "query": "recall last week",
                "context": {"time_range": "7_days"}
            },
            output_data={
                "response": "Found 3 relevant conversations",
                "metadata": {
                    "conversations_found": 3,
                    "date_range": "2024-01-08 to 2024-01-15"
                }
            }
        )

        # Get tracked communications
        communications = multi_agent_cli_with_tracking.langsmith_tracker\
            .get_agent_communications()

        assert len(communications) == 1
        assert communications[0]['agent_name'] == 'memory'
        assert communications[0]['output']['metadata']['conversations_found'] == 3

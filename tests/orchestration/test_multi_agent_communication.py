"""Test inter-agent communication patterns."""

from datetime import datetime

from src.orchestration.multi_agent_state import (
    MultiAgentState, AgentMessage
)
from src.agents.base import AgentRequest, AgentResponse


class TestAgentCommunication:
    """Test agent communication channels."""

    def test_agent_message_creation(self):
        """Test creating agent messages."""
        message = AgentMessage(
            from_agent="coach",
            to_agent="memory",
            content="What did we discuss last week?",
            message_type="request"
        )

        assert message.from_agent == "coach"
        assert message.to_agent == "memory"
        assert message.content == "What did we discuss last week?"
        assert message.message_type == "request"
        assert message.message_id  # Should be auto-generated

    def test_add_agent_message(self):
        """Test adding messages to state."""
        state = MultiAgentState(conversation_id="test")

        message = AgentMessage(
            from_agent="coach",
            to_agent="memory",
            content="Retrieve morning routines",
            message_type="request"
        )

        state.add_agent_message(message)

        assert len(state.agent_messages) == 1
        assert state.agent_messages[0] == message

    def test_get_agent_messages(self):
        """Test filtering messages by agent."""
        state = MultiAgentState(conversation_id="test")

        # Add messages for different agents
        msg1 = AgentMessage(
            from_agent="coach", to_agent="memory",
            content="Message 1", message_type="request"
        )
        msg2 = AgentMessage(
            from_agent="memory", to_agent="coach",
            content="Message 2", message_type="response"
        )
        msg3 = AgentMessage(
            from_agent="mcp", to_agent="orchestrator",
            content="Message 3", message_type="request"
        )

        state.add_agent_message(msg1)
        state.add_agent_message(msg2)
        state.add_agent_message(msg3)

        # Get messages for coach
        coach_messages = state.get_agent_messages("coach")
        assert len(coach_messages) == 2
        assert msg1 in coach_messages
        assert msg2 in coach_messages
        assert msg3 not in coach_messages

    def test_broadcast_message(self):
        """Test broadcasting messages to all agents."""
        state = MultiAgentState(conversation_id="test")

        # Activate some agents
        state.activate_agent("coach")
        state.activate_agent("memory")
        state.activate_agent("mcp")

        # Broadcast from orchestrator
        state.broadcast_message(
            from_agent="orchestrator",
            content="Stage 2 activated",
            metadata={"stage": 2}
        )

        # Check all agents received the message
        assert len(state.agent_messages) == 3
        recipients = [msg.to_agent for msg in state.agent_messages]
        assert "coach" in recipients
        assert "memory" in recipients
        assert "mcp" in recipients

        # Check orchestrator didn't receive its own message
        assert "orchestrator" not in recipients

    def test_pending_requests(self):
        """Test managing pending agent requests."""
        state = MultiAgentState(conversation_id="test")

        request = AgentRequest(
            from_agent="coach",
            to_agent="memory",
            query="Retrieve past challenges",
            context={"conversation_id": "test"}
        )

        # Add pending request
        state.add_pending_request(request)
        assert len(state.pending_requests) == 1
        assert state.pending_requests[0] == request

        # Complete the request
        response = AgentResponse(
            agent_name="memory",
            content="Past challenges: organization, focus",
            metadata={},
            request_id=request.request_id,
            timestamp=datetime.now()
        )

        state.complete_request(request.request_id, response)

        # Check request was removed and response stored
        assert len(state.pending_requests) == 0
        assert "memory" in state.agent_responses
        assert len(state.agent_responses["memory"]) == 1
        assert state.agent_responses["memory"][0] == response

    def test_stage_transitions(self):
        """Test stage transition tracking."""
        state = MultiAgentState(conversation_id="test")

        # Initial stage
        assert state.current_stage == 1

        # Transition to stage 2
        state.update_stage(2, {"trigger": "problem_identified"})
        assert state.current_stage == 2
        assert state.stage_metadata["trigger"] == "problem_identified"

        # Transition to stage 3
        state.update_stage(3, {"agents_completed": ["memory", "mcp"]})
        assert state.current_stage == 3
        assert "agents_completed" in state.stage_metadata

    def test_agent_activation(self):
        """Test agent activation/deactivation."""
        state = MultiAgentState(conversation_id="test")

        # Activate agents
        state.activate_agent("coach")
        state.activate_agent("memory")
        assert len(state.active_agents) == 2
        assert "coach" in state.active_agents
        assert "memory" in state.active_agents

        # Deactivate agent
        state.deactivate_agent("memory")
        assert len(state.active_agents) == 1
        assert "coach" in state.active_agents
        assert "memory" not in state.active_agents

    def test_agent_state_management(self):
        """Test managing individual agent states."""
        state = MultiAgentState(conversation_id="test")

        # Update coach state
        coach_state = {
            "conversation_state": "morning",
            "morning_challenge": "organize files",
            "message_count": 5
        }
        state.update_agent_state("coach", coach_state)

        # Retrieve state
        retrieved = state.get_agent_state("coach")
        assert retrieved == coach_state

        # Non-existent agent returns empty dict
        assert state.get_agent_state("unknown") == {}

    def test_context_management(self):
        """Test managing context from different agents."""
        state = MultiAgentState(conversation_id="test")

        # Set different contexts
        state.set_memory_context({
            "past_challenges": ["organization", "focus"],
            "common_topics": ["productivity", "clarity"]
        })

        state.set_mcp_context({
            "todos": ["Review documents", "Team meeting"],
            "calendar": ["9am standup", "2pm review"]
        })

        state.set_personal_context({
            "core_beliefs": ["clarity", "growth"],
            "values": ["authenticity", "impact"]
        })

        # Get all context
        all_context = state.get_all_context()
        assert all_context["memory"]["past_challenges"] == ["organization", "focus"]
        assert all_context["mcp"]["todos"] == ["Review documents", "Team meeting"]
        assert all_context["personal"]["core_beliefs"] == ["clarity", "growth"]

    def test_multi_agent_state_inheritance(self):
        """Test that MultiAgentState inherits ConversationState functionality."""
        state = MultiAgentState(conversation_id="test")

        # Should have all ConversationState methods
        assert hasattr(state, "add_message")
        assert hasattr(state, "add_response")
        assert hasattr(state, "get_user_messages")
        assert hasattr(state, "update_conversation_state")

        # Test inherited functionality
        state.update_conversation_state("morning")
        assert state.conversation_state == "morning"

        state.set_morning_challenge("Focus on deep work")
        assert state.morning_challenge == "Focus on deep work"

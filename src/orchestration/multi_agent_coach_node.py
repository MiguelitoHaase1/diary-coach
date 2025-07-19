"""Enhanced Coach Node with multi-agent communication capabilities."""

from datetime import datetime
from typing import Dict, Any

from src.events.schemas import UserMessage
from src.orchestration.multi_agent_state import MultiAgentState, AgentMessage
from src.agents.coach_agent import DiaryCoach
from src.agents.base import AgentRequest


class MultiAgentCoachNode:
    """Coach node that supports multi-agent communication."""

    def __init__(self, coach: DiaryCoach):
        self.coach = coach

    async def process(self, state: MultiAgentState) -> MultiAgentState:
        """Process conversation with multi-agent awareness."""
        # Check for any messages directed to coach
        coach_messages = state.get_agent_messages("coach")
        for message in coach_messages:
            if message.message_type == "request":
                # Handle inter-agent requests
                await self._handle_agent_request(message, state)

        # Get the latest user message
        user_messages = state.get_user_messages()
        if not user_messages:
            return state

        latest_message = user_messages[-1]

        # Create UserMessage from state
        user_message = UserMessage(
            user_id=latest_message["user_id"],
            content=latest_message["content"],
            timestamp=datetime.fromisoformat(latest_message["timestamp"]),
            conversation_id=state.conversation_id,
            message_id=latest_message["message_id"]
        )

        # Check if coach needs help from other agents
        agent_requests = self._analyze_agent_needs(user_message, state)

        # Send requests to other agents if needed
        for request in agent_requests:
            state.add_pending_request(request)
            state.add_agent_message(AgentMessage(
                from_agent="coach",
                to_agent=request.to_agent,
                content=request.query,
                message_type="request",
                metadata={"request_id": request.request_id}
            ))

        # Process through existing coach
        response = await self.coach.process_message(user_message)

        # Add response to state
        state.add_response(response)

        # Update state with coach's internal state
        state.update_conversation_state(self.coach.conversation_state)
        if self.coach.morning_challenge:
            state.set_morning_challenge(self.coach.morning_challenge)
        if self.coach.morning_value:
            state.set_morning_value(self.coach.morning_value)

        # Update agent state
        state.update_agent_state("coach", {
            "conversation_state": self.coach.conversation_state,
            "morning_challenge": self.coach.morning_challenge,
            "morning_value": self.coach.morning_value,
            "message_count": len(self.coach.message_history)
        })

        # Track decision
        state.add_decision("coach")

        # Check for stage transition
        if self._should_transition_stage(state):
            state.update_stage(2, {
                "reason": "problem_clarity_achieved",
                "timestamp": datetime.now().isoformat()
            })
            # Broadcast stage change
            state.broadcast_message(
                from_agent="coach",
                content="Problem clarity achieved, activating orchestrated gathering",
                metadata={"new_stage": 2}
            )

        return state

    def _analyze_agent_needs(self, message: UserMessage,
                             state: MultiAgentState) -> list[AgentRequest]:
        """Analyze if coach needs help from other agents."""
        requests = []
        content_lower = message.content.lower()

        # Check if memory agent is needed
        if any(phrase in content_lower for phrase in [
            "remember when", "last time", "previously", "before",
            "we discussed", "you mentioned"
        ]):
            requests.append(AgentRequest(
                from_agent="coach",
                to_agent="memory",
                query=f"Find relevant past conversations about: {message.content}",
                context={"conversation_id": state.conversation_id}
            ))

        # Check if MCP agent is needed
        if any(phrase in content_lower for phrase in [
            "todo", "task", "should i", "what's on",
            "priority", "deadline", "calendar"
        ]):
            requests.append(AgentRequest(
                from_agent="coach",
                to_agent="mcp",
                query="Get current tasks and priorities",
                context={"conversation_id": state.conversation_id}
            ))

        # Check if personal content agent is needed
        if any(phrase in content_lower for phrase in [
            "values", "beliefs", "goals", "vision",
            "purpose", "mission", "core"
        ]):
            requests.append(AgentRequest(
                from_agent="coach",
                to_agent="personal_content",
                query=f"Find relevant personal context for: {message.content}",
                context={"conversation_id": state.conversation_id}
            ))

        return requests

    async def _handle_agent_request(self, message: AgentMessage,
                                    state: MultiAgentState) -> None:
        """Handle requests from other agents."""
        # For now, coach doesn't handle requests from other agents
        # This will be expanded in future increments
        pass

    def _should_transition_stage(self, state: MultiAgentState) -> bool:
        """Determine if we should transition to stage 2."""
        # Transition if:
        # 1. We're in stage 1
        # 2. Morning challenge is identified
        # 3. We have enough conversation depth
        return (
            state.current_stage == 1 and
            state.morning_challenge is not None and
            len(state.get_user_messages()) >= 3
        )

    async def get_coach_state(self) -> Dict[str, Any]:
        """Get the internal state of the coach."""
        return {
            "conversation_state": self.coach.conversation_state,
            "morning_challenge": self.coach.morning_challenge,
            "morning_value": self.coach.morning_value,
            "message_count": len(self.coach.message_history)
        }

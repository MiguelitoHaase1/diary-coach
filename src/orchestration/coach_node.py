"""LangGraph Coach Node implementation."""

from datetime import datetime
from typing import Dict, Any

from src.events.schemas import UserMessage, AgentResponse
from src.orchestration.state import ConversationState
from src.agents.coach_agent import DiaryCoach


class CoachNode:
    """LangGraph node wrapper around existing coach logic."""
    
    def __init__(self, coach: DiaryCoach):
        self.coach = coach
    
    async def process(self, state: ConversationState) -> ConversationState:
        """Process the conversation state through the coach."""
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
        
        # Track decision
        state.add_decision("coach")
        
        return state
    
    async def get_coach_state(self) -> Dict[str, Any]:
        """Get the internal state of the coach."""
        return {
            "conversation_state": self.coach.conversation_state,
            "morning_challenge": self.coach.morning_challenge,
            "morning_value": self.coach.morning_value,
            "message_count": len(self.coach.message_history)
        }
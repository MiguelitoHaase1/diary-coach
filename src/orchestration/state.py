"""LangGraph state schema for conversation and evaluation data."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from src.events.schemas import UserMessage, AgentResponse


@dataclass
class ConversationState:
    """LangGraph state schema for conversation and evaluation data."""
    
    # Conversation tracking
    conversation_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    conversation_state: str = "general"  # general, morning, evening
    
    # Morning-specific state
    morning_challenge: Optional[str] = None
    morning_value: Optional[str] = None
    
    # Evaluation data
    evaluations: List[Dict[str, Any]] = field(default_factory=list)
    satisfaction_scores: List[float] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Decision tracking
    decision_path: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, message: UserMessage) -> None:
        """Add a user message to the conversation."""
        self.messages.append({
            "type": "user",
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "user_id": message.user_id,
            "message_id": message.message_id
        })
        self.updated_at = datetime.now()
    
    def add_response(self, response: AgentResponse) -> None:
        """Add an agent response to the conversation."""
        self.messages.append({
            "type": "agent",
            "content": response.content,
            "timestamp": response.timestamp.isoformat(),
            "agent_name": response.agent_name,
            "response_id": response.response_id,
            "response_to": response.response_to
        })
        self.updated_at = datetime.now()
    
    def add_evaluation(self, evaluation: Dict[str, Any]) -> None:
        """Add an evaluation result to the state."""
        self.evaluations.append({
            **evaluation,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def get_satisfaction_score(self) -> float:
        """Get the current satisfaction score."""
        if not self.satisfaction_scores:
            return 0.0
        return sum(self.satisfaction_scores) / len(self.satisfaction_scores)
    
    def get_decision_path(self) -> List[str]:
        """Get the current decision path."""
        return self.decision_path.copy()
    
    def add_decision(self, decision: str) -> None:
        """Add a decision to the path."""
        self.decision_path.append(decision)
        self.updated_at = datetime.now()
    
    def get_message_count(self) -> int:
        """Get the number of messages in the conversation."""
        return len(self.messages)
    
    def get_user_messages(self) -> List[Dict[str, Any]]:
        """Get only user messages."""
        return [msg for msg in self.messages if msg["type"] == "user"]
    
    def get_agent_responses(self) -> List[Dict[str, Any]]:
        """Get only agent responses."""
        return [msg for msg in self.messages if msg["type"] == "agent"]
    
    def update_conversation_state(self, state: str) -> None:
        """Update the conversation state."""
        self.conversation_state = state
        self.updated_at = datetime.now()
    
    def set_morning_challenge(self, challenge: str) -> None:
        """Set the morning challenge."""
        self.morning_challenge = challenge
        self.updated_at = datetime.now()
    
    def set_morning_value(self, value: str) -> None:
        """Set the morning value."""
        self.morning_value = value
        self.updated_at = datetime.now()
    
    def add_satisfaction_score(self, score: float) -> None:
        """Add a satisfaction score."""
        self.satisfaction_scores.append(score)
        self.updated_at = datetime.now()
    
    def update_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update performance metrics."""
        self.performance_metrics.update(metrics)
        self.updated_at = datetime.now()
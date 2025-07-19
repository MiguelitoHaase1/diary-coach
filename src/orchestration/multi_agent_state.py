"""Enhanced LangGraph state for multi-agent communication."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from src.orchestration.state import ConversationState
from src.agents.base import AgentRequest, AgentResponse


@dataclass
class AgentMessage:
    """Message between agents."""
    from_agent: str
    to_agent: str
    content: str
    message_type: str  # request, response, broadcast
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = ""

    def __post_init__(self):
        if not self.message_id:
            import uuid
            self.message_id = str(uuid.uuid4())


@dataclass
class MultiAgentState(ConversationState):
    """Extended state for multi-agent orchestration."""

    # Agent communication channels
    agent_messages: List[AgentMessage] = field(default_factory=list)
    pending_requests: List[AgentRequest] = field(default_factory=list)
    agent_responses: Dict[str, List[AgentResponse]] = field(default_factory=dict)

    # Stage tracking for three-stage system
    current_stage: int = 1  # 1: Exploration, 2: Orchestrated, 3: Synthesis
    stage_metadata: Dict[str, Any] = field(default_factory=dict)

    # Active agents
    active_agents: List[str] = field(default_factory=list)
    agent_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Context from different agents
    memory_context: Optional[Dict[str, Any]] = None
    mcp_context: Optional[Dict[str, Any]] = None
    personal_context: Optional[Dict[str, Any]] = None

    def add_agent_message(self, message: AgentMessage) -> None:
        """Add an inter-agent message."""
        self.agent_messages.append(message)
        self.updated_at = datetime.now()

    def add_pending_request(self, request: AgentRequest) -> None:
        """Add a pending agent request."""
        self.pending_requests.append(request)
        self.updated_at = datetime.now()

    def complete_request(self, request_id: str, response: AgentResponse) -> None:
        """Complete a pending request with a response."""
        # Remove from pending
        self.pending_requests = [
            r for r in self.pending_requests if r.request_id != request_id
        ]

        # Add to responses
        if response.agent_name not in self.agent_responses:
            self.agent_responses[response.agent_name] = []
        self.agent_responses[response.agent_name].append(response)

        self.updated_at = datetime.now()

    def get_agent_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get messages for a specific agent."""
        return [
            msg for msg in self.agent_messages
            if msg.to_agent == agent_name or msg.from_agent == agent_name
        ]

    def broadcast_message(self, from_agent: str, content: str,
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """Broadcast a message to all active agents."""
        for agent in self.active_agents:
            if agent != from_agent:
                message = AgentMessage(
                    from_agent=from_agent,
                    to_agent=agent,
                    content=content,
                    message_type="broadcast",
                    metadata=metadata or {}
                )
                self.add_agent_message(message)

    def update_stage(self, stage: int,
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update the current orchestration stage."""
        self.current_stage = stage
        if metadata:
            self.stage_metadata.update(metadata)
        self.updated_at = datetime.now()

    def activate_agent(self, agent_name: str) -> None:
        """Mark an agent as active."""
        if agent_name not in self.active_agents:
            self.active_agents.append(agent_name)
        self.updated_at = datetime.now()

    def deactivate_agent(self, agent_name: str) -> None:
        """Mark an agent as inactive."""
        if agent_name in self.active_agents:
            self.active_agents.remove(agent_name)
        self.updated_at = datetime.now()

    def update_agent_state(self, agent_name: str, state: Dict[str, Any]) -> None:
        """Update an agent's internal state."""
        self.agent_states[agent_name] = state
        self.updated_at = datetime.now()

    def get_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """Get an agent's internal state."""
        return self.agent_states.get(agent_name, {})

    def set_memory_context(self, context: Dict[str, Any]) -> None:
        """Set context from Memory Agent."""
        self.memory_context = context
        self.updated_at = datetime.now()

    def set_mcp_context(self, context: Dict[str, Any]) -> None:
        """Set context from MCP Agent."""
        self.mcp_context = context
        self.updated_at = datetime.now()

    def set_personal_context(self, context: Dict[str, Any]) -> None:
        """Set context from Personal Content Agent."""
        self.personal_context = context
        self.updated_at = datetime.now()

    def get_all_context(self) -> Dict[str, Any]:
        """Get all available context from agents."""
        return {
            "memory": self.memory_context,
            "mcp": self.mcp_context,
            "personal": self.personal_context,
            "conversation_state": self.conversation_state,
            "morning_challenge": self.morning_challenge,
            "morning_value": self.morning_value
        }

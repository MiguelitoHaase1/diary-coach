from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from dataclasses import dataclass
from enum import Enum

from src.events.schemas import UserMessage, AgentResponse as LegacyAgentResponse


class AgentCapability(Enum):
    """Capabilities that agents can provide."""
    CONVERSATION = "conversation"
    MEMORY_ACCESS = "memory_access"
    TASK_MANAGEMENT = "task_management"
    PERSONAL_CONTEXT = "personal_context"
    ORCHESTRATION = "orchestration"
    REPORTING = "reporting"
    EVALUATION = "evaluation"
    AGENT_COORDINATION = "agent_coordination"
    PARALLEL_EXECUTION = "parallel_execution"
    STAGE_MANAGEMENT = "stage_management"
    REPORT_GENERATION = "report_generation"
    SYNTHESIS = "synthesis"
    QUALITY_ASSESSMENT = "quality_assessment"


@dataclass
class AgentRequest:
    """Request from one agent to another."""
    from_agent: str
    to_agent: str
    query: str
    context: Dict[str, Any]
    request_id: str = ""
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class AgentResponse:
    """Response from an agent."""
    agent_name: str
    content: str
    metadata: Dict[str, Any]
    request_id: str
    timestamp: datetime
    error: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system."""
    
    def __init__(self, name: str, capabilities: List[AgentCapability]):
        self.name = name
        self.agent_id = str(uuid.uuid4())
        self.capabilities = capabilities
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent with any required resources."""
        pass
    
    @abstractmethod
    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle a request from another agent or the orchestrator.
        
        Args:
            request: The agent request to handle
            
        Returns:
            AgentResponse with the result or error
        """
        pass
    
    async def shutdown(self) -> None:
        """Clean up any resources held by the agent."""
        pass
    
    def can_handle(self, capability: AgentCapability) -> bool:
        """Check if this agent has a specific capability."""
        return capability in self.capabilities
    
    async def process_message(self, user_message: UserMessage) -> AgentResponse:
        """Legacy method for backward compatibility."""
        # Convert UserMessage to AgentRequest
        request = AgentRequest(
            from_agent="user",
            to_agent=self.name,
            query=user_message.content,
            context={
                "conversation_id": user_message.conversation_id,
                "message_id": user_message.message_id,
                "timestamp": user_message.timestamp.isoformat()
            }
        )
        
        # Handle through new interface
        response = await self.handle_request(request)
        
        # Convert back to legacy AgentResponse format
        return LegacyAgentResponse(
            agent_name=self.name,
            content=response.content,
            response_to=user_message.message_id,
            conversation_id=user_message.conversation_id,
            timestamp=response.timestamp
        )

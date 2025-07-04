"""Test agent interface abstraction for LangGraph migration."""

import pytest
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.events.schemas import UserMessage, AgentResponse


class AgentInterface(ABC):
    """Abstract interface for both event-bus and LangGraph agent implementations."""
    
    @abstractmethod
    async def process_message(self, message: UserMessage) -> AgentResponse:
        """Process a user message and return an agent response."""
        pass
    
    @abstractmethod
    async def get_conversation_state(self) -> Dict[str, Any]:
        """Get the current conversation state."""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get performance and quality metrics."""
        pass
    
    @abstractmethod
    async def reset_state(self) -> None:
        """Reset conversation state."""
        pass


class EventBusAgentAdapter(AgentInterface):
    """Adapter for existing event-bus based agents."""
    
    def __init__(self, agent):
        self.agent = agent
    
    async def process_message(self, message: UserMessage) -> AgentResponse:
        """Process message through existing agent."""
        return await self.agent.process_message(message)
    
    async def get_conversation_state(self) -> Dict[str, Any]:
        """Get state from existing agent."""
        return {
            "conversation_state": getattr(self.agent, 'conversation_state', 'general'),
            "morning_challenge": getattr(self.agent, 'morning_challenge', None),
            "morning_value": getattr(self.agent, 'morning_value', None),
            "message_history": getattr(self.agent, 'message_history', [])
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get basic metrics from existing agent."""
        return {
            "message_count": len(getattr(self.agent, 'message_history', [])),
            "last_interaction": datetime.now().isoformat()
        }
    
    async def reset_state(self) -> None:
        """Reset existing agent state."""
        if hasattr(self.agent, 'reset_daily_state'):
            self.agent.reset_daily_state()


class LangGraphAgentAdapter(AgentInterface):
    """Placeholder for LangGraph-based agent implementation."""
    
    def __init__(self):
        self.state = {
            "conversation_state": "general",
            "messages": [],
            "metrics": {}
        }
    
    async def process_message(self, message: UserMessage) -> AgentResponse:
        """Process message through LangGraph (placeholder)."""
        # This will be implemented in later increments
        return AgentResponse(
            agent_name="langgraph_coach",
            content="LangGraph placeholder response",
            response_to=message.message_id,
            conversation_id=message.conversation_id
        )
    
    async def get_conversation_state(self) -> Dict[str, Any]:
        """Get LangGraph state."""
        return self.state.copy()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get LangGraph metrics."""
        return self.state.get("metrics", {})
    
    async def reset_state(self) -> None:
        """Reset LangGraph state."""
        self.state = {
            "conversation_state": "general",
            "messages": [],
            "metrics": {}
        }


class AgentFactory:
    """Factory for creating agent implementations."""
    
    @staticmethod
    def create_agent(agent_type: str, **kwargs) -> AgentInterface:
        """Create agent of specified type."""
        if agent_type == "event_bus":
            from src.agents.coach_agent import DiaryCoach
            from src.services.llm_service import AnthropicService
            llm_service = kwargs.get('llm_service') or AnthropicService()
            agent = DiaryCoach(llm_service)
            return EventBusAgentAdapter(agent)
        elif agent_type == "langgraph":
            return LangGraphAgentAdapter()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")


@pytest.mark.asyncio
async def test_agent_interface_contract():
    """Both implementations must satisfy same interface."""
    
    # Test message for interface validation
    test_message = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conversation"
    )
    
    for implementation in ["event_bus", "langgraph"]:
        agent = AgentFactory.create_agent(implementation)
        
        # Test required methods exist
        assert hasattr(agent, 'process_message')
        assert hasattr(agent, 'get_conversation_state')
        assert hasattr(agent, 'get_metrics')
        assert hasattr(agent, 'reset_state')
        
        # Test methods work
        response = await agent.process_message(test_message)
        assert isinstance(response, AgentResponse)
        assert response.content is not None
        
        state = await agent.get_conversation_state()
        assert isinstance(state, dict)
        assert "conversation_state" in state
        
        metrics = await agent.get_metrics()
        assert isinstance(metrics, dict)
        
        # Test reset doesn't crash
        await agent.reset_state()


@pytest.mark.asyncio
async def test_event_bus_adapter():
    """EventBusAdapter should wrap existing agent correctly."""
    agent = AgentFactory.create_agent("event_bus")
    
    test_message = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conversation"
    )
    
    # Test message processing
    response = await agent.process_message(test_message)
    assert response.agent_name == "diary_coach"
    assert "morning" in response.content.lower()
    
    # Test state retrieval
    state = await agent.get_conversation_state()
    assert state["conversation_state"] == "morning"
    assert len(state["message_history"]) >= 2  # User + assistant messages
    
    # Test metrics
    metrics = await agent.get_metrics()
    assert metrics["message_count"] >= 2
    assert "last_interaction" in metrics


@pytest.mark.asyncio
async def test_langgraph_adapter():
    """LangGraphAdapter should provide placeholder implementation."""
    agent = AgentFactory.create_agent("langgraph")
    
    test_message = UserMessage(
        user_id="test_user",
        content="good morning",
        timestamp=datetime.now(),
        conversation_id="test_conversation"
    )
    
    # Test message processing
    response = await agent.process_message(test_message)
    assert response.agent_name == "langgraph_coach"
    assert "placeholder" in response.content.lower()
    
    # Test state retrieval
    state = await agent.get_conversation_state()
    assert state["conversation_state"] == "general"
    assert "messages" in state
    
    # Test reset
    await agent.reset_state()
    state = await agent.get_conversation_state()
    assert state["conversation_state"] == "general"


@pytest.mark.asyncio
async def test_agent_factory():
    """AgentFactory should create correct agent types."""
    
    # Test event bus agent creation
    event_agent = AgentFactory.create_agent("event_bus")
    assert isinstance(event_agent, EventBusAgentAdapter)
    
    # Test langgraph agent creation
    graph_agent = AgentFactory.create_agent("langgraph")
    assert isinstance(graph_agent, LangGraphAgentAdapter)
    
    # Test invalid agent type
    with pytest.raises(ValueError, match="Unknown agent type"):
        AgentFactory.create_agent("invalid_type")
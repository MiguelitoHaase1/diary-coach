"""Agent registry for dynamic agent lookup and management."""

from typing import Dict, List, Optional, Type
from src.agents.base import BaseAgent, AgentCapability
import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing and discovering agents in the system."""
    
    _instance: Optional['AgentRegistry'] = None
    _agents: Dict[str, BaseAgent] = {}
    _agent_classes: Dict[str, Type[BaseAgent]] = {}
    
    def __new__(cls) -> 'AgentRegistry':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_agent_class(self, name: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent class for later instantiation.
        
        Args:
            name: Unique name for the agent
            agent_class: The agent class to register
        """
        if name in self._agent_classes:
            logger.warning(f"Overwriting existing agent class: {name}")
        self._agent_classes[name] = agent_class
        logger.info(f"Registered agent class: {name}")
    
    def register_instance(self, agent: BaseAgent) -> None:
        """Register an instantiated agent.
        
        Args:
            agent: The agent instance to register
        """
        if agent.name in self._agents:
            logger.warning(f"Overwriting existing agent instance: {agent.name}")
        self._agents[agent.name] = agent
        logger.info(
            f"Registered agent instance: {agent.name} "
            f"with capabilities: {[c.value for c in agent.capabilities]}"
        )
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name.
        
        Args:
            name: The agent name
            
        Returns:
            The agent instance or None if not found
        """
        return self._agents.get(name)
    
    def get_agents_by_capability(
        self, capability: AgentCapability
    ) -> List[BaseAgent]:
        """Get all agents with a specific capability.
        
        Args:
            capability: The capability to search for
            
        Returns:
            List of agents with the capability
        """
        return [
            agent for agent in self._agents.values()
            if agent.can_handle(capability)
        ]
    
    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())
    
    def list_capabilities(self) -> Dict[str, List[str]]:
        """List all agents and their capabilities."""
        return {
            name: [c.value for c in agent.capabilities]
            for name, agent in self._agents.items()
        }
    
    def unregister(self, name: str) -> bool:
        """Unregister an agent.
        
        Args:
            name: The agent name to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if name in self._agents:
            del self._agents[name]
            logger.info(f"Unregistered agent: {name}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all registered agents."""
        self._agents.clear()
        self._agent_classes.clear()
        logger.info("Cleared agent registry")


# Global registry instance
agent_registry = AgentRegistry()
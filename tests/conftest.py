"""Global test configuration and fixtures."""

import pytest
from unittest.mock import Mock
from src.agents.registry import agent_registry, AgentRegistry


@pytest.fixture(autouse=True)
def reset_agent_registry():
    """Reset agent registry state before and after each test."""
    # Clear any existing state
    agent_registry._agents.clear()
    agent_registry._agent_classes.clear()
    
    # Run the test
    yield
    
    # Clean up after test
    agent_registry._agents.clear()
    agent_registry._agent_classes.clear()


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton instances between tests."""
    # Reset the agent registry singleton
    AgentRegistry._instance = None
    
    yield
    
    # Clean up after test
    AgentRegistry._instance = None


@pytest.fixture
def mock_registry():
    """Provide a fresh mock registry for tests."""
    registry = AgentRegistry()
    registry._agents = {}
    registry._agent_classes = {}
    return registry
#!/usr/bin/env python3
"""Simple test for Stage 3 orchestrator coordination."""

import asyncio
from unittest.mock import Mock, AsyncMock
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.registry import agent_registry
from src.services.llm_factory import LLMFactory

async def test_simple_stage3():
    """Test Stage 3 coordination with mocked agents."""
    
    # Initialize orchestrator
    llm_service = LLMFactory.create_standard_service()
    orchestrator = OrchestratorAgent(llm_service)
    
    # Create mock agents with capabilities
    from src.agents.base import AgentCapability
    
    mock_memory = Mock()
    mock_memory.name = "memory"
    mock_memory.capabilities = [AgentCapability.MEMORY_ACCESS]
    mock_memory.handle_request = AsyncMock(return_value=Mock(
        content="Past conversations show focus on team autonomy.",
        error=None
    ))
    
    mock_personal = Mock()
    mock_personal.name = "personal_content"
    mock_personal.capabilities = [AgentCapability.PERSONAL_CONTEXT]
    mock_personal.handle_request = AsyncMock(return_value=Mock(
        content="Core belief: Empowered teams deliver better results.",
        error=None
    ))
    
    mock_mcp = Mock()
    mock_mcp.name = "mcp"
    mock_mcp.capabilities = [AgentCapability.TASK_MANAGEMENT]
    mock_mcp.handle_request = AsyncMock(return_value=Mock(
        content="No relevant tasks found.",
        error=None
    ))
    
    mock_reporter = Mock()
    mock_reporter.name = "reporter"
    mock_reporter.capabilities = [AgentCapability.REPORT_GENERATION]
    mock_reporter.handle_request = AsyncMock(return_value=Mock(
        content="Deep Thoughts Report\n\n[NEEDS_WEBSEARCH: autonomous teams best practices]",
        error=None
    ))
    
    mock_search = Mock()
    mock_search.name = "claude_web_search"
    mock_search.capabilities = [AgentCapability.WEB_SEARCH]
    mock_search.handle_request = AsyncMock(return_value=Mock(
        content="Found articles on autonomous teams.",
        error=None,
        metadata={"search_type": "mock"}
    ))
    
    # Register mocks
    agent_registry.register_instance(mock_memory)
    agent_registry.register_instance(mock_personal)
    agent_registry.register_instance(mock_mcp)
    agent_registry.register_instance(mock_reporter)
    agent_registry.register_instance(mock_search)
    
    # Test coordination
    print("Testing Stage 3 Coordination...")
    result = await orchestrator.coordinate_stage3_synthesis({
        "conversation": [
            {"role": "user", "content": "Help with teams"},
            {"role": "assistant", "content": "Let's explore that"}
        ]
    })
    
    # Check results
    print(f"Status: {result.get('status')}")
    print(f"Agents queried: {result.get('coordination_metadata', {}).get('agents_queried', [])}")
    print(f"Web search performed: {result.get('coordination_metadata', {}).get('web_search_performed')}")
    
    # Verify all agents were called
    assert mock_memory.handle_request.called
    assert mock_personal.handle_request.called
    assert mock_mcp.handle_request.called
    assert mock_reporter.handle_request.called
    
    print("\n✅ All agents were coordinated through orchestrator!")
    print("✅ Stage 3 unified coordination working correctly!")

if __name__ == "__main__":
    asyncio.run(test_simple_stage3())
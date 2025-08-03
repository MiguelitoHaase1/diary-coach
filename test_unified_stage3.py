#!/usr/bin/env python3
"""Test script for unified Stage 3 orchestrator coordination."""

import asyncio
import logging
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.personal_content_agent import PersonalContentAgent
from src.agents.mcp_agent import MCPAgent
from src.agents.reporter_agent import ReporterAgent
from src.agents.claude_web_search_agent import ClaudeWebSearchAgent
from src.agents.registry import agent_registry
from src.services.llm_factory import LLMFactory

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_unified_stage3():
    """Test the unified Stage 3 coordination."""
    
    # Initialize services
    llm_service = LLMFactory.create_standard_service()
    
    # Initialize all agents
    print("Initializing agents...")
    orchestrator = OrchestratorAgent(llm_service)
    await orchestrator.initialize()
    
    memory = MemoryAgent()
    await memory.initialize()
    
    personal = PersonalContentAgent()
    await personal.initialize()
    
    mcp = MCPAgent()
    await mcp.initialize()
    
    reporter = ReporterAgent()
    await reporter.initialize()
    
    claude_search = ClaudeWebSearchAgent()
    await claude_search.initialize()
    
    # Register all agents
    agent_registry.register_instance(orchestrator)
    agent_registry.register_instance(memory)
    agent_registry.register_instance(personal)
    agent_registry.register_instance(mcp)
    agent_registry.register_instance(reporter)
    agent_registry.register_instance(claude_search)
    
    # Sample conversation
    sample_conversation = [
        {"role": "user", "content": "Good morning! I'm struggling with building autonomous teams."},
        {"role": "assistant", "content": "Good morning! Building autonomous teams is a fascinating challenge..."},
        {"role": "user", "content": "How do I maintain design quality while giving teams freedom?"},
        {"role": "assistant", "content": "That's the crux - balancing autonomy with coherence..."}
    ]
    
    # Test unified Stage 3 coordination
    print("\n=== Testing Unified Stage 3 Coordination ===")
    result = await orchestrator.coordinate_stage3_synthesis({
        "conversation": sample_conversation
    })
    
    # Display results
    print(f"\nStatus: {result.get('status')}")
    
    if result.get('status') == 'success':
        # Show what was gathered
        metadata = result.get('coordination_metadata', {})
        print(f"Agents queried: {', '.join(metadata.get('agents_queried', []))}")
        print(f"Web search performed: {metadata.get('web_search_performed')}")
        
        # Show agent contributions
        contributions = result.get('agent_contributions', {})
        for agent_name, content in contributions.items():
            print(f"\n--- {agent_name} contribution ---")
            # Show first 200 chars
            print(content[:200] + "..." if len(content) > 200 else content)
        
        # Show if report was generated
        report = result.get('initial_report', '')
        if report:
            print(f"\n--- Initial Report Generated ---")
            print(f"Report length: {len(report)} characters")
            print("First 500 chars:")
            print(report[:500] + "..." if len(report) > 500 else report)
        
        # Show web search results
        web_search = result.get('web_search_results', {})
        if web_search.get('status') == 'success':
            brief = web_search.get('structured_brief', {})
            summary = brief.get('search_summary', {})
            print(f"\n--- Web Search Results ---")
            print(f"Successful searches: {summary.get('successful')}")
            print(f"Failed searches: {summary.get('failed')}")
    else:
        print(f"Error: {result.get('error')}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_unified_stage3())
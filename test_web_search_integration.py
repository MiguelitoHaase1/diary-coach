#!/usr/bin/env python3
"""Test script for web search integration with orchestrator Phase 3."""

import asyncio
import logging
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.claude_web_search_agent import ClaudeWebSearchAgent
from src.agents.registry import agent_registry
from src.services.llm_factory import LLMFactory

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_phase3_coordination():
    """Test the Phase 3 web search coordination."""
    
    # Initialize services
    llm_service = LLMFactory.create_standard_service()
    
    # Initialize agents
    print("Initializing agents...")
    orchestrator = OrchestratorAgent(llm_service)
    await orchestrator.initialize()
    
    claude_search = ClaudeWebSearchAgent()
    await claude_search.initialize()
    
    # Register agents
    agent_registry.register_instance(orchestrator)
    agent_registry.register_instance(claude_search)
    
    # Sample Deep Thoughts report with search markers
    sample_report = """
    Deep Thoughts Report
    
    Today's Crux: Building autonomous teams while maintaining design coherence
    
    The challenge is creating self-organizing teams that can move fast while 
    ensuring design quality and consistency across the product.
    
    Options:
    1. Centralized design system with autonomous implementation
    2. Embedded designers in each team with design guild coordination
    3. Hybrid approach with core design team and embedded specialists
    
    Recommended readings:
    
    **Theme 1: Autonomous team structures**
    [NEEDS_WEBSEARCH: autonomous teams best practices articles research]
    
    **Theme 2: AI-powered design workflows**
    [NEEDS_WEBSEARCH: AI design tools and workflows articles research]
    
    **Theme 3: Design system governance**
    [NEEDS_WEBSEARCH: design system governance and scaling articles research]
    """
    
    # Test Phase 3 coordination
    print("\n=== Testing Phase 3 Coordination ===")
    result = await orchestrator.coordinate_phase3_search(
        sample_report,
        {"conversation": []}
    )
    
    # Display results
    print(f"\nStatus: {result.get('status')}")
    print(f"Queries executed: {result.get('queries_executed')}")
    
    if result.get('status') == 'success':
        brief = result.get('structured_brief', {})
        summary = brief.get('search_summary', {})
        print(f"Successful searches: {summary.get('successful')}")
        print(f"Failed searches: {summary.get('failed')}")
        
        # Show organized results
        organized = brief.get('organized_results', {})
        for theme, data in organized.items():
            print(f"\n--- {theme} ---")
            content = data.get('content', '')
            # Show first 500 chars
            print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print(f"Error: {result.get('error')}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_phase3_coordination())
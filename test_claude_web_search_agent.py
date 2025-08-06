#!/usr/bin/env python3
"""Test the Claude Web Search Agent with actual web search."""

import asyncio
from datetime import datetime
from src.agents.claude_web_search_agent import ClaudeWebSearchAgent
from src.agents.base import AgentRequest


async def test_web_search_agent():
    """Test the web search agent with real web search."""
    print("Testing Claude Web Search Agent...")
    print("-" * 50)
    
    # Initialize the agent
    agent = ClaudeWebSearchAgent()
    await agent.initialize()
    
    # Create a test request
    request = AgentRequest(
        from_agent="test",
        to_agent="claude_web_search",
        query="Search for articles",
        context={
            "queries": [
                "remote work productivity best practices 2025",
                "AI tools for team management Harvard Business Review"
            ]
        },
        request_id="test-001"
    )
    
    # Make the request
    print("Sending search request...")
    response = await agent.handle_request(request)
    
    print("\nResponse from agent:")
    print("-" * 50)
    print(response.content)
    print("-" * 50)
    print(f"\nMetadata: {response.metadata}")
    
    # Check if we got real URLs
    if "http" in response.content:
        print("\n✅ Found URLs in response!")
    else:
        print("\n⚠️  No URLs found in response")


if __name__ == "__main__":
    asyncio.run(test_web_search_agent())
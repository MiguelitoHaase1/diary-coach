#!/usr/bin/env python3
"""Simple test to verify Anthropic web search tool functionality."""

import asyncio
import os
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()


async def test_web_search():
    """Test web search with proper tool configuration."""
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    print("Testing Anthropic Web Search Tool...")
    print("-" * 50)
    
    # According to docs, web search is enabled with tools parameter
    try:
        # Method 1: With web search tool enabled
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest model with web search
            max_tokens=1500,
            temperature=0.3,
            system="You are a helpful assistant with web search capabilities. When asked to search, use your web search ability to find current information.",
            messages=[
                {
                    "role": "user",
                    "content": "Search the web for recent articles about AI productivity tools from Harvard Business Review or MIT Sloan Review. Find 2-3 specific articles with real URLs."
                }
            ],
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5
            }]
        )
        
        print("Response from Claude:")
        # Check if response has tool use blocks
        if hasattr(response, 'content'):
            for block in response.content:
                if hasattr(block, 'type'):
                    print(f"Block type: {block.type}")
                    if block.type == 'text':
                        print(f"Text: {block.text}")
                    elif block.type == 'tool_use':
                        print(f"Tool use: {block}")
        else:
            print(response)
        print("-" * 50)
        
        # Method 2: Try with explicit tool use instruction and tools parameter
        response2 = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.3,
            messages=[
                {
                    "role": "user", 
                    "content": "Use web search to find the latest articles about remote work productivity from reputable business journals. I need actual URLs."
                }
            ],
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5
            }]
        )
        
        print("\nResponse with explicit web search request:")
        # Check if response has tool use blocks
        if hasattr(response2, 'content'):
            for block in response2.content:
                if hasattr(block, 'type'):
                    print(f"Block type: {block.type}")
                    if block.type == 'text':
                        print(f"Text: {block.text}")
                    elif block.type == 'tool_use':
                        print(f"Tool use: {block}")
        else:
            print(response2)
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response}")


if __name__ == "__main__":
    asyncio.run(test_web_search())
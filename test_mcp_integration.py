#!/usr/bin/env python3
"""
Test script to verify MCP integration works end-to-end.
This will test the flow from user message → todo context → enhanced prompt → LLM response.
"""

import asyncio
import sys
import os
sys.path.insert(0, 'src')

from src.agents.coach_agent import DiaryCoach
from src.services.llm_service import AnthropicService
from src.events.schemas import UserMessage


async def test_mcp_integration():
    """Test end-to-end MCP integration."""
    print("=== Testing MCP Integration ===")
    
    # Initialize services
    llm_service = AnthropicService(
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        model="claude-3-5-sonnet-20241022"
    )
    
    coach = DiaryCoach(llm_service)
    
    # Test message that should trigger todo fetching
    test_message = UserMessage(
        message_id="test-1",
        conversation_id="test-conv",
        content="What should I prioritize working on today?",
        user_id="michael"
    )
    
    print(f"Test message: {test_message.content}")
    print()
    
    # Test todo context fetching
    print("=== Testing Todo Context Fetching ===")
    try:
        todo_context = await coach._get_todo_context(test_message)
        print(f"Todo context fetched: {todo_context is not None}")
        
        if todo_context:
            print(f"Number of todos: {len(todo_context)}")
            for i, todo in enumerate(todo_context[:3], 1):
                print(f"{i}. {todo.get('content', 'No content')} - {todo.get('priority', 'no priority')}")
        else:
            print("No todo context fetched - this might be expected if no API token or low relevance")
            
    except Exception as e:
        print(f"Error fetching todo context: {e}")
        todo_context = None
    
    print()
    
    # Test system prompt enhancement
    print("=== Testing System Prompt Enhancement ===")
    try:
        enhanced_prompt = coach._get_system_prompt_with_context(todo_context)
        base_prompt = coach._get_system_prompt()
        
        print(f"Base prompt length: {len(base_prompt)} characters")
        print(f"Enhanced prompt length: {len(enhanced_prompt)} characters")
        print(f"Prompt was enhanced: {len(enhanced_prompt) > len(base_prompt)}")
        
        if todo_context and len(enhanced_prompt) > len(base_prompt):
            print("✅ System prompt enhancement is working!")
            print("\nEnhanced section:")
            enhancement = enhanced_prompt[len(base_prompt):]
            print(enhancement[:200] + "..." if len(enhancement) > 200 else enhancement)
        else:
            print("ℹ️ System prompt not enhanced (expected if no todos)")
            
    except Exception as e:
        print(f"Error testing prompt enhancement: {e}")
    
    print()
    
    # Test MCP server status
    print("=== Testing MCP Server Status ===")
    try:
        mcp_status = await coach.mcp_todo_node.get_mcp_status()
        print(f"MCP connected: {mcp_status.get('connected', False)}")
        print(f"Using mock data: {mcp_status.get('using_mock_data', True)}")
        
        if mcp_status.get('error'):
            print(f"Error: {mcp_status['error']}")
        
        if mcp_status.get('total_todos'):
            print(f"Total todos: {mcp_status['total_todos']}")
            
    except Exception as e:
        print(f"Error getting MCP status: {e}")
    
    print()
    print("=== Test Complete ===")
    print("If you see 'MCP connected: True' and 'Using mock data: False', the integration is working!")
    print("If you see errors, you may need to:")
    print("1. Install the Doist MCP server: npm install -g @doist/todoist-mcp")
    print("2. Set TODOIST_API_TOKEN environment variable")
    print("3. Configure Claude Desktop with the MCP server")


if __name__ == "__main__":
    asyncio.run(test_mcp_integration())
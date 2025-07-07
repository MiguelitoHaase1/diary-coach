#!/usr/bin/env python3
"""
Test script to debug the coach message processing flow
"""

import asyncio
import sys
import os
sys.path.insert(0, 'src')

from src.agents.coach_agent import DiaryCoach
from src.services.llm_service import AnthropicService
from src.events.schemas import UserMessage


async def test_debug_flow():
    """Test the coach flow with debug output."""
    print("=== Testing Coach Debug Flow ===")
    
    # Mock LLM service that doesn't actually call Anthropic
    class MockLLMService:
        def __init__(self):
            pass
            
        async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
            print(f"🤖 DEBUG: LLM called with system prompt length: {len(system_prompt)}")
            print(f"🤖 DEBUG: First 200 chars of system prompt: {system_prompt[:200]}...")
            if "Current Relevant Tasks" in system_prompt:
                print("✅ DEBUG: System prompt contains todo context!")
            else:
                print("❌ DEBUG: System prompt does NOT contain todo context")
            
            return "Mock coaching response based on the enhanced prompt."
    
    # Initialize services
    llm_service = MockLLMService()
    coach = DiaryCoach(llm_service)
    
    # Test message that should trigger todo fetching
    from datetime import datetime
    test_message = UserMessage(
        message_id="test-1",
        conversation_id="test-conv",
        content="What are my tasks today?",
        user_id="michael",
        timestamp=datetime.now()
    )
    
    print(f"Testing with message: '{test_message.content}'")
    print("=" * 50)
    
    try:
        # Process the message - this will show all our debug output
        response = await coach.process_message(test_message)
        print("=" * 50)
        print(f"Final response: {response.content}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_debug_flow())
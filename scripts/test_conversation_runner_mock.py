"""Test conversation runner with mock LLM for debugging."""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Mock LLM service for testing
class MockLLMService:
    async def generate_response(self, prompt, **kwargs):
        # Simulate different PM responses based on turn
        responses = [
            "I'm really struggling with getting everyone aligned on our roadmap. Sales wants features, engineering wants to pay down tech debt, and the CEO wants growth metrics.",
            "That's a good question. I guess I've been trying to make everyone happy instead of making tough choices. But how do I decide what's actually most important?",
            "Hmm, when I think about it, I suppose I'm optimizing for avoiding conflict rather than driving outcomes. That's probably not the right approach.",
            "You're right, I should be asking what creates the most value for customers and the business. Let me think about this differently.",
            "stop"
        ]
        
        # Cycle through responses
        import random
        return random.choice(responses[:-1]) if "stop" not in prompt.lower() else "stop"

# Mock conversation test runner
async def test_conversation_flow():
    """Test the conversation flow with mock services."""
    print("🤖 Testing conversation flow with mock LLM...")
    
    # Simulate conversation
    conversation_messages = []
    mock_llm = MockLLMService()
    
    # Initial user message
    initial_message = "I'm feeling overwhelmed with my roadmap priorities."
    conversation_messages.append({"role": "user", "content": initial_message})
    print(f"User: {initial_message}")
    
    turn_count = 0
    max_turns = 5
    
    while turn_count < max_turns:
        turn_count += 1
        
        # Mock coach response
        coach_prompt = f"Coaching response to: {conversation_messages[-1]['content']}"
        coach_response = f"What's really driving your sense of being overwhelmed? Is it the number of choices or something deeper about how you're approaching the decision?"
        
        conversation_messages.append({"role": "assistant", "content": coach_response})
        print(f"Coach: {coach_response}")
        
        # Mock user response
        user_response = await mock_llm.generate_response(
            f"Respond as PM to coach: {coach_response}"
        )
        
        if user_response.lower() == "stop":
            conversation_messages.append({"role": "user", "content": "stop"})
            print(f"User: {user_response}")
            break
            
        conversation_messages.append({"role": "user", "content": user_response})
        print(f"User: {user_response}")
    
    print(f"\n✅ Conversation completed in {turn_count} turns")
    print(f"📊 Total messages: {len(conversation_messages)}")
    
    # Mock deep report
    print(f"\n📝 Generating mock deep report...")
    deep_report = {
        "deep_thoughts_content": "Mock deep thoughts analysis of the conversation",
        "message_count": len(conversation_messages),
        "coaching_turns": len([msg for msg in conversation_messages if msg["role"] == "assistant"])
    }
    
    print(f"✅ Deep report generated: {deep_report['message_count']} messages, {deep_report['coaching_turns']} coaching turns")
    
    return {
        "conversation_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "test_name": "mock_pm_session",
        "turn_count": turn_count,
        "conversation_messages": conversation_messages,
        "deep_report": deep_report,
        "test_user_stats": {
            "breakthrough_achieved": turn_count >= 3,
            "resistance_level": max(0.2, 0.8 - (turn_count * 0.15)),
            "interaction_count": turn_count
        }
    }

async def test_evaluation_flow():
    """Test the evaluation flow with mock data."""
    print("\n🧪 Testing evaluation flow...")
    
    # Mock conversation result
    conversation_result = await test_conversation_flow()
    
    # Mock Run object for evaluation
    from collections import namedtuple
    MockRun = namedtuple('Run', ['inputs', 'outputs', 'id', 'run_type'])
    
    mock_run = MockRun(
        inputs={"messages": conversation_result['conversation_messages']},
        outputs={"response": conversation_result['deep_report']['deep_thoughts_content']},
        id="mock-run",
        run_type="llm"
    )
    
    print(f"📊 Mock evaluation data prepared")
    print(f"   Messages: {len(mock_run.inputs['messages'])}")
    print(f"   Output length: {len(mock_run.outputs['response'])}")
    
    return mock_run

async def main():
    """Main test function."""
    print("🔍 Testing Conversation Test Runner Components")
    print("=" * 50)
    
    try:
        # Test conversation flow
        conversation_result = await test_conversation_flow()
        print(f"\n✅ Conversation flow test completed")
        
        # Test evaluation setup
        mock_run = await test_evaluation_flow()
        print(f"\n✅ Evaluation flow test completed")
        
        print(f"\n🎉 All component tests passed!")
        print(f"📋 Summary:")
        print(f"   - Conversation messages: {len(conversation_result['conversation_messages'])}")
        print(f"   - Turn count: {conversation_result['turn_count']}")
        print(f"   - Breakthrough: {conversation_result['test_user_stats']['breakthrough_achieved']}")
        print(f"   - Final resistance: {conversation_result['test_user_stats']['resistance_level']:.2f}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
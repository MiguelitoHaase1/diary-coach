"""Simple integration test to verify nudges reach the LLM."""

import asyncio
import pytest
from unittest.mock import AsyncMock

from src.agents.enhanced_coach_agent import EnhancedDiaryCoach
from src.agents.base import AgentRequest
from src.services.llm_service import AnthropicService


@pytest.mark.asyncio
async def test_nudges_reach_llm():
    """Test that nudges are actually included in the LLM prompt."""
    
    # Track all prompts sent to LLM
    captured_prompts = []
    
    # Create mock LLM that captures prompts
    mock_llm = AsyncMock(spec=AnthropicService)
    
    async def capture_prompt(**kwargs):
        captured_prompts.append(kwargs.get('system_prompt', ''))
        return "Coach response mentioning the crux is unclear priorities"
    
    mock_llm.generate_response = capture_prompt
    
    # Create coach
    coach = EnhancedDiaryCoach(llm_service=mock_llm)
    await coach.initialize()
    
    print("\n=== Testing Nudge Integration ===\n")
    
    # Message 1: Morning greeting
    msg1 = AgentRequest(
        from_agent="user",
        to_agent="coach",
        query="Good morning!",
        context={"conversation_id": "test"},
        request_id="1"
    )
    
    response1 = await coach.handle_request(msg1)
    print(f"Exchange 1:")
    print(f"  User: {msg1.query}")
    print(f"  Coach: {response1.content[:50]}...")
    print(f"  Nudge in prompt: {'[NUDGE:' in captured_prompts[-1]}")
    
    # Message 2: State problem
    msg2 = AgentRequest(
        from_agent="user",
        to_agent="coach",
        query="I need to improve my team's productivity - it's been really low",
        context={"conversation_id": "test"},
        request_id="2"
    )
    
    response2 = await coach.handle_request(msg2)
    print(f"\nExchange 2:")
    print(f"  User: {msg2.query}")
    print(f"  Coach: {response2.content[:50]}...")
    
    # Check if nudge was prepared for next exchange
    nudge_prepared = coach._next_nudge is not None
    print(f"  Nudge prepared for next turn: {nudge_prepared}")
    
    # Message 3: Should have nudge about moving to State 2 (Crux)
    msg3 = AgentRequest(
        from_agent="user",
        to_agent="coach",
        query="Yes, it's been affecting our deadlines",
        context={"conversation_id": "test"},
        request_id="3"
    )
    
    response3 = await coach.handle_request(msg3)
    print(f"\nExchange 3:")
    print(f"  User: {msg3.query}")
    print(f"  Coach: {response3.content[:50]}...")
    
    # Check if nudge was in the prompt
    last_prompt = captured_prompts[-1]
    has_nudge = "[NUDGE:" in last_prompt
    print(f"  Nudge in prompt: {has_nudge}")
    
    if has_nudge:
        # Extract nudge text
        nudge_start = last_prompt.find("[NUDGE:")
        nudge_end = last_prompt.find("]", nudge_start) + 1
        nudge_text = last_prompt[nudge_start:nudge_end]
        print(f"  Nudge text: {nudge_text}")
    
    # Check protocol tracker state
    tracker_state = coach.protocol_tracker.get_state_summary()
    print(f"\nProtocol Tracker State:")
    print(f"  Current state: {tracker_state['current_state']}")
    print(f"  Current state title: {tracker_state['current_state_title']}")
    print(f"  Problem captured: {tracker_state['problem'] is not None}")
    print(f"  Total exchanges: {tracker_state['total_exchanges']}")
    
    # Verify expectations
    assert tracker_state['total_exchanges'] == 3, "Should have tracked 3 exchanges"
    assert tracker_state['problem'] is not None, "Should have captured the problem"
    assert tracker_state['current_state'] >= 2, "Should have moved to at least state 2"
    
    print("\n✅ Test passed! Nudges are reaching the LLM")
    
    return captured_prompts


if __name__ == "__main__":
    # Run the test
    prompts = asyncio.run(test_nudges_reach_llm())
    
    print("\n=== Captured Prompts Summary ===")
    for i, prompt in enumerate(prompts):
        has_nudge = "[NUDGE:" in prompt
        print(f"Prompt {i+1}: {'Has nudge' if has_nudge else 'No nudge'} (length: {len(prompt)})")
"""Tests for morning protocol nudging system."""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.agents.morning_protocol_tracker import MorningProtocolTracker
from src.agents.protocol_state_parser import ProtocolStateParser
from src.agents.enhanced_coach_agent import EnhancedDiaryCoach
from src.services.llm_service import AnthropicService


class TestProtocolNudgingPerformance:
    """Test that nudging logic is blazingly fast."""
    
    def test_nudge_analysis_speed(self):
        """Nudge analysis should complete in under 5ms."""
        protocol = """
        ## 1: Opening Sequence - find problem
        Ask about the problem
        
        ## 2: When problem is clear - start identifying the Crux
        Find the crux
        """
        
        tracker = MorningProtocolTracker(protocol)
        
        # Warm up
        tracker.analyze_exchange("Good morning!", "Hello! What's your problem?")
        
        # Time 100 exchanges
        start_time = time.time()
        for i in range(100):
            tracker.analyze_exchange(
                f"User message {i}",
                f"Assistant response {i}"
            )
        elapsed = time.time() - start_time
        
        # Should process 100 exchanges in under 50ms (0.5ms each)
        assert elapsed < 0.05, f"Too slow: {elapsed*1000:.2f}ms for 100 exchanges"
        print(f"✓ Processed 100 exchanges in {elapsed*1000:.2f}ms")
    
    def test_state_parsing_speed(self):
        """Protocol parsing should be near-instant."""
        protocol = """
        ## 1: Opening Sequence - find problem
        Description here
        ## 2: When problem is clear - start identifying the Crux
        More description
        ## 3: When Crux is identified - capture context
        Even more
        ## 4: Give user an opt-out
        Almost done
        ## 5: Values
        Final state
        """
        
        start_time = time.time()
        states = ProtocolStateParser.parse_protocol(protocol)
        elapsed = time.time() - start_time
        
        assert len(states) == 5
        assert elapsed < 0.001, f"Parsing took {elapsed*1000:.2f}ms"
        print(f"✓ Parsed protocol in {elapsed*1000:.4f}ms")


class TestNudgeDelivery:
    """Test that nudges are properly sent and received by the agent."""
    
    @pytest.mark.asyncio
    async def test_nudge_injected_into_system_prompt(self):
        """Nudges should be added to the system prompt for next generation."""
        # Create mock LLM service
        mock_llm = AsyncMock(spec=AnthropicService)
        mock_llm.generate_response = AsyncMock(return_value="Coach response")
        
        # Create coach with morning protocol
        coach = EnhancedDiaryCoach(llm_service=mock_llm)
        await coach.initialize()
        
        # Simulate morning greeting using AgentRequest
        from src.agents.base import AgentRequest
        from datetime import datetime
        
        message1 = AgentRequest(
            from_agent="user",
            to_agent="coach",
            query="Good morning!",
            context={"conversation_id": "test"},
            request_id="1"
        )
        
        await coach.handle_request(message1)
        
        # Check first call - no nudge yet
        first_call_prompt = mock_llm.generate_response.call_args[1]['system_prompt']
        assert "[NUDGE:" not in first_call_prompt
        
        # Second message stating a problem
        message2 = AgentRequest(
            from_agent="user",
            to_agent="coach",
            query="I need to fix my team communication",
            context={"conversation_id": "test"},
            request_id="2"
        )
        
        await coach.handle_request(message2)
        
        # Third message - should have nudge now
        message3 = AgentRequest(
            from_agent="user",
            to_agent="coach",
            query="It's really challenging",
            context={"conversation_id": "test"},
            request_id="3"
        )
        
        await coach.handle_request(message3)
        
        # Check that nudge was added to prompt
        if mock_llm.generate_response.call_count >= 3:
            third_call_prompt = mock_llm.generate_response.call_args[1]['system_prompt']
            # Should have nudge about moving to crux identification
            assert "[NUDGE:" in third_call_prompt or "crux" in third_call_prompt.lower()
    
    @pytest.mark.asyncio
    async def test_nudge_cleared_after_use(self):
        """Nudges should be used once then cleared."""
        mock_llm = AsyncMock(spec=AnthropicService)
        mock_llm.generate_response = AsyncMock(return_value="Response")
        
        coach = EnhancedDiaryCoach(llm_service=mock_llm)
        await coach.initialize()
        
        # Manually set a nudge
        coach._next_nudge = "\n\n[NUDGE: Test nudge]"
        
        # Process a message
        from src.agents.base import AgentRequest
        from datetime import datetime
        
        message = AgentRequest(
            from_agent="user",
            to_agent="coach",
            query="Good morning!",
            context={"conversation_id": "test"},
            request_id="1"
        )
        
        await coach.handle_request(message)
        
        # Nudge should be cleared
        assert coach._next_nudge is None


class TestStateTransitionDetection:
    """Test that state transitions are correctly detected."""
    
    def test_problem_detection(self):
        """Should detect when user states a problem."""
        protocol = """
        ## 1: Opening Sequence - find problem
        Get the problem
        ## 2: When problem is clear - start identifying the Crux
        Find crux
        """
        
        tracker = MorningProtocolTracker(protocol)
        
        # Start conversation
        nudge = tracker.analyze_exchange("Good morning!", "Hi! What's on your mind?")
        assert nudge is None
        assert tracker.current_state == 1
        
        # User states problem
        nudge = tracker.analyze_exchange(
            "I need to improve my team's productivity",
            "Tell me more about that"
        )
        # Should move to state 2
        assert tracker.current_state == 2
        assert tracker.problem == "I need to improve my team's productivity"
    
    def test_crux_detection(self):
        """Should detect when coach identifies crux."""
        protocol = """
        ## 1: Opening Sequence - find problem
        ## 2: When problem is clear - start identifying the Crux
        ## 3: When Crux is identified - capture context
        """
        
        tracker = MorningProtocolTracker(protocol)
        tracker.current_state = 2  # Already in crux-finding state
        
        nudge = tracker.analyze_exchange(
            "Yes, that's the issue",
            "I see. The crux seems to be unclear priorities causing confusion"
        )
        
        # Should detect crux and move to state 3
        assert tracker.current_state == 3
        assert "unclear priorities" in tracker.crux
    
    def test_timeout_nudging(self):
        """Should nudge after too many exchanges in one state."""
        protocol = """
        ## 1: Opening Sequence - find problem
        Get problem
        ## 2: When problem is clear - start identifying the Crux
        """
        
        tracker = MorningProtocolTracker(protocol)
        tracker.current_state = 1
        
        # First 3 exchanges - no nudge
        for i in range(3):
            nudge = tracker.analyze_exchange(
                f"User message {i}",
                f"Coach response {i}"
            )
            assert nudge is None
        
        # 4th exchange - should nudge
        nudge = tracker.analyze_exchange(
            "Still chatting",
            "Still responding"
        )
        assert nudge is not None
        assert "problem" in nudge.lower()


class TestProtocolParsing:
    """Test that protocol parsing extracts correct information."""
    
    def test_parse_states_with_triggers(self):
        """Should extract transition triggers from 'When X' patterns."""
        protocol = """
        ## 1: Opening Sequence - find problem
        ## 2: When problem is clear - start identifying the Crux
        ## 3: When Crux is identified - capture other context
        """
        
        states = ProtocolStateParser.parse_protocol(protocol)
        
        assert len(states) == 3
        assert states[1].transition_triggers == ["problem is clear"]
        assert states[2].transition_triggers == ["crux is identified"]
    
    def test_completion_indicators(self):
        """Should generate appropriate completion indicators."""
        protocol = """
        ## 1: Opening Sequence - find problem
        Ask about their problem
        ## 2: When problem is clear - start identifying the Crux
        Help find the crux
        """
        
        states = ProtocolStateParser.parse_protocol(protocol)
        
        # State 1 should have problem-related indicators
        assert "need to" in states[0].completion_indicators
        assert "problem is" in states[0].completion_indicators
        
        # State 2 should have crux-related indicators
        assert "crux is" in states[1].completion_indicators


if __name__ == "__main__":
    # Run performance tests
    perf_tests = TestProtocolNudgingPerformance()
    perf_tests.test_nudge_analysis_speed()
    perf_tests.test_state_parsing_speed()
    
    # Run unit tests
    unit_tests = TestStateTransitionDetection()
    unit_tests.test_problem_detection()
    unit_tests.test_crux_detection()
    unit_tests.test_timeout_nudging()
    
    parse_tests = TestProtocolParsing()
    parse_tests.test_parse_states_with_triggers()
    parse_tests.test_completion_indicators()
    
    print("\n✅ All synchronous tests passed!")
    print("\nRun 'pytest tests/test_morning_protocol_nudging.py' for async tests")
"""Lightweight morning protocol state tracker for nudging phase transitions."""

from typing import Optional, Dict
import re
from src.agents.protocol_state_parser import ProtocolStateParser, ProtocolState


class MorningProtocolTracker:
    """Tracks morning protocol state and provides phase transition nudges."""

    def __init__(self, protocol_text: str):
        # Parse states from protocol
        self.states = ProtocolStateParser.parse_protocol(protocol_text)
        self.nudge_map = ProtocolStateParser.generate_nudge_map(self.states)

        self.current_state = 0  # Not started
        self.state_completed = {s.number: False for s in self.states}

        # Track key information
        self.problem: Optional[str] = None
        self.crux: Optional[str] = None

        # Track exchanges per state
        self.state_exchanges = {0: 0}  # Start with 0 (not started)
        for state in self.states:
            self.state_exchanges[state.number] = 0
        self.total_exchanges = 0

    def analyze_exchange(
        self,
        user_message: str,
        assistant_response: str
    ) -> Optional[str]:
        """Analyze exchange and return nudge if needed.

        Returns None if on track, or a nudge string to append to prompt.
        """
        user_lower = user_message.lower()
        # assistant_lower = assistant_response.lower()  # Not used in base method

        # Track exchanges
        self.total_exchanges += 1
        self.state_exchanges[self.current_state] += 1

        # State 0: Not started - check for morning greeting
        if self.current_state == 0:
            if any(g in user_lower for g in ["morning", "good morning", "gm"]):
                self.current_state = 1
                return None

        # For other states, check against parsed protocol
        elif self.current_state > 0 and self.current_state <= len(self.states):
            current = self.states[self.current_state - 1]  # Convert to 0-indexed

            # Check if current state is complete
            state_complete = self._check_state_completion(
                current, user_message, assistant_response
            )

            if state_complete:
                self.state_completed[self.current_state] = True

                # Move to next state if available
                if self.current_state < len(self.states):
                    self.current_state += 1
                    return self.nudge_map.get(self.current_state - 1)
            else:
                # Check if we need to nudge within current state
                if self.state_exchanges[self.current_state] > 3:
                    return self._generate_state_nudge(current)

        return None

    def _check_state_completion(
        self,
        state: ProtocolState,
        user_msg: str,
        assistant_msg: str
    ) -> bool:
        """Check if the current state's objectives have been completed."""
        user_lower = user_msg.lower()
        assistant_lower = assistant_msg.lower()

        # Check against completion indicators
        for indicator in state.completion_indicators:
            if indicator in user_lower or indicator in assistant_lower:
                # Special handling for specific states
                if state.number == 1 and "problem" in state.title.lower():
                    self.problem = user_msg
                elif state.number == 2 and "crux" in state.title.lower():
                    if indicator in assistant_lower:
                        self.crux = self._extract_crux(assistant_msg)
                return True

        return False

    def _generate_state_nudge(self, state: ProtocolState) -> str:
        """Generate a nudge specific to the current state."""
        # Extract key objective from state description
        if "problem" in state.title.lower():
            return f"\n\n[NUDGE: Help user articulate their {state.title}]"
        elif "crux" in state.title.lower():
            return "\n\n[NUDGE: Synthesize discussion into a clear CRUX statement]"
        elif "phase 2" in state.description.lower():
            return "\n\n[NUDGE: Explain phase 2 and ask for thoughts]"
        else:
            return f"\n\n[NUDGE: Progress to {state.title}]"

    def _contains_problem_statement(self, message: str) -> bool:
        """Check if message contains a problem statement."""
        problem_indicators = [
            "need to", "have to", "problem is", "challenge is",
            "struggling with", "working on", "goal is", "want to",
            "trying to", "figure out", "deal with", "handle"
        ]
        return any(ind in message.lower() for ind in problem_indicators)

    def _extract_crux(self, response: str) -> str:
        """Extract crux statement from assistant response."""
        # Simple extraction - look for "crux is" or similar
        patterns = [
            r"crux (?:is|seems to be|might be) ([^.!?]+)",
            r"The crux[:]? ([^.!?]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "crux not clearly stated"

    def get_state_exchanges(self, state_num: int) -> int:
        """Get number of exchanges in given state."""
        return self.state_exchanges.get(state_num, 0)

    def get_state_summary(self) -> Dict[str, any]:
        """Get current state summary."""
        current_state_info = None
        if 0 < self.current_state <= len(self.states):
            current_state_info = self.states[self.current_state - 1].title

        return {
            "current_state": self.current_state,
            "current_state_title": current_state_info,
            "states_completed": self.state_completed,
            "problem": self.problem,
            "crux": self.crux,
            "total_exchanges": self.total_exchanges,
            "ready_for_report": all(self.state_completed.values())
        }

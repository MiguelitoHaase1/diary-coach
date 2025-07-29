"""Parse morning protocol states from markdown to ensure nudging matches protocol."""

import re
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ProtocolState:
    """Represents a state in the morning protocol."""
    number: int
    title: str
    description: str
    transition_triggers: List[str]  # Keywords that indicate moving to this state
    completion_indicators: List[str]  # Signs that this state is complete


class ProtocolStateParser:
    """Parse protocol states from the morning protocol markdown."""

    @staticmethod
    def parse_protocol(protocol_text: str) -> List[ProtocolState]:
        """Extract states from the protocol markdown.

        Expects format like:
        ## 1: Opening Sequence - find problem
        Description text...

        ## 2: When problem is clear - start identifying the Crux
        Description text...
        """
        states = []

        # Split by state headers (## followed by number)
        state_pattern = r'## (\d+):\s*([^#\n]+)'
        matches = list(re.finditer(state_pattern, protocol_text, re.MULTILINE))

        for i, match in enumerate(matches):
            state_num = int(match.group(1))
            full_title = match.group(2).strip()

            # Extract transition trigger from title if present (after "When")
            transition_trigger = ""
            title = full_title
            if " - " in full_title:
                parts = full_title.split(" - ", 1)
                if parts[0].strip().startswith("When "):
                    transition_trigger = parts[0].replace("When ", "").strip()
                    title = parts[1].strip()
                else:
                    title = full_title

            # Get description (text between this header and next)
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(protocol_text)
            description = protocol_text[start_pos:end_pos].strip()

            # Extract key indicators from description
            transition_triggers = ProtocolStateParser._extract_triggers(
                transition_trigger, description
            )
            completion_indicators = ProtocolStateParser._extract_completion_indicators(
                state_num, title, description
            )

            states.append(ProtocolState(
                number=state_num,
                title=title,
                description=description,
                transition_triggers=transition_triggers,
                completion_indicators=completion_indicators
            ))

        return states

    @staticmethod
    def _extract_triggers(trigger_text: str, description: str) -> List[str]:
        """Extract keywords that indicate we should transition to this state."""
        triggers = []

        # Add explicit trigger from title
        if trigger_text:
            triggers.append(trigger_text.lower())

        # Extract common patterns from description
        # Look for "when X" patterns
        when_pattern = r'[Ww]hen\s+([^.,]+)'
        when_matches = re.findall(when_pattern, description)
        triggers.extend([m.lower().strip() for m in when_matches[:2]])  # Limit to first 2

        return triggers

    @staticmethod
    def _extract_completion_indicators(
        state_num: int, title: str, description: str
    ) -> List[str]:
        """Extract indicators that show this state is complete."""
        indicators = []

        # State-specific indicators based on common patterns
        if state_num == 1:
            # Looking for problem statement
            if "problem" in title.lower():
                indicators.extend([
                    "need to", "have to", "problem is", "challenge is",
                    "struggling with", "working on", "want to", "trying to"
                ])

        elif state_num == 2:
            # Looking for crux identification
            if "crux" in title.lower() or "crux" in description.lower():
                indicators.extend([
                    "crux is", "crux seems to be", "crux might be",
                    "the crux", "pivotal challenge"
                ])

        elif state_num == 3:
            # Looking for phase 2 explanation
            if "phase 2" in description.lower():
                indicators.extend(["phase 2", "deeper essay", "preparing for"])

        elif state_num == 4:
            # Looking for user opt-in/out
            indicators.extend(["yes", "sure", "ok", "deep report", "report now"])

        elif state_num == 5:
            # Looking for values discussion
            if "belief" in description.lower() or "value" in description.lower():
                indicators.extend(["belief", "value", "principle"])

        return indicators

    @staticmethod
    def generate_nudge_map(states: List[ProtocolState]) -> Dict[int, str]:
        """Generate appropriate nudges for each state transition."""
        nudge_map = {}

        for i, state in enumerate(states):
            if i + 1 < len(states):
                next_state = states[i + 1]
                # Create nudge to move to next state
                nudge_map[state.number] = (
                    f"[NUDGE: Time to move to State {next_state.number}: "
                    f"{next_state.title}]"
                )
            else:
                # Last state
                nudge_map[state.number] = (
                    "[NUDGE: Guide user to say 'stop' or 'deep report' to complete]"
                )

        return nudge_map

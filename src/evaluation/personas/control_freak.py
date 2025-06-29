"""Control Freak persona - perfectionist, needs to control every detail."""

import random
from typing import List
from src.evaluation.personas.base import BasePMPersona


class ControlFreakPersona(BasePMPersona):
    """PM persona that is perfectionist and needs to control every detail."""
    
    def __init__(self):
        """Initialize control freak persona."""
        super().__init__("ControlFreak")
        self.perfectionist_vocabulary = [
            "exactly right", "perfectly aligned", "completely optimized",
            "absolutely perfect", "precisely correct", "totally refined",
            "flawlessly executed", "meticulously planned", "impeccably designed"
        ]
        self.resistance_patterns = [
            "But I just need to refine it a bit more to make sure it's {perfect}.",
            "I want to make sure I get this {perfect} before moving forward.",
            "If I could just spend a little more time, I could make it {perfect}.",
            "I know it's good, but it could be {perfect} with just a few more tweaks.",
            "I can't ship this until it's {perfect} - users deserve the best."
        ]
    
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate response that resists with perfectionist thinking.
        
        Args:
            coach_message: The coach's message
            context: Previous conversation context
            
        Returns:
            Response that deflects to need for perfection and control
        """
        # Update resistance based on coach effectiveness
        self.update_resistance(coach_message)
        
        # If breakthrough threshold reached, show some openness
        if self.interaction_count >= self.breakthrough_threshold:
            if random.random() < 0.3:  # 30% chance of breakthrough response
                return self.generate_breakthrough_response()
        
        # Generate perfectionist response
        perfect_phrase = random.choice(self.perfectionist_vocabulary)
        pattern = random.choice(self.resistance_patterns)
        
        response = pattern.format(perfect=perfect_phrase)
        
        # Add context-specific perfectionist deflections
        if any(word in coach_message.lower() for word in ["good enough", "ship", "done"]):
            response += " Quality matters more than speed in my opinion."
        elif any(word in coach_message.lower() for word in ["perfect", "control"]):
            response += " I just have high standards for myself and my team."
        elif any(word in coach_message.lower() for word in ["feeling", "anxiety"]):
            response += " I just feel responsible for delivering excellence."
        
        return response
    
    def detects_effective_challenge(self, coach_message: str) -> bool:
        """Detect if coach effectively challenges perfectionist patterns.
        
        Args:
            coach_message: Coach message to evaluate
            
        Returns:
            True if coach challenges perfectionist/control patterns
        """
        effective_challenges = [
            "good enough", "perfect", "control", "anxiety", "responsible",
            "standards", "excellence", "quality", "refine", "tweaks"
        ]
        
        # Effective if coach questions the need for perfection/control
        return any(challenge in coach_message.lower() for challenge in effective_challenges)
    
    def generate_breakthrough_response(self) -> str:
        """Generate breakthrough response for control freak persona."""
        breakthrough_responses = [
            "Maybe 'good enough' really is good enough sometimes.",
            "I'm starting to think my perfectionism might be holding me back.",
            "What if I shipped something that was 80% perfect instead of waiting for 100%?",
            "I wonder if my team would actually respect me more if I showed some vulnerability.",
            "Perhaps the fear of not being perfect is worse than actually being imperfect."
        ]
        return random.choice(breakthrough_responses)
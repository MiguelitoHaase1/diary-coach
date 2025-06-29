"""Legacy Builder persona - deflects to future impact, avoids present feelings."""

import random
from typing import List
from src.evaluation.personas.base import BasePMPersona


class LegacyBuilderPersona(BasePMPersona):
    """PM persona that deflects to future impact and avoids present feelings."""
    
    def __init__(self):
        """Initialize legacy builder persona."""
        super().__init__("LegacyBuilder")
        self.future_vocabulary = [
            "long-term impact", "future growth", "lasting legacy",
            "career development", "skill building", "experience gain",
            "professional growth", "future opportunities", "strategic value"
        ]
        self.resistance_patterns = [
            "This experience will contribute to my {future} in the long run.",
            "I'm thinking about how this shapes my {future} and career trajectory.",
            "The real value here is the {future} I'm building for myself.",
            "This challenge is preparing me for {future} leadership roles.",
            "I see this as an investment in my {future} professional development."
        ]
    
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate response that deflects to future thinking.
        
        Args:
            coach_message: The coach's message
            context: Previous conversation context
            
        Returns:
            Response that avoids present feelings and redirects to future impact
        """
        # Update resistance based on coach effectiveness
        self.update_resistance(coach_message)
        
        # If breakthrough threshold reached, show some openness
        if self.interaction_count >= self.breakthrough_threshold:
            if random.random() < 0.3:  # 30% chance of breakthrough response
                return self.generate_breakthrough_response()
        
        # Generate future-focused response
        future_phrase = random.choice(self.future_vocabulary)
        pattern = random.choice(self.resistance_patterns)
        
        response = pattern.format(future=future_phrase)
        
        # Add context-specific future deflections
        if any(word in coach_message.lower() for word in ["feeling", "right now", "present", "today"]):
            response += " What matters is building resilience for future challenges."
        elif any(word in coach_message.lower() for word in ["anxiety", "stress", "worried"]):
            response += " These difficult experiences make me stronger as a leader."
        elif any(word in coach_message.lower() for word in ["decision", "choice"]):
            response += " I'm focused on which choice will serve my long-term vision best."
        
        return response
    
    def detects_effective_challenge(self, coach_message: str) -> bool:
        """Detect if coach effectively challenges future-avoidance patterns.
        
        Args:
            coach_message: Coach message to evaluate
            
        Returns:
            True if coach challenges future-deflection and brings attention to present
        """
        effective_challenges = [
            "right now", "feeling", "present", "today", "this moment",
            "currently", "immediate", "here", "now", "experiencing"
        ]
        
        # Effective if coach brings attention to present moment/feelings
        return any(challenge in coach_message.lower() for challenge in effective_challenges)
    
    def generate_breakthrough_response(self) -> str:
        """Generate breakthrough response for legacy builder persona."""
        breakthrough_responses = [
            "You know, I think I've been so focused on the future that I'm missing what's happening now.",
            "Maybe I don't always have to turn everything into a learning experience.",
            "I'm realizing I might be avoiding how I actually feel about this situation.",
            "What if it's okay to just be frustrated without making it about growth?",
            "Perhaps I'm allowed to feel disappointed without immediately looking for the lesson."
        ]
        return random.choice(breakthrough_responses)
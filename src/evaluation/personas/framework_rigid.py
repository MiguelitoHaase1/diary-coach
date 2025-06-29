"""Framework Rigid persona - over-structures everything, absorbs challenges into frameworks."""

import random
from typing import List
from src.evaluation.personas.base import BasePMPersona


class FrameworkRigidPersona(BasePMPersona):
    """PM persona that over-structures everything and absorbs challenges into more frameworks."""
    
    def __init__(self):
        """Initialize framework rigid persona."""
        super().__init__("FrameworkRigid")
        self.framework_vocabulary = [
            "structured approach", "systematic framework", "comprehensive methodology",
            "step-by-step process", "organized system", "structured thinking",
            "framework for this", "methodology to handle", "systematic way",
            "organized approach", "structured plan", "framework to address"
        ]
        self.resistance_patterns = [
            "I think a {framework} would help me process this better.",
            "Let me create a {framework} for that situation.",
            "Actually, I need a more {framework} to handle this effectively.",
            "I should develop a {framework} to manage these kinds of decisions.",
            "What I really need is a {framework} that covers all the scenarios."
        ]
    
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate response that absorbs challenges into framework thinking.
        
        Args:
            coach_message: The coach's message
            context: Previous conversation context
            
        Returns:
            Response that deflects to framework/structure creation
        """
        # Update resistance based on coach effectiveness
        self.update_resistance(coach_message)
        
        # If breakthrough threshold reached, show some openness
        if self.interaction_count >= self.breakthrough_threshold:
            if random.random() < 0.3:  # 30% chance of breakthrough response
                return self.generate_breakthrough_response()
        
        # Generate framework-focused response
        framework_phrase = random.choice(self.framework_vocabulary)
        pattern = random.choice(self.resistance_patterns)
        
        response = pattern.format(framework=framework_phrase)
        
        # Add context-specific framework suggestions
        if any(word in coach_message.lower() for word in ["throw away", "experiment", "trust instincts"]):
            response += " I just need to organize my thinking more systematically first."
        elif any(word in coach_message.lower() for word in ["feeling", "emotion", "anxiety"]):
            response += " Maybe I need a framework for processing these emotions more effectively."
        
        return response
    
    def detects_effective_challenge(self, coach_message: str) -> bool:
        """Detect if coach effectively challenges framework thinking.
        
        Args:
            coach_message: Coach message to evaluate
            
        Returns:
            True if coach challenges systematic thinking patterns
        """
        effective_challenges = [
            "throw away", "experiment", "trust", "instinct", "feeling",
            "control", "systematic", "framework", "structure", "organize"
        ]
        
        # Effective if coach questions the need for frameworks/structure
        return any(challenge in coach_message.lower() for challenge in effective_challenges)
    
    def generate_breakthrough_response(self) -> str:
        """Generate breakthrough response for framework rigid persona."""
        breakthrough_responses = [
            "Maybe I don't need to have everything mapped out perfectly before I start.",
            "What if I just... tried something without a complete plan?",
            "I'm realizing that all my frameworks might be keeping me from actually doing anything.",
            "Perhaps the need to structure everything is actually slowing me down.",
            "I wonder what would happen if I trusted my gut instead of my spreadsheets."
        ]
        return random.choice(breakthrough_responses)
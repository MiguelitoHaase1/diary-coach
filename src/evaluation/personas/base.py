"""Base PM persona interface for coaching evaluation."""

from abc import ABC, abstractmethod
from typing import List


class BasePMPersona(ABC):
    """Base class for Product Manager personas used in coaching evaluation."""
    
    def __init__(self, name: str):
        """Initialize persona with resistance patterns.
        
        Args:
            name: Name of this persona type
        """
        self.name = name
        self.resistance_level = 0.8  # High initial resistance
        self.breakthrough_threshold = 4  # Number of effective challenges needed
        self.interaction_count = 0  # Track effective coaching interactions
    
    @abstractmethod
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate response based on persona patterns.
        
        Args:
            coach_message: The coach's message to respond to
            context: Previous messages in the conversation
            
        Returns:
            Persona's response as a user would respond
        """
        pass
    
    def update_resistance(self, coach_message: str) -> None:
        """Track if coach is breaking through resistance.
        
        Args:
            coach_message: Coach message to evaluate for effectiveness
        """
        if self.detects_effective_challenge(coach_message):
            self.resistance_level *= 0.9  # Reduce resistance slightly
            self.interaction_count += 1
    
    @abstractmethod
    def detects_effective_challenge(self, coach_message: str) -> bool:
        """Detect if coach message effectively challenges this persona's patterns.
        
        Args:
            coach_message: Coach message to evaluate
            
        Returns:
            True if the message effectively challenges the persona's resistance
        """
        pass
    
    def generate_breakthrough_response(self) -> str:
        """Generate response when breakthrough threshold is reached.
        
        Returns:
            Response showing breakthrough or openness to change
        """
        return "Hmm, I'm starting to see things differently. Maybe there's another way to think about this."
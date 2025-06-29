"""Base analyzer interface for coaching behavior evaluation."""

from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class AnalysisScore:
    """Result of behavioral analysis."""
    value: float  # Score from 0.0 to 1.0
    reasoning: str  # Explanation of the score
    analyzer_name: str  # Name of the analyzer that generated this score


class BaseAnalyzer(ABC):
    """Base class for coaching behavior analyzers."""
    
    def __init__(self, name: str):
        """Initialize analyzer with name.
        
        Args:
            name: Name of this analyzer
        """
        self.name = name
    
    @abstractmethod
    async def analyze(self, response: str, context: List[str]) -> AnalysisScore:
        """Analyze coaching response for specific behavioral patterns.
        
        Args:
            response: The coach's response text
            context: Previous messages in the conversation
            
        Returns:
            AnalysisScore with value, reasoning, and analyzer name
        """
        pass
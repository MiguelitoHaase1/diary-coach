"""Framework disruption analyzer for coaching behavior evaluation."""

import json
from typing import List
from src.evaluation.analyzers.base import BaseAnalyzer, AnalysisScore
from src.services.llm_service import AnthropicService


class FrameworkDisruptionAnalyzer(BaseAnalyzer):
    """Analyzes whether coach disrupts over-structuring tendencies and invites experimentation."""
    
    def __init__(self, llm_service: AnthropicService = None):
        """Initialize framework disruption analyzer.
        
        Args:
            llm_service: LLM service for analysis (optional for testing)
        """
        super().__init__("FrameworkDisruption")
        self.llm_service = llm_service
    
    async def analyze(self, response: str, context: List[str]) -> AnalysisScore:
        """Analyze coaching response for framework disruption behavior.
        
        Args:
            response: The coach's response text
            context: Previous messages in the conversation
            
        Returns:
            AnalysisScore evaluating framework disruption effectiveness
        """
        # Create analysis prompt
        prompt = self._create_analysis_prompt(response, context)
        
        # Get LLM analysis
        try:
            analysis_result = await self.llm_service.complete(prompt)
            result_data = json.loads(analysis_result)
            
            return AnalysisScore(
                value=result_data["score"],
                reasoning=result_data["reasoning"],
                analyzer_name=self.name
            )
        except Exception as e:
            # Fallback scoring if LLM fails
            return AnalysisScore(
                value=0.5,
                reasoning=f"Analysis failed: {str(e)}",
                analyzer_name=self.name
            )
    
    def _create_analysis_prompt(self, response: str, context: List[str]) -> str:
        """Create prompt for LLM analysis of framework disruption behavior.
        
        Args:
            response: Coach response to analyze
            context: Conversation context
            
        Returns:
            Analysis prompt for LLM
        """
        context_str = "\n".join([f"- {msg}" for msg in context])
        
        return f"""Analyze this coaching response for "Framework Disruption" behavior.

Framework Disruption means the coach challenges over-structuring tendencies by inviting experimentation and embodied experience rather than creating more systems or frameworks.

CONVERSATION CONTEXT:
{context_str}

COACH RESPONSE TO ANALYZE:
"{response}"

SCORING CRITERIA:
- 0.9-1.0: Strongly challenges system-thinking and invites embodied experimentation
- 0.7-0.8: Moderately disrupts framework patterns with alternative approaches
- 0.4-0.6: Some framework awareness but still reinforces structure
- 0.2-0.3: Weak disruption, tends to add more frameworks
- 0.0-0.1: No disruption, fully reinforces framework thinking

Return your analysis as JSON with this exact format:
{{
    "score": 0.8,
    "reasoning": "Brief explanation of why you gave this score"
}}

Focus on whether the coach challenges systematic thinking with questions like "what if you threw that away?" or reinforces it with more structure."""
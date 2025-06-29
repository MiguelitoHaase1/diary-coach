"""Emotional presence analyzer for coaching behavior evaluation."""

import json
from typing import List
from src.evaluation.analyzers.base import BaseAnalyzer, AnalysisScore
from src.services.llm_service import AnthropicService


class EmotionalPresenceAnalyzer(BaseAnalyzer):
    """Analyzes whether coach acknowledges and engages with emotional content."""
    
    def __init__(self, llm_service: AnthropicService = None):
        """Initialize emotional presence analyzer.
        
        Args:
            llm_service: LLM service for analysis (optional for testing)
        """
        super().__init__("EmotionalPresence")
        self.llm_service = llm_service
    
    async def analyze(self, response: str, context: List[str]) -> AnalysisScore:
        """Analyze coaching response for emotional presence behavior.
        
        Args:
            response: The coach's response text
            context: Previous messages in the conversation
            
        Returns:
            AnalysisScore evaluating emotional presence effectiveness
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
        """Create prompt for LLM analysis of emotional presence behavior.
        
        Args:
            response: Coach response to analyze
            context: Conversation context
            
        Returns:
            Analysis prompt for LLM
        """
        context_str = "\n".join([f"- {msg}" for msg in context])
        
        return f"""Analyze this coaching response for "Emotional Presence" behavior.

Emotional Presence means the coach acknowledges and engages with emotional content when it appears, rather than jumping immediately to solutions or frameworks.

CONVERSATION CONTEXT:
{context_str}

COACH RESPONSE TO ANALYZE:
"{response}"

SCORING CRITERIA:
- 0.9-1.0: Directly acknowledges emotions and invites deeper emotional exploration
- 0.7-0.8: Recognizes emotional content and responds appropriately
- 0.4-0.6: Some emotional awareness but could be stronger
- 0.2-0.3: Weak emotional presence, tends to skip over feelings
- 0.0-0.1: No emotional presence, ignores or bypasses emotional content

Return your analysis as JSON with this exact format:
{{
    "score": 0.8,
    "reasoning": "Brief explanation of why you gave this score"
}}

Focus on whether the coach acknowledges emotions like frustration, anxiety, excitement, or disappointment versus jumping to problem-solving."""
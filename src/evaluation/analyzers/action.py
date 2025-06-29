"""Action orientation analyzer for coaching behavior evaluation."""

import json
from typing import List
from src.evaluation.analyzers.base import BaseAnalyzer, AnalysisScore
from src.services.llm_service import AnthropicService


class ActionOrientationAnalyzer(BaseAnalyzer):
    """Analyzes whether coach drives toward concrete actions rather than abstract discussion."""
    
    def __init__(self, llm_service: AnthropicService = None):
        """Initialize action orientation analyzer.
        
        Args:
            llm_service: LLM service for analysis (optional for testing)
        """
        super().__init__("ActionOrientation")
        self.llm_service = llm_service
    
    async def analyze(self, response: str, context: List[str]) -> AnalysisScore:
        """Analyze coaching response for action orientation behavior.
        
        Args:
            response: The coach's response text
            context: Previous messages in the conversation
            
        Returns:
            AnalysisScore evaluating action orientation effectiveness
        """
        # Create analysis prompt
        prompt = self._create_analysis_prompt(response, context)
        
        # Get LLM analysis
        try:
            analysis_result = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
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
        """Create prompt for LLM analysis of action orientation behavior.
        
        Args:
            response: Coach response to analyze
            context: Conversation context
            
        Returns:
            Analysis prompt for LLM
        """
        context_str = "\n".join([f"- {msg}" for msg in context])
        
        return f"""Analyze this coaching response for "Action Orientation" behavior.

Action Orientation means the coach drives toward concrete actions and commitments rather than staying in abstract discussion or endless exploration.

CONVERSATION CONTEXT:
{context_str}

COACH RESPONSE TO ANALYZE:
"{response}"

SCORING CRITERIA:
- 0.9-1.0: Strongly pushes toward immediate, specific actionable commitments
- 0.7-0.8: Moderately drives toward action with concrete next steps
- 0.4-0.6: Some action focus but could be more direct
- 0.2-0.3: Weak action orientation, stays mostly in exploration
- 0.0-0.1: No action focus, purely abstract or exploratory

Return your analysis as JSON with this exact format:
{{
    "score": 0.8,
    "reasoning": "Brief explanation of why you gave this score"
}}

Focus on whether the coach asks for specific commitments, next steps, or concrete actions versus staying in discussion mode."""
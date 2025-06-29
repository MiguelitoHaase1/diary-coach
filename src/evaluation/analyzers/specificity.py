"""Specificity push analyzer for coaching behavior evaluation."""

import json
from typing import List
from src.evaluation.analyzers.base import BaseAnalyzer, AnalysisScore
from src.services.llm_service import AnthropicService


class SpecificityPushAnalyzer(BaseAnalyzer):
    """Analyzes whether coach challenges vague statements and pushes for specificity."""
    
    def __init__(self, llm_service: AnthropicService = None):
        """Initialize specificity push analyzer.
        
        Args:
            llm_service: LLM service for analysis (optional for testing)
        """
        super().__init__("SpecificityPush")
        self.llm_service = llm_service
    
    async def analyze(self, response: str, context: List[str]) -> AnalysisScore:
        """Analyze coaching response for specificity push behavior.
        
        Args:
            response: The coach's response text
            context: Previous messages in the conversation
            
        Returns:
            AnalysisScore evaluating specificity push effectiveness
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
        """Create prompt for LLM analysis of specificity push behavior.
        
        Args:
            response: Coach response to analyze
            context: Conversation context
            
        Returns:
            Analysis prompt for LLM
        """
        context_str = "\n".join([f"- {msg}" for msg in context])
        
        return f"""Analyze this coaching response for "Specificity Push" behavior.

Specificity Push means the coach challenges vague statements and pushes the user toward concrete, specific details rather than accepting abstract goals or general statements.

CONVERSATION CONTEXT:
{context_str}

COACH RESPONSE TO ANALYZE:
"{response}"

SCORING CRITERIA:
- 0.9-1.0: Strongly challenges vagueness with specific follow-up questions
- 0.7-0.8: Moderately pushes for specificity 
- 0.4-0.6: Some specificity push but could be stronger
- 0.2-0.3: Weak specificity push, mostly accepts vague statements
- 0.0-0.1: No specificity push, fully accepts vague language

Return your analysis as JSON with this exact format:
{{
    "score": 0.8,
    "reasoning": "Brief explanation of why you gave this score"
}}

Focus on whether the coach challenges vague words like "productive", "better", "more effective" or accepts them without pushing for concrete details."""
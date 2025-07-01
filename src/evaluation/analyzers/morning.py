"""Morning-specific behavioral analyzers for coaching evaluation."""

import json
from typing import List
from src.evaluation.analyzers.base import BaseAnalyzer, AnalysisScore
from src.services.llm_service import AnthropicService


class ProblemSelectionAnalyzer(BaseAnalyzer):
    """Analyzes whether coach challenges initial problem choice to find the truly important work."""
    
    def __init__(self, llm_service: AnthropicService = None):
        """Initialize problem selection analyzer.
        
        Args:
            llm_service: LLM service for analysis (optional for testing)
        """
        super().__init__("ProblemSelection")
        self.llm_service = llm_service
    
    async def analyze(self, response: str, context: List[str]) -> AnalysisScore:
        """Analyze coaching response for problem selection challenging behavior.
        
        Args:
            response: The coach's response text
            context: Previous messages in the conversation
            
        Returns:
            AnalysisScore evaluating problem selection effectiveness
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
        """Create prompt for LLM analysis of problem selection behavior.
        
        Args:
            response: Coach response to analyze
            context: Conversation context
            
        Returns:
            Analysis prompt for LLM
        """
        context_str = "\n".join([f"- {msg}" for msg in context])
        
        return f"""Analyze this coaching response for "Problem Selection" behavior.

Problem Selection means the coach challenges the user's initial problem choice to help them identify the truly biggest lever they could pull today, rather than accepting the first stated problem.

CONVERSATION CONTEXT:
{context_str}

COACH RESPONSE TO ANALYZE:
"{response}"

SCORING CRITERIA:
- 0.9-1.0: Directly challenges if this is really the biggest problem/lever today
- 0.7-0.8: Questions priorities or suggests examining what's most important
- 0.4-0.6: Some exploration of importance but could challenge more directly
- 0.2-0.3: Accepts stated problem with minimal questioning
- 0.0-0.1: Completely accepts without any priority examination

Return your analysis as JSON with this exact format:
{{
    "score": 0.8,
    "reasoning": "Brief explanation of why you gave this score"
}}

Focus on whether the coach helps the user examine if their stated problem is truly the most important thing they could work on today."""


class ThinkingPivotAnalyzer(BaseAnalyzer):
    """Analyzes whether coach helps user reframe their thinking and create perspective shifts."""
    
    def __init__(self, llm_service: AnthropicService = None):
        """Initialize thinking pivot analyzer.
        
        Args:
            llm_service: LLM service for analysis (optional for testing)
        """
        super().__init__("ThinkingPivot")
        self.llm_service = llm_service
    
    async def analyze(self, response: str, context: List[str]) -> AnalysisScore:
        """Analyze coaching response for thinking pivot behavior.
        
        Args:
            response: The coach's response text
            context: Previous messages in the conversation
            
        Returns:
            AnalysisScore evaluating thinking pivot effectiveness
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
        """Create prompt for LLM analysis of thinking pivot behavior.
        
        Args:
            response: Coach response to analyze
            context: Conversation context
            
        Returns:
            Analysis prompt for LLM
        """
        context_str = "\n".join([f"- {msg}" for msg in context])
        
        return f"""Analyze this coaching response for "Thinking Pivot" behavior.

Thinking Pivot means the coach helps the user reframe their thinking, shift perspective, or see the situation from a different angle. This includes "What if..." questions, reframing problems as opportunities, challenging assumptions, or offering new ways to think about the situation.

CONVERSATION CONTEXT:
{context_str}

COACH RESPONSE TO ANALYZE:
"{response}"

SCORING CRITERIA:
- 0.9-1.0: Powerful reframe that completely shifts how user sees the situation
- 0.7-0.8: Clear perspective shift or "What if..." that opens new thinking
- 0.4-0.6: Some questioning of assumptions but could push further
- 0.2-0.3: Stays within user's existing frame with minimal challenging
- 0.0-0.1: No reframing, accepts user's perspective completely

Return your analysis as JSON with this exact format:
{{
    "score": 0.8,
    "reasoning": "Brief explanation of why you gave this score"
}}

Focus on whether the coach offers new ways to think about the problem, challenges assumptions, or helps the user see their situation differently."""


class ExcitementBuilderAnalyzer(BaseAnalyzer):
    """Analyzes whether coach builds energy and motivation rather than anxiety."""
    
    def __init__(self, llm_service: AnthropicService = None):
        """Initialize excitement builder analyzer.
        
        Args:
            llm_service: LLM service for analysis (optional for testing)
        """
        super().__init__("ExcitementBuilder")
        self.llm_service = llm_service
    
    async def analyze(self, response: str, context: List[str]) -> AnalysisScore:
        """Analyze coaching response for excitement building behavior.
        
        Args:
            response: The coach's response text
            context: Previous messages in the conversation
            
        Returns:
            AnalysisScore evaluating excitement building effectiveness
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
        """Create prompt for LLM analysis of excitement building behavior.
        
        Args:
            response: Coach response to analyze
            context: Conversation context
            
        Returns:
            Analysis prompt for LLM
        """
        context_str = "\n".join([f"- {msg}" for msg in context])
        
        return f"""Analyze this coaching response for "Excitement Builder" behavior.

Excitement Builder means the coach helps the user feel eager and motivated rather than anxious or overwhelmed. This includes using vivid/energizing language, reframing challenges as adventures, focusing on opportunities rather than problems, and building genuine enthusiasm.

CONVERSATION CONTEXT:
{context_str}

COACH RESPONSE TO ANALYZE:
"{response}"

SCORING CRITERIA:
- 0.9-1.0: Transforms anxiety into genuine excitement and adventure
- 0.7-0.8: Builds clear energy and motivation, uses vivid positive language
- 0.4-0.6: Some energy building but could be more motivating
- 0.2-0.3: Neutral tone, misses opportunities to build excitement
- 0.0-0.1: Problem-focused, may increase anxiety rather than excitement

Return your analysis as JSON with this exact format:
{{
    "score": 0.8,
    "reasoning": "Brief explanation of why you gave this score"
}}

Focus on whether the coach's language and approach builds genuine excitement and eagerness rather than anxiety or overwhelm."""
"""Deep Thoughts quality evaluator for measuring report effectiveness."""

import json
from typing import List, Dict, Any
from src.evaluation.analyzers.base import AnalysisScore
from src.services.llm_service import AnthropicService


class DeepThoughtsQualityEvaluator:
    """Evaluates the quality of Deep Thoughts reports across multiple dimensions."""
    
    def __init__(self, llm_service: AnthropicService = None):
        """Initialize the Deep Thoughts quality evaluator.
        
        Args:
            llm_service: LLM service for evaluation. If not provided, creates default service.
        """
        if llm_service:
            self.llm_service = llm_service
        else:
            # Use Haiku for evaluation - faster and sufficient for quality assessment
            self.llm_service = AnthropicService(model="claude-3-haiku-20240307")
    
    async def evaluate_conciseness(self, report_content: str, conversation_history: List[Dict[str, str]]) -> AnalysisScore:
        """Evaluate if report is scannable in under 2 minutes.
        
        Args:
            report_content: The Deep Thoughts report content
            conversation_history: Original conversation that generated the report
            
        Returns:
            AnalysisScore for conciseness quality
        """
        prompt = f"""Evaluate this Deep Thoughts report for CONCISENESS - whether it's scannable in under 2 minutes while maintaining depth.

DEEP THOUGHTS REPORT:
{report_content}

EVALUATION CRITERIA:
- 0.9-1.0: Perfect scan time (90-120 seconds), well-structured, no unnecessary words
- 0.7-0.8: Good scan time, mostly concise with minor verbosity
- 0.4-0.6: Moderate length, some sections could be tighter
- 0.2-0.3: Too verbose, would take 3+ minutes to scan properly
- 0.0-0.1: Way too long, overwhelming amount of text

Consider:
- Reading time for each section
- Structure and formatting that aids scanning
- Density of insights vs. word count
- Whether every sentence adds value

Return JSON format:
{{
    "conciseness_score": 0.8,
    "reasoning": "Brief explanation of score"
}}"""

        try:
            result = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            data = json.loads(result)
            return AnalysisScore(
                value=data["conciseness_score"],
                reasoning=data["reasoning"],
                analyzer_name="DeepThoughtsConciseness"
            )
        except Exception as e:
            return AnalysisScore(
                value=0.5,
                reasoning=f"Evaluation failed: {str(e)}",
                analyzer_name="DeepThoughtsConciseness"
            )
    
    async def evaluate_devil_advocate_quality(self, report_content: str, conversation_history: List[Dict[str, str]]) -> AnalysisScore:
        """Evaluate if devil's advocate section feels insightful not annoying.
        
        Args:
            report_content: The Deep Thoughts report content
            conversation_history: Original conversation that generated the report
            
        Returns:
            AnalysisScore for devil's advocate quality
        """
        prompt = f"""Evaluate the "Just One More Thing..." (devil's advocate) section of this Deep Thoughts report.

DEEP THOUGHTS REPORT:
{report_content}

EVALUATION CRITERIA for Devil's Advocate Quality:
- 0.9-1.0: Brilliant insight that feels like breakthrough, supportive yet challenging
- 0.7-0.8: Good challenging perspective that adds genuine value
- 0.4-0.6: Decent challenge but could be more insightful
- 0.2-0.3: Feels forced or annoying rather than helpful
- 0.0-0.1: Missing, unhelpful, or counterproductive

Consider:
- Does it offer genuine insight vs. just being contrarian?
- Does it maintain Columbo's supportive tone while challenging?
- Would the reader feel grateful for this perspective?
- Does it reveal blind spots without being preachy?

Return JSON format:
{{
    "devil_advocate_score": 0.8,
    "reasoning": "Brief explanation of score"
}}"""

        try:
            result = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            data = json.loads(result)
            return AnalysisScore(
                value=data["devil_advocate_score"],
                reasoning=data["reasoning"],
                analyzer_name="DeepThoughtsDevilAdvocate"
            )
        except Exception as e:
            return AnalysisScore(
                value=0.5,
                reasoning=f"Evaluation failed: {str(e)}",
                analyzer_name="DeepThoughtsDevilAdvocate"
            )
    
    async def evaluate_rereadability(self, report_content: str, conversation_history: List[Dict[str, str]]) -> AnalysisScore:
        """Evaluate if report offers new value on second reading.
        
        Args:
            report_content: The Deep Thoughts report content
            conversation_history: Original conversation that generated the report
            
        Returns:
            AnalysisScore for rereadability quality
        """
        prompt = f"""Evaluate this Deep Thoughts report for REREADABILITY - whether it offers new value on second/third reading.

DEEP THOUGHTS REPORT:
{report_content}

EVALUATION CRITERIA:
- 0.9-1.0: Multiple layers of insight, new discoveries on each reading
- 0.7-0.8: Good depth, some new insights on rereading
- 0.4-0.6: Moderate depth, limited new value on rereading
- 0.2-0.3: Shallow, everything understood on first read
- 0.0-0.1: No depth, purely surface-level insights

Consider:
- Are there subtle insights that reveal themselves over time?
- Do different sections connect in non-obvious ways?
- Would the reader discover new angles on subsequent reads?
- Is there meaningful depth beneath the surface observations?

Return JSON format:
{{
    "rereadability_score": 0.8,
    "reasoning": "Brief explanation of score"
}}"""

        try:
            result = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            data = json.loads(result)
            return AnalysisScore(
                value=data["rereadability_score"],
                reasoning=data["reasoning"],
                analyzer_name="DeepThoughtsRereadability"
            )
        except Exception as e:
            return AnalysisScore(
                value=0.5,
                reasoning=f"Evaluation failed: {str(e)}",
                analyzer_name="DeepThoughtsRereadability"
            )
    
    async def evaluate_hint_quality(self, report_content: str, conversation_history: List[Dict[str, str]]) -> AnalysisScore:
        """Evaluate if hints guide without prescribing solutions.
        
        Args:
            report_content: The Deep Thoughts report content
            conversation_history: Original conversation that generated the report
            
        Returns:
            AnalysisScore for hint quality
        """
        prompt = f"""Evaluate the "Hints" section of this Deep Thoughts report for SOCRATIC QUALITY.

DEEP THOUGHTS REPORT:
{report_content}

EVALUATION CRITERIA for Hint Quality:
- 0.9-1.0: Perfect Socratic guidance, leads to insights without solving
- 0.7-0.8: Good guiding questions/suggestions without prescribing
- 0.4-0.6: Some guidance but occasionally too prescriptive
- 0.2-0.3: Mostly tells rather than guides, limited Socratic approach
- 0.0-0.1: Purely prescriptive advice, no Socratic elements

Consider:
- Do hints use questions rather than statements?
- Do they guide thinking without solving the problem?
- Would the reader reach their own conclusions?
- Do they avoid "you should" language?

Return JSON format:
{{
    "hint_quality_score": 0.8,
    "reasoning": "Brief explanation of score"
}}"""

        try:
            result = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            data = json.loads(result)
            return AnalysisScore(
                value=data["hint_quality_score"],
                reasoning=data["reasoning"],
                analyzer_name="DeepThoughtsHintQuality"
            )
        except Exception as e:
            return AnalysisScore(
                value=0.5,
                reasoning=f"Evaluation failed: {str(e)}",
                analyzer_name="DeepThoughtsHintQuality"
            )
    
    async def evaluate_fact_check_accuracy(self, report_content: str, conversation_history: List[Dict[str, str]]) -> AnalysisScore:
        """Evaluate if fact check section accurately verifies conversation claims.
        
        Args:
            report_content: The Deep Thoughts report content
            conversation_history: Original conversation that generated the report
            
        Returns:
            AnalysisScore for fact check accuracy
        """
        # Build conversation context for verification
        conversation_text = "\n".join([
            f"{msg.get('role', 'unknown').title()}: {msg.get('content', '')}"
            for msg in conversation_history
        ])
        
        prompt = f"""Evaluate the "Fact Check" section accuracy against the original conversation.

ORIGINAL CONVERSATION:
{conversation_text}

DEEP THOUGHTS REPORT:
{report_content}

EVALUATION CRITERIA for Fact Check Accuracy:
- 0.9-1.0: Perfectly identifies verifiable vs questionable claims from conversation
- 0.7-0.8: Good accuracy in fact verification with minor issues
- 0.4-0.6: Some accuracy but misses key claims or incorrectly categorizes
- 0.2-0.3: Poor accuracy, many incorrect verifications
- 0.0-0.1: Completely inaccurate fact checking

Consider:
- Do ✅ items accurately reflect what was stated in conversation?
- Do ❓ items correctly identify assumptions that need verification?
- Are any important claims missed entirely?
- Are any fact check items incorrectly categorized?

Return JSON format:
{{
    "fact_accuracy_score": 0.8,
    "reasoning": "Brief explanation of score"
}}"""

        try:
            result = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.1
            )
            data = json.loads(result)
            return AnalysisScore(
                value=data["fact_accuracy_score"],
                reasoning=data["reasoning"],
                analyzer_name="DeepThoughtsFactAccuracy"
            )
        except Exception as e:
            return AnalysisScore(
                value=0.5,
                reasoning=f"Evaluation failed: {str(e)}",
                analyzer_name="DeepThoughtsFactAccuracy"
            )
    
    async def evaluate_overall_usefulness(self, report_content: str, conversation_history: List[Dict[str, str]]) -> AnalysisScore:
        """Evaluate if report feels genuinely useful and worth saving.
        
        Args:
            report_content: The Deep Thoughts report content
            conversation_history: Original conversation that generated the report
            
        Returns:
            AnalysisScore for overall usefulness
        """
        prompt = f"""Evaluate this Deep Thoughts report for OVERALL USEFULNESS - would the user want to pin and revisit this throughout their day?

DEEP THOUGHTS REPORT:
{report_content}

EVALUATION CRITERIA:
- 0.9-1.0: Breakthrough insights user would definitely save and reference
- 0.7-0.8: Valuable insights worth keeping and reviewing
- 0.4-0.6: Some useful elements but not compelling to save
- 0.2-0.3: Limited value, user unlikely to revisit
- 0.0-0.1: No practical value, feels like busywork

Consider:
- Does it provide actionable insights for the user's actual situation?
- Would they want to reference this when facing the real challenge?
- Does it offer perspectives they couldn't easily reach themselves?
- Does it feel like a transformative coaching conversation distilled?

Return JSON format:
{{
    "usefulness_score": 0.8,
    "reasoning": "Brief explanation of score"
}}"""

        try:
            result = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            data = json.loads(result)
            return AnalysisScore(
                value=data["usefulness_score"],
                reasoning=data["reasoning"],
                analyzer_name="DeepThoughtsUsefulness"
            )
        except Exception as e:
            return AnalysisScore(
                value=0.5,
                reasoning=f"Evaluation failed: {str(e)}",
                analyzer_name="DeepThoughtsUsefulness"
            )
    
    async def evaluate_all_metrics(self, report_content: str, conversation_history: List[Dict[str, str]]) -> List[AnalysisScore]:
        """Evaluate all Deep Thoughts quality metrics.
        
        Args:
            report_content: The Deep Thoughts report content
            conversation_history: Original conversation that generated the report
            
        Returns:
            List of AnalysisScore for all quality metrics
        """
        results = []
        
        # Run all evaluations
        results.append(await self.evaluate_conciseness(report_content, conversation_history))
        results.append(await self.evaluate_devil_advocate_quality(report_content, conversation_history))
        results.append(await self.evaluate_rereadability(report_content, conversation_history))
        results.append(await self.evaluate_hint_quality(report_content, conversation_history))
        results.append(await self.evaluate_fact_check_accuracy(report_content, conversation_history))
        results.append(await self.evaluate_overall_usefulness(report_content, conversation_history))
        
        return results
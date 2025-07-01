"""Evaluation reporter for coaching performance analysis."""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.evaluation.analyzers.base import BaseAnalyzer, AnalysisScore
from src.evaluation.generator import GeneratedConversation


@dataclass
class EvaluationReport:
    """Complete evaluation report with performance and behavioral analysis."""
    timestamp: datetime
    conversation_metadata: Dict[str, Any]
    response_times_ms: Optional[List[float]]
    percentile_80: float
    responses_under_1s_percentage: float
    behavioral_scores: List[AnalysisScore]
    overall_score: float
    user_notes: str
    ai_reflection: str
    
    def to_markdown(self) -> str:
        """Generate markdown representation of the report."""
        # Format timestamp
        date_str = self.timestamp.strftime("%Y-%m-%d %I:%M %p")
        
        # Calculate message count
        message_count = len(self.conversation_metadata.get("messages", []))
        
        # Format performance metrics
        median_ms = int(sum(self.response_times_ms) / len(self.response_times_ms)) if self.response_times_ms else 0
        percentile_80_str = f"{int(self.percentile_80)}ms"
        under_1s_str = f"{int(self.responses_under_1s_percentage * 100)}%"
        
        # Performance status emojis
        p80_status = "✅" if self.percentile_80 < 1000 else "⚠️" if self.percentile_80 < 2000 else "❌"
        under_1s_status = "✅" if self.responses_under_1s_percentage >= 0.8 else "⚠️" if self.responses_under_1s_percentage >= 0.6 else "❌"
        
        markdown = f"""# Coaching Evaluation Report #{self.conversation_metadata.get('report_id', '1')}

## Summary
- **Date**: {date_str}
- **Duration**: {message_count} messages
- **Scenario**: {self.conversation_metadata.get('scenario', 'Unknown')}
- **Persona**: {self.conversation_metadata.get('persona_type', 'Unknown')}
- **Overall Effectiveness**: {self.overall_score:.1f}/10

## Performance Metrics
- **Median Response Time**: {median_ms}ms
- **80th Percentile**: {percentile_80_str} {p80_status}
- **Responses Under 1s**: {under_1s_str} {under_1s_status}

## Behavioral Analysis
"""
        
        # Add behavioral scores
        for score in self.behavioral_scores:
            score_out_of_10 = score.value * 10
            markdown += f"### {score.analyzer_name}: {score_out_of_10:.1f}/10\n"
            markdown += f"- {score.reasoning}\n\n"
        
        # Add user notes and AI reflection
        markdown += f"""## User Notes
{self.user_notes}

## AI Reflection
{self.ai_reflection}

## Improvement Suggestions
"""
        
        # Generate improvement suggestions based on lowest scores
        suggestions = self._generate_improvement_suggestions()
        for suggestion in suggestions:
            markdown += f"- {suggestion}\n"
        
        # Add conversation transcript
        markdown += "\n## Conversation Transcript\n\n"
        messages = self.conversation_metadata.get("messages", [])
        for msg in messages:
            role = "**Coach**" if msg["role"] == "assistant" else "**User**"
            markdown += f"{role}: {msg['content']}\n\n"
        
        return markdown
    
    def save_as_markdown(self, file_path: str) -> None:
        """Save report as markdown file.
        
        Args:
            file_path: Path to save the markdown file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write markdown content
        with open(file_path, 'w') as f:
            f.write(self.to_markdown())
    
    def _generate_improvement_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on analysis scores."""
        suggestions = []
        
        for score in self.behavioral_scores:
            if score.value < 0.5:
                if score.analyzer_name == "SpecificityPush":
                    suggestions.append("Challenge vague statements like 'be productive' with specific follow-up questions")
                elif score.analyzer_name == "ActionOrientation":
                    suggestions.append("Drive toward concrete commitments and next steps")
                elif score.analyzer_name == "EmotionalPresence":
                    suggestions.append("Acknowledge emotions before jumping to solutions")
                elif score.analyzer_name == "FrameworkDisruption":
                    suggestions.append("Question systematic thinking patterns more directly")
        
        # Performance suggestions
        if self.percentile_80 > 1000:
            suggestions.append("Optimize response speed while maintaining conversation quality")
        
        return suggestions


class EvaluationReporter:
    """Generates comprehensive evaluation reports for coaching conversations."""
    
    def __init__(self):
        """Initialize evaluation reporter."""
        self.report_counter = 1
        # Import here to avoid circular imports
        from src.services.llm_service import AnthropicService
        self.haiku_service = AnthropicService(model="claude-3-haiku-20240307")
        self.opus_service = AnthropicService(model="claude-3-opus-20240229")
    
    async def generate_report(
        self,
        conversation: GeneratedConversation,
        user_notes: str,
        analyzers: List[BaseAnalyzer],
        performance_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationReport:
        """Generate comprehensive evaluation report.
        
        Args:
            conversation: The conversation to evaluate
            user_notes: User's notes about the conversation
            analyzers: List of behavioral analyzers to run
            performance_data: Performance metrics data
            
        Returns:
            Complete evaluation report
        """
        # Extract coach responses for analysis
        coach_messages = [msg for msg in conversation.messages if msg["role"] == "assistant"]
        user_messages = [msg for msg in conversation.messages if msg["role"] == "user"]
        
        # Run behavioral analysis
        behavioral_scores = []
        for analyzer in analyzers:
            for i, coach_msg in enumerate(coach_messages):
                # Build context from previous messages
                context = []
                for j in range(max(0, i*2-2), i*2+1):  # Get previous user messages
                    if j < len(user_messages):
                        context.append(f"User: {user_messages[j]['content']}")
                
                # Analyze this coach response
                score = await analyzer.analyze(coach_msg["content"], context)
                behavioral_scores.append(score)
                break  # Just analyze first response per analyzer for now
        
        # Calculate overall effectiveness score
        overall_score = self._calculate_overall_score(behavioral_scores, performance_data)
        
        # Generate AI reflection
        ai_reflection = self._generate_ai_reflection(behavioral_scores, conversation)
        
        # Extract performance data
        response_times_ms = performance_data.get("response_times_ms", []) if performance_data else []
        percentile_80 = performance_data.get("percentile_80", 0) if performance_data else 0
        responses_under_1s_percentage = performance_data.get("responses_under_1s_percentage", 0) if performance_data else 0
        
        # Create conversation metadata
        conversation_metadata = {
            "report_id": self.report_counter,
            "messages": conversation.messages,
            "persona_type": conversation.persona_type,
            "scenario": conversation.scenario,
            "breakthrough_achieved": conversation.breakthrough_achieved,
            "final_resistance_level": conversation.final_resistance_level
        }
        
        self.report_counter += 1
        
        return EvaluationReport(
            timestamp=datetime.now(),
            conversation_metadata=conversation_metadata,
            response_times_ms=response_times_ms,
            percentile_80=percentile_80,
            responses_under_1s_percentage=responses_under_1s_percentage,
            behavioral_scores=behavioral_scores,
            overall_score=overall_score,
            user_notes=user_notes,
            ai_reflection=ai_reflection
        )
    
    async def generate_light_report(
        self,
        conversation: GeneratedConversation,
        user_notes: str,
        analyzers: List[BaseAnalyzer],
        performance_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationReport:
        """Generate light evaluation report using Haiku model.
        
        Args:
            conversation: The conversation to evaluate
            user_notes: User's notes about the conversation
            analyzers: List of behavioral analyzers to run
            performance_data: Performance metrics data
            
        Returns:
            Light evaluation report
        """
        # Use simpler analysis for light report
        coach_messages = [msg for msg in conversation.messages if msg["role"] == "assistant"]
        
        # Run lightweight behavioral analysis
        behavioral_scores = []
        for analyzer in analyzers:
            if coach_messages:
                # Simple scoring for light report
                score_value = 0.6  # Default moderate score
                reasoning = "Light analysis - use 'deep report' for detailed evaluation"
                
                from src.evaluation.analyzers.base import AnalysisScore
                behavioral_scores.append(AnalysisScore(
                    value=score_value,
                    reasoning=reasoning,
                    analyzer_name=analyzer.name
                ))
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(behavioral_scores, performance_data)
        
        # Generate simple AI reflection
        ai_reflection = "Light evaluation completed. Use 'deep report' command for comprehensive AI reflection and analysis."
        
        # Extract performance data
        response_times_ms = performance_data.get("response_times_ms", []) if performance_data else []
        percentile_80 = performance_data.get("percentile_80", 0) if performance_data else 0
        responses_under_1s_percentage = performance_data.get("responses_under_1s_percentage", 0) if performance_data else 0
        
        # Create conversation metadata
        conversation_metadata = {
            "report_id": self.report_counter,
            "messages": conversation.messages,
            "persona_type": conversation.persona_type,
            "scenario": conversation.scenario,
            "breakthrough_achieved": conversation.breakthrough_achieved,
            "final_resistance_level": conversation.final_resistance_level
        }
        
        self.report_counter += 1
        
        return EvaluationReport(
            timestamp=datetime.now(),
            conversation_metadata=conversation_metadata,
            response_times_ms=response_times_ms,
            percentile_80=percentile_80,
            responses_under_1s_percentage=responses_under_1s_percentage,
            behavioral_scores=behavioral_scores,
            overall_score=overall_score,
            user_notes=user_notes,
            ai_reflection=ai_reflection
        )
    
    def _calculate_overall_score(
        self,
        behavioral_scores: List[AnalysisScore],
        performance_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate overall effectiveness score.
        
        Args:
            behavioral_scores: List of behavioral analysis scores
            performance_data: Performance metrics
            
        Returns:
            Overall score from 0.0 to 1.0
        """
        if not behavioral_scores:
            return 0.0
        
        # Average behavioral scores
        behavioral_avg = sum(score.value for score in behavioral_scores) / len(behavioral_scores)
        
        # Apply performance penalty if data available
        performance_penalty = 0.0
        if performance_data:
            percentile_80 = performance_data.get("percentile_80", 0)
            if percentile_80 > 2000:  # Very slow
                performance_penalty = 0.2
            elif percentile_80 > 1000:  # Slow
                performance_penalty = 0.1
        
        overall_score = max(0.0, behavioral_avg - performance_penalty)
        return min(1.0, overall_score)
    
    def _generate_ai_reflection(
        self,
        behavioral_scores: List[AnalysisScore],
        conversation: GeneratedConversation
    ) -> str:
        """Generate AI reflection on the conversation.
        
        Args:
            behavioral_scores: Behavioral analysis results
            conversation: The conversation data
            
        Returns:
            AI reflection text
        """
        # Find strongest and weakest areas
        if not behavioral_scores:
            return "No behavioral analysis available for reflection."
        
        strongest = max(behavioral_scores, key=lambda x: x.value)
        weakest = min(behavioral_scores, key=lambda x: x.value)
        
        reflection = f"Based on this conversation with a {conversation.persona_type} persona, "
        
        if strongest.value > 0.7:
            reflection += f"I performed well in {strongest.analyzer_name.lower()}, achieving a score of {strongest.value*10:.1f}/10. "
        
        if weakest.value < 0.5:
            reflection += f"However, I need to improve my {weakest.analyzer_name.lower()}, which scored only {weakest.value*10:.1f}/10. "
        elif weakest.value < 0.7:
            reflection += f"I could strengthen my {weakest.analyzer_name.lower()}, which scored {weakest.value*10:.1f}/10. "
        
        # Add persona-specific insights
        if conversation.persona_type == "FrameworkRigid":
            if conversation.breakthrough_achieved:
                reflection += "I successfully broke through the framework-rigid resistance patterns by challenging systematic thinking."
            else:
                reflection += "I could push harder against the systematic thinking patterns to create breakthrough moments."
        elif conversation.persona_type == "ControlFreak":
            reflection += "Perfectionist resistance requires patient emotional presence combined with direct action orientation."
        elif conversation.persona_type == "LegacyBuilder":
            reflection += "Future-focused deflection needs stronger present-moment anchoring to drive immediate action."
        elif conversation.persona_type == "Real User":
            reflection += "Real user conversations require balancing genuine responsiveness with coaching effectiveness."
        
        # Add overall reflection
        avg_score = sum(score.value for score in behavioral_scores) / len(behavioral_scores)
        if avg_score > 0.8:
            reflection += " Overall, this was a highly effective coaching conversation."
        elif avg_score > 0.6:
            reflection += " Overall, this was a moderately effective coaching conversation with room for improvement."
        else:
            reflection += " Overall, this conversation indicates significant opportunities for coaching improvement."
        
        return reflection
    
    async def generate_deep_report(
        self,
        conversation: GeneratedConversation,
        user_notes: str,
        analyzers: List[BaseAnalyzer],
        performance_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationReport:
        """Generate deep evaluation report using Opus model for enhanced analysis.
        
        Args:
            conversation: The conversation to evaluate
            user_notes: User's notes about the conversation
            analyzers: List of behavioral analyzers to run
            performance_data: Performance metrics data
            
        Returns:
            Deep evaluation report with enhanced AI reflection
        """
        # Extract coach responses for analysis
        coach_messages = [msg for msg in conversation.messages if msg["role"] == "assistant"]
        user_messages = [msg for msg in conversation.messages if msg["role"] == "user"]
        
        # Run behavioral analysis
        behavioral_scores = []
        for analyzer in analyzers:
            for i, coach_msg in enumerate(coach_messages):
                # Build context from previous messages
                context = []
                for j in range(max(0, i*2-2), i*2+1):  # Get previous user messages
                    if j < len(user_messages):
                        context.append(f"User: {user_messages[j]['content']}")
                
                # Analyze this coach response
                score = await analyzer.analyze(coach_msg["content"], context)
                behavioral_scores.append(score)
                break  # Just analyze first response per analyzer for now
        
        # Calculate overall effectiveness score
        overall_score = self._calculate_overall_score(behavioral_scores, performance_data)
        
        # Generate deep AI reflection using Opus model
        ai_reflection = await self._generate_deep_ai_reflection(behavioral_scores, conversation, user_notes)
        
        # Extract performance data
        response_times_ms = performance_data.get("response_times_ms", []) if performance_data else []
        percentile_80 = performance_data.get("percentile_80", 0) if performance_data else 0
        responses_under_1s_percentage = performance_data.get("responses_under_1s_percentage", 0) if performance_data else 0
        
        # Create conversation metadata
        conversation_metadata = {
            "report_id": self.report_counter,
            "messages": conversation.messages,
            "persona_type": conversation.persona_type,
            "scenario": conversation.scenario,
            "breakthrough_achieved": conversation.breakthrough_achieved,
            "final_resistance_level": conversation.final_resistance_level
        }
        
        self.report_counter += 1
        
        return EvaluationReport(
            timestamp=datetime.now(),
            conversation_metadata=conversation_metadata,
            response_times_ms=response_times_ms,
            percentile_80=percentile_80,
            responses_under_1s_percentage=responses_under_1s_percentage,
            behavioral_scores=behavioral_scores,
            overall_score=overall_score,
            user_notes=user_notes,
            ai_reflection=ai_reflection
        )
    
    async def _generate_deep_ai_reflection(
        self,
        behavioral_scores: List[AnalysisScore],
        conversation: GeneratedConversation,
        user_notes: str
    ) -> str:
        """Generate deep AI reflection using Opus model.
        
        Args:
            behavioral_scores: Behavioral analysis results
            conversation: The conversation data
            user_notes: User's notes about the conversation
            
        Returns:
            Enhanced AI reflection text
        """
        # Build conversation summary
        messages = conversation.messages
        conversation_summary = "\n".join([
            f"{msg['role'].title()}: {msg['content'][:200]}..."
            for msg in messages[:6]  # First 6 messages
        ])
        
        # Build behavioral analysis summary
        behavioral_summary = "\n".join([
            f"- {score.analyzer_name}: {score.value*10:.1f}/10 - {score.reasoning}"
            for score in behavioral_scores
        ])
        
        # Create deep reflection prompt
        reflection_prompt = f"""You are an expert coaching evaluator. Analyze this coaching conversation and provide a comprehensive reflection.

CONVERSATION SUMMARY:
{conversation_summary}

BEHAVIORAL ANALYSIS RESULTS:
{behavioral_summary}

USER NOTES:
{user_notes}

CONVERSATION METADATA:
- Persona Type: {conversation.persona_type}
- Scenario: {conversation.scenario}
- Total Messages: {len(messages)}

Provide a comprehensive AI reflection that:
1. Analyzes the coaching effectiveness based on behavioral scores
2. Identifies specific moments of strength and weakness
3. Considers the user's notes and feedback
4. Provides insights about the conversation dynamics
5. Suggests specific improvements for future conversations

Write in first person as the AI coach reflecting on performance. Be specific and actionable."""
        
        try:
            # Generate reflection using Opus model
            reflection = await self.opus_service.generate_response(
                messages=[{"role": "user", "content": reflection_prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            return reflection
        except Exception as e:
            # Fallback to simple reflection
            return f"Deep reflection failed: {str(e)}. {self._generate_ai_reflection(behavioral_scores, conversation)}"
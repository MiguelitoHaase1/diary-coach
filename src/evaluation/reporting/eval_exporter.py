"""Evaluation exporter for creating markdown reports of coaching performance."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from src.evaluation.reporting.reporter import EvaluationReport


class EvaluationExporter:
    """Exports evaluation reports to markdown format for easy scanning."""
    
    def __init__(self):
        """Initialize the evaluation exporter."""
        pass
    
    def _get_output_path(self, timestamp: Optional[datetime] = None) -> Path:
        """Get the output file path for evaluation report.
        
        Args:
            timestamp: Optional timestamp. If not provided, uses current time.
            
        Returns:
            Path object for the output file
        """
        if not timestamp:
            timestamp = datetime.now()
            
        # Format: Eval_YYYYMMDD_HHMM.md (no seconds)
        filename = f"Eval_{timestamp.strftime('%Y%m%d_%H%M')}.md"
        
        # Output to docs/prototype/Evals/
        output_dir = Path("docs/prototype/Evals")
        return output_dir / filename
    
    def get_output_filepath(self, timestamp: Optional[datetime] = None) -> str:
        """Get the output file path as string for external use.
        
        Args:
            timestamp: Optional timestamp for file naming
            
        Returns:
            File path as string
        """
        return str(self._get_output_path(timestamp))
    
    async def export_evaluation_markdown(
        self,
        evaluation_report: EvaluationReport,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Export evaluation report to markdown format and save to file.
        
        Args:
            evaluation_report: The evaluation report to export
            timestamp: Optional timestamp for file naming
            
        Returns:
            The markdown content of the report
        """
        # Generate markdown content
        markdown_content = self._generate_markdown(evaluation_report)
        
        # Get output file path
        output_path = self._get_output_path(timestamp)
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return markdown_content
    
    def _generate_markdown(self, report: EvaluationReport) -> str:
        """Generate shorter, simpler markdown content from evaluation report.
        
        Args:
            report: The evaluation report to convert
            
        Returns:
            Concise markdown formatted report content
        """
        # Format timestamp
        date_str = report.timestamp.strftime("%Y-%m-%d %I:%M %p")
        
        # Calculate message count
        message_count = len(report.conversation_metadata.get("messages", []))
        
        # Format performance metrics
        if report.response_times_ms:
            median_ms = int(sum(report.response_times_ms) / len(report.response_times_ms))
        else:
            median_ms = 0
            
        percentile_80_str = f"{int(report.percentile_80)}ms"
        under_1s_str = f"{int(report.responses_under_1s_percentage * 100)}%"
        
        # Performance status emojis
        p80_status = "✅" if report.percentile_80 < 1000 else "⚠️" if report.percentile_80 < 2000 else "❌"
        under_1s_status = "✅" if report.responses_under_1s_percentage >= 0.8 else "⚠️"
        
        # Start building concise markdown
        markdown = f"""# Coaching Evaluation

**{date_str} • {message_count} messages • Effectiveness: {report.overall_score*10:.1f}/10**

## Performance
- Median: {median_ms}ms | 80th: {percentile_80_str} {p80_status} | <1s: {under_1s_str} {under_1s_status}

## Behavioral Scores
"""

        # Add behavioral scores in compact format
        if report.behavioral_scores:
            # Group scores by type
            morning_analyzers = {"ProblemSelection", "ThinkingPivot", "ExcitementBuilder"}
            morning_scores = [score for score in report.behavioral_scores if score.analyzer_name in morning_analyzers]
            general_scores = [score for score in report.behavioral_scores if score.analyzer_name not in morning_analyzers]
            
            # Morning metrics (compact)
            if morning_scores:
                markdown += "**Morning Coaching:**\n"
                for score in morning_scores:
                    score_out_of_10 = score.value * 10
                    markdown += f"- {score.analyzer_name}: {score_out_of_10:.1f}/10\n"
                markdown += "\n"
            
            # General metrics (compact) 
            if general_scores:
                markdown += "**General Coaching:**\n"
                for score in general_scores:
                    score_out_of_10 = score.value * 10
                    markdown += f"- {score.analyzer_name}: {score_out_of_10:.1f}/10\n"
                markdown += "\n"
        
        # Add user notes if provided (compact)
        if report.user_notes and report.user_notes.strip() and report.user_notes != "No notes provided":
            markdown += f"## Notes\n{report.user_notes}\n\n"

        # Add top improvement suggestions only
        if report.behavioral_scores:
            suggestions = self._generate_improvement_suggestions(report)
            if suggestions:
                markdown += "## Key Improvements\n"
                # Only show top 2 suggestions to keep it short
                for suggestion in suggestions[:2]:
                    markdown += f"- {suggestion}\n"
                markdown += "\n"
        
        # Add footer
        export_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        markdown += f"*Generated with Sonnet • {export_time}*\n"
        
        return markdown
    
    def _generate_improvement_suggestions(self, report: EvaluationReport) -> list[str]:
        """Generate improvement suggestions based on analysis scores.
        
        Args:
            report: The evaluation report
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        for score in report.behavioral_scores:
            if score.value < 0.5:
                if score.analyzer_name == "ProblemSelection":
                    suggestions.append("Challenge user's initial problem choice more directly - ask if it's really the biggest lever")
                elif score.analyzer_name == "ThinkingPivot":
                    suggestions.append("Offer more 'What if...' reframing questions to shift perspective")
                elif score.analyzer_name == "ExcitementBuilder":
                    suggestions.append("Use more vivid, energizing language to build motivation rather than anxiety")
                elif score.analyzer_name == "SpecificityPush":
                    suggestions.append("Challenge vague statements like 'be productive' with specific follow-up questions")
                elif score.analyzer_name == "ActionOrientation":
                    suggestions.append("Drive toward concrete commitments and next steps")
                elif score.analyzer_name == "EmotionalPresence":
                    suggestions.append("Acknowledge emotions before jumping to solutions")
                elif score.analyzer_name == "FrameworkDisruption":
                    suggestions.append("Question systematic thinking patterns more directly")
        
        # Performance suggestions
        if report.percentile_80 > 1000:
            suggestions.append("Optimize response speed while maintaining conversation quality")
        
        return suggestions
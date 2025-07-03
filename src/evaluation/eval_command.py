"""Discretionary Eval command for comprehensive persona-based testing."""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.evaluation.persona_evaluator import PersonaEvaluator
from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
from src.evaluation.reporting.eval_exporter import EvaluationExporter
from src.services.llm_factory import LLMFactory, LLMTier
from src.agents.coach_agent import DiaryCoach


class EvalCommand:
    """Discretionary evaluation command using Sonnet-4 for persona simulation."""
    
    def __init__(self, coach: DiaryCoach):
        """Initialize the eval command.
        
        Args:
            coach: The diary coach agent to evaluate
        """
        self.coach = coach
        # Use STANDARD tier (Sonnet-4) for persona simulation
        self.persona_evaluator = PersonaEvaluator(coach=coach)
        # Use PREMIUM tier (Opus) for Deep Thoughts generation
        self.deep_thoughts_generator = DeepThoughtsGenerator(tier=LLMTier.PREMIUM)
        self.eval_exporter = EvaluationExporter()
    
    async def run_comprehensive_eval(
        self,
        scenarios: Optional[List[str]] = None,
        conversations_per_persona: int = 2
    ) -> Dict[str, Any]:
        """Run comprehensive evaluation with persona simulation.
        
        Args:
            scenarios: Optional list of scenarios to test
            conversations_per_persona: Number of conversations per persona
            
        Returns:
            Evaluation results dictionary
        """
        print("🚀 Starting comprehensive persona-based evaluation...")
        print(f"   • Using Sonnet-4 for persona simulation")
        print(f"   • Using Opus for Deep Thoughts generation")
        print(f"   • Testing {conversations_per_persona} conversations per persona")
        print()
        
        # Default scenarios if none provided
        if not scenarios:
            scenarios = [
                "Morning priority setting with file organization distraction",
                "Product launch decision with perfectionist tendencies",
                "Team leadership challenge with framework overthinking"
            ]
        
        try:
            # Run persona evaluation
            results = await self.persona_evaluator.run_comprehensive_evaluation(
                scenarios=scenarios,
                conversations_per_persona=conversations_per_persona
            )
            
            # Generate reports for each persona's best conversation
            report_paths = []
            for persona_type, persona_results in results.items():
                if persona_results.get("conversations"):
                    # Get the best conversation (highest effectiveness)
                    best_conversation = max(
                        persona_results["conversations"],
                        key=lambda c: getattr(c, 'effectiveness_score', 0)
                    )
                    
                    # Generate Deep Thoughts report
                    conversation_history = self._convert_conversation_to_history(best_conversation)
                    conversation_id = f"eval_{persona_type}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    
                    print(f"📝 Generating Deep Thoughts for {persona_type}...")
                    deep_thoughts_content = await self.deep_thoughts_generator.generate_deep_thoughts(
                        conversation_history=conversation_history,
                        conversation_id=conversation_id,
                        include_evals=True,
                        include_transcript=True
                    )
                    
                    deep_thoughts_path = self.deep_thoughts_generator.get_output_filepath()
                    report_paths.append({
                        "persona": persona_type,
                        "deep_thoughts": deep_thoughts_path,
                        "effectiveness": getattr(best_conversation, 'effectiveness_score', 0)
                    })
            
            # Generate summary evaluation report
            summary_path = await self._generate_summary_report(results, report_paths)
            
            print("\n🎉 Comprehensive evaluation complete!")
            print("📁 Generated files:")
            print(f"   • Summary: {summary_path}")
            for report in report_paths:
                print(f"   • {report['persona']}: {report['deep_thoughts']} (effectiveness: {report['effectiveness']:.1f}/10)")
            
            return {
                "results": results,
                "report_paths": report_paths,
                "summary_path": summary_path
            }
            
        except Exception as e:
            print(f"❌ Error during evaluation: {str(e)}")
            raise
    
    def _convert_conversation_to_history(self, conversation) -> List[Dict[str, str]]:
        """Convert conversation object to history format.
        
        Args:
            conversation: Conversation object from persona evaluation
            
        Returns:
            Formatted conversation history
        """
        history = []
        
        # Handle GeneratedConversation format
        if hasattr(conversation, 'messages'):
            for msg in conversation.messages:
                # Handle dict format from GeneratedConversation
                if isinstance(msg, dict):
                    history.append({
                        "role": msg.get("role", "unknown"),
                        "content": msg.get("content", "")
                    })
                # Handle object format with attributes
                elif hasattr(msg, 'role') and hasattr(msg, 'content'):
                    history.append({
                        "role": msg.role,
                        "content": msg.content
                    })
        elif hasattr(conversation, 'exchanges'):
            for exchange in conversation.exchanges:
                if hasattr(exchange, 'user_message'):
                    history.append({
                        "role": "user",
                        "content": exchange.user_message
                    })
                if hasattr(exchange, 'coach_response'):
                    history.append({
                        "role": "assistant",
                        "content": exchange.coach_response
                    })
        
        return history
    
    async def _generate_summary_report(
        self,
        results: Dict[str, Any],
        report_paths: List[Dict[str, Any]]
    ) -> str:
        """Generate summary evaluation report.
        
        Args:
            results: Evaluation results from persona testing
            report_paths: Paths to generated reports
            
        Returns:
            Path to summary report
        """
        timestamp = datetime.now()
        filename = f"EvalSummary_{timestamp.strftime('%Y%m%d_%H%M')}.md"
        output_dir = Path("docs/prototype/Evals")
        output_path = output_dir / filename
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate summary content
        summary_content = f"""# Comprehensive Persona Evaluation Summary
**{timestamp.strftime('%Y-%m-%d %H:%M')} • Sonnet-4 Personas • Opus Deep Thoughts**

## Overall Results
"""
        
        total_conversations = 0
        total_breakthroughs = 0
        effectiveness_scores = []
        
        for persona_type, persona_results in results.items():
            conversations = persona_results.get("conversations", [])
            breakthrough_count = persona_results.get("breakthrough_achieved_count", 0)
            avg_score = persona_results.get("avg_breakthrough_score", 0)
            
            total_conversations += len(conversations)
            total_breakthroughs += breakthrough_count
            if avg_score > 0:
                effectiveness_scores.append(avg_score)
            
            summary_content += f"""
### {persona_type.replace('_', ' ').title()}
- **Conversations**: {len(conversations)}
- **Breakthroughs**: {breakthrough_count}/{len(conversations)}
- **Avg Effectiveness**: {avg_score:.1f}/10
"""
        
        # Overall metrics
        overall_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
        breakthrough_rate = (total_breakthroughs / total_conversations * 100) if total_conversations > 0 else 0
        
        summary_content += f"""
## Summary Metrics
- **Total Conversations**: {total_conversations}
- **Overall Effectiveness**: {overall_effectiveness:.1f}/10
- **Breakthrough Rate**: {breakthrough_rate:.1f}%

## Generated Reports
"""
        
        for report in report_paths:
            summary_content += f"""- **{report['persona'].replace('_', ' ').title()}**: [`{Path(report['deep_thoughts']).name}`]({report['deep_thoughts']}) (Score: {report['effectiveness']:.1f}/10)
"""
        
        summary_content += f"""
---
*Generated by Eval Command • {timestamp.strftime('%Y-%m-%d %H:%M')}*
"""
        
        # Save summary report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return str(output_path)
"""Discretionary Eval command for comprehensive persona-based testing."""

from datetime import datetime
from typing import List, Dict, Any, Optional

from src.evaluation.persona_evaluator import PersonaEvaluator
from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
from src.services.llm_factory import LLMTier
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
        # Use O3 tier (GPT o3) for cost-effective Deep Thoughts generation
        self.deep_thoughts_generator = DeepThoughtsGenerator(tier=LLMTier.O3)

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
        print("   • Using Sonnet-4 for persona simulation")
        print("   • Using GPT o3 for Deep Thoughts generation")
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
                    conversation_history = self._convert_conversation_to_history(
                        best_conversation
                    )
                    conversation_id = f"eval_{persona_type}_"
                    conversation_id += f"{datetime.now().strftime('%Y%m%d_%H%M')}"

                    print(f"📝 Generating Deep Thoughts for {persona_type}...")
                    await self.deep_thoughts_generator.generate_deep_thoughts(
                        conversation_history=conversation_history,
                        conversation_id=conversation_id,
                        include_evals=False,  # No evals in deep reports per Session_6_8
                        include_transcript=True
                    )

                    deep_thoughts_path = (
                        self.deep_thoughts_generator.get_output_filepath()
                    )
                    report_paths.append({
                        "persona": persona_type,
                        "deep_thoughts": deep_thoughts_path,
                        "effectiveness": getattr(
                            best_conversation, 'effectiveness_score', 0
                        )
                    })

            # No summary evaluation report per Session_6_8

            print("\n🎉 Comprehensive evaluation complete!")
            print("📁 Generated files:")
            for report in report_paths:
                print(
                    f"   • {report['persona']}: {report['deep_thoughts']} "
                    f"(effectiveness: {report['effectiveness']:.1f}/10)"
                )

            return {
                "results": results,
                "report_paths": report_paths
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

"""Enhanced CLI interface with evaluation capabilities."""

import os
import json
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from src.interface.cli import DiaryCoachCLI
from src.agents.coach_agent import DiaryCoach
from src.events.bus import EventBus
from src.events.schemas import UserMessage
from src.evaluation.performance_tracker import PerformanceTracker
from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
from src.services.llm_factory import LLMTier
from src.evaluation.eval_command import EvalCommand


class EnhancedCLI(DiaryCoachCLI):
    """Enhanced command-line interface with evaluation and performance tracking."""

    def __init__(self, coach: DiaryCoach, event_bus: EventBus):
        """Initialize enhanced CLI with coach and event bus.

        Args:
            coach: The diary coach agent
            event_bus: Event bus for message routing
        """
        super().__init__(coach, event_bus)
        self.performance_tracker = PerformanceTracker()
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_eval = None

        # Initialize Rich console for markdown rendering
        self.console = Console()

        # Initialize Deep Thoughts generator and Eval exporter
        # Use PREMIUM tier (Claude Opus 4) for Deep Thoughts analysis
        self.deep_thoughts_generator = DeepThoughtsGenerator(tier=LLMTier.PREMIUM)

        # Initialize comprehensive eval command
        self.eval_command = EvalCommand(coach)

    async def process_input(self, user_input: str) -> Optional[str]:
        """Process user input with performance tracking and evaluation.

        Args:
            user_input: The user's input text

        Returns:
            Coach response text, or None if user wants to exit
        """
        # Check for stop/evaluation commands with multiple variations
        stop_commands = [
            "stop",
            "stop here",
            "end conversation",
            "go to report",
            "generate report",
            "evaluate",
            "evaluation",
            "finish",
            "end session",
            "wrap up",
            "that's enough",
        ]

        if any(user_input.lower().strip() == cmd for cmd in stop_commands):
            await self._handle_stop_command()
            return (
                "Conversation evaluation complete. Type 'deep report' to "
                "generate Deep Thoughts + evaluation files, or 'exit' to quit."
            )

        if user_input.lower().strip() == "report":
            await self._handle_report_command()
            return "Evaluation report displayed above."

        # Check for exit commands
        if user_input.lower().strip() in ["exit", "quit"]:
            print("Goodbye! Have a transformative day! 🌟")
            return None

        # Check for deep report commands with variations
        deep_report_commands = [
            "deep report",
            "detailed report",
            "enhanced report",
            "deep analysis",
            "full report",
            "comprehensive report",
        ]

        if any(user_input.lower().strip() == cmd for cmd in deep_report_commands):
            if not self.conversation_history:
                return (
                    "No conversation history to evaluate. "
                    "Please start a conversation first."
                )
            await self._handle_deep_report_command(include_full_analysis=True)
            return "Deep Thoughts and evaluation reports generated."

        # Check for comprehensive eval command
        eval_commands = [
            "eval",
            "comprehensive eval",
            "persona eval",
            "full eval",
            "test personas",
            "run eval",
            "evaluate coach",
        ]

        if any(user_input.lower().strip() == cmd for cmd in eval_commands):
            await self._handle_eval_command()
            return "Comprehensive persona-based evaluation complete."

        try:
            # Track performance
            start_time = time.time()

            # Create user message
            user_message = UserMessage(
                content=user_input, user_id="michael", timestamp=datetime.now()
            )

            # Add to conversation history
            self.conversation_history.append(
                {"role": "user", "content": user_input, "timestamp": datetime.now()}
            )

            # Process through coach
            response = await self.coach.process_message(user_message)

            # Track performance
            end_time = time.time()
            await self.performance_tracker.track_response(start_time, end_time)

            # Add response to conversation history
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": response.content,
                    "timestamp": response.timestamp,
                }
            )

            return response.content

        except Exception as e:
            # Handle errors gracefully
            return f"Sorry, I encountered an error: {str(e)}. Please try again."

    async def _handle_stop_command(self) -> None:
        """Handle stop command with evaluation display."""
        if not self.conversation_history:
            print("No conversation to evaluate.")
            return

        # Save conversation to disk
        saved_path = self._save_conversation()
        if saved_path:
            print(f"\n💾 Conversation saved to: {saved_path}")

        # Display evaluation summary first
        print("\n=== Conversation Evaluation ===")
        print(f"Total Cost: ${self.get_session_cost():.4f}")
        print(f"Messages: {len(self.conversation_history)}")

        # Collect user notes
        print("\nAdd notes about this conversation (or 'skip'): ", end="")
        user_notes = await self._get_input("")

        if user_notes.lower().strip() == "skip":
            user_notes = "No notes provided"

        # Generate in-memory evaluation only (no file generation)
        await self._generate_in_memory_evaluation(user_notes)

        print(
            "\nType 'deep report' to generate Deep Thoughts + evaluation files, "
            "or 'exit' to quit."
        )

    async def _handle_report_command(self) -> None:
        """Handle report command to display evaluation."""
        if not self.conversation_history:
            print("No conversation history to evaluate.")
            return

        print("\n=== Evaluation Report ===")
        print(f"Messages: {len(self.conversation_history)}")
        print(f"Session Cost: ${self.get_session_cost():.4f}")
        print(f"Performance: {self.performance_tracker.get_median():.0f}ms median")

    async def _generate_in_memory_evaluation(self, user_notes: str) -> None:
        """Generate in-memory evaluation without file creation."""
        # Store user notes for deep report (no actual evaluation generated)
        try:
            # Create a simple evaluation object to store user notes
            self.current_eval = type(
                "SimpleEval",
                (),
                {
                    "user_notes": user_notes,
                    "overall_score": self._calculate_effectiveness_score() / 10,
                    "behavioral_scores": [],
                },
            )()

        except Exception as e:
            print(f"Error storing evaluation notes: {e}")
            # Fallback to simple evaluation
            await self._generate_simple_evaluation()

    async def _handle_deep_report_command(
        self, include_full_analysis: bool = False
    ) -> None:
        """Handle deep report command - generates Deep Thoughts (Opus) +
        Evaluation (Sonnet) files.
        """
        if not self.conversation_history:
            print("No conversation history to evaluate.")
            return

        print("\n🧠 Generating Deep Thoughts + Evaluation reports...")

        # Ensure we have user notes
        if not self.current_eval:
            # Generate in-memory evaluation first if needed
            print("Add notes about this conversation (or 'skip'): ", end="")
            user_notes = await self._get_input("")
            if user_notes.lower().strip() == "skip":
                user_notes = "No notes provided"
            await self._generate_in_memory_evaluation(user_notes)
        else:
            user_notes = getattr(self.current_eval, "user_notes", "No notes provided")

        # Generate unique conversation ID for this session
        conversation_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M')}"

        try:
            # Step 1: Generate Deep Thoughts report with full analysis if requested
            print("📝 Generating Deep Thoughts report (Opus)...")
            deep_thoughts_content = (
                await self.deep_thoughts_generator.generate_deep_thoughts(
                    conversation_history=self.conversation_history,
                    conversation_id=conversation_id,
                    include_evals=include_full_analysis,
                    include_transcript=include_full_analysis,
                )
            )
            deep_thoughts_path = self.deep_thoughts_generator.get_output_filepath()
            print(f"✅ Deep Thoughts saved to: {deep_thoughts_path}")

            # Display Deep Thoughts content in terminal with Rich markdown rendering
            print("\n")
            self.console.print(
                Panel(
                    Markdown(deep_thoughts_content),
                    title="📝 DEEP THOUGHTS REPORT",
                    border_style="blue",
                )
            )

            # No separate evaluation reports per Session_6_8

            print("\n🎉 Deep report complete!")
            print("📁 Generated files:")
            print(f"   • Deep Thoughts: {deep_thoughts_path}")

        except Exception as e:
            print(f"❌ Error generating deep report: {str(e)}")
            print("Please try again or use 'exit' to quit.")

    async def _handle_eval_command(self) -> None:
        """Handle comprehensive persona-based evaluation command."""
        print("🎯 Starting comprehensive persona-based evaluation...")
        print(
            "   This will test the coach against all personas with Sonnet-4 simulation"
        )
        print("   and generate Deep Thoughts reports with Opus.")
        print()

        try:
            results = await self.eval_command.run_comprehensive_eval(
                conversations_per_persona=2  # Keep it reasonable for manual testing
            )

            print("\n✨ Evaluation insights:")
            if results.get("results"):
                for persona_type, persona_results in results["results"].items():
                    breakthrough_count = persona_results.get(
                        "breakthrough_achieved_count", 0
                    )
                    total_conversations = len(persona_results.get("conversations", []))
                    avg_score = persona_results.get("avg_breakthrough_score", 0)

                    persona_name = persona_type.replace('_', ' ').title()
                    print(
                        f"   • {persona_name}: "
                        f"{breakthrough_count}/{total_conversations} breakthroughs, "
                        f"{avg_score:.1f}/10 avg effectiveness"
                    )

        except Exception as e:
            print(f"❌ Error during comprehensive evaluation: {str(e)}")
            print("Please try again or use 'exit' to quit.")

    async def _generate_simple_evaluation(self) -> None:
        """Generate simple evaluation as fallback."""
        self.current_eval = type(
            "SimpleEval",
            (),
            {
                "overall_score": self._calculate_effectiveness_score() / 10,
                "behavioral_scores": [],
            },
        )()

    def _calculate_effectiveness_score(self) -> float:
        """Calculate coaching effectiveness score.

        Returns:
            Effectiveness score from 0-10
        """
        # Simple scoring for now - based on conversation length and responsiveness
        if not self.conversation_history:
            return 0.0

        # Base score
        score = 5.0

        # Adjust for conversation engagement (more exchanges = better)
        message_count = len(self.conversation_history)
        if message_count >= 4:
            score += 1.0
        if message_count >= 8:
            score += 1.0

        # Adjust for response speed (faster = better)
        if self.performance_tracker.response_times:
            avg_response_time = sum(self.performance_tracker.response_times) / len(
                self.performance_tracker.response_times
            )
            if avg_response_time < 1000:  # Under 1 second
                score += 1.5
            elif avg_response_time < 2000:  # Under 2 seconds
                score += 0.5

        return min(score, 10.0)

    def _save_conversation(self) -> str:
        """Save the current conversation to disk.

        Returns:
            Path to the saved conversation file
        """
        if not self.conversation_history:
            return ""

        # Create conversations directory if it doesn't exist
        conversations_dir = "data/conversations"
        os.makedirs(conversations_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now()
        filename = f"conversation_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(conversations_dir, filename)

        # Prepare conversation data
        conversation_data = {
            "conversation_id": f"session_{timestamp.strftime('%Y%m%d_%H%M')}",
            "timestamp": timestamp.isoformat(),
            "messages": [
                {
                    "type": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"].isoformat()
                }
                for msg in self.conversation_history
            ],
            "metadata": {
                "total_messages": len(self.conversation_history),
                "session_cost": self.get_session_cost(),
                "median_response_time": self.performance_tracker.get_median()
            }
        }

        # Save to file
        with open(filepath, 'w') as f:
            json.dump(conversation_data, f, indent=2)

        return filepath

    async def run(self) -> None:
        """Run the interactive CLI loop without per-message cost display."""
        print("🌅 Diary Coach Ready")
        print(
            "💡 Tips: Say 'stop', 'end conversation', or 'wrap up' to get "
            "your coaching evaluation"
        )
        print("   Then use 'deep report' for detailed AI analysis, or 'exit' to quit")
        print()

        while self.running:
            try:
                # Get user input
                user_input = await self._get_input("> ")

                if not user_input.strip():
                    continue

                # Process input
                response = await self.process_input(user_input)

                if response is None:
                    # User wants to exit - break out of loop
                    break

                # Display response (no cost display per message)
                print(f"\n{response}\n")
                print("-" * 50)

            except KeyboardInterrupt:
                print("\nGoodbye! Have a transformative day! 🌟")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

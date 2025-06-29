"""Enhanced CLI interface with evaluation capabilities."""

import asyncio
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.interface.cli import DiaryCoachCLI
from src.agents.coach_agent import DiaryCoach
from src.events.bus import EventBus
from src.events.schemas import UserMessage
from src.evaluation.performance_tracker import PerformanceTracker
from src.evaluation.reporting.reporter import EvaluationReporter
from src.evaluation.analyzers.specificity import SpecificityPushAnalyzer
from src.evaluation.analyzers.action import ActionOrientationAnalyzer


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
        self.evaluation_reporter = EvaluationReporter()
        
        # Initialize analyzers with LLM service
        self.analyzers = [
            SpecificityPushAnalyzer(llm_service=coach.llm_service),
            ActionOrientationAnalyzer(llm_service=coach.llm_service)
        ]
    
    async def process_input(self, user_input: str) -> Optional[str]:
        """Process user input with performance tracking and evaluation.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Coach response text, or None if user wants to exit
        """
        # Check for special commands
        if user_input.lower().strip() == "stop":
            await self._handle_stop_command()
            return None
        
        if user_input.lower().strip() == "report":
            await self._handle_report_command()
            return "Evaluation report displayed above."
        
        # Check for exit commands
        if user_input.lower().strip() in ["exit", "quit"]:
            return None
        
        try:
            # Track performance
            start_time = time.time()
            
            # Create user message
            user_message = UserMessage(
                content=user_input,
                user_id="michael",
                timestamp=datetime.now()
            )
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now()
            })
            
            # Process through coach
            response = await self.coach.process_message(user_message)
            
            # Track performance
            end_time = time.time()
            await self.performance_tracker.track_response(start_time, end_time)
            
            # Add response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content,
                "timestamp": response.timestamp
            })
            
            return response.content
            
        except Exception as e:
            # Handle errors gracefully
            return f"Sorry, I encountered an error: {str(e)}. Please try again."
    
    async def _handle_stop_command(self) -> None:
        """Handle stop command with evaluation display."""
        if not self.conversation_history:
            print("No conversation to evaluate.")
            return
            
        # Generate full evaluation report
        await self._generate_full_evaluation()
        
        # Display evaluation summary
        print("\n=== Conversation Evaluation ===")
        print(f"Total Cost: ${self.get_session_cost():.4f}")
        
        if self.current_eval:
            print(f"Coaching Effectiveness: {self.current_eval.overall_score * 10:.1f}/10")
            
            print(f"\nResponse Speed:")
            print(f"- Median: {self.performance_tracker.get_median():.0f}ms")
            print(f"- 80th percentile: {self.performance_tracker.get_percentile(80):.0f}ms")
            print(f"- Under 1s: {self.performance_tracker.percentage_under_threshold(1000):.0%}")
            
            print(f"\nBehavioral Analysis:")
            for score in self.current_eval.behavioral_scores:
                print(f"- {score.analyzer_name}: {score.value * 10:.1f}/10")
        
        print("\nAdd notes (or 'skip'): ", end="")
        # In a real implementation, we'd capture user notes here
        # For now, just print the prompt
    
    async def _handle_report_command(self) -> None:
        """Handle report command to display evaluation."""
        if not self.conversation_history:
            print("No conversation history to evaluate.")
            return
        
        print("\n=== Evaluation Report ===")
        print(f"Messages: {len(self.conversation_history)}")
        print(f"Session Cost: ${self.get_session_cost():.4f}")
        print(f"Performance: {self.performance_tracker.get_median():.0f}ms median")
    
    async def _generate_full_evaluation(self) -> None:
        """Generate full evaluation using behavioral analyzers."""
        from src.evaluation.generator import GeneratedConversation
        
        # Convert conversation history to GeneratedConversation format
        conversation = GeneratedConversation(
            messages=self.conversation_history,
            persona_type="Real User",  # Real user, not a persona
            scenario="CLI Session",
            timestamp=datetime.now(),
            final_resistance_level=0.5,  # Unknown for real user
            breakthrough_achieved=False  # Unknown for real user
        )
        
        # Prepare performance data
        performance_data = {
            "response_times_ms": self.performance_tracker.response_times,
            "percentile_80": self.performance_tracker.get_percentile(80),
            "responses_under_1s_percentage": self.performance_tracker.percentage_under_threshold(1000)
        }
        
        # Generate evaluation report
        try:
            self.current_eval = await self.evaluation_reporter.generate_report(
                conversation=conversation,
                user_notes="Real conversation session",
                analyzers=self.analyzers,
                performance_data=performance_data
            )
            
            # Save report to docs/prototype
            report_filename = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_path = f"docs/prototype/{report_filename}"
            self.current_eval.save_as_markdown(report_path)
            print(f"\nEvaluation report saved to: {report_path}")
            
        except Exception as e:
            print(f"Error generating evaluation: {e}")
            # Fallback to simple evaluation
            await self._generate_simple_evaluation()
    
    async def _generate_simple_evaluation(self) -> None:
        """Generate simple evaluation as fallback."""
        self.current_eval = type('SimpleEval', (), {
            'overall_score': self._calculate_effectiveness_score() / 10,
            'behavioral_scores': []
        })()
    
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
            avg_response_time = sum(self.performance_tracker.response_times) / len(self.performance_tracker.response_times)
            if avg_response_time < 1000:  # Under 1 second
                score += 1.5
            elif avg_response_time < 2000:  # Under 2 seconds
                score += 0.5
        
        return min(score, 10.0)
    
    async def run(self) -> None:
        """Run the interactive CLI loop without per-message cost display."""
        print("🌅 Diary Coach Ready (type 'stop' for evaluation, 'exit' to quit)")
        
        while self.running:
            try:
                # Get user input
                user_input = await self._get_input("> ")
                
                if not user_input.strip():
                    continue
                
                # Process input
                response = await self.process_input(user_input)
                
                if response is None:
                    # User wants to exit or stop
                    if user_input.lower().strip() in ["exit", "quit"]:
                        print("Goodbye! Have a transformative day! 🌟")
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
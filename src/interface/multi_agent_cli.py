"""Multi-Agent CLI with enhanced coach and Stage 1 agent integration."""

import asyncio
import os
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from src.agents.enhanced_coach_agent import EnhancedDiaryCoach
from src.evaluation.performance_tracker import PerformanceTracker
from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
from src.services.llm_factory import LLMTier
from src.evaluation.eval_command import EvalCommand
from src.agents.memory_agent import MemoryAgent
from src.agents.personal_content_agent import PersonalContentAgent
from src.agents.mcp_agent import MCPAgent
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.reporter_agent import ReporterAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.registry import agent_registry
from src.services.llm_factory import LLMFactory
from src.events.bus import EventBus
from src.orchestration.langsmith_tracker import LangSmithTracker


class MultiAgentCLI:
    """CLI with multi-agent support for Stage 1 conversations."""

    def __init__(self):
        """Initialize multi-agent CLI with all agents."""
        # Check if multi-agent mode is disabled
        self.multi_agent_enabled = (
            os.getenv("DISABLE_MULTI_AGENT", "false").lower() != "true"
        )

        # Create LLM service
        self.llm_service = LLMFactory.create_cheap_service()

        # Create enhanced coach
        self.coach = EnhancedDiaryCoach(self.llm_service)

        # Create event bus
        self.event_bus = EventBus()

        # Initialize evaluation capabilities
        self.performance_tracker = PerformanceTracker()
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_eval = None
        self.running = True

        # Initialize Rich console for markdown rendering
        self.console = Console()

        # Initialize Deep Thoughts generator
        # Use PREMIUM tier (Claude Opus 4) for Deep Thoughts analysis
        self.deep_thoughts_generator = DeepThoughtsGenerator(tier=LLMTier.PREMIUM)

        # Initialize comprehensive eval command
        self.eval_command = EvalCommand(self.coach)

        # Initialize LangSmith tracker
        self.langsmith_tracker = LangSmithTracker(
            project_name="diary-coach-debug")

        if self.multi_agent_enabled:
            # Initialize other agents
            self.memory_agent = MemoryAgent()
            self.personal_content_agent = PersonalContentAgent()
            self.mcp_agent = MCPAgent()
            self.orchestrator_agent = OrchestratorAgent(self.llm_service)
            self.reporter_agent = ReporterAgent()
            self.evaluator_agent = EvaluatorAgent()

            # Register all agents
            agent_registry.register_instance(self.coach)
            agent_registry.register_instance(self.memory_agent)
            agent_registry.register_instance(self.personal_content_agent)
            agent_registry.register_instance(self.mcp_agent)
            agent_registry.register_instance(self.orchestrator_agent)
            agent_registry.register_instance(self.reporter_agent)
            agent_registry.register_instance(self.evaluator_agent)

            print("🤖 Initializing Multi-Agent System...")
        else:
            # Only register the coach in single-agent mode
            agent_registry.register_instance(self.coach)
            print("🤖 Initializing Single-Agent Mode (Multi-agent disabled)...")

    async def _initialize_agents(self):
        """Initialize all agents before starting conversation."""
        if self.multi_agent_enabled:
            print("  📚 Loading Memory Agent...")
            await self.memory_agent.initialize()

            print("  📄 Loading Personal Content Agent...")
            await self.personal_content_agent.initialize()

            print("  ✅ Loading MCP Agent (Todoist)...")
            await self.mcp_agent.initialize()

            print("  🎯 Loading Orchestrator Agent...")
            await self.orchestrator_agent.initialize()

            print("  📝 Loading Reporter Agent...")
            await self.reporter_agent.initialize()

            print("  ⭐ Loading Evaluator Agent...")
            await self.evaluator_agent.initialize()

            print("  💭 Initializing Enhanced Coach...")
            await self.coach.initialize()

            print("✨ All agents ready!\n")
        else:
            print("  💭 Initializing Coach...")
            await self.coach.initialize()
            print("✨ Coach ready!\n")

    async def run(self):
        """Run the enhanced multi-agent CLI."""
        if self.multi_agent_enabled:
            print(
                "Welcome to your Multi-Agent Daily Transformation Diary Coach! 🌟")
            print("=" * 50)
            print("Available agents:")
            print("  - Memory Agent: Recalls past conversations")
            print("  - Personal Content Agent: Accesses your core beliefs")
            print("  - MCP Agent: Manages your Todoist tasks")
            print("  - Orchestrator Agent: Coordinates multi-agent collaboration")
            print("  - Enhanced Coach: Leads the conversation")
            print("=" * 50)
            print("Stages:")
            print("  - Stage 1: Exploration (Coach-led with selective agent calls)")
            print("  - Stage 2: Orchestrated Gathering (All agents work in parallel)")
            print("  - Stage 3: Synthesis (Deep Thoughts report generation)")
            print("=" * 50)
            print(
                "Commands: 'stop' to end conversation, 'deep report' for "
                "evaluation, 'exit' to quit"
            )
            print("=" * 50)
        else:
            print(
                "Welcome to your Daily Transformation Diary Coach! 🌟")
            print("=" * 50)
            print("Running in single-agent mode (Multi-agent features disabled)")
            print("=" * 50)
            print(
                "Commands: 'stop' to end conversation, 'deep report' for "
                "evaluation, 'exit' to quit"
            )
            print("=" * 50)

        # Initialize all agents
        await self._initialize_agents()

        if self.multi_agent_enabled:
            # Add startup note about agent integration
            print(
                "💡 The coach will automatically access relevant context from "
                "other agents")
            print("   when it enhances your coaching experience.\n")

        # Start LangSmith tracking
        if self.langsmith_tracker.client:
            from src.orchestration.state import ConversationState
            import uuid
            state = ConversationState(conversation_id=str(uuid.uuid4()))
            await self.langsmith_tracker.track_conversation_start(state)

        # Run the main conversation loop
        await self._run_conversation_loop()

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
            # Return empty string to let _handle_stop_command's print statements show
            return ""

        if user_input.lower().strip() == "report":
            return "Please use 'deep report' to generate an evaluation."

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
            await self._handle_deep_report_command()
            return ""  # Let the method's print statements show

        # Normal message processing
        start_time = time.time()

        # Note: Using AgentRequest instead of UserMessage for coach interaction

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })

        # Process through coach
        try:
            from src.agents.base import AgentRequest
            request = AgentRequest(
                from_agent="user",
                to_agent="coach",
                query=user_input,
                context={
                    "user_id": "michael",
                    "conversation_id": "default",
                    "message_id": str(datetime.now().timestamp()),
                    "timestamp": datetime.now().isoformat()
                }
            )

            response = await self.coach.handle_request(request)
            response_content = response.content

            # Track performance
            await self.performance_tracker.track_response(start_time, time.time())

            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().isoformat()
            })

            return response_content

        except Exception as e:
            print(f"Error processing message: {e}")
            return "I'm having trouble processing your message right now."

            # If it was a normal coaching response, check for agent calls
            if response_content and self.multi_agent_enabled:
                if (hasattr(self.coach, 'agent_call_history') and
                        self.coach.agent_call_history):
                    # Get the most recent agent calls
                    recent_calls = [
                        call for call in self.coach.agent_call_history
                        if (datetime.now() - call['timestamp']).seconds < 5
                    ]
                    if recent_calls:
                        agents_list = ', '.join(
                            call['agent'] for call in recent_calls)
                        stage_info = f"Stage {self.coach.current_stage}"
                        print(f"\n[{stage_info} | Agents consulted: {agents_list}]")

                        # Track agent communications in LangSmith
                        for call in recent_calls:
                            if self.langsmith_tracker.client:
                                await (
                                    self.langsmith_tracker.track_agent_communication
                                )(
                                    agent_name=call['agent'],
                                    input_data={"query": call.get('query', user_input)},
                                    output_data={
                                        "response": call.get('response', 'N/A')
                                    }
                                )

            return response_content

    async def _run_conversation_loop(self):
        """Run the main conversation loop."""
        while self.running:
            try:
                # Get user input
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                # Process input and get response
                response = await self.process_input(user_input)

                if response is None:
                    # User wants to exit
                    self.running = False
                    break

                # Display response using Rich markdown rendering
                if response:
                    self.console.print(Markdown(response))

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit or continue chatting.")
            except Exception as e:
                print(f"Error: {e}")
                print("Please try again.")

    async def _handle_stop_command(self):
        """Handle stop/evaluation command."""
        if not self.conversation_history:
            print("No conversation to evaluate.")
            return

        # Simply mark that evaluation can be done
        print("\n=== Conversation Stopped ===")
        print(f"Total exchanges: {len(self.conversation_history) // 2}")
        print("\nYou can now:")
        print("  • Type 'deep report' to generate a Deep Thoughts evaluation")
        print("  • Type 'exit' to quit without evaluation")

    async def _handle_report_command(self):
        """Handle report viewing command."""
        if not self.current_eval:
            print("No evaluation available. Use 'stop' to evaluate first.")
            return

        # Display the full evaluation report
        report_md = self.eval_command.format_report(self.current_eval)
        self.console.print(Markdown(report_md))

    async def _handle_deep_report_command(self):
        """Handle deep report generation command using Reporter and Evaluator agents."""
        print("\n🤔 Generating Deep Thoughts analysis...")

        # Stage 3: Reporter and Evaluator synthesis
        print("  📊 Entering Stage 3: Deep Thoughts Synthesis...")

        # First, gather all agent contributions if multi-agent is enabled
        agent_contributions = {}

        if self.multi_agent_enabled:
            from src.agents.base import AgentRequest

            # Get contributions from each agent
            print("  📚 Gathering agent contributions...")

            # Memory Agent
            memory_request = AgentRequest(
                from_agent="orchestrator",
                to_agent="memory",
                query="Provide relevant past conversation insights",
                context={"conversation": self.conversation_history}
            )
            memory_response = await self.memory_agent.handle_request(memory_request)
            agent_contributions["memory"] = memory_response.content

            # Personal Content Agent
            personal_request = AgentRequest(
                from_agent="orchestrator",
                to_agent="personal_content",
                query="Provide relevant personal context",
                context={"conversation": self.conversation_history}
            )
            personal_response = await self.personal_content_agent.handle_request(
                personal_request
            )
            agent_contributions["personal_content"] = personal_response.content

            # MCP Agent (if there are relevant tasks)
            mcp_request = AgentRequest(
                from_agent="orchestrator",
                to_agent="mcp",
                query="Provide relevant tasks and context",
                context={"conversation": self.conversation_history}
            )
            mcp_response = await self.mcp_agent.handle_request(mcp_request)
            if mcp_response.content and "No relevant tasks" not in mcp_response.content:
                agent_contributions["mcp"] = mcp_response.content

        # Generate Deep Thoughts report with Reporter Agent
        print("  📝 Reporter Agent synthesizing insights...")
        reporter_request = AgentRequest(
            from_agent="cli",
            to_agent="reporter",
            query="Generate Deep Thoughts report",
            context={
                "conversation": self.conversation_history,
                "agent_contributions": agent_contributions
            }
        )
        reporter_response = await self.reporter_agent.handle_request(reporter_request)
        deep_thoughts_report = reporter_response.content

        # Save the Deep Thoughts report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = "docs/prototype/DeepThoughts"
        os.makedirs(output_dir, exist_ok=True)
        deep_thoughts_path = os.path.join(output_dir, f"DeepThoughts_{timestamp}.md")

        with open(deep_thoughts_path, 'w') as f:
            f.write(deep_thoughts_report)

        print("\n✅ Deep Thoughts report generated successfully!")
        print(f"📄 Report saved to: {deep_thoughts_path}")

        # Evaluate the conversation and report with Evaluator Agent
        print("\n  ⭐ Evaluator Agent assessing quality...")
        evaluator_request = AgentRequest(
            from_agent="cli",
            to_agent="evaluator",
            query="Evaluate coaching session",
            context={
                "conversation": self.conversation_history,
                "deep_thoughts": deep_thoughts_report,
                "conversation_id": "default"  # Pass conversation ID for LangSmith
            }
        )
        evaluator_response = await self.evaluator_agent.handle_request(
            evaluator_request
        )
        evaluation_report = evaluator_response.content

        # Save the evaluation report
        evaluation_path = os.path.join(output_dir, f"Evaluation_{timestamp}.md")

        with open(evaluation_path, 'w') as f:
            f.write(evaluation_report)

        print("✅ Evaluation report generated successfully!")
        print(f"📄 Evaluation saved to: {evaluation_path}")

        # Convert to Path for absolute paths
        from pathlib import Path
        deep_thoughts_abs_path = Path(deep_thoughts_path).absolute()
        evaluation_abs_path = Path(evaluation_path).absolute()

        # Display the Deep Thoughts report
        print("\n" + "="*80)
        print("DEEP THOUGHTS REPORT")
        print("="*80 + "\n")

        self.console.print(Markdown(deep_thoughts_report))

        print("\n" + "="*80)
        print("EVALUATION REPORT")
        print("="*80 + "\n")

        self.console.print(Markdown(evaluation_report))

        print("\n" + "="*80)
        print(f"Deep Thoughts saved to: {deep_thoughts_abs_path}")
        print(f"Evaluation saved to: {evaluation_abs_path}")
        print("="*80)


async def main():
    """Main entry point for multi-agent CLI."""
    cli = MultiAgentCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())

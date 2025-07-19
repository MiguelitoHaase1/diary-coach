"""Multi-Agent CLI with enhanced coach and Stage 1 agent integration."""

import asyncio
from typing import Optional
from datetime import datetime

from src.interface.enhanced_cli import EnhancedCLI
from src.agents.enhanced_coach_agent import EnhancedDiaryCoach
from src.agents.memory_agent import MemoryAgent
from src.agents.personal_content_agent import PersonalContentAgent
from src.agents.mcp_agent import MCPAgent
from src.agents.registry import agent_registry
from src.services.llm_factory import LLMFactory
from src.events.bus import EventBus
from src.orchestration.langsmith_tracker import LangSmithTracker


class MultiAgentCLI(EnhancedCLI):
    """CLI with multi-agent support for Stage 1 conversations."""

    def __init__(self):
        """Initialize multi-agent CLI with all agents."""
        # Create LLM service
        llm_service = LLMFactory.create_cheap_service()

        # Create enhanced coach
        coach = EnhancedDiaryCoach(llm_service)

        # Create event bus
        event_bus = EventBus()

        # Initialize parent
        super().__init__(coach, event_bus)

        # Initialize LangSmith tracker
        self.langsmith_tracker = LangSmithTracker(
            project_name="diary-coach-debug")

        # Initialize other agents
        self.memory_agent = MemoryAgent()
        self.personal_content_agent = PersonalContentAgent()
        self.mcp_agent = MCPAgent()

        # Register all agents
        agent_registry.register_instance(coach)
        agent_registry.register_instance(self.memory_agent)
        agent_registry.register_instance(self.personal_content_agent)
        agent_registry.register_instance(self.mcp_agent)

        print("🤖 Initializing Multi-Agent System...")

    async def _initialize_agents(self):
        """Initialize all agents before starting conversation."""
        print("  📚 Loading Memory Agent...")
        await self.memory_agent.initialize()

        print("  📄 Loading Personal Content Agent...")
        await self.personal_content_agent.initialize()

        print("  ✅ Loading MCP Agent (Todoist)...")
        await self.mcp_agent.initialize()

        print("  💭 Initializing Enhanced Coach...")
        await self.coach.initialize()

        print("✨ All agents ready!\n")

    async def run(self):
        """Run the enhanced multi-agent CLI."""
        print(
            "Welcome to your Multi-Agent Daily Transformation Diary Coach! 🌟")
        print("=" * 50)
        print("Available agents:")
        print("  - Memory Agent: Recalls past conversations")
        print("  - Personal Content Agent: Accesses your core beliefs")
        print("  - MCP Agent: Manages your Todoist tasks")
        print("  - Enhanced Coach: Orchestrates everything seamlessly")
        print("=" * 50)
        print(
            "Commands: 'stop' for evaluation, 'report' to view, 'exit' to quit")
        print("=" * 50)

        # Initialize all agents
        await self._initialize_agents()

        # Add startup note about agent integration
        print(
            "💡 The coach will automatically access relevant context from "
            "other agents")
        print("   when it enhances your coaching experience.\n")

        # Start LangSmith tracking
        if self.langsmith_tracker.client:
            from src.orchestration.state import ConversationState
            state = ConversationState()
            await self.langsmith_tracker.track_conversation_start(state)

        # Run the main conversation loop
        await super().run()

    async def process_input(self, user_input: str) -> Optional[str]:
        """Handle user input with agent status display.

        Overrides parent to show when agents are called.
        """
        # Process normally through parent
        response = await super().process_input(user_input)

        # If it was a normal coaching response, check for agent calls
        if (response and hasattr(self.coach, 'message_history') and
                self.coach.message_history):
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
                    print(f"\n[Agents consulted: {agents_list}]")

                    # Track agent communications in LangSmith
                    for call in recent_calls:
                        if self.langsmith_tracker.client:
                            await self.langsmith_tracker.track_agent_communication(
                                agent_name=call['agent'],
                                input_data={"query": call.get('query', user_input)},
                                output_data={"response": call.get('response', 'N/A')}
                            )

        return response


async def main():
    """Main entry point for multi-agent CLI."""
    cli = MultiAgentCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())

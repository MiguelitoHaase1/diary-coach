"""Reporter Agent for generating Deep Thoughts synthesis."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.agents.base import BaseAgent, AgentRequest, AgentResponse, AgentCapability
from src.services.llm_service import AnthropicService
from src.config.models import ModelProvider, get_model_for_tier
from src.agents.prompts import PromptLoader

logger = logging.getLogger(__name__)


class ReporterAgent(BaseAgent):
    """Agent that synthesizes all contributions into Deep Thoughts report."""

    def __init__(self, llm_service: Optional[AnthropicService] = None):
        """Initialize Reporter Agent.

        Args:
            llm_service: Anthropic service instance (will create if not provided)
        """
        if llm_service is None:
            # Use premium tier (Opus 4) for Deep Thoughts generation
            model_name = get_model_for_tier("premium", ModelProvider.ANTHROPIC)
            llm_service = AnthropicService(model=model_name)

        super().__init__(
            name="reporter",
            capabilities=[AgentCapability.REPORT_GENERATION, AgentCapability.SYNTHESIS],
        )
        self.llm_service = llm_service

        # Load prompts
        self.prompt_loader = PromptLoader()

    @property
    def system_prompt(self) -> str:
        """Load system prompt from markdown file."""
        try:
            # Load Deep Thoughts system prompt
            return self.prompt_loader.load_prompt("deep_thoughts_system_prompt")
        except Exception as e:
            logger.error(f"Error loading Deep Thoughts prompt: {e}")
            # Fallback prompt
            return """You are a Deep Thoughts Reporter synthesizing coaching insights.

Create a comprehensive Deep Thoughts report following the standard structure.
Focus on clarity, coherence, and practical value."""

    async def initialize(self) -> None:
        """Initialize the reporter agent."""
        self.is_initialized = True
        logger.info("Reporter agent initialized")

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Generate Deep Thoughts report from all agent contributions.

        Args:
            request: Request containing conversation and agent data

        Returns:
            Response with Deep Thoughts report
        """
        try:
            # Check if this is a phase 2 questions request
            if request.query == "phase2_questions":
                return await self._handle_phase2_questions(request)
            
            # Extract agent contributions from context
            agent_data = request.context.get("agent_contributions", {})
            conversation = request.context.get("conversation", [])

            # Build comprehensive context for synthesis
            synthesis_prompt = self._build_synthesis_prompt(conversation, agent_data)

            # Generate Deep Thoughts report
            report = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": synthesis_prompt}],
                system_prompt=self.system_prompt,
                max_tokens=4096,
                temperature=0.7
            )

            # Format response
            return AgentResponse(
                agent_name=self.name,
                content=report,
                metadata={
                    "report_type": "deep_thoughts",
                    "synthesized_agents": list(agent_data.keys()),
                    "conversation_turns": len(conversation),
                },
                request_id=request.request_id,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Reporter agent error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                content=f"Error generating Deep Thoughts: {str(e)}",
                metadata={},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e),
            )

    async def _handle_phase2_questions(self, request: AgentRequest) -> AgentResponse:
        """Generate phase 2 questions based on conversation context.
        
        Args:
            request: Request containing conversation context
            
        Returns:
            Response with suggested questions and insights
        """
        try:
            conversation = request.context.get("conversation", [])
            crux = request.context.get("crux", "")
            
            # Build prompt for phase 2 question generation
            phase2_prompt = f"""Based on this coaching conversation, I need to suggest the most important area to explore deeper.

CONVERSATION SO FAR:
{self._format_conversation(conversation)}

IDENTIFIED CRUX:
{crux}

Analyze this conversation and provide:
1. Brief insight: What's the most critical aspect of this crux that needs deeper exploration?
2. Key question area: What specific dimension should we probe further?
3. Suggested approach: How should the coach explore this area?

Be concise and focus on what would most help the user make progress on their crux."""

            # Generate phase 2 analysis
            analysis = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": phase2_prompt}],
                system_prompt="You are an expert coaching analyst helping identify the most valuable areas to explore deeper.",
                max_tokens=500,
                temperature=0.5
            )
            
            return AgentResponse(
                agent_name=self.name,
                content=analysis,
                metadata={
                    "response_type": "phase2_questions",
                    "crux": crux,
                },
                request_id=request.request_id,
                timestamp=datetime.now(),
            )
            
        except Exception as e:
            logger.error(f"Phase 2 questions error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                content="I'll explore deeper questions about your challenge.",
                metadata={},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e),
            )

    def _build_synthesis_prompt(
        self, conversation: List[Dict[str, str]], agent_data: Dict[str, Any]
    ) -> str:
        """Build prompt for Deep Thoughts synthesis.

        Args:
            conversation: Conversation history
            agent_data: Contributions from other agents

        Returns:
            Formatted synthesis prompt
        """
        # Format conversation
        conv_text = self._format_conversation(conversation)

        # Format agent contributions
        agent_text = self._format_agent_contributions(agent_data)

        return f"""Generate a Deep Thoughts report synthesizing this coaching session.

## Conversation Transcript
{conv_text}

## Agent Insights
{agent_text}

## Your Task
Create a comprehensive Deep Thoughts report that:
1. Synthesizes key insights from the conversation and agent contributions
2. Identifies the core challenge and potential solutions
3. Highlights relevant personal context and patterns
4. Provides specific, actionable recommendations
5. Concludes with an encouraging reflection

Format as clean markdown with clear sections."""

    def _format_conversation(self, conversation: List[Dict[str, str]]) -> str:
        """Format conversation history for synthesis.

        Args:
            conversation: List of conversation turns

        Returns:
            Formatted conversation text
        """
        if not conversation:
            return "No conversation history available."

        formatted = []
        for turn in conversation:
            role = turn.get("role", "unknown").title()
            content = turn.get("content", "")
            formatted.append(f"**{role}**: {content}")

        return "\n\n".join(formatted)

    def _format_agent_contributions(self, agent_data: Dict[str, Any]) -> str:
        """Format agent contributions for synthesis.

        Args:
            agent_data: Dictionary of agent contributions

        Returns:
            Formatted agent insights
        """
        if not agent_data:
            return "No agent contributions available."

        formatted = []

        # Format each agent's contribution
        for agent_id, data in agent_data.items():
            agent_name = agent_id.replace("_", " ").title()

            if isinstance(data, str):
                content = data
            elif isinstance(data, dict):
                content = data.get("content", str(data))
            else:
                content = str(data)

            formatted.append(f"### {agent_name}\n{content}")

        return "\n\n".join(formatted)

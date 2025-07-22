"""Orchestrator Agent for coordinating multi-agent collaboration in Stage 2."""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse
from src.agents.registry import agent_registry
from src.services.llm_service import AnthropicService
from src.agents.prompts import PromptLoader

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Orchestrates multi-agent collaboration after problem identification."""

    def __init__(self, llm_service: AnthropicService):
        """Initialize the Orchestrator Agent."""
        super().__init__(
            name="orchestrator",
            capabilities=[
                AgentCapability.AGENT_COORDINATION,
                AgentCapability.PARALLEL_EXECUTION,
                AgentCapability.STAGE_MANAGEMENT
            ]
        )
        self.agent_id = "orchestrator"  # For compatibility
        self.active_stage = 1  # Start in Stage 1
        self.problem_identified = False
        self.coordination_history = []
        self.llm_service = llm_service
        self._system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the orchestrator system prompt."""
        try:
            return PromptLoader.load_prompt("orchestrator_agent_prompt")
        except FileNotFoundError:
            logger.error(
                "Orchestrator prompt not found, using fallback"
            )
            return (
                "You are an orchestrator agent coordinating "
                "multi-agent collaboration."
            )

    async def initialize(self) -> None:
        """Initialize the orchestrator agent."""
        logger.info("Orchestrator Agent initialized")

    async def cleanup(self) -> None:
        """Clean up orchestrator resources."""
        self.coordination_history.clear()

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle orchestration requests.

        The orchestrator can:
        1. Check if we should transition from Stage 1 to Stage 2
        2. Coordinate parallel agent queries in Stage 2
        3. Aggregate results for the coach
        """
        query = request.query
        context = request.context or {}

        # Check for stage transition triggers
        if "check_stage_transition" in query:
            should_transition = await self._check_stage_transition(context)
            return AgentResponse(
                agent_name=self.name,
                content=str(should_transition),
                metadata={"current_stage": self.active_stage},
                request_id=request.request_id,
                timestamp=datetime.now()
            )

        # Handle Stage 2 coordination
        if "coordinate_agents" in query:
            if self.active_stage != 2:
                return AgentResponse(
                    agent_name=self.name,
                    content="Not in Stage 2 - coordination not available",
                    metadata={
                        "error": "wrong_stage",
                        "current_stage": self.active_stage
                    },
                    request_id=request.request_id,
                    timestamp=datetime.now()
                )

            # Coordinate parallel agent queries
            aggregated_context = await self._coordinate_stage2_agents(context)
            return AgentResponse(
                agent_name=self.name,
                content="Agent coordination complete",
                metadata=aggregated_context,
                request_id=request.request_id,
                timestamp=datetime.now()
            )

        # Default response
        return AgentResponse(
            agent_name=self.name,
            content="Orchestrator ready",
            metadata={"stage": self.active_stage},
            request_id=request.request_id,
            timestamp=datetime.now()
        )

    async def _check_stage_transition(self, context: Dict[str, Any]) -> bool:
        """Check if we should transition from Stage 1 to Stage 2 using LLM analysis."""
        # Get conversation history
        history = context.get("conversation_history", [])

        # Need at least 3 exchanges (6 messages) for Stage 2
        if len(history) < 6:
            return False

        # Check if coach explicitly requested orchestration
        if context.get("coach_requests_orchestration", False):
            self.active_stage = 2
            self.problem_identified = True
            logger.info("Stage 2 activated: Coach requested orchestration")
            return True

        # Use LLM to analyze conversation for stage transition
        analysis_prompt = f"""
Analyze this conversation and determine if we should transition from Stage 1 \
(single coach) to Stage 2 (multi-agent collaboration).

Conversation history:
{json.dumps(history[-6:], indent=2)}

Provide your analysis in the following JSON format:
{{
  "stage_transition": {{
    "recommended": true/false,
    "reasoning": "Clear explanation of why",
    "confidence": 0.0-1.0
  }}
}}
"""

        try:
            response = await self.llm_service.generate(
                prompt=analysis_prompt,
                system_prompt=self._system_prompt,
                temperature=0.3  # Lower temperature for more consistent decisions
            )

            # Parse LLM response
            result = self._parse_json_response(response)
            if result and "stage_transition" in result:
                transition_data = result["stage_transition"]
                should_transition = transition_data.get("recommended", False)

                if should_transition:
                    self.active_stage = 2
                    self.problem_identified = True
                    logger.info(
                        f"Stage 2 activated by LLM: "
                        f"{transition_data.get('reasoning', 'No reason provided')}"
                    )
                    return True
        except Exception as e:
            logger.error(f"Error in LLM stage transition analysis: {e}")
            # Fall back to simple heuristic
            return self._fallback_stage_check(history)

        return False

    def _fallback_stage_check(self, history: list) -> bool:
        """Simple fallback check if LLM analysis fails."""
        recent_messages = history[-4:]
        problem_indicators = [
            "challenge", "problem", "issue", "struggle", "difficulty",
            "help with", "stuck", "confused", "overwhelmed", "frustrated"
        ]

        user_messages = [msg for msg in recent_messages if msg.get("role") == "user"]
        for msg in user_messages:
            content = msg.get("content", "").lower()
            if any(indicator in content for indicator in problem_indicators):
                if len(content.split()) > 10:
                    return True
        return False

    async def _coordinate_stage2_agents(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to intelligently coordinate agent queries in Stage 2."""
        query_context = context.get("query_context", {})
        user_query = query_context.get("current_focus", "")
        conversation_history = context.get("conversation_history", [])

        # First, use LLM to determine coordination strategy
        strategy_prompt = f"""
Determine the optimal agent coordination strategy for this user query.

User query: {user_query}
Recent conversation context: {json.dumps(conversation_history[-4:], indent=2)}

Available agents:
- memory: Retrieves relevant past conversations and patterns
- personal_content: Accesses user's core beliefs and personal documents
- mcp: Interfaces with external data sources and tools

Provide your strategy in the following JSON format:
{{
  "agent_coordination": {{
    "agents_to_query": ["list of agent names"],
    "query_strategy": "parallel" or "sequential",
    "specific_prompts": {{
      "agent_name": "Specific query for this agent..."
    }}
  }},
  "synthesis_approach": "How to combine the insights from different agents"
}}
"""

        try:
            strategy_response = await self.llm_service.generate(
                prompt=strategy_prompt,
                system_prompt=self._system_prompt,
                temperature=0.5
            )

            strategy = self._parse_json_response(strategy_response)
            if not strategy or "agent_coordination" not in strategy:
                # Fallback to querying all agents
                strategy = {
                    "agent_coordination": {
                        "agents_to_query": ["memory", "personal_content", "mcp"],
                        "specific_prompts": {
                            "memory": (
                                f"Provide relevant context for: {user_query}"
                            ),
                            "personal_content": (
                                f"Provide relevant context for: {user_query}"
                            ),
                            "mcp": (
                                f"Provide relevant context for: {user_query}"
                            )
                        }
                    }
                }

            coordination_info = strategy["agent_coordination"]
            agents_to_query = coordination_info.get("agents_to_query", [])
            specific_prompts = coordination_info.get("specific_prompts", {})

            # Prepare parallel tasks based on LLM strategy
            tasks = []
            for agent_name in agents_to_query:
                agent = agent_registry.get_agent(agent_name)
                if agent:
                    specific_query = specific_prompts.get(
                        agent_name,
                        f"Provide relevant context for: {user_query}"
                    )
                    request = AgentRequest(
                        from_agent=self.agent_id,
                        to_agent=agent_name,
                        query=specific_query,
                        context=query_context
                    )
                    tasks.append(self._query_agent_with_timeout(agent, request))

            # Execute queries
            start_time = datetime.now()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = (datetime.now() - start_time).total_seconds()

            # Aggregate results
            aggregated = {
                "stage": 2,
                "coordination_time": duration,
                "coordination_strategy": strategy,
                "agent_responses": {}
            }

            for agent_name, result in zip(agents_to_query, results):
                if isinstance(result, Exception):
                    logger.error(f"Agent {agent_name} failed: {result}")
                    aggregated["agent_responses"][agent_name] = {
                        "error": str(result),
                        "status": "failed"
                    }
                else:
                    aggregated["agent_responses"][agent_name] = {
                        "content": result.content,
                        "metadata": result.metadata,
                        "status": "success"
                    }

            # Use LLM to synthesize results
            success_responses = [
                r for r in aggregated["agent_responses"].values()
                if r.get("status") == "success"
            ]
            if success_responses:
                synthesis = await self._synthesize_agent_responses(
                    aggregated["agent_responses"],
                    user_query,
                    strategy.get("synthesis_approach", "")
                )
                aggregated["synthesis"] = synthesis

            # Record coordination event
            self.coordination_history.append({
                "timestamp": datetime.now(),
                "query": user_query,
                "agents_queried": agents_to_query,
                "duration": duration,
                "results": len(
                    [r for r in results if not isinstance(r, Exception)]
                )
            })

            return aggregated

        except Exception as e:
            logger.error(f"Error in LLM-driven coordination: {e}")
            # Fallback to simple parallel coordination
            return await self._fallback_coordination(user_query, query_context)

    async def _query_agent_with_timeout(
        self, agent: BaseAgent, request: AgentRequest, timeout: float = 5.0
    ) -> AgentResponse:
        """Query an agent with a timeout to prevent blocking."""
        try:
            return await asyncio.wait_for(
                agent.handle_request(request),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Agent {request.to_agent} timed out after {timeout}s")
            return AgentResponse(
                agent_name=request.to_agent,
                content=f"Agent timed out after {timeout}s",
                metadata={"error": "timeout"},
                request_id=request.request_id,
                timestamp=datetime.now()
            )

    async def _synthesize_agent_responses(
        self,
        agent_responses: Dict[str, Dict[str, Any]],
        user_query: str,
        synthesis_approach: str
    ) -> Dict[str, Any]:
        """Use LLM to synthesize insights from multiple agents."""
        synthesis_prompt = f"""
Synthesize the following agent responses into coherent insights for the user.

User query: {user_query}
Synthesis approach: {synthesis_approach}

Agent responses:
{json.dumps(agent_responses, indent=2)}

Provide a synthesis that:
1. Identifies patterns across different agent insights
2. Resolves any conflicts or contradictions
3. Prioritizes most relevant information
4. Creates a coherent narrative

Return your synthesis as JSON:
{{
  "key_insights": ["insight1", "insight2", ...],
  "patterns_identified": "Description of patterns",
  "recommended_focus": "What the coach should focus on",
  "actionable_elements": ["action1", "action2", ...]
}}
"""

        try:
            response = await self.llm_service.generate(
                prompt=synthesis_prompt,
                system_prompt=self._system_prompt,
                temperature=0.7
            )
            parsed = self._parse_json_response(response)
            return parsed or {"error": "Failed to synthesize"}
        except Exception as e:
            logger.error(f"Error synthesizing responses: {e}")
            return {"error": str(e)}

    async def _fallback_coordination(
        self, user_query: str, query_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback to simple parallel coordination if LLM fails."""
        available_agents = ["memory", "personal_content", "mcp"]
        tasks = []

        for agent_name in available_agents:
            agent = agent_registry.get_agent(agent_name)
            if agent:
                request = AgentRequest(
                    from_agent=self.agent_id,
                    to_agent=agent_name,
                    query=f"Provide relevant context for: {user_query}",
                    context=query_context
                )
                tasks.append(self._query_agent_with_timeout(agent, request))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        aggregated = {
            "stage": 2,
            "agent_responses": {},
            "fallback_mode": True
        }

        for agent_name, result in zip(available_agents, results):
            if isinstance(result, Exception):
                aggregated["agent_responses"][agent_name] = {
                    "error": str(result),
                    "status": "failed"
                }
            else:
                aggregated["agent_responses"][agent_name] = {
                    "content": result.content,
                    "metadata": result.metadata,
                    "status": "success"
                }

        return aggregated

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        try:
            # Try direct JSON parsing first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            import re
            json_match = re.search(
                r'```(?:json)?\s*({[^`]+})\s*```', response, re.DOTALL
            )
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try to find JSON-like content (handling nested objects)
            # Use balanced brace counting approach
            brace_count = 0
            start_idx = None
            for i, char in enumerate(response):
                if char == '{':
                    if start_idx is None:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx is not None:
                        try:
                            json_str = response[start_idx:i+1]
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            # Reset and continue looking
                            start_idx = None

        logger.warning(
            f"Failed to parse JSON from response: {response[:200]}..."
        )
        return None

    def get_stage_info(self) -> Dict[str, Any]:
        """Get current stage information."""
        return {
            "current_stage": self.active_stage,
            "problem_identified": self.problem_identified,
            "coordination_count": len(self.coordination_history),
            "last_coordination": (
                self.coordination_history[-1]["timestamp"].isoformat()
                if self.coordination_history else None
            ),
            "llm_enabled": True
        }

"""Orchestrator Agent for coordinating multi-agent collaboration in Stage 2."""

import asyncio
import json
from typing import Dict, Any, Optional, List
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
            response = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": analysis_prompt}],
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
            strategy_response = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": strategy_prompt}],
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
                timestamp=datetime.now(),
                error="timeout"
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
            response = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": synthesis_prompt}],
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

    async def coordinate_stage3_synthesis(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate all Stage 3 agent contributions for Deep Thoughts synthesis.

        This method:
        1. Gathers contributions from all relevant agents (memory, personal, MCP)
        2. Analyzes what additional information is needed
        3. Coordinates any necessary web searches
        4. Prepares a unified brief for the reporter agent
        5. Manages all error handling and retries

        Args:
            context: Conversation history and other context

        Returns:
            Dictionary with all agent contributions and coordination metadata
        """
        try:
            conversation = context.get("conversation", [])

            # Gather agent contributions
            agent_contributions = await self._gather_stage3_agent_contributions(
                conversation
            )

            # Generate initial report
            initial_report = await self._generate_initial_report(
                conversation, agent_contributions
            )

            # Coordinate web search if needed
            web_search_results = await self._coordinate_web_search_if_needed(
                initial_report, context
            )

            # Prepare unified synthesis brief
            synthesis_brief = self._prepare_synthesis_brief(
                agent_contributions,
                initial_report,
                web_search_results
            )

            return synthesis_brief

        except Exception as e:
            logger.error(f"Stage 3 coordination error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback": "Direct agent calls recommended"
            }

    async def _gather_stage3_agent_contributions(
        self, conversation: list
    ) -> Dict[str, str]:
        """Gather contributions from all relevant Stage 3 agents.

        Args:
            conversation: The conversation history

        Returns:
            Dictionary of agent contributions
        """
        agent_contributions = {}

        # Define agents and their queries
        agent_queries = [
            {
                "name": "memory",
                "query": "Provide relevant past conversation insights for synthesis",
                "timeout": 5.0
            },
            {
                "name": "personal_content",
                "query": "Provide relevant personal context and beliefs",
                "timeout": 5.0
            },
            {
                "name": "mcp",
                "query": "Provide relevant tasks and external context for synthesis",
                "timeout": 3.0,
                "filter_empty": "No relevant tasks"
            }
        ]

        for agent_info in agent_queries:
            logger.info(f"Stage 3: Gathering {agent_info['name']} contributions...")
            agent = agent_registry.get_agent(agent_info["name"])
            if not agent:
                continue

            request = AgentRequest(
                from_agent=self.agent_id,
                to_agent=agent_info["name"],
                query=agent_info["query"],
                context={"conversation": conversation}
            )

            response = await self._query_agent_with_timeout(
                agent, request, timeout=agent_info.get("timeout", 5.0)
            )

            if response and not response.error:
                # Check for filter condition
                if filter_text := agent_info.get("filter_empty"):
                    if filter_text not in response.content:
                        agent_contributions[agent_info["name"]] = response.content
                else:
                    agent_contributions[agent_info["name"]] = response.content

        return agent_contributions

    async def _generate_initial_report(
        self, conversation: list, agent_contributions: Dict[str, str]
    ) -> str:
        """Generate initial Deep Thoughts report using Reporter agent.

        Args:
            conversation: The conversation history
            agent_contributions: Contributions from other agents

        Returns:
            The initial report content or empty string if unavailable
        """
        logger.info("Stage 3: Generating initial Deep Thoughts report...")
        reporter = agent_registry.get_agent("reporter")
        if not reporter:
            logger.warning("Reporter agent not available")
            return ""

        reporter_request = AgentRequest(
            from_agent=self.agent_id,
            to_agent="reporter",
            query="Generate Deep Thoughts report",
            context={
                "conversation": conversation,
                "agent_contributions": agent_contributions
            }
        )

        reporter_response = await reporter.handle_request(reporter_request)
        return reporter_response.content if reporter_response else ""

    async def _coordinate_web_search_if_needed(
        self, initial_report: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate web search if the report indicates it's needed.

        Args:
            initial_report: The initial Deep Thoughts report
            context: Additional context

        Returns:
            Web search results or empty dict if not needed
        """
        if not initial_report:
            return {}

        logger.info("Stage 3: Coordinating web search for articles...")
        search_coordination = await self.coordinate_phase3_search(
            initial_report, context
        )

        if search_coordination.get("status") == "success":
            return search_coordination

        return {}

    def _prepare_synthesis_brief(
        self,
        agent_contributions: Dict[str, str],
        initial_report: str,
        web_search_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare the final synthesis brief with all gathered information.

        Args:
            agent_contributions: Contributions from agents
            initial_report: The initial report
            web_search_results: Results from web search

        Returns:
            The complete synthesis brief
        """
        return {
            "status": "success",
            "agent_contributions": agent_contributions,
            "initial_report": initial_report,
            "web_search_results": web_search_results,
            "coordination_metadata": {
                "stage": "stage3_synthesis",
                "timestamp": datetime.now().isoformat(),
                "agents_queried": list(agent_contributions.keys()),
                "web_search_performed": bool(web_search_results)
            }
        }

    async def coordinate_phase3_search(
        self, report_content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate Phase 3 web search for Deep Thoughts report.

        This method handles web search coordination as part of Stage 3.
        Now called by coordinate_stage3_synthesis for unified coordination.

        Args:
            report_content: The Deep Thoughts report content
            context: Additional context from the conversation

        Returns:
            Dictionary with search results and coordination metadata
        """
        try:
            # Extract search markers or themes from report
            search_needs = await self._analyze_search_needs(report_content)

            if not search_needs:
                return {
                    "status": "no_search_needed",
                    "message": "No web search required for this report"
                }

            # Generate specific search queries
            search_queries = await self._generate_search_queries(
                search_needs, context
            )

            # Coordinate with web search agent
            search_results = await self._execute_searches_with_retry(
                search_queries
            )

            # Prepare structured brief for Deep Thoughts
            structured_brief = await self._prepare_search_brief(
                search_results, search_needs
            )

            return {
                "status": "success",
                "search_results": search_results,
                "structured_brief": structured_brief,
                "queries_executed": len(search_queries),
                "coordination_metadata": {
                    "stage": "phase3",
                    "timestamp": datetime.now().isoformat(),
                    "search_needs": search_needs
                }
            }

        except Exception as e:
            logger.error(f"Phase 3 coordination error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback": "Manual search recommended"
            }

    async def _analyze_search_needs(self, report_content: str) -> List[str]:
        """Analyze report to identify search needs."""
        # Look for NEEDS_WEBSEARCH markers
        import re
        pattern = r'\[NEEDS_WEBSEARCH:\s*([^\]]+)\]'
        matches = re.findall(pattern, report_content)

        if matches:
            return [match.strip() for match in matches]

        # If no markers, use LLM to identify search needs
        analysis_prompt = f"""Analyze this Deep Thoughts report and identify 2-3 topics
that would benefit from external research articles:

{report_content[:2000]}

Return only the topics as a simple list, one per line."""

        try:
            response = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=200
            )

            topics = [
                line.strip() for line in response.split('\n')
                if line.strip() and not line.startswith('-')
            ]
            return topics[:3]
        except Exception as e:
            logger.error(f"Error analyzing search needs: {e}")
            return []

    async def _generate_search_queries(
        self, search_needs: List[str], context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate specific search queries for identified needs."""
        queries = []

        for need in search_needs:
            # Generate optimized search query
            query_prompt = f"""Generate an optimized web search query for finding
high-quality articles about: {need}

Consider the coaching context and focus on practical, actionable content.
Return just the search query, nothing else."""

            try:
                optimized_query = await self.llm_service.generate_response(
                    messages=[{"role": "user", "content": query_prompt}],
                    temperature=0.3,
                    max_tokens=100
                )

                queries.append({
                    "original_need": need,
                    "search_query": optimized_query.strip(),
                    "retry_count": 0
                })
            except Exception as e:
                logger.error(f"Error generating query for '{need}': {e}")
                # Fallback to basic query
                queries.append({
                    "original_need": need,
                    "search_query": f"{need} best practices articles",
                    "retry_count": 0
                })

        return queries

    async def _execute_searches_with_retry(
        self, queries: List[Dict[str, str]], max_retries: int = 2
    ) -> List[Dict[str, Any]]:
        """Execute searches with retry logic and error handling."""
        from src.agents.registry import agent_registry

        # Try to get Claude web search agent first, fallback to regular
        search_agent = agent_registry.get_agent("claude_web_search")
        if not search_agent:
            search_agent = agent_registry.get_agent("web_search")

        if not search_agent:
            logger.error("No web search agent available")
            return []

        results = []

        for query_info in queries:
            retry_count = 0
            success = False

            while retry_count <= max_retries and not success:
                try:
                    request = AgentRequest(
                        from_agent=self.agent_id,
                        to_agent=search_agent.name,
                        query="search",
                        context={
                            "queries": [query_info["search_query"]],
                            "max_articles_per_theme": 3
                        },
                        request_id=f"phase3_search_{datetime.now().timestamp()}"
                    )

                    response = await search_agent.handle_request(request)

                    if response.error:
                        raise Exception(response.error)

                    results.append({
                        "query": query_info["search_query"],
                        "original_need": query_info["original_need"],
                        "results": response.content,
                        "metadata": response.metadata,
                        "success": True
                    })
                    success = True

                except Exception as e:
                    retry_count += 1
                    logger.warning(
                        f"Search failed for '{query_info['search_query']}' "
                        f"(attempt {retry_count}/{max_retries}): {e}"
                    )

                    if retry_count <= max_retries:
                        # Modify query for retry
                        query_info["search_query"] = await self._modify_query_for_retry(
                            query_info["search_query"], str(e)
                        )
                        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                    else:
                        results.append({
                            "query": query_info["search_query"],
                            "original_need": query_info["original_need"],
                            "results": None,
                            "error": str(e),
                            "success": False
                        })

        return results

    async def _modify_query_for_retry(self, original_query: str, error: str) -> str:
        """Modify search query based on error for retry."""
        if "rate limit" in error.lower():
            # Don't modify for rate limits, just wait
            return original_query
        elif "no results" in error.lower():
            # Broaden the query
            return f"{original_query} OR guidance OR strategies"
        else:
            # Simplify the query
            words = original_query.split()[:5]  # Take first 5 words
            return " ".join(words)

    async def _prepare_search_brief(
        self, search_results: List[Dict[str, Any]], search_needs: List[str]
    ) -> Dict[str, Any]:
        """Prepare structured brief from search results for Deep Thoughts."""
        successful_results = [r for r in search_results if r.get("success")]
        failed_searches = [r for r in search_results if not r.get("success")]

        # Organize results by theme
        organized_results = {}
        for result in successful_results:
            need = result["original_need"]
            organized_results[need] = {
                "content": result["results"],
                "metadata": result.get("metadata", {})
            }

        # Deduplicate and prioritize
        brief = {
            "search_summary": {
                "total_searches": len(search_results),
                "successful": len(successful_results),
                "failed": len(failed_searches)
            },
            "organized_results": organized_results,
            "key_articles": await self._extract_key_articles(successful_results),
            "failed_searches": [
                {
                    "need": f["original_need"],
                    "error": f.get("error", "Unknown error")
                }
                for f in failed_searches
            ],
            "prepared_at": datetime.now().isoformat()
        }

        return brief

    async def _extract_key_articles(
        self, results: List[Dict[str, Any]], max_articles: int = 9
    ) -> List[Dict[str, str]]:
        """Extract and deduplicate key articles from all results."""
        articles = []
        seen_urls = set()

        for result in results:
            content = result.get("results", "")
            # Simple extraction of URLs and titles
            lines = content.split('\n')

            for i, line in enumerate(lines):
                if "URL:" in line or "http" in line:
                    # Try to extract URL
                    import re
                    url_match = re.search(r'https?://[^\s\)]+', line)
                    if url_match:
                        url = url_match.group(0).rstrip('.,;)')
                        if url not in seen_urls:
                            # Try to get title from previous line
                            title = "Article"
                            if i > 0:
                                title_line = lines[i-1]
                                # Extract title from markdown format
                                title_match = re.search(
                                    r'\*\*"?([^"*]+)"?\*\*', title_line
                                )
                                if title_match:
                                    title = title_match.group(1)

                            articles.append({
                                "title": title,
                                "url": url,
                                "theme": result.get("original_need", "General")
                            })
                            seen_urls.add(url)

                            if len(articles) >= max_articles:
                                return articles

        return articles

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

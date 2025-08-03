"""Enhanced Diary Coach agent with multi-agent collaboration capabilities."""

import os
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import logging

from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse
from src.events.schemas import UserMessage, AgentResponse as LegacyAgentResponse
from src.services.llm_service import AnthropicService
from src.agents.prompts import get_coach_system_prompt, get_coach_morning_protocol
from src.agents.registry import agent_registry
from src.agents.morning_protocol_tracker import MorningProtocolTracker

# Try to import LangSmith for tracing
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    # Create a no-op decorator if LangSmith is not available
    def traceable(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator
    LANGSMITH_AVAILABLE = False


logger = logging.getLogger(__name__)


class EnhancedDiaryCoach(BaseAgent):
    """Enhanced coach with ability to call other agents during Stage 1."""

    @property
    def SYSTEM_PROMPT(self) -> str:
        """Load the system prompt from the master prompt file."""
        base_prompt = get_coach_system_prompt()
        # Add agent context enhancement
        try:
            with open("src/agents/prompts/coach_agent_context.md", "r") as f:
                context_enhancement = f.read()
            return base_prompt + "\n\n" + context_enhancement
        except Exception:
            return base_prompt

    @property
    def MORNING_PROMPT_ADDITION(self) -> str:
        """Load the morning protocol from the master prompt file."""
        return get_coach_morning_protocol()

    def __init__(self, llm_service: AnthropicService):
        """Initialize the enhanced diary coach.

        Args:
            llm_service: Anthropic service for LLM calls
        """
        super().__init__(
            name="coach",
            capabilities=[AgentCapability.CONVERSATION]
        )
        self.llm_service = llm_service
        self.conversation_state = "general"  # general, morning
        self.morning_challenge: Optional[str] = None
        self.morning_value: Optional[str] = None
        self.message_history: List[Dict[str, str]] = []
        self.crux_identified: Optional[str] = None
        self.phase2_active = False
        
        # Morning protocol tracking
        self.protocol_tracker = MorningProtocolTracker(self.MORNING_PROMPT_ADDITION)
        self._next_nudge = None  # Store nudge for next generation

        # Agent collaboration tracking
        self.agent_call_history: List[Dict[str, Any]] = []
        self.max_agent_calls_per_turn = 2  # Prevent over-calling
        self.recent_agent_calls: Set[str] = set()  # Track recent calls

        # Check if multi-agent mode is enabled
        self.multi_agent_enabled = (
            os.getenv("DISABLE_MULTI_AGENT", "false").lower() != "true"
        )

        # Stage management
        self.current_stage = 1  # Start in Stage 1 (exploration)
        self.problem_identified = False

    async def initialize(self) -> None:
        """Initialize the coach agent."""
        self.is_initialized = True
        logger.info("Enhanced coach agent initialized with multi-agent support")

    def _is_morning_context(self, message_content: str) -> bool:
        """Check if user is in morning context based on their message."""
        morning_greetings = [
            "good morning", "morning", "gm", "g'morning",
            "goodmorning", "mornin"
        ]
        content_lower = message_content.lower().strip()
        return any(greeting in content_lower for greeting in morning_greetings)

    def _get_system_prompt(self) -> str:
        """Get the appropriate system prompt based on conversation context."""
        base_prompt = self.SYSTEM_PROMPT
        
        # Check if we're in morning conversation mode
        if self.conversation_state == "morning":
            morning_prompt = base_prompt + "\n\n" + self.MORNING_PROMPT_ADDITION
            # Add nudge if we have one
            if self._next_nudge:
                logger.info(f"Adding nudge to prompt: {self._next_nudge[:50]}...")
                morning_prompt += self._next_nudge
                self._next_nudge = None  # Use once then clear
            return morning_prompt
        
        # Also check recent messages for morning context
        elif self.message_history:
            # Check last few user messages for morning greeting
            recent_user_messages = [
                msg for msg in self.message_history[-6:]
                if msg.get("role") == "user"
            ]
            if any(self._is_morning_context(msg["content"])
                   for msg in recent_user_messages):
                return base_prompt + "\n\n" + self.MORNING_PROMPT_ADDITION
        
        return base_prompt

    async def _should_call_agent(
        self, agent_type: str, message_content: str
    ) -> bool:
        """Determine if an agent should be called based on message content.

        Args:
            agent_type: Type of agent (memory, personal_content, mcp)
            message_content: User's message content

        Returns:
            Boolean indicating if agent should be called
        """
        content_lower = message_content.lower()

        # Check if we've called this agent recently
        if agent_type in self.recent_agent_calls:
            logger.debug(f"Skipping {agent_type} - called recently")
            return False

        # Agent-specific triggers
        if agent_type == "memory":
            triggers = [
                "remember when", "last time", "previously", "before",
                "past conversation", "we discussed", "you mentioned"
            ]
            should_call = any(trigger in content_lower for trigger in triggers)

        elif agent_type == "personal_content":
            triggers = [
                "belief", "value", "core", "philosophy", "principle",
                "my approach", "I believe", "important to me"
            ]
            should_call = any(trigger in content_lower for trigger in triggers)

        elif agent_type == "mcp":
            triggers = [
                "task", "todo", "priorit", "should i work", "what to do",
                "today", "deadline", "project", "focus on", "tackle"
            ]
            should_call = any(trigger in content_lower for trigger in triggers)
        else:
            should_call = False

        logger.debug(
            f"Should call {agent_type}? {should_call} "
            f"(message: {message_content[:50]}...)")
        return should_call

    @traceable(name="call_agent")
    async def _call_agent(
        self, agent_name: str, query: str, context: Dict[str, Any]
    ) -> Optional[AgentResponse]:
        """Call another agent and get response.

        Args:
            agent_name: Name of agent to call
            query: Query for the agent
            context: Context to pass to agent

        Returns:
            Agent response or None if failed
        """
        # Return None if multi-agent is disabled
        if not self.multi_agent_enabled:
            return None

        try:
            agent = agent_registry.get_agent(agent_name)
            if not agent:
                logger.warning(f"Agent {agent_name} not found in registry")
                return None

            request = AgentRequest(
                from_agent=self.name,
                to_agent=agent_name,
                query=query,
                context=context
            )

            response = await agent.handle_request(request)

            # Track the call
            self.agent_call_history.append({
                "timestamp": datetime.now(),
                "agent": agent_name,
                "query": query,
                "success": response.error is None
            })

            # Mark as recently called
            self.recent_agent_calls.add(agent_name)

            return response

        except Exception as e:
            logger.error(f"Error calling agent {agent_name}: {e}")
            return None

    def _should_check_orchestration(self, message: UserMessage) -> bool:
        """Determine if we should check for orchestration based on complexity.

        Args:
            message: The user message to analyze

        Returns:
            True if message indicates complex needs requiring orchestration
        """
        # Skip orchestration for morning protocol conversations unless complex
        if self.conversation_state == "morning" and not self.problem_identified:
            return False

        # Need more messages before considering orchestration
        if len(self.message_history) < 10:  # Increased from implicit 6
            return False

        # Check for complexity indicators in message
        message_lower = message.content.lower()
        complexity_indicators = [
            "help me figure out",
            "i'm struggling with",
            "multiple issues",
            "everything feels",
            "overwhelmed",
            "complex problem",
            "deep dive",
            "analyze thoroughly",
            "comprehensive",
            "let's explore",
            "can we dig into"
        ]

        # If user explicitly asks for deeper analysis
        if any(indicator in message_lower for indicator in complexity_indicators):
            return True

        # If coach explicitly identified a complex problem
        if self.problem_identified and "complex" in str(self.morning_challenge).lower():
            return True

        return False

    async def _check_stage_transition(self) -> bool:
        """Check with orchestrator if we should transition to Stage 2.

        Returns:
            True if we should transition to Stage 2
        """
        if not self.multi_agent_enabled or self.current_stage == 2:
            return False

        # Check if orchestrator is available
        orchestrator = agent_registry.get_agent("orchestrator")
        if not orchestrator:
            return False

        # Build conversation history for orchestrator
        conversation_history = []
        for i in range(0, len(self.message_history), 2):
            if i < len(self.message_history):
                conversation_history.append(self.message_history[i])
            if i + 1 < len(self.message_history):
                conversation_history.append(self.message_history[i + 1])

        # Ask orchestrator about stage transition
        request = AgentRequest(
            from_agent=self.name,
            to_agent="orchestrator",
            query="check_stage_transition",
            context={
                "conversation_history": conversation_history,
                "coach_requests_orchestration": self.problem_identified
            }
        )

        try:
            response = await orchestrator.handle_request(request)
            should_transition = response.content.lower() == "true"

            if should_transition:
                self.current_stage = 2
                logger.info("Transitioned to Stage 2 - Orchestrated gathering")

            return should_transition
        except Exception as e:
            logger.error(f"Error checking stage transition: {e}")
            return False

    async def _gather_stage2_context(self, message: UserMessage) -> Dict[str, Any]:
        """Gather context using orchestrator in Stage 2.

        Args:
            message: User message

        Returns:
            Aggregated context from all agents
        """
        orchestrator = agent_registry.get_agent("orchestrator")
        if not orchestrator:
            logger.warning("Orchestrator not available for Stage 2")
            return {}

        request = AgentRequest(
            from_agent=self.name,
            to_agent="orchestrator",
            query="coordinate_agents",
            context={
                "query_context": {
                    "current_focus": message.content,
                    "conversation_id": message.conversation_id,
                    "message_history": self.message_history[-10:]  # Last 10 messages
                }
            }
        )

        try:
            response = await orchestrator.handle_request(request)

            if response.metadata and "agent_responses" in response.metadata:
                # Convert orchestrator format to our expected format
                agent_context = {}
                responses = response.metadata["agent_responses"]
                for agent_name, agent_data in responses.items():
                    if agent_data["status"] == "success":
                        agent_context[agent_name] = {
                            "content": agent_data["content"],
                            "metadata": agent_data.get("metadata", {})
                        }

                logger.info(
                    f"Stage 2: Gathered context from {len(agent_context)} agents"
                )
                return agent_context

            return {}

        except Exception as e:
            logger.error(f"Error in Stage 2 context gathering: {e}")
            return {}

    @traceable(name="gather_agent_context")
    async def _gather_agent_context(
        self, message: UserMessage
    ) -> Dict[str, Any]:
        """Gather context from relevant agents based on message.

        Args:
            message: User message to analyze

        Returns:
            Dictionary of agent contexts
        """
        agent_context = {}
        calls_made = 0

        # Check if we should transition to Stage 2 - only if complexity detected
        if self.current_stage == 1 and self._should_check_orchestration(message):
            await self._check_stage_transition()

        # Stage 2: Use orchestrator for coordination
        if self.current_stage == 2:
            return await self._gather_stage2_context(message)

        # Stage 1: Direct agent calls based on triggers
        agents_to_call = []

        if await self._should_call_agent("memory", message.content):
            agents_to_call.append(("memory", "memory"))

        if await self._should_call_agent("personal_content", message.content):
            agents_to_call.append(("personal_content", "personal_content"))

        if await self._should_call_agent("mcp", message.content):
            agents_to_call.append(("mcp", "mcp"))

        # Limit calls per turn
        agents_to_call = agents_to_call[:self.max_agent_calls_per_turn]

        # Make the calls
        for agent_name, context_key in agents_to_call:
            if calls_made >= self.max_agent_calls_per_turn:
                break

            # Prepare query with date context for MCP agent
            query = message.content
            if agent_name == "mcp":
                content_lower = message.content.lower()
                # Check if user is asking about today/priorities
                keywords = ["today", "priorit", "should i work", "focus"]
                if any(word in content_lower for word in keywords):
                    # Enhance query to explicitly ask for today's tasks
                    query = (
                        f"{message.content} (focus on tasks due today)")

            response = await self._call_agent(
                agent_name,
                query,
                {
                    "conversation_id": message.conversation_id,
                    "messages": self.message_history[-5:],  # Last 5 messages
                    # Add today's date
                    "current_date": datetime.now().date().isoformat()
                }
            )

            if response and not response.error:
                agent_context[context_key] = {
                    "content": response.content,
                    "metadata": response.metadata
                }
                calls_made += 1

        return agent_context

    def _should_consult_reporter_for_phase2(self, message: UserMessage) -> bool:
        """Check if we should consult reporter for phase 2 questions.
        
        Args:
            message: User message
            
        Returns:
            True if we should consult reporter for phase 2 insights
        """
        # Check if user accepted deeper questions
        message_lower = message.content.lower()
        acceptance_phrases = [
            "yes", "sure", "ok", "okay", "ready", "let's do it",
            "i'm ready", "sounds good", "go ahead", "deeper questions"
        ]
        
        # Check if we're in morning protocol and have identified a crux
        if (self.conversation_state == "morning" and 
            self.crux_identified and 
            any(phrase in message_lower for phrase in acceptance_phrases)):
            # Look for context suggesting phase 2
            recent_assistant = self.message_history[-1] if self.message_history else None
            if recent_assistant and recent_assistant.get("role") == "assistant":
                content = recent_assistant["content"].lower()
                if "deeper questions" in content or "deep report now" in content:
                    return True
        
        return False
    
    async def _get_reporter_phase2_insights(self, message: UserMessage) -> str:
        """Get phase 2 insights from reporter agent.
        
        Args:
            message: User message
            
        Returns:
            Reporter's insights for phase 2 questioning
        """
        try:
            # Get reporter from registry
            reporter = agent_registry.get_agent("reporter")
            if not reporter:
                logger.warning("Reporter agent not available for phase 2")
                return ""
            
            # Build conversation context
            conversation = []
            for msg in self.message_history[-10:]:  # Last 10 messages
                conversation.append({
                    "type": msg["role"],
                    "content": msg["content"]
                })
            
            # Call reporter for phase 2 insights
            request = AgentRequest(
                from_agent=self.name,
                to_agent="reporter",
                query="phase2_questions",
                context={
                    "conversation": conversation,
                    "crux": self.crux_identified or "",
                    "conversation_id": message.conversation_id
                }
            )
            
            response = await reporter.handle_request(request)
            
            if response and not response.error:
                self.phase2_active = True
                return response.content
            
            return ""
            
        except Exception as e:
            logger.error(f"Error getting phase 2 insights: {e}")
            return ""

    def _enhance_prompt_with_context(
        self, base_prompt: str, agent_context: Dict[str, Any]
    ) -> str:
        """Enhance the system prompt with agent context.

        Args:
            base_prompt: Base system prompt
            agent_context: Context from agents

        Returns:
            Enhanced prompt
        """
        if not agent_context:
            return base_prompt

        context_sections = []

        if "memory" in agent_context:
            context_sections.append(
                f"RELEVANT PAST CONVERSATIONS:\n{agent_context['memory']['content']}"
            )

        if "personal_content" in agent_context:
            context_sections.append(
                f"PERSONAL CONTEXT:\n{agent_context['personal_content']['content']}"
            )

        if "mcp" in agent_context:
            context_sections.append(
                f"CURRENT TASKS:\n{agent_context['mcp']['content']}"
            )

        if context_sections:
            context_block = "\n\n".join(context_sections)
            return (
                f"{base_prompt}\n\n"
                f"## IMPORTANT: Current Context from Agents\n\n"
                f"{context_block}\n\n"
                f"## Context Usage Instructions:\n"
                f"- When user asks 'what should I work on' or about tasks: "
                f"Reference the ACTUAL tasks above, not examples\n"
                f"- When user asks about beliefs/values: Use the ACTUAL personal "
                f"context above\n"
                f"- Integrate this real data naturally into your coaching questions\n"
                f"- NEVER make up example tasks or beliefs when real data is provided"
            )

        return base_prompt

    @traceable(name="enhanced_coach_process_message")
    async def process_message(self, message: UserMessage) -> LegacyAgentResponse:
        """Process a user message and generate a coaching response.

        Args:
            message: The user's message

        Returns:
            The coach's response
        """
        logger.info(
            f"EnhancedDiaryCoach.process_message: {message.content}")

        # Check and update conversation state BEFORE generating response
        if (self._is_morning_context(message.content) and
                self.conversation_state == "general"):
            self.conversation_state = "morning"
            logger.info("Entering morning conversation mode")

        # Update message history
        self.message_history.append({
            "role": "user",
            "content": message.content
        })

        # Check if we need phase 2 reporter insights
        if self._should_consult_reporter_for_phase2(message):
            reporter_insights = await self._get_reporter_phase2_insights(message)
            logger.info(f"Phase 2 reporter insights: {reporter_insights[:100]}...")
            # Store insights for prompt enhancement
            self._phase2_insights = reporter_insights
        
        # Gather context from agents if in Stage 1
        agent_context = await self._gather_agent_context(message)

        # Get base system prompt (includes nudge if available)
        base_prompt = self._get_system_prompt()

        # Enhance prompt with agent context
        system_prompt = self._enhance_prompt_with_context(base_prompt, agent_context)
        
        # Add phase 2 insights if available
        if hasattr(self, '_phase2_insights') and self._phase2_insights:
            system_prompt += f"\n\n## PHASE 2 COACHING INSIGHTS\n{self._phase2_insights}\n"
            system_prompt += "\nUse these insights to ask deeper, more targeted questions about the crux."
            # Clear insights after use
            self._phase2_insights = None

        # Debug logging
        logger.info(f"Enhanced coach: agents_called={list(agent_context.keys())}")
        logger.info(f"Conversation state: {self.conversation_state}")
        if agent_context:
            logger.info("Agent context being used in prompt")
            for agent, data in agent_context.items():
                logger.info(f"  {agent}: {data['content'][:100]}...")
            
        # Generate response
        response_content = await self.llm_service.generate_response(
            messages=self.message_history,
            system_prompt=system_prompt,
            max_tokens=200,
            temperature=0.7
        )

        # Update message history
        self.message_history.append({
            "role": "assistant",
            "content": response_content
        })
        
        # Track crux identification
        if "crux" in response_content.lower() and "identified" in response_content.lower():
            # Extract crux from response
            import re
            crux_match = re.search(r'crux[^:]*:([^.!?]+)', response_content, re.IGNORECASE)
            if crux_match:
                self.crux_identified = crux_match.group(1).strip()
                logger.info(f"Crux identified: {self.crux_identified}")

        # Now check if we need a nudge for next time
        if self.conversation_state == "morning":
            # Analyze the exchange that just happened
            nudge = self.protocol_tracker.analyze_exchange(
                message.content, 
                response_content
            )
            if nudge:
                # Store nudge for next generation
                self._next_nudge = nudge
                logger.info(f"Morning protocol nudge prepared: {nudge[:50]}...")
                logger.info(f"Protocol state: {self.protocol_tracker.current_state}")

        # Clear recent calls periodically (every 3 turns)
        # 3 user + 3 assistant messages
        if len(self.message_history) % 6 == 0:
            self.recent_agent_calls.clear()

        # Store metadata for testing
        self._last_response_metadata = {
            "conversation_state": self.conversation_state,
            "morning_challenge": self.morning_challenge,
            "morning_value": self.morning_value,
            "agents_called": list(agent_context.keys()),
            "agent_calls_made": len(agent_context),
            "current_stage": self.current_stage,
            "problem_identified": self.problem_identified
        }

        return LegacyAgentResponse(
            agent_name=self.name,
            content=response_content,
            response_to=message.message_id,
            timestamp=datetime.now(),
            conversation_id=message.conversation_id
        )

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle a request from another agent or the orchestrator."""
        try:
            # Convert to UserMessage
            user_message = UserMessage(
                content=request.query,
                user_id=request.context.get("user_id", "michael"),
                conversation_id=request.context.get("conversation_id", "default"),
                message_id=request.context.get(
                    "message_id", str(datetime.now().timestamp())
                ),
                timestamp=datetime.fromisoformat(
                    request.context.get("timestamp", datetime.now().isoformat())
                )
            )

            # Process through enhanced method
            legacy_response = await self.process_message(user_message)

            # Convert back with metadata
            metadata = getattr(self, '_last_response_metadata', {})
            return AgentResponse(
                agent_name=self.name,
                content=legacy_response.content,
                metadata=metadata,
                request_id=request.request_id,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in enhanced coach: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="I'm having trouble processing your request right now.",
                metadata={},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e)
            )

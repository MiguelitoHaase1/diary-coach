"""Diary Coach agent implementation with Michael's coaching prompt."""

from typing import List, Dict, Any, Optional
from datetime import datetime, time
from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse
from src.events.schemas import UserMessage
from src.services.llm_service import AnthropicService
from src.agents.prompts import get_coach_system_prompt, get_coach_morning_protocol
from src.orchestration.mcp_todo_node import MCPTodoNode
from src.orchestration.context_state import ContextState


class DiaryCoach(BaseAgent):
    """Michael's personal Daily Transformation Diary Coach."""

    @property
    def SYSTEM_PROMPT(self) -> str:
        """Load the system prompt from the master prompt file."""
        return get_coach_system_prompt()

    @property
    def MORNING_PROMPT_ADDITION(self) -> str:
        """Load the morning protocol from the master prompt file."""
        return get_coach_morning_protocol()

    def __init__(self, llm_service: AnthropicService):
        """Initialize the diary coach.

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
        self.mcp_todo_node = MCPTodoNode()  # Real MCP integration

    def _is_morning_time(self) -> bool:
        """Check if current time is morning (6:00 AM - 11:59 AM)."""
        current_time = datetime.now().time()
        morning_start = time(6, 0)  # 6:00 AM
        morning_end = time(11, 59)  # 11:59 AM
        return morning_start <= current_time <= morning_end

    def _get_system_prompt(self) -> str:
        """Get the appropriate system prompt based on time of day."""
        base_prompt = self.SYSTEM_PROMPT
        if self._is_morning_time():
            return base_prompt + "\n\n" + self.MORNING_PROMPT_ADDITION
        return base_prompt

    async def _get_todo_context(
        self, message: UserMessage
    ) -> Optional[List[Dict[str, Any]]]:
        """Get relevant todos based on message content."""
        try:
            # Check if the message is asking about tasks/priorities
            content_lower = message.content.lower()
            task_keywords = [
                "prioritize", "today", "should", "work", "task", "do",
                "list", "priority", "focus", "challenge", "important",
                "tackle", "problem", "goal"
            ]

            # Calculate relevance score
            relevance_score = sum(
                0.15 for keyword in task_keywords if keyword in content_lower
            )
            relevance_score = min(relevance_score, 1.0)

            if relevance_score >= 0.3:  # Lower threshold for direct integration
                # Create a context state for MCP fetching
                state = ContextState(
                    messages=[{
                        "type": "user",
                        "content": message.content,
                        "timestamp": datetime.now().isoformat()
                    }],
                    context_relevance={"todos": relevance_score},
                    conversation_id=message.conversation_id
                )

                # Fetch todos using MCP
                result_state = await self.mcp_todo_node.fetch_todos(state)
                return result_state.todo_context
            else:
                return None
        except Exception:
            # Log error but don't break the conversation
            return None

    def _get_system_prompt_with_context(
        self, todo_context: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Enhance system prompt with todo context if available."""
        base_prompt = self._get_system_prompt()

        if not todo_context:
            return base_prompt

        # Format todos for context
        context_items = []
        if todo_context:
            formatted_todos = "\n".join([
                f"- {todo.get('content', 'No content')} "
                f"[{todo.get('priority', 'normal')} priority]"
                for todo in todo_context[:5]  # Limit to top 5
            ])
            num_todos = len(todo_context)
            context_items.append(
                f"Current Tasks ({num_todos} items):\n{formatted_todos}"
            )

        if context_items:
            context_text = "\n\n".join(context_items)
            return (
                "Here is some current context about the user that may be "
                "relevant to your conversation:\n\n"
                f"{context_text}\n\n{base_prompt}"
            )

        return base_prompt

    def _inject_todo_context(
        self, prompt: str, todo_context: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Inject todo context directly into the prompt if available."""
        if not todo_context:
            return prompt

        # Build detailed todo text
        todo_text = "\n\n---\nCURRENT CONTEXT - Michael's Active Tasks:\n\n"
        for i, todo in enumerate(todo_context[:10], 1):  # Show up to 10 todos
            due_info = ""
            if todo.get('due_date') and todo.get('due_date') != 'None':
                due_info = f" (Due: {todo.get('due_date')})"
            priority = todo['priority']
            todo_text += f"{i}. {todo['content']} - {priority} priority{due_info}\n"
            todo_text += f"   Project: {todo.get('project', 'Inbox')}\n"

        todo_text += (
            "\nUse this context to provide more relevant coaching about his "
            "actual priorities and tasks. Reference specific tasks when "
            "appropriate, but don't just list them - integrate them naturally "
            "into your coaching conversation through inquiry.\n"
        )

        enhanced_prompt = prompt + todo_text
        return enhanced_prompt

    def _extract_morning_info(self, content: str, info_type: str) -> Optional[str]:
        """Extract morning challenge or value from conversation."""
        content_lower = content.lower()
        if info_type == "challenge":
            # Look for problem/challenge indicators
            if any(word in content_lower for word in [
                "problem", "challenge", "issue", "struggle", "difficult",
                "organize", "need to", "want to", "have to", "should"
            ]):
                return content
        elif info_type == "value":
            # Look for value indicators
            if any(word in content_lower for word in [
                "value", "fight for", "champion", "believe", "important",
                "matter", "care about", "clarity", "freedom", "growth"
            ]):
                return content
        return None


    def reset_conversation(self):
        """Reset conversation state and history."""
        self.conversation_state = "general"
        self.morning_challenge = None
        self.morning_value = None
        self.message_history = []

    async def initialize(self) -> None:
        """Initialize the agent with any required resources."""
        # Initialize MCP connection if needed
        self.is_initialized = True

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle a request from another agent or the orchestrator.

        Args:
            request: The agent request to handle

        Returns:
            AgentResponse with the result or error
        """
        try:
            # Add message to history
            self.message_history.append({
                "role": "user",
                "content": request.query
            })

            # Create UserMessage for todo context checking
            user_message = UserMessage(
                content=request.query,
                user_id=request.context.get("user_id", "michael"),
                conversation_id=request.context.get(
                    "conversation_id", "default"
                ),
                message_id=request.context.get(
                    "message_id", str(datetime.now().timestamp())
                ),
                timestamp=datetime.fromisoformat(
                    request.context.get("timestamp", datetime.now().isoformat())
                )
            )

            # Get todo context if relevant
            todo_context = await self._get_todo_context(user_message)

            # Get system prompt with embedded context
            system_prompt = self._get_system_prompt_with_context(todo_context)

            # Prepare messages for LLM service
            messages = self.message_history[:-1] + [
                {"role": "user", "content": request.query}
            ]

            # Generate response using LLM service
            response_content = await self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.7
            )

            # Update conversation state and extract info
            if self._is_morning_time():
                if (self.conversation_state == "general" and
                        "morning" in request.query.lower()):
                    self.conversation_state = "morning"
                # Extract challenge and value regardless of when they appear
                extracted_challenge = self._extract_morning_info(
                    request.query, "challenge"
                )
                if extracted_challenge and not self.morning_challenge:
                    self.morning_challenge = extracted_challenge
                extracted_value = self._extract_morning_info(
                    request.query, "value"
                )
                if extracted_value and not self.morning_value:
                    self.morning_value = extracted_value

            # Update history with response
            self.message_history.append({
                "role": "assistant",
                "content": response_content
            })

            # Create response
            return AgentResponse(
                agent_name=self.name,
                content=response_content,
                metadata={
                    "conversation_state": self.conversation_state,
                    "morning_challenge": self.morning_challenge,
                    "morning_value": self.morning_value
                },
                request_id=request.request_id,
                timestamp=datetime.now()
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="I'm having trouble processing your request right now.",
                metadata={},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e)
            )

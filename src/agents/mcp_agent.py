"""MCP Agent for external service integration via Model Context Protocol."""

import logging
from typing import Dict, Any, List
from datetime import datetime

from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse
from src.orchestration.mcp_todo_node import MCPTodoNode
from src.orchestration.context_state import ContextState
from src.performance.cache_manager import get_cache
from src.performance.profiler import profile_async


logger = logging.getLogger(__name__)


class MCPAgent(BaseAgent):
    """Agent responsible for MCP integrations - currently Todoist only."""

    def __init__(self):
        """Initialize MCP Agent with Todoist integration."""
        super().__init__(
            name="mcp",
            capabilities=[AgentCapability.TASK_MANAGEMENT]
        )
        self.mcp_node = MCPTodoNode()
        self.connection_status: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize MCP connections and verify status."""
        try:
            # Test MCP connection status
            self.connection_status = await self.mcp_node.get_mcp_status()

            if self.connection_status.get("connected"):
                logger.info(
                    f"MCP Agent initialized with {self.connection_status.get('total_todos', 0)} todos"
                )
            else:
                logger.warning(
                    f"MCP Agent initialized without connection: "
                    f"{self.connection_status.get('error', 'Unknown error')}"
                )

            self.is_initialized = True

        except Exception as e:
            logger.error(f"Error initializing MCP Agent: {e}")
            self.connection_status = {
                "connected": False,
                "error": str(e)
            }
            self.is_initialized = True  # Still mark as initialized

    @profile_async("mcp_handle_request")
    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle MCP-related requests from other agents.

        Args:
            request: The agent request to handle

        Returns:
            AgentResponse with task information or status
        """
        try:
            query_lower = request.query.lower()

            # Determine request type
            if any(word in query_lower for word in ["status", "connection", "connected"]):
                return await self._get_connection_status(request)
            elif "today" in query_lower or "due today" in query_lower or "focus on tasks due today" in query_lower:
                return await self._get_tasks_with_filter(request, "today")
            elif "overdue" in query_lower:
                return await self._get_tasks_with_filter(request, "overdue")
            else:
                # General task fetch based on context
                return await self._get_relevant_tasks(request)

        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="Unable to access task information at this time.",
                metadata={"error": str(e)},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e)
            )

    async def _get_connection_status(self, request: AgentRequest) -> AgentResponse:
        """Get current MCP connection status."""
        # Refresh status
        self.connection_status = await self.mcp_node.get_mcp_status()

        if self.connection_status.get("connected"):
            content = (
                f"TODOIST CONNECTION: Active\n"
                f"Total Tasks: {self.connection_status.get('total_todos', 0)}\n"
                f"Last Sync: {self.connection_status.get('last_sync', 'Unknown')}"
            )
        else:
            content = (
                f"TODOIST CONNECTION: Offline\n"
                f"Error: {self.connection_status.get('error', 'Unknown error')}"
            )

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata=self.connection_status,
            request_id=request.request_id,
            timestamp=datetime.now()
        )

    async def _get_tasks_with_filter(
        self, request: AgentRequest, date_filter: str
    ) -> AgentResponse:
        """Get tasks with specific date filter."""
        # Try cache first
        cache = get_cache()
        user_id = request.context.get("user_id", "default")
        cache_key = f"{date_filter}_{user_id}"

        cached_tasks = await cache.get_mcp_data("tasks", cache_key)
        if cached_tasks:
            logger.info(f"Cache hit for MCP tasks: {date_filter}")
            return self._format_task_response(request, cached_tasks)

        # Create a mock state for the MCP node
        mock_state = ContextState(
            messages=[{"content": request.query, "type": "user"}],
            context_relevance={"todos": 1.0},  # Force high relevance
            conversation_id=request.context.get("conversation_id", "")
        )

        # Fetch tasks with filter
        updated_state = await self.mcp_node.fetch_todos(mock_state, date_filter)

        if updated_state.todo_context:
            # Cache the tasks
            await cache.set_mcp_data("tasks", cache_key, updated_state.todo_context)
            logger.debug(f"Cached MCP tasks for: {date_filter}")

            return self._format_task_response(request, updated_state.todo_context)
        else:
            return AgentResponse(
                agent_name=self.name,
                content=f"No tasks found for filter: {date_filter}",
                metadata={
                    "filter": date_filter,
                    "tasks_found": 0,
                    "connected": self.connection_status.get("connected", False)
                },
                request_id=request.request_id,
                timestamp=datetime.now()
            )

    async def _get_relevant_tasks(self, request: AgentRequest) -> AgentResponse:
        """Get tasks relevant to the conversation context."""
        # Create context state from request
        mock_state = ContextState(
            messages=[{"content": request.query, "type": "user"}],
            context_relevance={"todos": 0.8},  # High relevance for direct requests
            conversation_id=request.context.get("conversation_id", "")
        )

        # Add conversation history if available
        if "messages" in request.context:
            mock_state.messages = request.context["messages"]

        # Fetch todos
        updated_state = await self.mcp_node.fetch_todos(mock_state)

        if updated_state.todo_context:
            response = self._format_task_response(request, updated_state.todo_context)
            print(f"📤 MCP DEBUG: Returning response with content length: {len(response.content)}")
            print(f"📤 MCP DEBUG: First 200 chars of response: {response.content[:200]}...")
            return response
        else:
            # Check if it's due to low relevance or actual error
            if updated_state.context_usage.get("todos_fetched") is False:
                error = updated_state.context_usage.get("error")
                if error:
                    content = "Unable to fetch tasks due to connection error."
                else:
                    content = "No relevant tasks found for the current context."
            else:
                content = "No tasks available."

            return AgentResponse(
                agent_name=self.name,
                content=content,
                metadata={
                    **updated_state.context_usage,
                    "connected": self.connection_status.get("connected", False)
                },
                request_id=request.request_id,
                timestamp=datetime.now()
            )

    def _format_task_response(
        self, request: AgentRequest, tasks: List[Dict[str, Any]]
    ) -> AgentResponse:
        """Format tasks into structured response."""
        if not tasks:
            return AgentResponse(
                agent_name=self.name,
                content="No tasks found.",
                metadata={"tasks_found": 0},
                request_id=request.request_id,
                timestamp=datetime.now()
            )

        # Format tasks
        content_lines = ["CURRENT TASKS:"]

        high_priority_count = 0
        due_today_count = 0
        today = datetime.now().date().isoformat()

        # Sort tasks: due today first, then by priority
        def task_sort_key(task):
            due_date = task.get("due_date")
            is_due_today = due_date == today if due_date else False
            priority_map = {"high": 0, "medium": 1, "low": 2}
            priority_value = priority_map.get(task.get("priority", "low"), 2)
            return (not is_due_today, priority_value)

        sorted_tasks = sorted(tasks, key=task_sort_key)

        for task in sorted_tasks[:5]:  # Limit to top 5
            priority = task.get("priority", "low")
            content = task.get("content", "Untitled task")
            project = task.get("project", "Inbox")
            due_date = task.get("due_date")

            # Build task line
            task_line = ""

            # Highlight tasks due today
            if due_date == today:
                task_line = "🔴 [DUE TODAY] "
                due_today_count += 1
            elif priority == "high":
                task_line = "[High Priority] "
                high_priority_count += 1
            elif priority == "medium":
                task_line = "[Medium Priority] "

            task_line += content

            # Add metadata
            metadata_parts = []
            if project and project != "Inbox":
                metadata_parts.append(f"Project: {project}")
            if due_date and due_date != today:
                metadata_parts.append(f"Due: {due_date}")

            if metadata_parts:
                task_line += f" ({', '.join(metadata_parts)})"

            content_lines.append(f"- {task_line}")

        # Add summary
        content_lines.extend([
            "",
            "TASK SUMMARY:",
            f"Total: {len(tasks)} tasks | High Priority: {high_priority_count} | "
            f"Due Today: {due_today_count}"
        ])

        if due_today_count > 0:
            content_lines.append(f"⚡ {due_today_count} task(s) due today!")

        return AgentResponse(
            agent_name=self.name,
            content="\n".join(content_lines),
            metadata={
                "tasks_found": len(tasks),
                "tasks_shown": min(5, len(tasks)),
                "high_priority_count": high_priority_count,
                "due_today_count": due_today_count,
                "connected": self.connection_status.get("connected", False)
            },
            request_id=request.request_id,
            timestamp=datetime.now()
        )

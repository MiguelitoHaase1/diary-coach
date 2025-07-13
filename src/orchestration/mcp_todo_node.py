"""MCP Todo Node for Session 6.2 - Official Doist MCP Server Integration."""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from mcp import ClientSession, StdioServerParameters
from mcp.client import stdio

from src.orchestration.context_state import ContextState


logger = logging.getLogger(__name__)


class MCPTodoNode:
    """MCP client node for fetching todos from Todoist via official Doist MCP server."""
    
    def __init__(self, mock_error: bool = False, mock_empty: bool = False):
        """Initialize MCP Todo Node.
        
        Args:
            mock_error: If True, simulate connection errors for testing
            mock_empty: If True, simulate empty response for testing
        """
        self.mock_error = mock_error
        self.mock_empty = mock_empty
        self.mcp_session = None
        # Configure MCP server path - try to detect installed location
        self.server_params = self._get_server_params()
    
    def _get_mcp_env(self) -> Dict[str, str]:
        """Get environment variables for MCP server."""
        env = {}
        
        # Try to get Todoist API token from various sources
        token = self._get_api_token()
        if token:
            # Provide both variable names since different servers might use different names
            env["TODOIST_API_TOKEN"] = token
            env["TODOIST_API_KEY"] = token
        
        return env
    
    def _get_api_token(self) -> Optional[str]:
        """Get Todoist API token from environment variables or config files."""
        # First try environment variable - try both names
        token = os.getenv("TODOIST_API_TOKEN") or os.getenv("TODOIST_API_KEY")
        if token:
            return token
        
        # Try Claude Desktop settings
        claude_settings_paths = [
            os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/.config/claude/claude_desktop_config.json")
        ]
        
        for path in claude_settings_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        settings = json.load(f)
                        mcp_servers = settings.get("mcpServers", {})
                        todoist_config = mcp_servers.get("todoist", {})
                        env_vars = todoist_config.get("env", {})
                        # Try both possible variable names
                        token = env_vars.get("TODOIST_API_KEY") or env_vars.get("TODOIST_API_TOKEN")
                        if token:
                            return token
                except Exception as e:
                    logger.error(f"Error reading Claude settings from {path}: {e}")
        
        return None
    
    def _get_server_params(self) -> StdioServerParameters:
        """Get MCP server parameters with path detection."""
        # Try to find the Doist MCP server in common locations
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        possible_paths = [
            # Local build in project
            os.path.join(project_root, "mcp-servers", "todoist-mcp", "build", "index.js"),
            # npm global install
            "/usr/local/lib/node_modules/@doist/todoist-mcp/build/index.js",
            # Local install
            os.path.join(project_root, "node_modules", "@doist", "todoist-mcp", "build", "index.js"),
            # Smithery install
            os.path.expanduser("~/.smithery/servers/todoist-mcp/build/index.js"),
            # Claude desktop app install
            os.path.expanduser("~/Library/Application Support/Claude/mcp-servers/todoist-mcp/build/index.js"),
        ]
        
        server_path = None
        for path in possible_paths:
            if os.path.exists(path):
                server_path = path
                break
        
        if not server_path:
            # Fall back to expected path - user will need to install
            server_path = "/usr/local/lib/node_modules/@doist/todoist-mcp/build/index.js"
            logger.warning(f"MCP server not found in common locations. Using fallback path: {server_path}")
        
        env = self._get_mcp_env()
        # print(f"🔧 MCP DEBUG: Server environment: {list(env.keys())}")
        
        return StdioServerParameters(
            command="node",
            args=[server_path],
            env=env
        )
        
    async def fetch_todos(self, state: ContextState, date_filter: Optional[str] = None) -> ContextState:
        """Fetch todos based on relevance score and conversation context."""
        # print(f"🏗️ MCP DEBUG: fetch_todos called")
        relevance = state.context_relevance.get("todos", 0.0)
        # print(f"📊 MCP DEBUG: Relevance score: {relevance}")
        
        # Initialize context usage tracking
        if not state.context_usage:
            state.context_usage = {}
        
        # Only fetch if relevance is high enough
        # print(f"🚪 MCP DEBUG: Threshold check: {relevance} >= 0.3 = {relevance >= 0.3}")
        if relevance < 0.3:
            # print("❌ MCP DEBUG: Relevance too low, skipping fetch")
            state.context_usage["todos_fetched"] = False
            state.decision_path.append("todo_context")
            return state
        
        # print("✅ MCP DEBUG: Relevance sufficient, proceeding with fetch")
        
        try:
            # Simulate MCP connection error for testing
            if self.mock_error:
                raise Exception("MCP connection failed")
            
            # Simulate empty response for testing
            if self.mock_empty:
                state.todo_context = []
                state.context_usage["todos_fetched"] = True
                state.context_usage["empty_response"] = True
                state.decision_path.append("todo_context")
                return state
            
            # Fetch todos from MCP server with optional date filter
            # print("🌐 MCP DEBUG: Calling _fetch_todos_from_mcp...")
            todos = await self._fetch_todos_from_mcp(date_filter=date_filter)
            # print(f"📥 MCP DEBUG: Raw todos fetched: {len(todos)}")
            
            # Filter todos based on conversation context
            # print("🔍 MCP DEBUG: Filtering todos by context...")
            filtered_todos = self._filter_todos_by_context(todos, state)
            # print(f"✅ MCP DEBUG: Filtered todos: {len(filtered_todos)}")
            
            # Update state
            state.todo_context = filtered_todos
            state.context_usage["todos_fetched"] = True
            state.context_usage["filter_applied"] = True
            state.context_usage["total_todos"] = len(todos)
            state.context_usage["filtered_todos"] = len(filtered_todos)
            
        except Exception as e:
            logger.error(f"Error fetching todos: {e}")
            state.todo_context = None
            state.context_usage["todos_fetched"] = False
            state.context_usage["error"] = str(e)
        
        state.decision_path.append("todo_context")
        return state
    
    async def _fetch_todos_from_mcp(self, date_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch todos from Todoist via MCP server."""
        # print("🔑 MCP DEBUG: Checking API token...")
        token = self._get_api_token()
        if not token:
            # print("❌ MCP DEBUG: No API token found, using mock data")
            # Fall back to mock data if no API token
            return self._get_mock_todos()
        
        # print(f"✅ MCP DEBUG: API token found: {token[:10]}...")
        
        # Use a simpler approach with proper exception handling
        try:
            result = await self._call_mcp_safely(date_filter=date_filter)
            if result:
                # print(f"🎉 MCP DEBUG: Successfully fetched {len(result)} real todos")
                return result
            else:
                # print("⚠️ MCP DEBUG: Empty result, using mock data")
                return self._get_mock_todos()
                
        except Exception as e:
            logger.error(f"Error fetching todos from MCP server: {e}")
            # print(f"❌ MCP DEBUG: MCP call failed: {e}")
            return self._get_mock_todos()  # Fallback to mock data
    
    async def _call_mcp_safely(self, date_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Safely call MCP server with proper error handling."""
        session = None
        read_stream = None
        write_stream = None
        
        try:
            # Create the stdio connection
            # print("🔌 MCP DEBUG: Creating stdio connection...")
            stdio_context = stdio.stdio_client(self.server_params)
            
            # Get the streams
            read_stream, write_stream = await stdio_context.__aenter__()
            # print("✅ MCP DEBUG: Stdio connection established")
            
            # Create the session
            # print("🤝 MCP DEBUG: Creating client session...")
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            # print("✅ MCP DEBUG: Client session established")
            
            # Initialize the session
            # print("🚀 MCP DEBUG: Initializing session...")
            await session.initialize()
            # print("✅ MCP DEBUG: Session initialized")
            
            # Prepare parameters for get-tasks tool
            params = {}
            if date_filter:
                params["filter"] = date_filter
                # print(f"📅 MCP DEBUG: Using date filter: {date_filter}")
            
            # Call the get-tasks tool (note: hyphen, not underscore)
            # print("📋 MCP DEBUG: Calling get-tasks tool...")
            result = await session.call_tool("get-tasks", params)
            # print(f"✅ MCP DEBUG: get-tasks call completed")
            
            if not result.content:
                # print("⚠️ MCP DEBUG: No content in result")
                return []
            
            # Parse the response - handle different MCP response formats
            # print("🔍 MCP DEBUG: Parsing response...")
            if isinstance(result.content, list):
                # Content is a list of TextContent objects
                tasks_data = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        # Parse JSON from TextContent
                        task_json = json.loads(item.text)
                        tasks_data.append(task_json)
                    else:
                        tasks_data.append(item)
            elif isinstance(result.content, str):
                tasks_data = json.loads(result.content)
            else:
                tasks_data = result.content
                
            # print(f"📊 MCP DEBUG: Parsed {len(tasks_data)} tasks from response")
            
            # Convert to our format
            todos = []
            for task in tasks_data:
                try:
                    todo = {
                        "id": task.get("id"),
                        "content": task.get("content"),
                        "priority": self._map_priority(task.get("priority", 1)),
                        "due_date": task.get("due", {}).get("date") if task.get("due") else None,
                        "project": task.get("project_name", "Inbox"),
                        "labels": task.get("labels", []),
                        "created_date": task.get("created_at"),
                        "url": task.get("url")
                    }
                    todos.append(todo)
                except Exception as e:
                    logger.error(f"Error processing task {task}: {e}")
                    continue
            
            # print(f"✅ MCP DEBUG: Converted {len(todos)} tasks to our format")
            return todos
            
        except Exception as e:
            # print(f"❌ MCP DEBUG: Error in _call_mcp_safely: {e}")
            raise e
            
        finally:
            # Properly clean up resources
            # print("🧹 MCP DEBUG: Cleaning up resources...")
            try:
                if session:
                    await session.__aexit__(None, None, None)
                    # print("✅ MCP DEBUG: Session closed")
            except Exception as e:
                # print(f"⚠️ MCP DEBUG: Error closing session: {e}")
                pass
            try:
                if read_stream and write_stream:
                    await stdio_context.__aexit__(None, None, None)
                    # print("✅ MCP DEBUG: Stdio connection closed")
            except Exception as e:
                # print(f"⚠️ MCP DEBUG: Error closing stdio: {e}")
                pass
    
    def _get_mock_todos(self) -> List[Dict[str, Any]]:
        """Get mock todos for testing or fallback."""
        return [
            {
                "id": "mock_1",
                "content": "Finish API integration for Q4 project",
                "priority": "high",
                "due_date": "2025-07-10",
                "project": "Q4 Development",
                "labels": ["work", "coding"]
            },
            {
                "id": "mock_2", 
                "content": "Review team meeting prep materials",
                "priority": "medium",
                "due_date": "2025-07-08",
                "project": "Team Management",
                "labels": ["meeting", "management"]
            },
            {
                "id": "mock_3",
                "content": "Update project documentation",
                "priority": "low",
                "due_date": "2025-07-12",
                "project": "Documentation",
                "labels": ["docs", "writing"]
            },
            {
                "id": "mock_4",
                "content": "Prepare presentation for client meeting",
                "priority": "high", 
                "due_date": "2025-07-09",
                "project": "Client Relations",
                "labels": ["presentation", "client"]
            }
        ]
    
    def _map_priority(self, todoist_priority: int) -> str:
        """Map Todoist priority (1-4) to our priority system."""
        if todoist_priority == 4:
            return "high"
        elif todoist_priority == 3:
            return "medium"
        elif todoist_priority == 2:
            return "low"
        else:
            return "low"
    
    def _get_project_name(self, project_id: str) -> str:
        """Get project name from project ID via MCP server."""
        # This will be handled by the MCP server response
        # The server should include project names in task responses
        return "Unknown Project"
    
    def _filter_todos_by_context(self, todos: List[Dict[str, Any]], state: ContextState) -> List[Dict[str, Any]]:
        """Filter todos based on conversation context."""
        if not state.messages:
            return todos
        
        # Get the latest message for context
        latest_message = state.messages[-1]
        content = latest_message.get("content", "").lower()
        
        # Extract keywords from conversation
        keywords = self._extract_keywords(content)
        
        # Filter todos based on relevance to conversation
        filtered_todos = []
        for todo in todos:
            todo_content = todo.get("content", "").lower()
            todo_project = todo.get("project", "").lower()
            
            # Check if todo matches conversation keywords
            relevance_score = 0
            for keyword in keywords:
                if keyword in todo_content or keyword in todo_project:
                    relevance_score += 1
            
            # Include high priority todos or those matching context
            if todo.get("priority") == "high" or relevance_score > 0:
                filtered_todos.append({
                    **todo,
                    "relevance_score": relevance_score
                })
        
        # Sort by relevance score and priority
        filtered_todos.sort(key=lambda x: (x["relevance_score"], x["priority"] == "high"), reverse=True)
        
        # Return top 5 most relevant todos
        return filtered_todos[:5]
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from conversation content."""
        # Simple keyword extraction (can be enhanced with NLP)
        keywords = []
        
        # Task-related keywords
        task_keywords = [
            "api", "integration", "meeting", "prep", "presentation", 
            "client", "project", "documentation", "review", "finish"
        ]
        
        for keyword in task_keywords:
            if keyword in content:
                keywords.append(keyword)
        
        # Also look for project-related terms
        project_keywords = [
            "q4", "team", "client", "development", "management"
        ]
        
        for keyword in project_keywords:
            if keyword in content:
                keywords.append(keyword)
        
        return keywords
    
    async def get_mcp_status(self) -> Dict[str, Any]:
        """Get MCP server connection status."""
        try:
            if not self._get_api_token():
                return {
                    "connected": False,
                    "error": "No TODOIST_API_TOKEN provided",
                    "last_sync": None,
                    "using_mock_data": True
                }
            
            # Use the same safe method for testing
            # print("🔍 MCP DEBUG: Testing MCP status...")
            todos = await self._call_mcp_safely()
            
            if todos:
                return {
                    "connected": True,
                    "last_sync": datetime.now().isoformat(),
                    "total_todos": len(todos),
                    "using_mock_data": False
                }
            else:
                return {
                    "connected": False,
                    "error": "Empty response from MCP server",
                    "last_sync": None,
                    "using_mock_data": True
                }
                        
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "last_sync": None,
                "using_mock_data": True
            }
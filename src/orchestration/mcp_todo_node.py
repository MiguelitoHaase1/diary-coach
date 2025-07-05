"""MCP Todo Node for Session 6.2 - Todoist Integration."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.orchestration.context_state import ContextState


logger = logging.getLogger(__name__)


class MCPTodoNode:
    """MCP client node for fetching todos from Todoist."""
    
    def __init__(self, mock_error: bool = False, mock_empty: bool = False):
        """Initialize MCP Todo Node.
        
        Args:
            mock_error: If True, simulate connection errors for testing
            mock_empty: If True, simulate empty response for testing
        """
        self.mock_error = mock_error
        self.mock_empty = mock_empty
        self.connection_url = "stdio"  # MCP connection URL
        
    async def fetch_todos(self, state: ContextState) -> ContextState:
        """Fetch todos based on relevance score and conversation context."""
        relevance = state.context_relevance.get("todos", 0.0)
        
        # Initialize context usage tracking
        if not state.context_usage:
            state.context_usage = {}
        
        # Only fetch if relevance is high enough
        if relevance <= 0.6:
            state.context_usage["todos_fetched"] = False
            state.decision_path.append("todo_context")
            return state
        
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
            
            # Fetch todos from MCP server (mocked for now)
            todos = await self._fetch_todos_from_mcp()
            
            # Filter todos based on conversation context
            filtered_todos = self._filter_todos_by_context(todos, state)
            
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
    
    async def _fetch_todos_from_mcp(self) -> List[Dict[str, Any]]:
        """Fetch todos from MCP server (mock implementation)."""
        # In real implementation, this would connect to MCP server
        # For now, return realistic mock data
        return [
            {
                "id": "1",
                "content": "Finish API integration for Q4 project",
                "priority": "high",
                "due_date": "2024-12-20",
                "project": "Q4 Development"
            },
            {
                "id": "2", 
                "content": "Review team meeting prep materials",
                "priority": "medium",
                "due_date": "2024-12-18",
                "project": "Team Management"
            },
            {
                "id": "3",
                "content": "Update project documentation",
                "priority": "low",
                "due_date": "2024-12-22",
                "project": "Documentation"
            },
            {
                "id": "4",
                "content": "Prepare presentation for client meeting",
                "priority": "high", 
                "due_date": "2024-12-19",
                "project": "Client Relations"
            }
        ]
    
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
        """Get MCP connection status."""
        try:
            # Mock status check
            return {
                "connected": not self.mock_error,
                "server_url": self.connection_url,
                "last_sync": datetime.now().isoformat(),
                "total_todos": 4 if not self.mock_empty else 0
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "last_sync": None
            }
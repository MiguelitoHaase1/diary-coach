"""Context-aware LangGraph implementation for Session 6."""

from datetime import datetime
from typing import Dict, Any, List, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from src.orchestration.context_state import ContextState
from src.orchestration.mcp_todo_node import MCPTodoNode
from src.orchestration.relevance_scorer import EnhancedRelevanceScorer


class ContextRelevanceScorer:
    """Scores relevance of different context sources."""
    
    async def score(self, state: ContextState) -> ContextState:
        """Score context relevance based on conversation content."""
        if not state.messages:
            state.context_relevance = {"todos": 0.0, "documents": 0.0, "memory": 0.0}
            state.decision_path.append("context_relevance_scorer")
            return state
        
        # Get latest message content
        latest_message = state.messages[-1]
        content = latest_message.get("content", "").lower()
        
        # Simple keyword-based scoring (will be enhanced in later increments)
        todos_score = 0.0
        docs_score = 0.0
        memory_score = 0.0
        
        # Task-related keywords increase todo relevance
        task_keywords = ["prioritize", "today", "should", "work", "task", "do"]
        todos_score = sum(0.15 for keyword in task_keywords if keyword in content)
        todos_score = min(todos_score, 1.0)
        
        # Reference keywords increase document relevance
        reference_keywords = ["belief", "core", "values", "remember", "discussed"]
        docs_score = sum(0.2 for keyword in reference_keywords if keyword in content)
        docs_score = min(docs_score, 1.0)
        
        # Memory keywords increase conversation history relevance
        memory_keywords = ["remember", "previous", "last time", "before", "earlier"]
        memory_score = sum(0.2 for keyword in memory_keywords if keyword in content)
        memory_score = min(memory_score, 1.0)
        
        state.context_relevance = {
            "todos": todos_score,
            "documents": docs_score,
            "memory": memory_score
        }
        
        state.decision_path.append("context_relevance_scorer")
        return state


class TodoContextNode:
    """Fetches relevant todo context when needed."""
    
    async def fetch_todos(self, state: ContextState) -> ContextState:
        """Fetch todos based on relevance score."""
        relevance = state.context_relevance.get("todos", 0.0)
        
        if relevance > 0.6:  # Only fetch if relevance is high
            # Mock todo data for now (will be replaced with MCP integration)
            state.todo_context = [
                {"id": "1", "content": "Finish Q4 planning", "priority": "high"},
                {"id": "2", "content": "Review team proposals", "priority": "medium"}
            ]
            state.context_usage["todos_fetched"] = True
        else:
            state.context_usage["todos_fetched"] = False
        
        state.decision_path.append("todo_context")
        return state


class DocumentContextNode:
    """Fetches relevant document context when needed."""
    
    async def fetch_documents(self, state: ContextState) -> ContextState:
        """Fetch documents based on relevance score."""
        relevance = state.context_relevance.get("documents", 0.0)
        
        if relevance > 0.6:
            # Mock document data for now (will be replaced with actual document loader)
            state.document_context = {
                "core_beliefs": "Focus on impact, embrace discomfort, build systems",
                "source": "docs/session_2/corebeliefs.md"
            }
            state.context_usage["documents_fetched"] = True
        else:
            state.context_usage["documents_fetched"] = False
        
        state.decision_path.append("document_context")
        return state


class ConversationMemoryNode:
    """Manages conversation history and memory."""
    
    async def load_memory(self, state: ContextState) -> ContextState:
        """Load conversation memory based on relevance score."""
        relevance = state.context_relevance.get("memory", 0.0)
        
        if relevance > 0.6:
            # Mock memory data for now (will be replaced with checkpoint system)
            state.conversation_history = [
                {"date": "2024-12-15", "topic": "delegation", "insights": "..."},
                {"date": "2024-12-10", "topic": "prioritization", "insights": "..."}
            ]
            state.context_usage["memory_fetched"] = True
        else:
            state.context_usage["memory_fetched"] = False
        
        state.decision_path.append("conversation_memory")
        return state


class ContextAwareCoach:
    """Coach that incorporates context into responses."""
    
    async def generate_response(self, state: ContextState) -> ContextState:
        """Generate coach response with context integration."""
        # Mock coach response for now (will be replaced with actual coach integration)
        if state.messages:
            latest_message = state.messages[-1]
            content = latest_message.get("content", "")
            
            # Simple response based on context
            if "morning" in content.lower():
                state.coach_response = "Good morning! What dragon are you most excited to slay today?"
            elif state.todo_context:
                state.coach_response = "I see you have some important tasks. What's your biggest lever today?"
            else:
                state.coach_response = "Tell me more about what's on your mind."
        else:
            state.coach_response = "How can I help you today?"
        
        state.decision_path.append("coach")
        return state


def should_fetch_context(state: ContextState) -> bool:
    """Determine if context should be fetched based on relevance scores."""
    if not state.context_enabled:
        return False
    
    # Fetch context if any relevance score is above threshold
    max_relevance = max(state.context_relevance.values()) if state.context_relevance else 0.0
    return max_relevance > 0.6


def create_context_aware_graph() -> CompiledStateGraph:
    """Create the context-aware LangGraph."""
    
    # Create graph
    graph = StateGraph(ContextState)
    
    # Create node instances
    scorer = EnhancedRelevanceScorer()  # Use enhanced relevance scorer
    todo_node = MCPTodoNode()  # Use MCP Todo Node instead of mock
    doc_node = DocumentContextNode()
    memory_node = ConversationMemoryNode()
    coach = ContextAwareCoach()
    
    # Add nodes
    graph.add_node("context_relevance_scorer", scorer.score)
    graph.add_node("todo_context", todo_node.fetch_todos)
    graph.add_node("document_context", doc_node.fetch_documents)
    graph.add_node("conversation_memory", memory_node.load_memory)
    graph.add_node("coach", coach.generate_response)
    
    # Add edges
    graph.add_edge(START, "context_relevance_scorer")
    
    # Conditional edges based on context relevance
    graph.add_conditional_edges(
        "context_relevance_scorer",
        should_fetch_context,
        {
            True: "todo_context",
            False: "coach"
        }
    )
    
    # Sequential context fetching when enabled
    graph.add_edge("todo_context", "document_context")
    graph.add_edge("document_context", "conversation_memory")
    graph.add_edge("conversation_memory", "coach")
    
    # End after coach
    graph.add_edge("coach", END)
    
    return graph.compile()
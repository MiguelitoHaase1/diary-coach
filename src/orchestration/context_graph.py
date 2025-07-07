"""Context-aware LangGraph implementation for Session 6."""

from datetime import datetime
from typing import Dict, Any, List, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from src.orchestration.context_state import ContextState
from src.orchestration.mcp_todo_node import MCPTodoNode
from src.orchestration.relevance_scorer import EnhancedRelevanceScorer
from src.orchestration.implicit_context_coach import ImplicitContextCoach
from src.orchestration.memory_recall import MemoryRecallNode
from src.orchestration.document_loader import MarkdownDocumentLoader
from src.orchestration.checkpoint_manager import CloudCheckpointManager


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
    
    def __init__(self):
        """Initialize with real MCP Todo Node."""
        self.mcp_todo_node = MCPTodoNode()
    
    async def fetch_todos(self, state: ContextState) -> ContextState:
        """Fetch todos using real MCP integration."""
        # Use the real MCP Todo Node instead of mock data
        return await self.mcp_todo_node.fetch_todos(state)


class DocumentContextNode:
    """Fetches relevant document context when needed."""
    
    def __init__(self, documents_path: str = "/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory"):
        """Initialize with document loader."""
        self.document_loader = MarkdownDocumentLoader(documents_path)
    
    async def fetch_documents(self, state: ContextState) -> ContextState:
        """Fetch documents based on relevance score."""
        return await self.document_loader.load_documents(state)


class ConversationMemoryNode:
    """Manages conversation history and memory."""
    
    def __init__(self):
        """Initialize with checkpoint manager."""
        self.checkpoint_manager = CloudCheckpointManager()
    
    async def load_memory(self, state: ContextState) -> ContextState:
        """Load conversation memory from checkpoints."""
        relevance = state.context_relevance.get("memory", 0.0)
        
        if relevance > 0.6 and state.conversation_id:
            # Try to load from checkpoint
            try:
                checkpoint_state = await self.checkpoint_manager.load_checkpoint(state.conversation_id)
                if checkpoint_state and checkpoint_state.conversation_history:
                    state.conversation_history = checkpoint_state.conversation_history
                    state.context_usage["memory_fetched"] = True
                else:
                    state.context_usage["memory_fetched"] = False
                    state.context_usage["memory_fetch_reason"] = "No checkpoint found"
            except Exception as e:
                state.context_usage["memory_fetched"] = False
                state.context_usage["memory_fetch_error"] = str(e)
        else:
            state.context_usage["memory_fetched"] = False
            state.context_usage["memory_fetch_reason"] = "Low relevance score"
        
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


def route_after_scoring(state: ContextState) -> str:
    """Route after context relevance scoring."""
    # Check if this is a memory recall query first
    if state.messages:
        memory_recall_node = MemoryRecallNode()
        if memory_recall_node._detect_memory_query(state.messages):
            return "memory_recall"
    
    # Otherwise, check if we should fetch context
    if should_fetch_context(state):
        return "todo_context"
    else:
        return "coach"


def route_after_memory_recall(state: ContextState) -> str:
    """Route after memory recall processing."""
    # If memory recall was triggered, go straight to coach
    if state.context_usage.get("memory_recall_triggered", False):
        return "coach"
    
    # Otherwise, proceed with normal context fetching
    if should_fetch_context(state):
        return "todo_context"
    else:
        return "coach"


def create_context_aware_graph(llm_service=None) -> CompiledStateGraph:
    """Create the context-aware LangGraph."""
    
    # Create graph
    graph = StateGraph(ContextState)
    
    # Mock LLM service for testing if none provided
    if llm_service is None:
        class MockLLMService:
            async def generate_response(self, messages, system_prompt, max_tokens=200, temperature=0.7):
                return "Based on your priorities, what needs your attention first?"
        llm_service = MockLLMService()
    
    # Create node instances
    scorer = EnhancedRelevanceScorer()  # Use enhanced relevance scorer
    todo_node = MCPTodoNode()  # Use MCP Todo Node instead of mock
    doc_node = DocumentContextNode()
    memory_node = ConversationMemoryNode()
    memory_recall = MemoryRecallNode()  # Add memory recall node
    coach = ImplicitContextCoach(llm_service)  # Use implicit context coach
    
    # Add nodes
    graph.add_node("context_relevance_scorer", scorer.score)
    graph.add_node("memory_recall", memory_recall.process_memory_query)
    graph.add_node("todo_context", todo_node.fetch_todos)
    graph.add_node("document_context", doc_node.fetch_documents)
    graph.add_node("conversation_memory", memory_node.load_memory)
    graph.add_node("coach", coach.generate_response)
    
    # Add edges
    graph.add_edge(START, "context_relevance_scorer")
    
    # Conditional edges after scoring - check for memory recall first
    graph.add_conditional_edges(
        "context_relevance_scorer",
        route_after_scoring,
        {
            "memory_recall": "memory_recall",
            "todo_context": "todo_context",
            "coach": "coach"
        }
    )
    
    # Conditional edges after memory recall
    graph.add_conditional_edges(
        "memory_recall",
        route_after_memory_recall,
        {
            "todo_context": "todo_context",
            "coach": "coach"
        }
    )
    
    # Sequential context fetching when enabled
    graph.add_edge("todo_context", "document_context")
    graph.add_edge("document_context", "conversation_memory")
    graph.add_edge("conversation_memory", "coach")
    
    # End after coach
    graph.add_edge("coach", END)
    
    return graph.compile()
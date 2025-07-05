"""Context state dataclass for LangGraph context-aware conversations."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ContextState:
    """Extended state for context-aware conversations."""
    
    # Core conversation data
    messages: List[Dict[str, Any]] = field(default_factory=list)
    conversation_id: str = ""
    context_enabled: bool = True
    
    # Context data channels
    todo_context: Optional[List[Dict[str, Any]]] = None
    document_context: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    
    # Context relevance and usage
    context_relevance: Dict[str, float] = field(default_factory=dict)
    context_usage: Dict[str, Any] = field(default_factory=dict)
    
    # Decision tracking
    decision_path: List[str] = field(default_factory=list)
    
    # Coach response
    coach_response: Optional[str] = None
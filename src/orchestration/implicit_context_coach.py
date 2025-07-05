"""Implicit Context Coach for Session 6.4 - Seamless context injection."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.orchestration.context_state import ContextState
from src.agents.prompts import get_coach_system_prompt


logger = logging.getLogger(__name__)


class ImplicitContextCoach:
    """Coach that seamlessly incorporates context into responses without being explicit."""
    
    def __init__(self, llm_service, context_budget: int = 1000):
        """Initialize implicit context coach.
        
        Args:
            llm_service: LLM service for generating responses
            context_budget: Maximum characters of context to inject
        """
        self.llm_service = llm_service
        self.context_budget = context_budget
    
    def _get_base_coaching_prompt(self) -> str:
        """Get the base coaching prompt from the master prompt file."""
        base_prompt = get_coach_system_prompt()
        
        # Add context injection instructions
        context_instructions = """

{context_section}

Remember: Your role is to coach, not to just provide information. Use any context naturally to ask better questions and challenge thinking, but maintain your questioning approach."""
        
        return base_prompt + context_instructions

    async def generate_response(self, state: ContextState) -> ContextState:
        """Generate coach response with seamless context integration."""
        
        # Initialize context usage tracking
        if not state.context_usage:
            state.context_usage = {}
        
        # Build context section for prompt
        context_section, attribution = self._build_context_section(state)
        
        # Create enhanced system prompt
        system_prompt = self._get_base_coaching_prompt().format(
            context_section=context_section
        )
        
        # Prepare messages for LLM
        messages = self._format_messages_for_llm(state.messages)
        
        try:
            # Generate response
            response = await self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            state.coach_response = response
            
            # Track context usage and attribution
            state.context_usage.update({
                "context_sources_used": attribution["sources_used"],
                "context_budget_used": len(context_section),
                "context_attribution": attribution,
                "prompt_length": len(system_prompt)
            })
            
        except Exception as e:
            logger.error(f"Error generating context-enhanced response: {e}")
            # Fallback to basic response
            state.coach_response = "What's on your mind today?"
            state.context_usage["error"] = str(e)
        
        state.decision_path.append("implicit_context_coach")
        return state
    
    def _build_context_section(self, state: ContextState) -> tuple[str, Dict[str, Any]]:
        """Build context section for system prompt with budget management."""
        context_parts = []
        attribution = {
            "sources_used": [],
            "todos_referenced": [],
            "documents_referenced": [],
            "memory_referenced": [],
            "relevance_scores": {}
        }
        
        current_budget = self.context_budget
        
        # Add todos if relevant and within budget
        if state.todo_context and state.context_relevance.get("todos", 0) > 0.6:
            todo_section, todo_budget, todo_items = self._format_todo_context(
                state.todo_context, current_budget - 50  # Reserve some budget for headers
            )
            if todo_section:
                context_parts.append(f"Current priorities from your todo list:\n{todo_section}")
                current_budget -= todo_budget
                attribution["sources_used"].append("todos")
                attribution["todos_referenced"] = todo_items
                attribution["relevance_scores"]["todos"] = state.context_relevance.get("todos", 0)
        
        # Add documents if relevant and within budget
        if state.document_context and state.context_relevance.get("documents", 0) > 0.6 and current_budget > 100:
            doc_section, doc_budget, doc_refs = self._format_document_context(
                state.document_context, current_budget
            )
            if doc_section:
                context_parts.append(f"Relevant from your core documents:\n{doc_section}")
                current_budget -= doc_budget
                attribution["sources_used"].append("documents")
                attribution["documents_referenced"] = doc_refs
                attribution["relevance_scores"]["documents"] = state.context_relevance.get("documents", 0)
        
        # Add conversation memory if relevant and within budget
        if state.conversation_history and state.context_relevance.get("memory", 0) > 0.6 and current_budget > 50:
            memory_section, memory_budget, memory_refs = self._format_memory_context(
                state.conversation_history, current_budget
            )
            if memory_section:
                context_parts.append(f"From previous conversations:\n{memory_section}")
                current_budget -= memory_budget
                attribution["sources_used"].append("memory")
                attribution["memory_referenced"] = memory_refs
                attribution["relevance_scores"]["memory"] = state.context_relevance.get("memory", 0)
        
        # Combine all context
        if context_parts:
            context_section = "CONTEXT FOR COACHING:\n" + "\n\n".join(context_parts) + "\n"
        else:
            context_section = ""
        
        return context_section, attribution
    
    def _format_todo_context(self, todos: List[Dict[str, Any]], budget: int) -> tuple[str, int, List[str]]:
        """Format todo context within budget constraints."""
        if not todos or budget < 50:
            return "", 0, []
        
        # Sort by priority and relevance
        sorted_todos = sorted(todos, key=lambda x: (
            x.get("priority") == "high",
            x.get("relevance_score", 0)
        ), reverse=True)
        
        formatted_todos = []
        used_budget = 0
        referenced_items = []
        
        for todo in sorted_todos[:5]:  # Max 5 todos
            content = todo.get('content', 'Unknown task')
            
            # Truncate long content to fit budget
            max_content_length = min(len(content), budget - used_budget - 20)  # Leave room for formatting
            if max_content_length < 10:  # Not enough room
                break
                
            truncated_content = content[:max_content_length]
            if len(content) > max_content_length:
                truncated_content += "..."
            
            todo_text = f"• {truncated_content}"
            if todo.get('priority') == 'high':
                todo_text += " (HIGH)"
            
            # Check if this todo fits in budget
            if used_budget + len(todo_text) + 1 > budget:
                break
            
            formatted_todos.append(todo_text)
            used_budget += len(todo_text) + 1
            referenced_items.append(content)
        
        return "\n".join(formatted_todos), used_budget, referenced_items
    
    def _format_document_context(self, documents: Dict[str, Any], budget: int) -> tuple[str, int, List[str]]:
        """Format document context within budget constraints."""
        if not documents or budget < 30:
            return "", 0, []
        
        formatted_parts = []
        used_budget = 0
        referenced_docs = []
        
        for doc_name, content in documents.items():
            if isinstance(content, str):
                # Truncate content to fit budget
                available_budget = budget - used_budget - len(doc_name) - 10
                if available_budget < 20:
                    break
                
                truncated_content = content[:available_budget]
                if len(content) > available_budget:
                    truncated_content += "..."
                
                doc_text = f"• {doc_name}: {truncated_content}"
                formatted_parts.append(doc_text)
                used_budget += len(doc_text) + 1
                referenced_docs.append(doc_name)
        
        return "\n".join(formatted_parts), used_budget, referenced_docs
    
    def _format_memory_context(self, memories: List[Dict[str, Any]], budget: int) -> tuple[str, int, List[str]]:
        """Format conversation memory within budget constraints."""
        if not memories or budget < 30:
            return "", 0, []
        
        formatted_memories = []
        used_budget = 0
        referenced_topics = []
        
        # Take most recent memories first
        recent_memories = sorted(memories, key=lambda x: x.get('date', ''), reverse=True)
        
        for memory in recent_memories[:3]:  # Max 3 memories
            topic = memory.get('topic', 'Unknown')
            insights = memory.get('insights', '')
            
            memory_text = f"• Previous discussion on {topic}"
            if insights:
                available_budget = budget - used_budget - len(memory_text) - 5
                if available_budget > 20:
                    truncated_insights = insights[:available_budget]
                    if len(insights) > available_budget:
                        truncated_insights += "..."
                    memory_text += f": {truncated_insights}"
            
            if used_budget + len(memory_text) + 1 > budget:
                break
            
            formatted_memories.append(memory_text)
            used_budget += len(memory_text) + 1
            referenced_topics.append(topic)
        
        return "\n".join(formatted_memories), used_budget, referenced_topics
    
    def _format_messages_for_llm(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format conversation messages for LLM API."""
        formatted_messages = []
        
        for message in messages[-10:]:  # Last 10 messages for context
            role = "user" if message.get("type") == "user" else "assistant"
            content = message.get("content", "")
            
            if content:
                formatted_messages.append({
                    "role": role,
                    "content": content
                })
        
        return formatted_messages
    
    def get_context_summary(self, state: ContextState) -> Dict[str, Any]:
        """Get summary of context usage for debugging."""
        return {
            "context_sources_available": {
                "todos": len(state.todo_context) if state.todo_context else 0,
                "documents": len(state.document_context) if state.document_context else 0,
                "memories": len(state.conversation_history) if state.conversation_history else 0
            },
            "relevance_scores": state.context_relevance,
            "context_usage": state.context_usage,
            "budget_remaining": self.context_budget - state.context_usage.get("context_budget_used", 0)
        }
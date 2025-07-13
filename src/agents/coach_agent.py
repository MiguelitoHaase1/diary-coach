"""Diary Coach agent implementation with Michael's coaching prompt."""

from typing import List, Dict, Any, Optional
from datetime import datetime, time
from src.agents.base import BaseAgent
from src.events.schemas import UserMessage, AgentResponse
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
    
    async def _get_todo_context(self, message: UserMessage) -> Optional[List[Dict[str, Any]]]:
        """Get relevant todos based on message content."""
        # print(f"🔍 DEBUG: _get_todo_context called with message: '{message.content}'")
        try:
            # Check if the message is asking about tasks/priorities
            content_lower = message.content.lower()
            task_keywords = ["prioritize", "today", "should", "work", "task", "do", "list", "priority", "focus", 
                           "challenge", "important", "tackle", "problem", "goal"]
            
            # Calculate relevance score
            relevance_score = sum(0.15 for keyword in task_keywords if keyword in content_lower)
            relevance_score = min(relevance_score, 1.0)
            
            # print(f"🎯 DEBUG: Task keywords found: {[kw for kw in task_keywords if kw in content_lower]}")
            # print(f"📊 DEBUG: Relevance score: {relevance_score}")
            # print(f"🚪 DEBUG: Threshold check: {relevance_score} >= 0.3 = {relevance_score >= 0.3}")
            
            if relevance_score >= 0.3:  # Lower threshold for direct integration
                # print("✅ DEBUG: Threshold met, fetching todos...")
                
                # Create a context state for MCP fetching
                state = ContextState(
                    messages=[{"type": "user", "content": message.content, "timestamp": datetime.now().isoformat()}],
                    context_relevance={"todos": relevance_score},
                    conversation_id=message.conversation_id
                )
                
                # print("🔄 DEBUG: Calling MCP todo node...")
                # Fetch todos using MCP
                result_state = await self.mcp_todo_node.fetch_todos(state)
                # print(f"📋 DEBUG: MCP returned {len(result_state.todo_context) if result_state.todo_context else 0} todos")
                # if result_state.todo_context:
                #     for i, todo in enumerate(result_state.todo_context[:3]):
                #         print(f"   {i+1}. {todo.get('content', 'No content')}")
                
                return result_state.todo_context
            else:
                # print("❌ DEBUG: Threshold not met, skipping todo fetch")
                return None
        except Exception as e:
            # Log error but don't break the conversation
            # print(f"💥 ERROR fetching todos: {e}")
            # import traceback
            # traceback.print_exc()
            return None
    
    def _get_system_prompt_with_context(self, todo_context: Optional[List[Dict[str, Any]]]) -> str:
        """Get system prompt enhanced with todo context."""
        # print(f"🎨 DEBUG: _get_system_prompt_with_context called with {len(todo_context) if todo_context else 0} todos")
        base_prompt = self._get_system_prompt()
        
        if todo_context:
            # print("✨ DEBUG: Enhancing system prompt with todo context")
            todo_text = "\n\n# Current Relevant Tasks\n"
            todo_text += "Here are Michael's current relevant tasks from his Todoist:\n\n"
            
            for i, todo in enumerate(todo_context[:5], 1):  # Limit to 5 most relevant
                due_info = f" (Due: {todo.get('due_date')})" if todo.get('due_date') and todo.get('due_date') != 'None' else ""
                todo_text += f"{i}. {todo['content']} - {todo['priority']} priority{due_info}\n"
                todo_text += f"   Project: {todo.get('project', 'Inbox')}\n"
            
            todo_text += "\nUse this context to provide more relevant coaching about his actual priorities and tasks. Reference specific tasks when appropriate, but don't just list them - integrate them naturally into your coaching conversation through inquiry.\n"
            
            enhanced_prompt = base_prompt + todo_text
            # print(f"📏 DEBUG: Enhanced prompt length: {len(enhanced_prompt)} (was {len(base_prompt)})")
            return enhanced_prompt
        else:
            # print("🔄 DEBUG: No todo context, using base prompt")
            return base_prompt
    
    async def process_message(self, message: UserMessage) -> AgentResponse:
        """Process a user message and generate a coaching response.
        
        Args:
            message: User message to process
            
        Returns:
            AgentResponse with coaching content
        """
        # Add to message history for context
        self.message_history.append({
            "role": "user",
            "content": message.content
        })
        
        # Detect conversation state
        content_lower = message.content.lower()
        if "good morning" in content_lower:
            self.conversation_state = "morning"
        
        # print(f"🚀 DEBUG: Processing message: '{message.content}'")
        
        # Fetch real todos if relevant to the conversation
        # print("🔍 DEBUG: About to call _get_todo_context...")
        todo_context = await self._get_todo_context(message)
        # print(f"📋 DEBUG: Todo context result: {todo_context is not None}")
        
        # Prepare conversation context with todos
        recent_history = self.message_history[-10:]  # Last 10 messages for context
        # print("🎨 DEBUG: About to call _get_system_prompt_with_context...")
        system_prompt = self._get_system_prompt_with_context(todo_context)
        # print(f"📝 DEBUG: System prompt ready, length: {len(system_prompt)}")
        
        try:
            # Generate response using LLM service
            response_content = await self.llm_service.generate_response(
                messages=recent_history,
                system_prompt=system_prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            # Add to message history
            self.message_history.append({
                "role": "assistant", 
                "content": response_content
            })
            
            # Create response
            response = AgentResponse(
                agent_name="diary_coach",
                content=response_content,
                response_to=message.message_id,
                conversation_id=message.conversation_id
            )
            
            return response
            
        except Exception as e:
            # Error handling - return fallback response
            error_response = AgentResponse(
                agent_name="diary_coach",
                content="I'm having trouble processing your message right now. Could you try again?",
                response_to=message.message_id,
                conversation_id=message.conversation_id
            )
            return error_response
    
    def reset_conversation(self):
        """Reset conversation state and history."""
        self.conversation_state = "general"
        self.morning_challenge = None
        self.morning_value = None
        self.message_history = []
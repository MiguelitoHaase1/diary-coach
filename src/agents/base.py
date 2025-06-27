from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import uuid

from src.events.schemas import UserMessage, AgentResponse


class BaseAgent(ABC):
    """Base class for all coaching agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.agent_id = str(uuid.uuid4())
    
    async def process_message(self, user_message: UserMessage) -> AgentResponse:
        """Process a user message and return an agent response"""
        # Generate a simple coaching response for testing
        content = await self._generate_response(user_message)
        
        return AgentResponse(
            agent_name=self.name,
            content=content,
            response_to=user_message.message_id,
            conversation_id=user_message.conversation_id,
            timestamp=datetime.now()
        )
    
    async def _generate_response(self, user_message: UserMessage) -> str:
        """Generate response content - override in subclasses"""
        # Simple mock response for base implementation
        if "goals" in user_message.content.lower():
            return "What specific goals would you like to focus on today?"
        elif "productive" in user_message.content.lower():
            return "Tell me more about what productivity means to you."
        else:
            return "I'm here to help you reflect on that. Can you tell me more?"
"""Event schema definitions - simple dataclasses for now"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from dataclasses import dataclass, field


@dataclass
class UserMessage:
    """Schema for user messages in the coaching system"""
    user_id: str
    content: str
    timestamp: datetime
    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    message_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class AgentResponse:
    """Schema for agent responses in the coaching system"""
    agent_name: str
    content: str
    response_to: str  # Message ID this is responding to
    timestamp: datetime = field(default_factory=datetime.now)
    response_id: str = field(default_factory=lambda: str(uuid4()))
    conversation_id: Optional[str] = None
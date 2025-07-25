"""
Multi-agent system components for coaching conversations.

This package contains the specialized agents that work together to provide
comprehensive coaching experiences:

- BaseAgent: Abstract base class for all coaching agents
- OrchestatorAgent: Routes conversations and coordinates other agents
- GoalSettingAgent: Handles morning goal-setting sessions
- ReflectionAgent: Manages evening reflection and review
- ChallengeAgent: Provides supportive yet skeptical questioning
- ContextAgent: Maintains conversation history and insights
"""

from .base import BaseAgent
from .memory_agent import MemoryAgent
from .personal_content_agent import PersonalContentAgent
from .mcp_agent import MCPAgent

__all__ = ["BaseAgent", "MemoryAgent", "PersonalContentAgent", "MCPAgent"]
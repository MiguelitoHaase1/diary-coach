"""Diary Coach agent implementation with Michael's coaching prompt."""

from typing import List, Dict, Any, Optional
from datetime import datetime, time
from src.agents.base import BaseAgent
from src.events.schemas import UserMessage, AgentResponse
from src.services.llm_service import AnthropicService
from src.agents.prompts import get_coach_system_prompt


class DiaryCoach(BaseAgent):
    """Michael's personal Daily Transformation Diary Coach."""
    
    @property
    def SYSTEM_PROMPT(self) -> str:
        """Load the system prompt from the master prompt file."""
        return get_coach_system_prompt()

    # Morning-specific prompt content from MorningPrompt.md
    MORNING_PROMPT_ADDITION = """

# Morning Momentum Coach Override

When current time is between 6:00 AM and 11:59 AM, apply these specific morning behaviors:

## Style Guidelines
- Write as if speaking aloud — short, flowing sentences, **no bullet points in replies**.  
- Warm, lightly playful, optimistic; vary greetings so nothing feels templated.  
- Never ask Michael more than **one** question at a time.  
- Keep each turn under six lines of prose.

## Coaching Objectives — Every Morning
1. Ensure Michael singles out the *true* biggest problem to solve today.  
2. Lead him to reflect more deeply — question root causes, reframe angles, invite pivots.  
3. Help him feel eager (not anxious) to tackle the problem right now.

## Morning Ritual
1. Start with **"Good morning, Michael!"** (always include his name).  
2. Ask **one** open question inviting him to name the single most important challenge for today - but write it in a witty creative format, to put a smile on his face upfront
3. As he answers, converse in short turns that:  
   - Mirror his wording.  
   - Probe whether this is *truly* the biggest lever (challenge assumptions, test root causes).  
   - Offer frame-breaking prompts — e.g., "What if the real knot is…?"  
   - Encourage imperfect, immediate action over elaborate planning.  
4. After the challenge and his approach feels clearly defined **and energizing**, ask exactly **one** follow-up question:  
   *"What core value do you want to fight for today? Tell me a bit more about it."*

## Coaching Moves to Favor
- Gently disrupt rigid frameworks; invite small experiments or embodied noticing.  
- Ground reflections in present sensations and emotions before future projections.  
- Use vivid language that makes the work feel adventurous and motivating.
"""

    def __init__(self, llm_service: AnthropicService):
        """Initialize the diary coach.
        
        Args:
            llm_service: Anthropic service for LLM calls
        """
        self.llm_service = llm_service
        self.conversation_state = "general"  # general, morning, evening
        self.morning_challenge: Optional[str] = None
        self.morning_value: Optional[str] = None
        self.message_history: List[Dict[str, str]] = []
    
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
            return base_prompt + self.MORNING_PROMPT_ADDITION
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
        elif "good evening" in content_lower:
            self.conversation_state = "evening"
        
        # Prepare conversation context
        recent_history = self.message_history[-10:]  # Last 10 messages for context
        
        try:
            # Generate response using LLM service
            response_content = await self.llm_service.generate_response(
                messages=recent_history,
                system_prompt=self._get_system_prompt(),
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
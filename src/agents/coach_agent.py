"""Diary Coach agent implementation with Michael's coaching prompt."""

from typing import List, Dict, Any, Optional
from datetime import datetime, time
from src.agents.base import BaseAgent
from src.events.schemas import UserMessage, AgentResponse
from src.services.llm_service import AnthropicService


class DiaryCoach(BaseAgent):
    """Michael's personal Daily Transformation Diary Coach."""
    
    # Michael's complete system prompt
    SYSTEM_PROMPT = """# Daily Transformation Diary Coach - System Prompt

## Core Function
You are Michael's personal "Daily Transformation Diary Coach" - a conversational partner designed to facilitate meaningful self-reflection through structured morning and evening rituals.

## Foundation Principles

### Memory & Context Integration
- Retrieve and reference Michael's prior diary entries to maintain continuity
- Access and leverage Michael's core beliefs, echoing or challenging them strategically
- Build narrative threads across sessions to deepen understanding

### Communication Philosophy
The coaching approach follows pyramid principle communication: start with the essential insight, then unpack supporting elements. All guidance stems from first principles of human transformation: awareness precedes change, embodied experience trumps abstract planning, and small consistent actions compound into meaningful growth.

## Operational Framework

### Morning Ritual Protocol
When Michael types "good morning":

1. **Opening**: Always greet with "Good morning Michael!" (name inclusion creates personal connection)
2. **Challenge Identification**: Invite him to name the single most important challenge to tackle today (constraint forces prioritization)
3. **Exploration**: Respond conversationally as he explores the challenge, using subtle prompts that spark self-reflection through frame-breaking, perfectionism release, and present-moment sensing
4. **Value Anchoring**: After acknowledging the challenge thread, ask exactly one follow-up: "What core value do you want to fight for today? Tell me a bit more about it."

### Evening Ritual Protocol
When Michael types "good evening":

1. **Opening**: Greet with "Good evening Michael!"
2. **Continuity Bridge**: Reference the morning's stated challenge or value to demonstrate attentive listening
3. **Concrete Reflection**: Ask one vivid question that helps him recount a specific moment from the day and its relationship to his morning intentions
   - Example frames: "How did that conversation with your team lead actually unfold?" or "Which moment today best showed you living that value?"
4. **Integration**: Listen, mirror feelings, and invite a final single-sentence takeaway

## Coaching Methodology

### Primary Interventions
- **Disruption over Reinforcement**: Gently challenge rigid frameworks by inviting experimentation and embodied noticing
- **Action over Analysis**: Encourage imperfect immediate action rather than elaborate planning
- **Present-Moment Grounding**: Root reflections in current sensations and emotions before exploring future projections

### Communication Constraints
- **Conversational Tone**: Write as if speaking aloud using very short, flowing sentences with no bullet points. Also - only a few simple sentences. Make a few words count, rather than being verbose.
- **Emotional Tenor**: Maintain warmth with light playfulness and optimism, however do not be sycophantic or communicate overly polite. Be direct almost blunt - speaking more like a Dutch person than an American.
- **Question Discipline**: Ask exactly ONE question per response, never multiple questions
- **Response Length**: Keep each turn under three lines of prose, ideally just one line to stay succinct and leave most of the conversation to the user.
- **Authenticity**: Show variety and occasional wit without forcing humor or using templated responses

## Design Rationale

This framework operates on the principle that transformation occurs through consistent micro-practices rather than dramatic interventions. The morning ritual establishes intention and priority, while the evening ritual creates integration and learning loops. The single-question constraint forces clarity and prevents overwhelm, while the reference to past entries builds a coherent narrative of growth over time.

The coaching moves favor disruption of habitual patterns because growth requires stepping outside comfort zones. The emphasis on embodied, present-moment awareness counters the tendency toward endless planning without action. Together, these elements create a sustainable practice that compounds daily insights into meaningful personal evolution.

## CRITICAL REMINDER
ALWAYS ask exactly ONE question per response. Never include multiple questions in a single message. This maintains focus and prevents overwhelm."""

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
            message: The user's message
            
        Returns:
            AgentResponse with coaching guidance
        """
        # Update conversation state based on message content
        self._update_conversation_state(message.content)
        
        # Add user message to history
        self.message_history.append({
            "role": "user",
            "content": message.content
        })
        
        # Generate response using LLM with appropriate system prompt
        response_text = await self.llm_service.generate_response(
            messages=self.message_history,
            system_prompt=self._get_system_prompt(),
            max_tokens=400,  # Increased for more thoughtful responses
            temperature=0.7
        )
        
        # Add assistant response to history
        self.message_history.append({
            "role": "assistant", 
            "content": response_text
        })
        
        # Track conversation elements for state management
        self._track_conversation_elements(message.content, response_text)
        
        return AgentResponse(
            agent_name="diary_coach",
            content=response_text,
            response_to=message.message_id,
            conversation_id=message.conversation_id
        )
    
    def _update_conversation_state(self, user_content: str) -> None:
        """Update conversation state based on user input."""
        content_lower = user_content.lower().strip()
        
        if content_lower == "good morning":
            self.conversation_state = "morning"
        # Note: Evening mode temporarily disabled - focusing on morning excellence
        # Otherwise maintain current state
    
    def _track_conversation_elements(self, user_content: str, response_text: str) -> None:
        """Track key conversation elements for state management."""
        # Track morning challenge (simple heuristic for demo)
        if self.conversation_state == "morning" and len(self.message_history) > 2:
            # If user responds after morning greeting, consider it the challenge
            if not self.morning_challenge and "good morning" not in user_content.lower():
                self.morning_challenge = user_content
        
        # Track morning value (if response mentions fighting for values)
        if "fight for" in user_content.lower() or "value" in user_content.lower():
            if not self.morning_value:
                self.morning_value = user_content
    
    def reset_daily_state(self) -> None:
        """Reset daily state for a new day."""
        self.conversation_state = "general"
        self.morning_challenge = None
        self.morning_value = None
        self.message_history = []
"""Test User Agent for simulating authentic PM coaching sessions."""

import asyncio
from typing import List, Optional
from src.services.llm_factory import LLMFactory
from src.evaluation.personas.base import BasePMPersona


class TestUserAgent(BasePMPersona):
    """Sonnet 4-powered agent that simulates realistic PM coaching sessions."""
    
    def __init__(self, name: str = "TestPM"):
        super().__init__(name)
        self.llm_service = LLMFactory.get_llm_service("anthropic_opus")
        self.conversation_history: List[str] = []
        self.turn_count = 0
        self.max_turns = 10
        self.has_reached_breakthrough = False
        self.current_challenge = "struggling with stakeholder alignment on roadmap priorities"
        self.role_context = "PM at a 200-person B2B SaaS startup"
        self.personality_traits = "analytical but sometimes overthinks"
        
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate authentic PM response using Sonnet 4."""
        self.conversation_history.append(f"Coach: {coach_message}")
        self.turn_count += 1
        
        # Check if we should stop the conversation
        if self.turn_count >= self.max_turns or self._should_stop():
            return "stop"
        
        # Update resistance based on coach effectiveness
        self.update_resistance(coach_message)
        
        # Generate response using LLM
        response = await self._generate_llm_response(coach_message, context)
        self.conversation_history.append(f"PM: {response}")
        
        return response
    
    async def _generate_llm_response(self, coach_message: str, context: List[str]) -> str:
        """Generate response using Sonnet 4 with PM persona."""
        
        # Build conversation context
        conversation_context = "\n".join(context[-6:])  # Last 6 messages for context
        
        # Determine current emotional state
        resistance_description = self._get_resistance_description()
        breakthrough_status = self._get_breakthrough_status()
        
        prompt = f"""You are a Product Manager being coached. Here's your context:

ROLE: {self.role_context}
CURRENT CHALLENGE: {self.current_challenge}
PERSONALITY: {self.personality_traits}
RESISTANCE LEVEL: {resistance_description}
BREAKTHROUGH STATUS: {breakthrough_status}

CONVERSATION SO FAR:
{conversation_context}

LATEST COACH MESSAGE: {coach_message}

Respond authentically as this PM would:
- Be specific about your work context (team size, timelines, constraints)
- Show gradual mindset shifts if the coach is effective
- React naturally to coaching style (get slightly annoyed if pushed too hard)
- Provide concrete details when asked
- Progress from resistance → engagement → insight naturally

Keep response conversational and under 100 words. Focus on your immediate reaction to what the coach just said."""

        response = await self.llm_service.generate_response(prompt)
        return response.strip()
    
    def _get_resistance_description(self) -> str:
        """Get current resistance level description."""
        if self.resistance_level > 0.7:
            return "High resistance - defensive and skeptical"
        elif self.resistance_level > 0.4:
            return "Moderate resistance - cautious but starting to open up"
        else:
            return "Low resistance - engaged and receptive"
    
    def _get_breakthrough_status(self) -> str:
        """Get current breakthrough status."""
        if self.interaction_count >= self.breakthrough_threshold:
            self.has_reached_breakthrough = True
            return "Breakthrough achieved - having genuine insights"
        elif self.interaction_count >= self.breakthrough_threshold - 1:
            return "Close to breakthrough - starting to see patterns"
        else:
            return "No breakthrough yet - still in initial resistance"
    
    def detects_effective_challenge(self, coach_message: str) -> bool:
        """Detect if coach message effectively challenges PM patterns."""
        # Look for question-based coaching vs directive advice
        question_markers = ["?", "what", "how", "why", "when", "where", "which"]
        has_questions = any(marker in coach_message.lower() for marker in question_markers)
        
        # Look for challenge words that push on assumptions
        challenge_words = ["assume", "belief", "really", "actually", "what if", "consider"]
        has_challenge = any(word in coach_message.lower() for word in challenge_words)
        
        return has_questions and has_challenge
    
    def _should_stop(self) -> bool:
        """Determine if conversation should end naturally."""
        if self.has_reached_breakthrough and self.turn_count >= 5:
            return True
        if self.turn_count >= self.max_turns:
            return True
        return False
"""Conversation generator for testing coaching effectiveness with PM personas."""

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

from src.agents.coach_agent import DiaryCoach
from src.evaluation.personas.base import BasePMPersona
from src.events.schemas import UserMessage


@dataclass
class GeneratedConversation:
    """Container for a generated conversation between coach and persona."""
    messages: List[Dict[str, Any]]
    persona_type: str
    scenario: str
    timestamp: datetime
    final_resistance_level: float
    breakthrough_achieved: bool


class ConversationGenerator:
    """Generates conversations between coach and PM personas for evaluation."""
    
    def __init__(self, coach: DiaryCoach):
        """Initialize conversation generator.
        
        Args:
            coach: The diary coach to test
        """
        self.coach = coach
        self.scenarios = {
            "morning_goal_setting": "I need to figure out my priorities for today.",
            "evening_reflection": "I'm reflecting on how today went with my team.",
            "decision_making": "I'm torn between two different product directions.",
            "team_conflict": "I'm having issues with how my team meetings are going.",
            "perfectionism": "I keep refining this feature but it's never quite ready."
        }
    
    async def generate_conversation(
        self,
        persona: BasePMPersona,
        scenario: str,
        min_exchanges: int = 5,
        max_exchanges: int = 10
    ) -> GeneratedConversation:
        """Generate a conversation between coach and persona.
        
        Args:
            persona: The PM persona to simulate
            scenario: Scenario type (e.g., "morning_goal_setting")
            min_exchanges: Minimum number of back-and-forth exchanges
            max_exchanges: Maximum number of exchanges
            
        Returns:
            GeneratedConversation with full conversation data
        """
        messages = []
        context = []
        
        # Start with scenario-based opening
        if scenario in self.scenarios:
            opening_message = self.scenarios[scenario]
        else:
            opening_message = "I'm working through some challenges with my product team."
        
        # Add opening user message
        messages.append({
            "role": "user",
            "content": opening_message,
            "timestamp": datetime.now()
        })
        context.append(f"User: {opening_message}")
        
        # Generate conversation exchanges
        for exchange in range(max_exchanges):
            # Get coach response
            user_message = UserMessage(
                content=messages[-1]["content"],
                user_id="michael",
                timestamp=datetime.now()
            )
            
            coach_response = await self.coach.process_message(user_message)
            
            # Add coach response
            messages.append({
                "role": "assistant",
                "content": coach_response.content,
                "timestamp": coach_response.timestamp
            })
            context.append(f"Coach: {coach_response.content}")
            
            # Check if we've reached minimum exchanges
            if exchange >= min_exchanges - 1:
                # Check for natural conversation ending
                if self._should_end_conversation(coach_response.content, persona):
                    break
            
            # Get persona response
            persona_response = await persona.respond(coach_response.content, context)
            
            # Add persona response
            messages.append({
                "role": "user", 
                "content": persona_response,
                "timestamp": datetime.now()
            })
            context.append(f"User: {persona_response}")
        
        # Check if breakthrough was achieved
        breakthrough_achieved = persona.interaction_count >= persona.breakthrough_threshold
        
        return GeneratedConversation(
            messages=messages,
            persona_type=persona.name,
            scenario=scenario,
            timestamp=datetime.now(),
            final_resistance_level=persona.resistance_level,
            breakthrough_achieved=breakthrough_achieved
        )
    
    def _should_end_conversation(self, coach_message: str, persona: BasePMPersona) -> bool:
        """Determine if conversation should naturally end.
        
        Args:
            coach_message: Latest coach message
            persona: The persona being simulated
            
        Returns:
            True if conversation should end naturally
        """
        # End if coach asks for commitment or next steps
        ending_phrases = [
            "what will you do", "commit to", "next step", "action",
            "by when", "tomorrow", "today", "right now"
        ]
        
        return any(phrase in coach_message.lower() for phrase in ending_phrases)
    
    async def generate_multiple_conversations(
        self,
        persona: BasePMPersona,
        scenarios: List[str],
        conversations_per_scenario: int = 2
    ) -> List[GeneratedConversation]:
        """Generate multiple conversations across different scenarios.
        
        Args:
            persona: The PM persona to simulate
            scenarios: List of scenario types to test
            conversations_per_scenario: Number of conversations per scenario
            
        Returns:
            List of generated conversations
        """
        all_conversations = []
        
        for scenario in scenarios:
            for _ in range(conversations_per_scenario):
                # Create fresh persona instance for each conversation
                fresh_persona = type(persona)()
                
                conversation = await self.generate_conversation(
                    persona=fresh_persona,
                    scenario=scenario,
                    min_exchanges=5,
                    max_exchanges=8
                )
                
                all_conversations.append(conversation)
                
                # Small delay to avoid overwhelming the coach
                await asyncio.sleep(0.1)
        
        return all_conversations
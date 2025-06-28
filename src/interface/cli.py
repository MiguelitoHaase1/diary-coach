"""CLI interface for diary coach conversations."""

import asyncio
import sys
from datetime import datetime
from typing import Optional
from src.agents.coach_agent import DiaryCoach
from src.events.bus import EventBus
from src.events.schemas import UserMessage


class DiaryCoachCLI:
    """Command-line interface for diary coach conversations."""
    
    def __init__(self, coach: DiaryCoach, event_bus: EventBus):
        """Initialize CLI with coach and event bus.
        
        Args:
            coach: The diary coach agent
            event_bus: Event bus for message routing
        """
        self.coach = coach
        self.event_bus = event_bus
        self.running = True
    
    async def process_input(self, user_input: str) -> Optional[str]:
        """Process user input and return coach response.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Coach response text, or None if user wants to exit
        """
        # Check for exit commands
        if user_input.lower().strip() in ["exit", "quit"]:
            return None
        
        try:
            # Create user message
            user_message = UserMessage(
                content=user_input,
                user_id="michael",
                timestamp=datetime.now()
            )
            
            # Process through coach
            response = await self.coach.process_message(user_message)
            
            return response.content
            
        except Exception as e:
            # Handle errors gracefully
            return f"Sorry, I encountered an error: {str(e)}. Please try again."
    
    def get_session_cost(self) -> float:
        """Get current session cost from coach's LLM service."""
        return self.coach.llm_service.session_cost
    
    async def run(self) -> None:
        """Run the interactive CLI loop."""
        print("🌅 Diary Coach Ready (type 'exit' to quit)")
        
        while self.running:
            try:
                # Get user input
                user_input = await self._get_input("> ")
                
                if not user_input.strip():
                    continue
                
                # Process input
                response = await self.process_input(user_input)
                
                if response is None:
                    # User wants to exit
                    print("Goodbye! Have a transformative day! 🌟")
                    break
                
                # Display response
                print(f"\n{response}\n")
                
                # Display cost information
                cost = self.get_session_cost()
                print(f"💰 Session cost: ${cost:.4f}")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\nGoodbye! Have a transformative day! 🌟")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    async def _get_input(self, prompt: str) -> str:
        """Get async input from user.
        
        Args:
            prompt: The input prompt to display
            
        Returns:
            User input string
        """
        # For now, use synchronous input
        # In a real implementation, we might use aioconsole or similar
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)
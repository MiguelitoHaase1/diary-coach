"""Main entry point for the diary coach system."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from src.services.llm_service import AnthropicService
from src.agents.coach_agent import DiaryCoach
from src.interface.enhanced_cli import EnhancedCLI
from src.events.bus import EventBus
from src.persistence.conversation_storage import ConversationStorage


async def create_diary_coach_system():
    """Create and initialize the complete diary coach system."""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    # Create LLM service
    llm_service = AnthropicService(
        api_key=api_key,
        model=os.getenv("COACH_MODEL", "claude-sonnet-4-20250514")
    )
    
    # Create coach agent
    coach = DiaryCoach(llm_service=llm_service)
    
    # Create event bus
    event_bus = EventBus()
    
    # Create CLI interface
    cli = EnhancedCLI(coach=coach, event_bus=event_bus)
    
    # Create conversation storage
    storage_path = Path.cwd() / "conversations"
    conversation_storage = ConversationStorage(base_path=storage_path)
    
    return {
        "llm_service": llm_service,
        "coach": coach,
        "cli": cli,
        "event_bus": event_bus,
        "conversation_storage": conversation_storage
    }


async def main():
    """Main entry point for running the diary coach."""
    try:
        # Initialize system
        system = await create_diary_coach_system()
        cli = system["cli"]
        
        # Run the CLI
        await cli.run()
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
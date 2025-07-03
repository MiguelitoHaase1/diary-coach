#!/usr/bin/env python3
"""Direct script to run comprehensive evaluation."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.agents.coach_agent import DiaryCoach
from src.services.llm_service import AnthropicService
from src.evaluation.eval_command import EvalCommand


async def main():
    """Run comprehensive evaluation directly."""
    print("🚀 Starting comprehensive persona-based evaluation...")
    
    try:
        # Initialize coach with standard service
        llm_service = AnthropicService(model="claude-3-5-sonnet-20241022")
        coach = DiaryCoach(llm_service=llm_service)
        
        # Initialize eval command
        eval_command = EvalCommand(coach)
        
        # Run comprehensive evaluation
        results = await eval_command.run_comprehensive_eval(
            conversations_per_persona=2
        )
        
        print("\n✨ Evaluation complete!")
        print("Check the generated files in docs/prototype/")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""Test script for manual subjective evaluation feature."""

import asyncio
import os
from dotenv import load_dotenv
from src.evaluation.conversation_test_runner import ConversationTestRunner

async def run_test_with_manual_eval():
    """Run a conversation test and generate deep report with evaluations."""
    
    # Load environment variables
    load_dotenv()
    
    print("\n" + "=" * 60)
    print("DEEP REPORT TEST")
    print("This will run a coaching conversation and generate a deep report with evaluations.")
    print("=" * 60 + "\n")
    
    # Create test runner
    runner = ConversationTestRunner()
    
    try:
        # Run a single test
        print("Starting coaching conversation test...")
        result = await runner.run_conversation_test(
            test_name="manual_eval_test"
        )
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        # Show summary
        print(f"\nConversation Summary:")
        print(f"- Total turns: {result['turn_count']}")
        print(f"- Messages: {result['test_user_stats']['interaction_count']}")
        print(f"- Breakthrough achieved: {result['test_user_stats']['breakthrough_achieved']}")
        
        # The automatic evaluations are now included in the deep report
        
        print("\nCheck the following directories for outputs:")
        print("- Deep Thoughts: docs/prototype/DeepThoughts/")
        print("- Manual Evaluations: docs/prototype/manual_evals/")
        
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(run_test_with_manual_eval())
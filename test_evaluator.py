#!/usr/bin/env python3
"""
Quick test to verify evaluators are working.
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add project root to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from langsmith.schemas import Run, Example
from src.evaluation.langsmith_evaluators import ProblemSignificanceEvaluator


async def test_evaluator():
    """Test a single evaluator with a mock run."""
    
    # Create a mock run
    mock_run = Run(
        id=uuid.uuid4(),
        name="test",
        run_type="chain",
        start_time=datetime.now(),
        trace_id=uuid.uuid4(),
        inputs={
            "messages": [
                {"role": "user", "content": "I'm feeling overwhelmed with all my tasks at work. I don't know where to start or what's most important."},
                {"role": "assistant", "content": "I can hear that you're feeling overwhelmed. Tell me, what would happen if you didn't address this feeling of being overwhelmed?"}
            ]
        },
        outputs={
            "response": "I can hear that you're feeling overwhelmed. Tell me, what would happen if you didn't address this feeling of being overwhelmed?"
        }
    )
    
    # Create evaluator
    evaluator = ProblemSignificanceEvaluator()
    
    # Test the async evaluation
    print("🔬 Testing evaluator...")
    try:
        # Let's also capture the raw LLM response to debug JSON parsing
        conversation = mock_run.inputs.get("messages", [])
        coach_response = mock_run.outputs.get("response", "")
        client_statement = evaluator._extract_client_statement(conversation)
        eval_prompt = evaluator._build_eval_prompt(conversation, coach_response, client_statement)
        
        # Call LLM directly to see raw response
        messages = [{"role": "user", "content": eval_prompt}]
        raw_response = await evaluator.llm_service.generate_response(messages)
        print(f"📝 Raw LLM response: {raw_response}")
        
        # Now test the full evaluation
        result = await evaluator.aevaluate_run(mock_run)
        print(f"✅ Evaluator result: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Evaluator failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_evaluator())
    if success:
        print("\n🎉 Evaluator test passed!")
    else:
        print("\n💥 Evaluator test failed!")
        sys.exit(1)
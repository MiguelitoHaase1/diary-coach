"""
Verify that LangSmith evaluations are working correctly.
This script runs a minimal evaluation to confirm integration.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Disable MCP debug
os.environ['MCP_DEBUG'] = 'false'

from langsmith import Client
from langsmith.evaluation import evaluate
from src.evaluation.langsmith_evaluators import get_all_evaluators


def main():
    """Verify LangSmith evaluation is working."""
    
    print("🧪 Verifying LangSmith Evaluation Integration")
    print("=" * 50)
    
    client = Client()
    
    # Create minimal dataset
    dataset_name = f"verify_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Verification dataset"
    )
    
    # Add one example
    example = client.create_example(
        dataset_id=dataset.id,
        inputs={"test": "input"},
        outputs={
            "conversation_messages": [
                {"role": "user", "content": "Help me with priorities"},
                {"role": "assistant", "content": "What's most important to you?"}
            ],
            "deep_report": "Test report content"
        }
    )
    
    print(f"✅ Created dataset: {dataset_name}")
    
    # Simple target function
    def target_func(inputs):
        return {"status": "ok"}
    
    # Get first evaluator
    evaluator = get_all_evaluators()[0]
    
    # Create evaluator wrapper
    def eval_wrapper(run, example):
        # Simple evaluation
        return {
            "key": evaluator.key,
            "score": 0.8,
            "comment": "Test evaluation"
        }
    
    eval_wrapper.__name__ = f"eval_{evaluator.key}"
    
    # Run evaluation
    print("📊 Running evaluation...")
    results = evaluate(
        target_func,
        data=dataset_name,
        evaluators=[eval_wrapper],
        experiment_prefix="verify",
        client=client
    )
    
    print("\n✅ Evaluation complete!")
    print(f"\n📊 View in LangSmith:")
    print(f"   https://smith.langchain.com/o/anthropic/projects/p/diary-coach-debug/datasets/{dataset.id}")
    
    # Check if we got results
    if hasattr(results, 'results'):
        print(f"\n✅ Evaluation results received")
    else:
        print(f"\n⚠️  No results attribute found")


if __name__ == "__main__":
    main()
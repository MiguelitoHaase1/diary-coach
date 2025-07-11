"""
Simple test to verify LangSmith evaluation integration.
This creates a minimal dataset and runs evaluations to ensure they appear in the dashboard.
"""

import asyncio
import os
import sys
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Disable MCP debug output
os.environ['MCP_DEBUG'] = 'false'

from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

from src.evaluation.langsmith_evaluators import get_all_evaluators


def create_simple_dataset(client: Client) -> str:
    """Create a simple dataset for testing."""
    
    dataset_name = f"coaching_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Simple test dataset for evaluation"
    )
    
    # Create a simple example
    example_conversation = [
        {"role": "user", "content": "I'm overwhelmed with priorities"},
        {"role": "assistant", "content": "What's the most important thing you need to tackle?"},
        {"role": "user", "content": "I guess getting stakeholder alignment"},
        {"role": "assistant", "content": "What would alignment look like specifically?"}
    ]
    
    example = client.create_example(
        dataset_id=dataset.id,
        inputs={"conversation_id": "test_001"},
        outputs={
            "conversation_messages": example_conversation,
            "deep_report": "The coach helped identify stakeholder alignment as key priority."
        }
    )
    
    print(f"✅ Created dataset '{dataset_name}' with 1 example")
    return dataset_name


def simple_coach_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Simple function for testing."""
    return {"status": "completed", "conversation_id": inputs.get("conversation_id")}


def create_simple_evaluator(evaluator):
    """Create a simplified evaluator wrapper."""
    
    def eval_func(run: Run, example: Example) -> Dict[str, Any]:
        """Simple sync evaluator."""
        
        # For testing, just return a fixed score
        return {
            "key": evaluator.key,
            "score": 0.75,
            "comment": f"Test evaluation for {evaluator.key}"
        }
    
    eval_func.__name__ = f"eval_{evaluator.key}"
    return eval_func


async def test_langsmith_evaluation():
    """Test LangSmith evaluation with minimal setup."""
    
    print("🧪 Testing LangSmith Evaluation Integration")
    print("=" * 50)
    
    client = Client()
    
    # Create simple dataset
    dataset_name = create_simple_dataset(client)
    
    # Get just first 2 evaluators for testing
    evaluators = get_all_evaluators()[:2]
    simple_evaluators = [create_simple_evaluator(e) for e in evaluators]
    
    print(f"\n📊 Running evaluation with {len(simple_evaluators)} evaluators...")
    
    try:
        # Run evaluation (synchronous version for simplicity)
        results = evaluate(
            simple_coach_function,
            data=dataset_name,
            evaluators=simple_evaluators,
            experiment_prefix="test_eval",
            metadata={
                "test_type": "simple",
                "timestamp": datetime.now().isoformat()
            },
            client=client
        )
        
        print("\n✅ Evaluation completed!")
        
        # Get project info
        project = os.getenv('LANGSMITH_PROJECT', 'default')
        
        print(f"\n📊 View results at:")
        print(f"   https://smith.langchain.com/o/anthropic/projects/p/{project}/datasets")
        print(f"   Dataset: {dataset_name}")
        
        # Print any available metrics
        if hasattr(results, 'aggregate_metrics'):
            print("\n📈 Results:")
            for metric, value in results.aggregate_metrics.items():
                print(f"   {metric}: {value}")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point."""
    await test_langsmith_evaluation()


if __name__ == "__main__":
    asyncio.run(main())
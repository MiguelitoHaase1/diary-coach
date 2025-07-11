"""
Proper LangSmith evaluation integration for the coaching system.

This script properly integrates the 7 evaluators with LangSmith's evaluation framework,
ensuring that evaluation results appear in the LangSmith dashboard.
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from langsmith import Client
from langsmith.evaluation import evaluate, aevaluate
from langsmith.schemas import Example, Run

from src.evaluation.conversation_test_runner import ConversationTestRunner
from src.evaluation.langsmith_evaluators import get_all_evaluators
from src.evaluation.average_score_evaluator import AverageScoreEvaluator
from src.orchestration.context_graph import create_context_aware_graph
from src.services.llm_factory import LLMFactory, LLMTier


async def create_evaluation_dataset(client: Client, num_conversations: int = 2) -> str:
    """Create a dataset with test coaching conversations."""
    
    print(f"📊 Creating evaluation dataset with {num_conversations} conversations...")
    
    # Create dataset
    dataset_name = f"coaching_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Coaching conversations for evaluation"
    )
    
    # Run test conversations
    test_runner = ConversationTestRunner()
    test_results = await test_runner.run_batch_tests(num_conversations)
    
    # Create examples
    examples_created = 0
    for result in test_results:
        if "error" not in result:
            # The input is just the conversation ID
            # The output is the full conversation data
            example = client.create_example(
                dataset_id=dataset.id,
                inputs={
                    "conversation_id": result["conversation_id"],
                    "test_name": result["test_name"]
                },
                outputs={
                    "conversation_messages": result["conversation_messages"],
                    "deep_report": result["deep_report"]["deep_thoughts_content"],
                    "test_user_stats": result["test_user_stats"],
                    "context_usage": result["context_usage"]
                }
            )
            examples_created += 1
            print(f"  ✅ Created example: {result['test_name']}")
    
    print(f"✅ Dataset '{dataset_name}' created with {examples_created} examples")
    return dataset_name


async def coach_conversation_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Function that represents a complete coaching conversation.
    For evaluation purposes, we're using pre-generated conversations from the dataset.
    """
    
    # In a real scenario, this would run a full conversation
    # For evaluation, we return the expected outputs structure
    return {
        "conversation_id": inputs.get("conversation_id"),
        "status": "completed",
        "message": "Using pre-generated conversation from dataset"
    }


def create_langsmith_evaluator(evaluator):
    """Convert our evaluator to a LangSmith-compatible evaluator function."""
    
    async def evaluate_run(run: Run, example: Example) -> Dict[str, Any]:
        """LangSmith evaluator function that uses our custom evaluator."""
        
        # The example outputs contain the full conversation data
        conversation_messages = example.outputs.get("conversation_messages", [])
        deep_report = example.outputs.get("deep_report", "")
        
        # Create a run-like object with the conversation data
        class ConversationRun:
            def __init__(self, conversation, deep_report):
                self.id = run.id
                self.inputs = {"messages": conversation}
                self.outputs = {"response": deep_report}
                self.run_type = "llm"
                self.start_time = run.start_time
                self.trace_id = run.trace_id
        
        conversation_run = ConversationRun(conversation_messages, deep_report)
        
        # Run our evaluator
        result = await evaluator.aevaluate_run(conversation_run)
        
        # Format for LangSmith
        return {
            "key": evaluator.key,
            "score": result.get("score", 0.0),
            "comment": result.get("reasoning", ""),
            "feedback": result.get("feedback", {})
        }
    
    # Set the function name for LangSmith
    evaluate_run.__name__ = f"evaluate_{evaluator.key}"
    
    return evaluate_run


async def run_langsmith_evaluation():
    """Run evaluation using LangSmith's proper evaluation framework."""
    
    print("🚀 Running LangSmith Evaluation Integration")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("LANGSMITH_API_KEY"):
        print("❌ LANGSMITH_API_KEY not set")
        return
    
    client = Client()
    
    # Step 1: Create dataset
    dataset_name = await create_evaluation_dataset(client, num_conversations=2)
    
    # Step 2: Get evaluators and convert them
    print("\n📊 Preparing evaluators...")
    evaluators = get_all_evaluators()
    average_evaluator = AverageScoreEvaluator()
    all_evaluators = evaluators + [average_evaluator]
    
    # Convert to LangSmith evaluators
    langsmith_evaluators = [create_langsmith_evaluator(e) for e in all_evaluators]
    
    print(f"✅ Prepared {len(langsmith_evaluators)} evaluators:")
    for evaluator in all_evaluators:
        print(f"   - {evaluator.key}")
    
    # Step 3: Run evaluation
    print(f"\n🧪 Running evaluation on dataset '{dataset_name}'...")
    
    try:
        # Use aevaluate for async evaluators
        results = await aevaluate(
            coach_conversation_function,
            data=dataset_name,
            evaluators=langsmith_evaluators,
            experiment_prefix="coaching_eval",
            metadata={
                "evaluator_count": len(langsmith_evaluators),
                "timestamp": datetime.now().isoformat(),
                "evaluation_type": "full_conversation"
            },
            max_concurrency=2,  # Limit concurrency to avoid rate limits
            client=client
        )
        
        print("\n✅ Evaluation complete!")
        
        # Extract experiment name from results
        experiment_name = getattr(results, 'experiment_name', 'coaching_eval')
        
        print(f"\n📊 View results in LangSmith:")
        print(f"   https://smith.langchain.com/o/anthropic/datasets/{dataset_name}")
        print(f"   Look for experiment: {experiment_name}")
        
        # Try to get aggregate metrics if available
        if hasattr(results, 'aggregate_metrics'):
            print("\n📈 Aggregate Metrics:")
            for metric, value in results.aggregate_metrics.items():
                if isinstance(value, dict) and 'mean' in value:
                    print(f"   {metric}: {value['mean']:.2f}")
                else:
                    print(f"   {metric}: {value}")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_single_evaluator():
    """Test a single evaluator to verify it's working."""
    
    print("\n🧪 Testing single evaluator...")
    
    # Get first evaluator
    evaluators = get_all_evaluators()
    if not evaluators:
        print("❌ No evaluators found")
        return
    
    evaluator = evaluators[0]
    print(f"Testing: {evaluator.key}")
    
    # Create sample data
    from langsmith.schemas import Run
    import uuid
    
    sample_conversation = [
        {"role": "user", "content": "I need help with priorities"},
        {"role": "assistant", "content": "What's most important to you right now?"}
    ]
    
    mock_run = Run(
        id=str(uuid.uuid4()),
        name="test_evaluation",
        inputs={"messages": sample_conversation},
        outputs={"response": "Sample deep report"},
        run_type="llm",
        start_time=datetime.now(),
        trace_id=str(uuid.uuid4())
    )
    
    try:
        result = await evaluator.aevaluate_run(mock_run)
        print(f"✅ Evaluation successful!")
        print(f"   Score: {result.get('score', 0.0)}")
        print(f"   Key: {result.get('key', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {str(e)}")


async def main():
    """Main entry point."""
    
    # Test single evaluator first
    await test_single_evaluator()
    
    # Run full evaluation
    await run_langsmith_evaluation()


if __name__ == "__main__":
    asyncio.run(main())
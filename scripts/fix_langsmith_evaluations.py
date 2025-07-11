"""
Fix LangSmith evaluation integration by using proper LangSmith dataset and evaluation API.

The issue: We're creating mock Run objects instead of using real LangSmith evaluation framework.
The solution: Use LangSmith's dataset and evaluation API properly.
"""

import asyncio
import os
from typing import List, Dict, Any
from datetime import datetime
import json
from dotenv import load_dotenv

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


async def create_langsmith_dataset():
    """Create a LangSmith dataset with test conversations."""
    
    client = Client()
    
    # Create dataset
    dataset_name = f"coaching_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Test coaching conversations for evaluation"
    )
    
    print(f"📊 Created dataset: {dataset_name}")
    
    # Run test conversations
    test_runner = ConversationTestRunner()
    test_results = await test_runner.run_batch_tests(2)  # Run 2 test conversations
    
    # Create examples from test results
    examples_created = 0
    for result in test_results:
        if "error" not in result:
            # Create example with conversation as input and deep report as output
            example = client.create_example(
                dataset_id=dataset.id,
                inputs={
                    "messages": result["conversation_messages"],
                    "conversation_id": result["conversation_id"],
                    "test_name": result["test_name"]
                },
                outputs={
                    "deep_report": result["deep_report"]["deep_thoughts_content"],
                    "test_user_stats": result["test_user_stats"],
                    "context_usage": result["context_usage"]
                }
            )
            examples_created += 1
            print(f"✅ Created example: {result['test_name']}")
    
    print(f"📊 Dataset created with {examples_created} examples")
    return dataset


async def coach_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Function that represents a coaching conversation for LangSmith evaluation."""
    
    # Extract conversation messages
    messages = inputs.get("messages", [])
    conversation_id = inputs.get("conversation_id", f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Since we already have the full conversation, we just need to generate a deep report
    llm_service = LLMFactory.create_service(LLMTier.O3)
    from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
    
    deep_thoughts_generator = DeepThoughtsGenerator(tier=LLMTier.O3)
    deep_thoughts = await deep_thoughts_generator.generate_deep_thoughts(
        conversation_history=messages,
        conversation_id=conversation_id,
        include_evals=False,
        include_transcript=False
    )
    
    return {
        "deep_report": deep_thoughts,
        "conversation_messages": messages,
        "message_count": len(messages)
    }


async def run_proper_langsmith_evaluation():
    """Run evaluation using proper LangSmith API."""
    
    print("🚀 Running proper LangSmith evaluation...")
    
    # Check environment
    if not os.getenv("LANGSMITH_API_KEY"):
        print("❌ LANGSMITH_API_KEY not set")
        return
    
    client = Client()
    
    # Step 1: Create dataset with test conversations
    dataset = await create_langsmith_dataset()
    
    # Step 2: Get all evaluators
    evaluators = get_all_evaluators()
    average_evaluator = AverageScoreEvaluator()
    all_evaluators = evaluators + [average_evaluator]
    
    print(f"\n📊 Running evaluation with {len(all_evaluators)} evaluators...")
    
    # Step 3: Run evaluation using LangSmith's aevaluate
    try:
        results = await aevaluate(
            coach_function,
            data=dataset.name,
            evaluators=all_evaluators,
            experiment_prefix="coaching_eval",
            metadata={
                "evaluator_count": len(all_evaluators),
                "timestamp": datetime.now().isoformat()
            },
            max_concurrency=4
        )
        
        print("\n✅ Evaluation complete!")
        print(f"📊 View results at: https://smith.langchain.com/o/{os.getenv('LANGSMITH_PROJECT', 'default')}/datasets/{dataset.id}")
        
        # Extract and display summary statistics
        aggregate_metrics = results.aggregate_metrics if hasattr(results, 'aggregate_metrics') else {}
        
        print("\n📈 Summary Statistics:")
        for metric_name, metric_value in aggregate_metrics.items():
            if isinstance(metric_value, dict) and 'mean' in metric_value:
                print(f"  {metric_name}: {metric_value['mean']:.2f}")
            else:
                print(f"  {metric_name}: {metric_value}")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_direct_feedback_submission():
    """Test direct feedback submission to LangSmith."""
    
    print("\n🧪 Testing direct feedback submission...")
    
    client = Client()
    
    # Create a test run
    run = client.create_run(
        name="test_coaching_conversation",
        run_type="chain",
        inputs={"test": "direct feedback test"},
        project_name=os.getenv('LANGSMITH_PROJECT', 'diary-coach-debug')
    )
    
    print(f"📊 Created test run: {run.id}")
    
    # Submit feedback
    try:
        client.create_feedback(
            run_id=run.id,
            key="test_score",
            score=0.85,
            comment="Testing direct feedback submission"
        )
        print(f"✅ Feedback submitted successfully")
        print(f"📊 View at: https://smith.langchain.com/project/{os.getenv('LANGSMITH_PROJECT')}/runs/{run.id}")
        
    except Exception as e:
        print(f"❌ Feedback submission failed: {str(e)}")
    
    # End the run
    client.update_run(
        run.id,
        outputs={"status": "test_complete"},
        end_time=datetime.now()
    )


async def main():
    """Main entry point."""
    
    print("🔧 LangSmith Evaluation Fix")
    print("=" * 50)
    
    # Check environment
    print("📊 Environment Check:")
    print(f"  LANGSMITH_API_KEY: {'✅ Set' if os.getenv('LANGSMITH_API_KEY') else '❌ Not set'}")
    print(f"  LANGSMITH_PROJECT: {os.getenv('LANGSMITH_PROJECT', 'Not set')}")
    print(f"  ANTHROPIC_API_KEY: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Not set'}")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    
    # Test direct feedback first
    await test_direct_feedback_submission()
    
    # Run proper evaluation
    await run_proper_langsmith_evaluation()


if __name__ == "__main__":
    asyncio.run(main())
"""Automated conversation test suite for regression detection."""

import asyncio
import argparse
from typing import List, Dict, Any
from datetime import datetime
import json
import os

from src.evaluation.conversation_test_runner import ConversationTestRunner
from src.evaluation.langsmith_evaluators import get_all_evaluators
from src.evaluation.average_score_evaluator import AverageScoreEvaluator


async def run_test_suite(
    test_count: int = 3,
    save_results: bool = True,
    verbose: bool = False
) -> Dict[str, Any]:
    """Run automated conversation test suite.
    
    Args:
        test_count: Number of test conversations to run
        save_results: Whether to save results to file
        verbose: Whether to print detailed results
        
    Returns:
        Test suite results summary
    """
    
    print(f"🤖 Starting conversation test suite with {test_count} tests...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize test runner
    test_runner = ConversationTestRunner()
    
    # Run batch tests
    start_time = datetime.now()
    test_results = await test_runner.run_batch_tests(test_count)
    end_time = datetime.now()
    
    # Calculate summary statistics
    successful_tests = [r for r in test_results if "error" not in r]
    failed_tests = [r for r in test_results if "error" in r]
    
    total_duration = (end_time - start_time).total_seconds()
    avg_duration_per_test = total_duration / test_count if test_count > 0 else 0
    
    # Calculate conversation quality metrics
    conversation_stats = _calculate_conversation_stats(successful_tests)
    
    # Save results if requested
    if save_results:
        results_path = await test_runner.save_test_results(
            test_results,
            f"docs/prototype/ConversationTests/TestSuite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        print(f"💾 Results saved to: {results_path}")
    
    # Print summary
    print(f"\n📊 Test Suite Summary")
    print(f"=" * 50)
    print(f"Total Tests: {test_count}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {len(successful_tests)/test_count*100:.1f}%")
    print(f"Total Duration: {total_duration:.1f}s")
    print(f"Avg Duration/Test: {avg_duration_per_test:.1f}s")
    
    if conversation_stats:
        print(f"\n🎯 Conversation Quality")
        print(f"Avg Turn Count: {conversation_stats['avg_turns']:.1f}")
        print(f"Avg Breakthrough Rate: {conversation_stats['breakthrough_rate']:.1%}")
        print(f"Avg Resistance Reduction: {conversation_stats['avg_resistance_reduction']:.1%}")
    
    # Print detailed results if verbose
    if verbose:
        print(f"\n📝 Detailed Results")
        print(f"=" * 50)
        
        for i, result in enumerate(test_results, 1):
            print(f"\nTest {i}: {result.get('test_name', 'Unknown')}")
            
            if "error" in result:
                print(f"  ❌ ERROR: {result['error']}")
                continue
            
            print(f"  ✅ SUCCESS")
            print(f"  Turns: {result.get('turn_count', 0)}")
            
            user_stats = result.get('test_user_stats', {})
            print(f"  Breakthrough: {'Yes' if user_stats.get('breakthrough_achieved') else 'No'}")
            print(f"  Final Resistance: {user_stats.get('resistance_level', 0):.2f}")
            
            context_usage = result.get('context_usage', {})
            todos_fetched = context_usage.get('todos_fetched', False)
            print(f"  Context Used: {'Yes' if todos_fetched else 'No'}")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"  - {test.get('test_name', 'Unknown')}: {test.get('error', 'Unknown error')}")
    
    # Build summary result
    summary = {
        "test_count": test_count,
        "successful": len(successful_tests),
        "failed": len(failed_tests),
        "success_rate": len(successful_tests) / test_count if test_count > 0 else 0,
        "total_duration_seconds": total_duration,
        "avg_duration_per_test": avg_duration_per_test,
        "conversation_stats": conversation_stats,
        "timestamp": datetime.now().isoformat(),
        "results_saved": save_results
    }
    
    return summary


def _calculate_conversation_stats(successful_tests: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate conversation quality statistics from successful tests."""
    
    if not successful_tests:
        return {}
    
    turn_counts = []
    breakthrough_achieved = []
    resistance_reductions = []
    
    for test in successful_tests:
        # Turn count
        turn_count = test.get('turn_count', 0)
        if turn_count > 0:
            turn_counts.append(turn_count)
        
        # Breakthrough achievement
        user_stats = test.get('test_user_stats', {})
        breakthrough_achieved.append(user_stats.get('breakthrough_achieved', False))
        
        # Resistance reduction (assuming started at 0.8)
        initial_resistance = 0.8
        final_resistance = user_stats.get('resistance_level', 0.8)
        resistance_reduction = (initial_resistance - final_resistance) / initial_resistance
        resistance_reductions.append(max(0, resistance_reduction))
    
    return {
        "avg_turns": sum(turn_counts) / len(turn_counts) if turn_counts else 0,
        "breakthrough_rate": sum(breakthrough_achieved) / len(breakthrough_achieved) if breakthrough_achieved else 0,
        "avg_resistance_reduction": sum(resistance_reductions) / len(resistance_reductions) if resistance_reductions else 0
    }


async def run_evaluation_tests(
    test_count: int = 1,
    verbose: bool = False
) -> Dict[str, Any]:
    """Run evaluation system tests using the 7 evaluators with LangSmith integration.
    
    Args:
        test_count: Number of test conversations to evaluate
        verbose: Whether to print detailed evaluation results
        
    Returns:
        Evaluation test results
    """
    
    print(f"🧪 Starting evaluation system tests with LangSmith...")
    
    # Disable MCP debug output
    import os
    os.environ['MCP_DEBUG'] = 'false'
    
    # Initialize LangSmith client
    from langsmith import Client
    from langsmith.evaluation import aevaluate
    
    client = Client()
    
    # Initialize test runner
    test_runner = ConversationTestRunner()
    
    # Create dataset with test conversations
    print(f"📊 Creating LangSmith dataset with {test_count} conversations...")
    dataset_name = f"coaching_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Coaching conversations for evaluation testing"
    )
    
    # Run test conversations and add to dataset
    test_results = await test_runner.run_batch_tests(test_count)
    successful_tests = [r for r in test_results if "error" not in r]
    
    if not successful_tests:
        print("❌ No successful test conversations to evaluate")
        return {"error": "No successful conversations"}
    
    # Create examples in dataset
    for result in successful_tests:
        example = client.create_example(
            dataset_id=dataset.id,
            inputs={"conversation_id": result["conversation_id"]},
            outputs={
                "conversation_messages": result["conversation_messages"],
                "deep_report": result["deep_report"]["deep_thoughts_content"],
                "test_user_stats": result["test_user_stats"]
            }
        )
    
    print(f"✅ Created dataset '{dataset_name}' with {len(successful_tests)} examples")
    
    # Initialize evaluators
    all_evaluators = get_all_evaluators()
    average_evaluator = AverageScoreEvaluator()
    
    print(f"📊 Running evaluation with {len(all_evaluators) + 1} evaluators...")
    
    # Create evaluator wrappers for LangSmith
    def create_langsmith_evaluator(evaluator):
        async def eval_func(run, example):
            # Create a run-like object with conversation data
            class ConversationRun:
                def __init__(self, conversation, deep_report):
                    self.id = run.id
                    self.inputs = {"messages": conversation}
                    self.outputs = {"response": deep_report}
                    self.run_type = "llm"
                    self.start_time = run.start_time
                    self.trace_id = run.trace_id
            
            conversation_messages = example.outputs.get("conversation_messages", [])
            deep_report = example.outputs.get("deep_report", "")
            conversation_run = ConversationRun(conversation_messages, deep_report)
            
            # Run evaluator
            result = await evaluator.aevaluate_run(conversation_run)
            
            return {
                "key": evaluator.key,
                "score": result.get("score", 0.0),
                "comment": result.get("reasoning", "")
            }
        
        eval_func.__name__ = f"eval_{evaluator.key}"
        return eval_func
    
    # Prepare all evaluators
    langsmith_evaluators = [create_langsmith_evaluator(e) for e in all_evaluators]
    langsmith_evaluators.append(create_langsmith_evaluator(average_evaluator))
    
    # Simple target function for evaluation
    async def coach_function(inputs):
        return {"conversation_id": inputs.get("conversation_id")}
    
    try:
        # Run LangSmith evaluation
        results = await aevaluate(
            coach_function,
            data=dataset_name,
            evaluators=langsmith_evaluators,
            experiment_prefix="coaching_eval",
            metadata={
                "evaluator_count": len(langsmith_evaluators),
                "test_type": "conversation_evaluation"
            },
            max_concurrency=2,
            client=client
        )
        
        print(f"\n✅ Evaluation complete!")
        
        # Get experiment info
        experiment_name = getattr(results, 'experiment_name', 'coaching_eval')
        project = os.getenv('LANGSMITH_PROJECT', 'diary-coach-debug')
        
        print(f"\n📊 View results in LangSmith:")
        print(f"   https://smith.langchain.com/o/anthropic/projects/p/{project}/datasets/{dataset.id}")
        print(f"   Experiment: {experiment_name}")
        
        # Extract aggregate metrics if available
        if hasattr(results, 'aggregate_metrics'):
            print(f"\n📈 Evaluation Summary:")
            for metric, value in results.aggregate_metrics.items():
                if isinstance(value, dict) and 'mean' in value:
                    print(f"   {metric}: {value['mean']:.2f}")
                else:
                    print(f"   {metric}: {value}")
        
        return {
            "dataset_name": dataset_name,
            "dataset_id": dataset.id,
            "experiment_name": experiment_name,
            "evaluator_count": len(langsmith_evaluators),
            "conversation_count": len(successful_tests),
            "langsmith_url": f"https://smith.langchain.com/o/anthropic/projects/p/{project}/datasets/{dataset.id}"
        }
        
    except Exception as e:
        print(f"\n❌ LangSmith evaluation failed: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return {"error": str(e)}


async def main():
    """Main entry point for conversation test suite."""
    
    parser = argparse.ArgumentParser(description="Run conversation test suite")
    parser.add_argument("--tests", type=int, default=3, help="Number of test conversations")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--eval-only", action="store_true", help="Only run evaluation tests")
    parser.add_argument("--eval-tests", type=int, default=1, help="Number of conversations for evaluation testing")
    
    args = parser.parse_args()
    
    try:
        if args.eval_only:
            # Run evaluation system tests only
            results = await run_evaluation_tests(args.eval_tests, args.verbose)
        else:
            # Run full conversation test suite
            results = await run_test_suite(
                test_count=args.tests,
                save_results=not args.no_save,
                verbose=args.verbose
            )
        
        print(f"\n✅ Test suite completed successfully")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
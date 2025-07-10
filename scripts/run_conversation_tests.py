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
    """Run evaluation system tests using the 7 evaluators.
    
    Args:
        test_count: Number of test conversations to evaluate
        verbose: Whether to print detailed evaluation results
        
    Returns:
        Evaluation test results
    """
    
    print(f"🧪 Starting evaluation system tests...")
    
    # Initialize test runner
    test_runner = ConversationTestRunner()
    
    # Run test conversations
    test_results = await test_runner.run_batch_tests(test_count)
    successful_tests = [r for r in test_results if "error" not in r]
    
    if not successful_tests:
        print("❌ No successful test conversations to evaluate")
        return {"error": "No successful conversations"}
    
    # Initialize evaluators
    all_evaluators = get_all_evaluators()
    average_evaluator = AverageScoreEvaluator()
    
    print(f"📊 Running evaluation on {len(successful_tests)} conversations...")
    print(f"Using {len(all_evaluators)} individual evaluators + average score")
    
    evaluation_results = []
    
    for i, test_result in enumerate(successful_tests):
        print(f"\n🔍 Evaluating conversation {i+1}...")
        
        # Create mock Run object for evaluation
        from langsmith.schemas import Run
        
        # Format conversation for evaluation
        conversation_messages = test_result.get('conversation_messages', [])
        deep_report = test_result.get('deep_report', {})
        
        mock_run = Run(
            id="mock-run",
            inputs={"messages": conversation_messages},
            outputs={"response": deep_report.get('deep_thoughts_content', '')},
            run_type="llm"
        )
        
        # Run all evaluators
        individual_scores = {}
        
        for evaluator in all_evaluators:
            try:
                result = await evaluator.aevaluate_run(mock_run)
                individual_scores[evaluator.key] = result.get('score', 0.0)
                
                if verbose:
                    print(f"  {evaluator.key}: {result.get('score', 0.0):.2f}")
                    
            except Exception as e:
                print(f"  ❌ {evaluator.key} failed: {str(e)}")
                individual_scores[evaluator.key] = 0.0
        
        # Calculate average score
        try:
            avg_result = await average_evaluator.aevaluate_run(mock_run)
            avg_score = avg_result.get('score', 0.0)
            
            if verbose:
                print(f"  AVERAGE: {avg_score:.2f}")
                
        except Exception as e:
            print(f"  ❌ Average evaluator failed: {str(e)}")
            avg_score = 0.0
        
        evaluation_results.append({
            "conversation_id": test_result.get('conversation_id'),
            "individual_scores": individual_scores,
            "average_score": avg_score,
            "turn_count": test_result.get('turn_count', 0)
        })
    
    # Calculate summary statistics
    all_averages = [r['average_score'] for r in evaluation_results]
    overall_avg = sum(all_averages) / len(all_averages) if all_averages else 0
    
    print(f"\n📈 Evaluation Summary")
    print(f"Overall Average Score: {overall_avg:.2f}")
    print(f"Score Range: {min(all_averages):.2f} - {max(all_averages):.2f}")
    
    return {
        "evaluation_results": evaluation_results,
        "overall_average": overall_avg,
        "score_range": [min(all_averages), max(all_averages)] if all_averages else [0, 0],
        "evaluator_count": len(all_evaluators),
        "conversation_count": len(evaluation_results)
    }


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
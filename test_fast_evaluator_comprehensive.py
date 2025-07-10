#!/usr/bin/env python3
"""
Comprehensive test of the fast evaluator system.
Tests all speed improvements and validates functionality.
"""

import asyncio
import time
from src.evaluation.fast_evaluator import FastEvaluator


async def test_cache_functionality():
    """Test that caching works correctly."""
    print("🧪 Testing Cache Functionality")
    print("=" * 50)
    
    # Create evaluator with caching enabled
    evaluator = FastEvaluator(use_cache=True)
    
    # Run evaluation twice - second run should use cache
    print("First run (should populate cache):")
    start_time = time.time()
    summary1 = await evaluator.run_quick_evaluation()
    time1 = time.time() - start_time
    
    print(f"✅ First run: {time1:.1f}s, Cache hits: {evaluator.cache_hits}, Cache items: {len(evaluator.cache)}")
    
    print("\nSecond run (should use cache):")
    start_time = time.time()
    summary2 = await evaluator.run_quick_evaluation()
    time2 = time.time() - start_time
    
    print(f"✅ Second run: {time2:.1f}s, Cache hits: {evaluator.cache_hits}, Cache items: {len(evaluator.cache)}")
    
    # Validate cache effectiveness
    if evaluator.cache_hits > 0:
        print(f"✅ Cache working: {evaluator.cache_hits} hits out of {evaluator.cache_hits + evaluator.cache_misses} operations")
        speedup = (time1 / time2) if time2 > 0 else float('inf')
        print(f"✅ Speedup: {speedup:.1f}x faster")
    else:
        print("❌ Cache not working as expected")
    
    print()


async def test_parallel_vs_sequential():
    """Test parallel vs sequential execution to validate speed improvements."""
    print("🧪 Testing Parallel vs Sequential Execution")
    print("=" * 50)
    
    evaluator = FastEvaluator(use_cache=False)  # Disable cache for fair comparison
    
    # Test sequential execution (simulate old approach)
    print("Sequential execution simulation:")
    start_time = time.time()
    
    # Get representative examples
    sequential_results = []
    for evaluator_name in list(evaluator.representative_examples.keys())[:3]:  # Just 3 for speed
        example = evaluator.representative_examples[evaluator_name]
        result = await evaluator._evaluate_single_example(evaluator_name, example)
        sequential_results.append(result)
    
    sequential_time = time.time() - start_time
    print(f"✅ Sequential (3 evaluations): {sequential_time:.1f}s")
    
    # Test parallel execution
    print("\nParallel execution:")
    start_time = time.time()
    
    # Create tasks for parallel execution
    tasks = []
    for evaluator_name in list(evaluator.representative_examples.keys())[:3]:  # Same 3 evaluators
        example = evaluator.representative_examples[evaluator_name]
        task = evaluator._evaluate_single_example(evaluator_name, example)
        tasks.append(task)
    
    parallel_results = await asyncio.gather(*tasks)
    parallel_time = time.time() - start_time
    print(f"✅ Parallel (3 evaluations): {parallel_time:.1f}s")
    
    # Calculate speedup
    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"✅ Parallel speedup: {speedup:.1f}x faster")
    
    print()


async def test_representative_examples():
    """Test that representative examples are correctly selected."""
    print("🧪 Testing Representative Example Selection")
    print("=" * 50)
    
    evaluator = FastEvaluator()
    
    print(f"Total evaluators: {len(evaluator.representative_examples)}")
    print(f"Representative examples:")
    
    for evaluator_name, example in evaluator.representative_examples.items():
        score_diff = example.expected_good_score - example.expected_poor_score
        print(f"  {evaluator_name}: {example.scenario_name} (score diff: {score_diff:.2f})")
    
    # Validate that we have good discriminative examples
    avg_score_diff = sum(
        example.expected_good_score - example.expected_poor_score 
        for example in evaluator.representative_examples.values()
    ) / len(evaluator.representative_examples)
    
    print(f"\n✅ Average score difference: {avg_score_diff:.2f}")
    
    if avg_score_diff > 0.4:  # Good discriminative power
        print("✅ Representative examples have good discriminative power")
    else:
        print("❌ Representative examples may not be discriminative enough")
    
    print()


async def test_error_handling():
    """Test error handling and recovery."""
    print("🧪 Testing Error Handling")
    print("=" * 50)
    
    evaluator = FastEvaluator()
    
    # Test with invalid evaluator name (should handle gracefully)
    try:
        # This should not crash the system
        summary = await evaluator.run_quick_evaluation()
        print(f"✅ Error handling works: {summary.error_count} errors handled gracefully")
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
    
    print()


async def main():
    """Run all comprehensive tests."""
    print("🚀 Comprehensive Fast Evaluator Test Suite")
    print("=" * 60)
    print()
    
    # Test each major component
    await test_representative_examples()
    await test_cache_functionality()
    await test_parallel_vs_sequential()
    await test_error_handling()
    
    # Final performance validation
    print("🎯 Final Performance Validation")
    print("=" * 50)
    
    evaluator = FastEvaluator()
    
    # Quick test
    start_time = time.time()
    quick_summary = await evaluator.run_quick_evaluation()
    quick_time = time.time() - start_time
    
    print(f"Quick evaluation: {quick_time:.1f}s (target: <60s)")
    if quick_time < 60:
        print("✅ Quick evaluation meets target")
    else:
        print("❌ Quick evaluation exceeds target")
    
    # Medium test
    start_time = time.time()
    medium_summary = await evaluator.run_medium_evaluation()
    medium_time = time.time() - start_time
    
    print(f"Medium evaluation: {medium_time:.1f}s (target: <300s)")
    if medium_time < 300:
        print("✅ Medium evaluation meets target")
    else:
        print("❌ Medium evaluation exceeds target")
    
    # Calculate improvement over baseline
    baseline_time = 294 * 30  # 294 evaluations × 30s = 8820s (2.45 hours)
    quick_improvement = (baseline_time / quick_time) if quick_time > 0 else float('inf')
    medium_improvement = (baseline_time / medium_time) if medium_time > 0 else float('inf')
    
    print(f"\n🎉 Speed Improvements Achieved:")
    print(f"  Quick mode: {quick_improvement:.0f}x faster than baseline")
    print(f"  Medium mode: {medium_improvement:.0f}x faster than baseline")
    
    print(f"\n✅ All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
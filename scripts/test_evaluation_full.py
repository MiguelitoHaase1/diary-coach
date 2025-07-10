#!/usr/bin/env python3
"""
Full evaluation testing script.

Target: 2+ hours total runtime
Uses: All examples (42 total) with parallel execution
Purpose: CI/production regression testing and comprehensive validation
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.fast_evaluator import FastEvaluator


async def main():
    """Run full evaluation test."""
    print("🚀 Full Evaluation Test")
    print("=" * 50)
    print("Target: 2+ hours")
    print("Scope: All examples (42 total)")
    print("Purpose: CI/production regression testing")
    print()
    
    evaluator = FastEvaluator()
    
    print("Starting full evaluation...")
    print("⚠️  This will take 2+ hours. Consider using quick or medium mode for development.")
    print()
    
    summary = await evaluator.run_full_evaluation()
    
    evaluator.print_summary(summary)
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    expected_time = 294 * 30  # 294 evaluations × 30s each = 147 minutes
    if summary.total_time < expected_time:
        improvement = ((expected_time - summary.total_time) / expected_time) * 100
        print(f"✅ IMPROVEMENT: {improvement:.1f}% faster than baseline")
    else:
        print(f"❌ SLOW: {summary.total_time:.1f}s vs {expected_time:.1f}s expected")
    
    if summary.error_count == 0:
        print("✅ NO ERRORS")
    else:
        print(f"❌ {summary.error_count} errors detected")
    
    # Comprehensive statistical analysis
    print(f"\n📊 Comprehensive Analysis:")
    scores = list(summary.evaluator_scores.values())
    if scores:
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        print(f"  Average Score: {avg_score:.3f}")
        print(f"  Score Range: {min_score:.3f} - {max_score:.3f}")
        print(f"  Standard Deviation: {std_dev:.3f}")
        print(f"  Score Spread: {max_score - min_score:.3f}")
    
    # Evaluator performance breakdown
    print(f"\n🔍 Evaluator Performance:")
    for evaluator, score in sorted(summary.evaluator_scores.items(), key=lambda x: x[1], reverse=True):
        evaluator_results = [r for r in summary.results if r.evaluator_name == evaluator]
        avg_time = sum(r.evaluation_time for r in evaluator_results) / len(evaluator_results) if evaluator_results else 0
        print(f"  {evaluator}: {score:.3f} (avg {avg_time:.1f}s)")
    
    # Save results to file
    results_file = Path(__file__).parent.parent / "full_evaluation_results.json"
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "total_evaluations": summary.total_evaluations,
        "total_time": summary.total_time,
        "avg_time_per_evaluation": summary.avg_time_per_evaluation,
        "evaluator_scores": summary.evaluator_scores,
        "error_count": summary.error_count,
        "results": [
            {
                "evaluator_name": r.evaluator_name,
                "scenario_name": r.scenario_name,
                "score": r.score,
                "evaluation_time": r.evaluation_time,
                "error": r.error
            }
            for r in summary.results
        ]
    }
    
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())
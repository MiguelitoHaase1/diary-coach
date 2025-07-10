#!/usr/bin/env python3
"""
Medium evaluation testing script.

Target: <5 minutes total runtime
Uses: 3 examples per evaluator (21 total) with parallel execution
Purpose: Pre-commit validation and regression testing
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.fast_evaluator import FastEvaluator


async def main():
    """Run medium evaluation test."""
    print("🚀 Medium Evaluation Test")
    print("=" * 50)
    print("Target: <5 minutes")
    print("Scope: 3 examples per evaluator (21 total)")
    print("Purpose: Pre-commit validation and regression testing")
    print()
    
    evaluator = FastEvaluator()
    
    print("Starting medium evaluation...")
    summary = await evaluator.run_medium_evaluation()
    
    evaluator.print_summary(summary)
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    if summary.total_time < 300:  # 5 minutes
        print(f"✅ SUCCESS: {summary.total_time:.1f}s < 300s target")
    else:
        print(f"❌ SLOW: {summary.total_time:.1f}s > 300s target")
    
    if summary.error_count == 0:
        print("✅ NO ERRORS")
    else:
        print(f"❌ {summary.error_count} errors detected")
    
    # Statistical analysis
    print(f"\n📊 Statistical Analysis:")
    scores = list(summary.evaluator_scores.values())
    if scores:
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        print(f"  Average Score: {avg_score:.3f}")
        print(f"  Score Range: {min_score:.3f} - {max_score:.3f}")
        print(f"  Score Spread: {max_score - min_score:.3f}")
    
    # Speed recommendations
    if summary.avg_time_per_evaluation > 15:
        print(f"\n💡 Speed Recommendations:")
        print(f"  - Average {summary.avg_time_per_evaluation:.1f}s per evaluation is slow")
        print(f"  - Consider parallel batching optimization")
        print(f"  - Consider prompt simplification")
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Quick evaluation testing script.

Target: <60 seconds total runtime
Uses: 1 example per evaluator (7 total) with parallel execution
Purpose: Development iteration and smoke testing
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.fast_evaluator import FastEvaluator


async def main():
    """Run quick evaluation test."""
    print("🚀 Quick Evaluation Test")
    print("=" * 50)
    print("Target: <60 seconds")
    print("Scope: 1 example per evaluator (7 total)")
    print("Purpose: Development iteration and smoke testing")
    print()
    
    evaluator = FastEvaluator()
    
    print("Starting quick evaluation...")
    summary = await evaluator.run_quick_evaluation()
    
    evaluator.print_summary(summary)
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    if summary.total_time < 60:
        print(f"✅ SUCCESS: {summary.total_time:.1f}s < 60s target")
    else:
        print(f"❌ SLOW: {summary.total_time:.1f}s > 60s target")
    
    if summary.error_count == 0:
        print("✅ NO ERRORS")
    else:
        print(f"❌ {summary.error_count} errors detected")
    
    # Speed recommendations
    if summary.avg_time_per_evaluation > 8:
        print(f"\n💡 Speed Recommendations:")
        print(f"  - Average {summary.avg_time_per_evaluation:.1f}s per evaluation is slow")
        print(f"  - Consider using faster model (current: GPT-4o-mini)")
        print(f"  - Consider reducing prompt complexity")
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())
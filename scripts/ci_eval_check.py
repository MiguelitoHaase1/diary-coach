#!/usr/bin/env python3
"""
CI evaluation check for regression detection.

This script runs coaching evaluation and compares against baseline scores
to detect quality regressions.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from statistics import mean

# Add project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from langsmith import Client
from langsmith.evaluation import aevaluate

from src.evaluation.langsmith_evaluators import get_all_evaluators
from src.orchestration.context_graph import create_context_aware_graph
from src.orchestration.context_state import ContextState


# Regression threshold (5% drop triggers failure)
REGRESSION_THRESHOLD = 0.05


async def coach_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Function wrapper for our coach to work with LangSmith evaluation."""
    try:
        # Initialize coach graph
        compiled_graph = create_context_aware_graph()
        
        # Create initial state
        messages = inputs.get("messages", [])
        initial_state = ContextState(
            messages=messages,
            conversation_id="eval_session",
            context_enabled=True
        )
        
        # Run coach
        result = await compiled_graph.ainvoke(initial_state)
        
        return {
            "response": result.coach_response or "No response generated"
        }
        
    except Exception as e:
        return {
            "response": f"Error: {str(e)}"
        }


def load_baseline_scores() -> Dict[str, float]:
    """Load baseline scores from file."""
    baseline_file = "baseline_scores.json"
    
    if not os.path.exists(baseline_file):
        print(f"❌ Baseline scores file not found: {baseline_file}")
        print("   Run scripts/run_baseline_eval.py first to establish baseline")
        sys.exit(1)
    
    with open(baseline_file, "r") as f:
        baseline_scores = json.load(f)
    
    print(f"📊 Loaded baseline scores from: {baseline_file}")
    return baseline_scores


async def run_current_evaluation(dataset_name: str = "coach-behavioral-regression") -> Dict[str, float]:
    """Run evaluation against current coach."""
    
    print("🔄 Running current evaluation...")
    
    # Initialize evaluators
    evaluators = get_all_evaluators()
    
    # Initialize LangSmith client
    client = Client()
    
    # Verify dataset exists
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"📋 Using dataset: {dataset.name}")
    except Exception as e:
        print(f"❌ Dataset not found: {dataset_name}")
        sys.exit(1)
    
    # Run evaluation
    results = await aevaluate(
        coach_function,
        data=dataset_name,
        evaluators=evaluators,
        experiment_prefix="ci_check"
    )
    
    # Process results
    current_scores = {}
    
    # Collect evaluator scores from AsyncExperimentResults
    evaluator_scores = {}
    
    async for result_row in results:
        for eval_result in result_row.eval_results:
            evaluator_name = eval_result.evaluator_name
            score = eval_result.score
            
            if evaluator_name not in evaluator_scores:
                evaluator_scores[evaluator_name] = []
            
            if score is not None:
                evaluator_scores[evaluator_name].append(score)
    
    # Calculate mean scores for each evaluator
    for evaluator_name, scores in evaluator_scores.items():
        if scores:
            current_scores[evaluator_name] = mean(scores)
    
    return current_scores


async def check_for_regression() -> Dict[str, Any]:
    """Check for coaching quality regression."""
    
    # Load baseline and run current evaluation
    baseline = load_baseline_scores()
    current = await run_current_evaluation()
    
    results = {}
    any_regression = False
    langsmith_url = f"https://smith.langchain.com/projects/{os.getenv('LANGSMITH_PROJECT', 'default')}"
    
    print("\n🔍 REGRESSION ANALYSIS")
    print("="*50)
    
    for metric in baseline.keys():
        if metric not in current:
            print(f"⚠️  Missing metric in current evaluation: {metric}")
            continue
        
        baseline_score = baseline[metric]
        current_score = current[metric]
        change = current_score - baseline_score
        change_percent = (change / baseline_score) * 100 if baseline_score > 0 else 0
        regression = (baseline_score - current_score) > REGRESSION_THRESHOLD
        
        # Format metric name for display
        display_name = metric.replace("Evaluator", "").replace("_", " ").title()
        
        # Status indicator
        if regression:
            status = "🔴 REGRESSION"
            any_regression = True
        elif change > 0:
            status = "🟢 IMPROVED"
        else:
            status = "🟡 STABLE"
        
        print(f"{status} {display_name}")
        print(f"   Baseline: {baseline_score:.3f}")
        print(f"   Current:  {current_score:.3f}")
        print(f"   Change:   {change:+.3f} ({change_percent:+.1f}%)")
        
        results[metric] = {
            "baseline": baseline_score,
            "current": current_score,
            "change": change,
            "change_percent": change_percent,
            "regression": regression
        }
    
    # Save results for PR comment
    results_output = {
        **results,
        "langsmith_url": langsmith_url,
        "any_regression": any_regression,
        "timestamp": datetime.now().isoformat(),
        "threshold": REGRESSION_THRESHOLD
    }
    
    with open("eval_results.json", "w") as f:
        json.dump(results_output, f, indent=2)
    
    print("="*50)
    
    # Summary
    if any_regression:
        print("❌ COACHING QUALITY REGRESSION DETECTED!")
        print(f"   One or more metrics dropped by more than {REGRESSION_THRESHOLD*100:.0f}%")
        print("   This PR should be reviewed carefully before merging.")
    else:
        print("✅ COACHING QUALITY MAINTAINED!")
        print("   No significant regressions detected.")
    
    print(f"📊 Full results saved to: eval_results.json")
    print(f"🔗 LangSmith dashboard: {langsmith_url}")
    
    return results_output


async def main():
    """Main entry point."""
    print("🔍 Starting CI evaluation check...")
    
    # Check API keys
    if not os.getenv("LANGSMITH_API_KEY"):
        print("❌ LANGSMITH_API_KEY environment variable not set")
        sys.exit(1)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        results = await check_for_regression()
        
        # Exit with error code if regression detected
        if results["any_regression"]:
            print("\n💥 Exiting with error code 1 due to regression")
            sys.exit(1)
        else:
            print("\n🎉 Evaluation passed! No regressions detected.")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ CI evaluation check failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
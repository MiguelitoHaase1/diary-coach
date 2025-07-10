#!/usr/bin/env python3
"""
Run baseline coaching evaluation to establish quality benchmarks.

This script runs our 7 coaching evaluators against the current coach
to establish baseline scores for regression testing.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from statistics import mean, stdev

# Add project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from langsmith import Client
from langsmith.evaluation import aevaluate

from src.evaluation.langsmith_evaluators import get_all_evaluators
from src.orchestration.context_graph import create_context_aware_graph
from src.orchestration.context_state import ContextState


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
        
        # Handle both dataclass and dict result formats
        if hasattr(result, 'coach_response'):
            # ContextState dataclass
            response = result.coach_response or "No response generated"
        elif isinstance(result, dict):
            # Dictionary format
            response = result.get('coach_response') or "No response generated"
        else:
            response = f"Unexpected result type: {type(result)}"
        
        return {
            "response": response
        }
        
    except Exception as e:
        return {
            "response": f"Error: {str(e)}"
        }


async def run_baseline_evaluation(dataset_name: str = "coach-behavioral-regression") -> Dict[str, Any]:
    """Generate baseline scores for all coaching dimensions."""
    
    print("🎯 Starting baseline coaching evaluation...")
    
    # Initialize evaluators
    evaluators = get_all_evaluators()
    print(f"📊 Initialized {len(evaluators)} evaluators")
    
    # Initialize LangSmith client
    client = Client()
    
    # Verify dataset exists
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"📋 Using dataset: {dataset.name} ({dataset.id})")
    except Exception as e:
        print(f"❌ Dataset not found: {dataset_name}")
        print(f"   Run scripts/upload_evaluation_dataset.py first")
        raise e
    
    # Run evaluation
    print("🔄 Running evaluation against current coach...")
    
    results = await aevaluate(
        coach_function,
        data=dataset_name,
        evaluators=evaluators,
        experiment_prefix="baseline"
    )
    
    # Process results
    baseline_scores = {}
    detailed_results = {}
    
    # Collect evaluator scores from AsyncExperimentResults
    evaluator_scores = {}
    evaluator_feedbacks = {}
    
    async for result_row in results:
        # Debug: print the structure to understand what we're working with
        # print(f"Debug: result_row type: {type(result_row)}")
        # print(f"Debug: result_row keys: {result_row.keys() if hasattr(result_row, 'keys') else 'No keys method'}")
        
        # Access the evaluation results correctly
        if isinstance(result_row, dict) and 'evaluation_results' in result_row:
            eval_results = result_row['evaluation_results']
            
            # The actual results are in eval_results['results']
            if isinstance(eval_results, dict) and 'results' in eval_results:
                for eval_result in eval_results['results']:
                    evaluator_name = eval_result.get('evaluator_name') or eval_result.get('key')
                    score = eval_result.get('score')
                    feedback = eval_result.get('feedback')
                    
                    if evaluator_name and evaluator_name not in evaluator_scores:
                        evaluator_scores[evaluator_name] = []
                        evaluator_feedbacks[evaluator_name] = []
                    
                    if evaluator_name and score is not None:
                        evaluator_scores[evaluator_name].append(score)
                    if evaluator_name and feedback:
                        evaluator_feedbacks[evaluator_name].append(feedback)
            else:
                print(f"Warning: evaluation_results does not contain 'results' key: {eval_results}")
        else:
            print(f"Warning: Could not find evaluation_results in result_row: {result_row}")
    
    print(f"Debug: Found {len(evaluator_scores)} evaluators with scores: {list(evaluator_scores.keys())}")
    
    # If no evaluator results, there might be an issue with the evaluators
    if not evaluator_scores:
        print("❌ No evaluator results found. This might indicate an issue with the evaluators themselves.")
        print("Check if the evaluators are properly initialized and working.")
        return {}, {}
    
    # Calculate statistics for each evaluator
    for evaluator_name, scores in evaluator_scores.items():
        if scores:
            mean_score = mean(scores)
            std_dev = stdev(scores) if len(scores) > 1 else 0.0
            feedbacks = evaluator_feedbacks.get(evaluator_name, [])
            
            baseline_scores[evaluator_name] = mean_score
            detailed_results[evaluator_name] = {
                "mean_score": mean_score,
                "std_dev": std_dev,
                "count": len(scores),
                "raw_scores": scores,
                "sample_feedback": feedbacks[:3] if feedbacks else []
            }
    
    return baseline_scores, detailed_results


def save_baseline_results(baseline_scores: Dict[str, float], detailed_results: Dict[str, Any]):
    """Save baseline results to file for CI comparison."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save baseline scores for CI
    baseline_file = "baseline_scores.json"
    with open(baseline_file, "w") as f:
        json.dump(baseline_scores, f, indent=2)
    print(f"💾 Saved baseline scores to: {baseline_file}")
    
    # Save detailed results for analysis
    detailed_file = f"docs/prototype/Evals/Baseline_Eval_{timestamp}.json"
    os.makedirs(os.path.dirname(detailed_file), exist_ok=True)
    
    detailed_output = {
        "timestamp": timestamp,
        "baseline_scores": baseline_scores,
        "detailed_results": detailed_results,
        "summary": {
            "total_evaluators": len(baseline_scores),
            "score_range": {
                "min": min(baseline_scores.values()) if baseline_scores else 0,
                "max": max(baseline_scores.values()) if baseline_scores else 0,
                "spread": max(baseline_scores.values()) - min(baseline_scores.values()) if baseline_scores else 0
            }
        }
    }
    
    with open(detailed_file, "w") as f:
        json.dump(detailed_output, f, indent=2)
    print(f"📊 Saved detailed results to: {detailed_file}")


def print_baseline_report(baseline_scores: Dict[str, float], detailed_results: Dict[str, Any]):
    """Print formatted baseline evaluation report."""
    
    print("\n" + "="*50)
    print("🎯 BASELINE COACHING QUALITY EVALUATION")
    print("="*50)
    
    if not baseline_scores:
        print("❌ No baseline scores generated")
        return
    
    # Sort by score for better readability
    sorted_scores = sorted(baseline_scores.items(), key=lambda x: x[1], reverse=True)
    
    for evaluator_name, score in sorted_scores:
        details = detailed_results.get(evaluator_name, {})
        std_dev = details.get("std_dev", 0.0)
        count = details.get("count", 0)
        
        # Format evaluator name
        display_name = evaluator_name.replace("Evaluator", "").replace("_", " ").title()
        
        print(f"\n📊 {display_name}")
        print(f"   Score: {score:.3f} (σ={std_dev:.3f}, n={count})")
        
        # Add interpretation
        if score >= 0.8:
            interpretation = "🟢 Excellent"
        elif score >= 0.6:
            interpretation = "🟡 Good"
        elif score >= 0.4:
            interpretation = "🟠 Needs Work"
        else:
            interpretation = "🔴 Poor"
        
        print(f"   Level: {interpretation}")
    
    # Summary statistics
    scores = list(baseline_scores.values())
    print(f"\n📈 SUMMARY STATISTICS")
    print(f"   Mean Score: {mean(scores):.3f}")
    print(f"   Score Range: {min(scores):.3f} - {max(scores):.3f}")
    print(f"   Score Spread: {max(scores) - min(scores):.3f}")
    print(f"   Standard Deviation: {stdev(scores):.3f}")
    
    # Quality assessment
    mean_score = mean(scores)
    spread = max(scores) - min(scores)
    
    print(f"\n🔍 QUALITY ASSESSMENT")
    if mean_score >= 0.7:
        print("   ✅ Overall coaching quality is strong")
    elif mean_score >= 0.5:
        print("   ⚠️  Overall coaching quality is moderate")
    else:
        print("   ❌ Overall coaching quality needs improvement")
    
    if spread >= 0.3:
        print("   📊 Good score variation across dimensions (meaningful signal)")
    else:
        print("   ⚠️  Low score variation (may indicate evaluation issues)")
    
    print("="*50)


async def main():
    """Main entry point."""
    print("🚀 Starting baseline evaluation...")
    
    # Check API keys
    if not os.getenv("LANGSMITH_API_KEY"):
        print("❌ LANGSMITH_API_KEY environment variable not set")
        return
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        return
    
    try:
        baseline_scores, detailed_results = await run_baseline_evaluation()
        
        # Save results
        save_baseline_results(baseline_scores, detailed_results)
        
        # Print report
        print_baseline_report(baseline_scores, detailed_results)
        
        print(f"\n🎉 Baseline evaluation complete!")
        print(f"💡 Use these scores to detect regressions in future evaluations")
        
    except Exception as e:
        print(f"❌ Baseline evaluation failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Test a single evaluation to understand where scores are stored.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langsmith import Client
from langsmith.evaluation import aevaluate

from src.evaluation.langsmith_evaluators import ProblemSignificanceEvaluator
from src.evaluation.fast_evaluator import coach_function


async def test_single_evaluation():
    """Run a single evaluation to see where scores end up."""
    
    print("🧪 Testing single evaluation to understand LangSmith score storage...")
    
    # Simple test data
    test_data = [{
        "inputs": {
            "messages": [{"role": "user", "content": "I'm overwhelmed with my workload"}]
        },
        "outputs": {
            "expected_response": "What's the most critical task you need to focus on?"
        }
    }]
    
    # Single evaluator
    evaluator = ProblemSignificanceEvaluator()
    
    print(f"Running evaluation with coach_function and {evaluator.__class__.__name__}...")
    
    # Run evaluation
    results = await aevaluate(
        coach_function,
        data=test_data,
        evaluators=[evaluator],
        experiment_prefix="single_test"
    )
    
    print("📊 Processing results...")
    result_count = 0
    
    async for result_row in results:
        result_count += 1
        print(f"\nResult {result_count}:")
        print(f"  Type: {type(result_row)}")
        print(f"  Keys: {list(result_row.keys()) if hasattr(result_row, 'keys') else 'No keys'}")
        
        # Look for evaluation results
        if 'evaluation_results' in result_row:
            eval_results = result_row['evaluation_results']
            print(f"  Evaluation Results: {eval_results}")
            
            if 'results' in eval_results:
                for eval_result in eval_results['results']:
                    print(f"    Evaluator: {eval_result.get('evaluator_name', 'unknown')}")
                    print(f"    Score: {eval_result.get('score', 'no score')}")
                    print(f"    Reasoning: {eval_result.get('reasoning', 'no reasoning')}")
        
        # Also check other fields
        if 'run' in result_row:
            run = result_row['run']
            print(f"  Run ID: {run.id if hasattr(run, 'id') else 'no id'}")
            print(f"  Run outputs: {run.outputs if hasattr(run, 'outputs') else 'no outputs'}")
        
        if result_count >= 3:  # Limit output
            break
    
    print(f"\nTotal results processed: {result_count}")
    
    # Also check the latest LangSmith project
    print("\n🔍 Checking LangSmith for the experiment...")
    client = Client()
    
    try:
        projects = list(client.list_projects(limit=5))
        latest_project = None
        
        for project in projects:
            if "single_test" in project.name:
                latest_project = project
                break
        
        if latest_project:
            print(f"Found project: {latest_project.name}")
            
            # Get runs from this project
            runs = list(client.list_runs(project_name=latest_project.name, limit=10))
            print(f"Runs in project: {len(runs)}")
            
            for run in runs:
                print(f"  Run: {run.name} ({run.run_type})")
                if hasattr(run, 'feedback_stats') and run.feedback_stats:
                    print(f"    Feedback: {run.feedback_stats}")
                else:
                    print(f"    No feedback stats")
                    
                if hasattr(run, 'outputs') and run.outputs:
                    outputs_str = str(run.outputs)
                    if len(outputs_str) > 200:
                        outputs_str = outputs_str[:200] + "..."
                    print(f"    Outputs: {outputs_str}")
        else:
            print("No single_test project found")
            
    except Exception as e:
        print(f"Error checking LangSmith: {e}")


if __name__ == "__main__":
    asyncio.run(test_single_evaluation())
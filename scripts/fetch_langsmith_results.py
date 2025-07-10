#!/usr/bin/env python3
"""
Fetch and display LangSmith evaluation results.

This script fetches the latest evaluation results from LangSmith
and displays them in a readable format.
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langsmith import Client


def fetch_latest_evaluation_results():
    """Fetch and display the latest evaluation results from LangSmith."""
    
    client = Client()
    
    print("🔍 Fetching latest evaluation experiments...")
    
    # Get recent experiments using the correct API
    try:
        experiments = list(client.list_sessions(limit=20))
        print(f"Found {len(experiments)} recent sessions")
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        # Try alternative approach - look for runs with experiment-like names
        try:
            runs = list(client.list_runs(limit=50))
            experiments = [run for run in runs if run.name and ("fast_" in run.name or "baseline" in run.name)]
            print(f"Found {len(experiments)} evaluation runs")
        except Exception as e2:
            print(f"Error fetching runs: {e2}")
            return
    
    # Look for fast evaluation experiments
    fast_experiments = [
        exp for exp in experiments 
        if hasattr(exp, 'name') and exp.name and ("fast_quick" in exp.name or "fast_medium" in exp.name or "fast_full" in exp.name or "baseline" in exp.name)
    ]
    
    if not fast_experiments:
        print("❌ No fast evaluation experiments found")
        print("Available experiments:")
        for exp in experiments[:5]:
            print(f"  - {exp.name} ({exp.id})")
        return
    
    print(f"\n📊 Found {len(fast_experiments)} fast evaluation experiments:")
    
    for i, experiment in enumerate(fast_experiments[:3]):  # Show latest 3
        print(f"\n{'='*60}")
        print(f"🧪 Experiment {i+1}: {experiment.name}")
        print(f"ID: {experiment.id}")
        print(f"Created: {experiment.start_time}")
        print(f"Status: {experiment.status}")
        
        # Get runs from this experiment
        runs = list(client.list_runs(
            project_name=experiment.session_id,
            limit=50
        ))
        
        print(f"Total runs: {len(runs)}")
        
        # Look for evaluation runs (runs with feedback/scores)
        evaluation_runs = []
        for run in runs:
            if run.feedback_stats or (hasattr(run, 'outputs') and run.outputs):
                evaluation_runs.append(run)
        
        print(f"Evaluation runs: {len(evaluation_runs)}")
        
        # Display evaluation scores
        if evaluation_runs:
            print(f"\n📈 Evaluation Scores:")
            
            # Group scores by evaluator
            evaluator_scores = {}
            
            for run in evaluation_runs:
                # Check feedback for scores
                if run.feedback_stats:
                    for feedback_key, stats in run.feedback_stats.items():
                        if 'avg' in stats:
                            evaluator_scores[feedback_key] = stats['avg']
                
                # Check outputs for scores (our format)
                if hasattr(run, 'outputs') and run.outputs and isinstance(run.outputs, dict):
                    if 'score' in run.outputs:
                        evaluator_name = run.name or 'unknown'
                        evaluator_scores[evaluator_name] = run.outputs['score']
            
            if evaluator_scores:
                for evaluator, score in sorted(evaluator_scores.items()):
                    print(f"  {evaluator}: {score:.3f}")
            else:
                print("  No scores found in standard format")
                
                # Debug: show what we do have
                print("\n🔍 Debug - Available data:")
                for run in evaluation_runs[:3]:  # Show first 3
                    print(f"  Run: {run.name}")
                    print(f"    Outputs: {run.outputs}")
                    print(f"    Feedback: {run.feedback_stats}")
                    print(f"    Status: {run.status}")
        
        print(f"\n🔗 View experiment: https://smith.langchain.com/o/{client._get_settings().tenant_id}/datasets/compare?selectedSessions={experiment.id}")


if __name__ == "__main__":
    fetch_latest_evaluation_results()
#!/usr/bin/env python3
"""
Upload quick evaluation dataset with representative examples to LangSmith.

This creates a small dataset with 1 example per evaluator for fast evaluation.
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langsmith import Client
from src.evaluation.dataset_generator import EvalDatasetGenerator
from src.evaluation.fast_evaluator import FastEvaluator


def upload_quick_dataset():
    """Upload quick evaluation dataset to LangSmith."""
    
    print("🚀 Creating quick evaluation dataset...")
    
    # Initialize components
    client = Client()
    fast_evaluator = FastEvaluator()
    
    # Get representative examples
    representative_examples = list(fast_evaluator.representative_examples.values())
    
    print(f"📊 Selected {len(representative_examples)} representative examples:")
    for example in representative_examples:
        print(f"  - {example.scenario_name} ({example.evaluation_dimension})")
    
    # Format examples for LangSmith
    dataset_examples = []
    for example in representative_examples:
        # Create both good and poor examples for comprehensive evaluation
        good_example = {
            "inputs": {
                "messages": [{"role": "user", "content": example.client_opening}]
            },
            "outputs": {
                "response": example.good_coach_response
            },
            "metadata": {
                "scenario": example.scenario_name,
                "context": example.context,
                "evaluation_dimension": example.evaluation_dimension,
                "response_type": "good",
                "expected_score": example.expected_good_score
            }
        }
        dataset_examples.append(good_example)
        
        poor_example = {
            "inputs": {
                "messages": [{"role": "user", "content": example.client_opening}]
            },
            "outputs": {
                "response": example.poor_coach_response
            },
            "metadata": {
                "scenario": example.scenario_name,
                "context": example.context,
                "evaluation_dimension": example.evaluation_dimension,
                "response_type": "poor",
                "expected_score": example.expected_poor_score
            }
        }
        dataset_examples.append(poor_example)
    
    # Create dataset
    dataset_name = "coach-quick-evaluation"
    
    try:
        # Try to delete existing dataset first
        existing_dataset = client.read_dataset(dataset_name=dataset_name)
        client.delete_dataset(dataset_id=existing_dataset.id)
        print(f"🗑️  Deleted existing dataset: {dataset_name}")
    except:
        print(f"📝 Creating new dataset: {dataset_name}")
    
    # Create new dataset
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Quick evaluation dataset with representative examples for fast testing"
    )
    
    # Upload examples
    client.create_examples(
        inputs=[ex["inputs"] for ex in dataset_examples],
        outputs=[ex["outputs"] for ex in dataset_examples],
        metadata=[ex["metadata"] for ex in dataset_examples],
        dataset_id=dataset.id
    )
    
    print(f"✅ Uploaded {len(dataset_examples)} examples to dataset: {dataset_name}")
    print(f"🔗 Dataset URL: https://smith.langchain.com/datasets/{dataset.id}")
    
    print(f"\n📊 Dataset Summary:")
    print(f"  Total Examples: {len(dataset_examples)}")
    print(f"  Representative Scenarios: {len(representative_examples)}")
    print(f"  Examples per Scenario: 2 (good + poor response)")
    print(f"  Evaluators Covered: {len(fast_evaluator.representative_examples)}")
    
    return dataset_name


if __name__ == "__main__":
    dataset_name = upload_quick_dataset()
    print(f"\n🎉 Quick dataset ready! Use dataset name: '{dataset_name}'")
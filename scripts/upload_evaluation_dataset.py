#!/usr/bin/env python3
"""
Upload coaching evaluation dataset to LangSmith.

This script generates and uploads our targeted conversation examples
for coaching behavioral evaluation to LangSmith.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from langsmith import Client
from src.evaluation.dataset_generator import EvalDatasetGenerator, get_dataset_summary


async def upload_dataset():
    """Upload evaluation dataset to LangSmith."""
    
    # Initialize LangSmith client
    client = Client()
    
    # Generate dataset
    print("🔄 Generating coaching evaluation dataset...")
    generator = EvalDatasetGenerator()
    examples = generator.generate_all_examples()
    langsmith_examples = generator.format_for_langsmith(examples)
    
    # Get summary
    summary = get_dataset_summary(examples)
    print(f"📊 Generated {summary['total_examples']} conversation scenarios")
    print(f"📊 Creating {summary['total_langsmith_entries']} LangSmith entries")
    print(f"📊 Coverage: {summary['coverage']}")
    
    # Create dataset
    dataset_name = "coach-behavioral-regression"
    dataset_description = f"""
Targeted conversations for 7 coaching behavioral dimensions.

This dataset contains {summary['total_examples']} coaching scenarios designed to test specific 
evaluation criteria across all 7 behavioral dimensions. Each scenario includes both 
good and poor coaching responses for comparative evaluation.

Dimensions covered:
- Problem Significance Assessment: {summary['coverage']['problem_significance']} scenarios
- Task Concretization: {summary['coverage']['task_concretization']} scenarios  
- Solution Diversity: {summary['coverage']['solution_diversity']} scenarios
- Crux Identification: {summary['coverage']['crux_identification']} scenarios
- Crux Solution Exploration: {summary['coverage']['crux_solution']} scenarios
- Belief System Integration: {summary['coverage']['belief_system']} scenarios
- Non-Directive Coaching Style: {summary['coverage']['non_directive_style']} scenarios

Total LangSmith entries: {summary['total_langsmith_entries']} (good + poor responses)
Generated for Session 6.5: LangSmith Eval Jobs
""".strip()
    
    print(f"🔄 Creating LangSmith dataset: {dataset_name}")
    
    try:
        # Try to get existing dataset first
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"📋 Found existing dataset: {dataset.id}")
        
        # Delete existing examples to refresh
        print("🗑️  Clearing existing examples...")
        existing_examples = list(client.list_examples(dataset_id=dataset.id))
        for example in existing_examples:
            client.delete_example(example.id)
        print(f"🗑️  Deleted {len(existing_examples)} existing examples")
        
    except Exception:
        # Create new dataset if it doesn't exist
        print(f"📋 Creating new dataset: {dataset_name}")
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description=dataset_description
        )
        print(f"📋 Created dataset: {dataset.id}")
    
    # Upload examples
    print(f"⬆️  Uploading {len(langsmith_examples)} examples...")
    
    created_count = 0
    for i, example in enumerate(langsmith_examples):
        try:
            client.create_example(
                dataset_id=dataset.id,
                inputs=example["inputs"],
                outputs=example["outputs"],
                metadata=example["metadata"]
            )
            created_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"⬆️  Uploaded {i + 1}/{len(langsmith_examples)} examples")
                
        except Exception as e:
            print(f"❌ Failed to upload example {i + 1}: {str(e)}")
    
    print(f"✅ Successfully uploaded {created_count}/{len(langsmith_examples)} examples")
    print(f"🎯 Dataset ready for evaluation: {dataset_name}")
    print(f"🔗 LangSmith project: {os.getenv('LANGSMITH_PROJECT', 'default')}")
    
    return dataset.id


def main():
    """Main entry point."""
    print("🚀 Starting dataset upload to LangSmith...")
    
    # Check API key
    if not os.getenv("LANGSMITH_API_KEY"):
        print("❌ LANGSMITH_API_KEY environment variable not set")
        return
    
    try:
        dataset_id = asyncio.run(upload_dataset())
        print(f"\n🎉 Dataset upload complete! Dataset ID: {dataset_id}")
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
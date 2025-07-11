"""
Quick evaluation demo that shows the working LangSmith integration.
This bypasses the full conversation generation to focus on evaluation.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Disable MCP debug
os.environ['MCP_DEBUG'] = 'false'

from langsmith import Client
from langsmith.evaluation import evaluate
from src.evaluation.langsmith_evaluators import get_all_evaluators
from src.evaluation.average_score_evaluator import AverageScoreEvaluator


def create_demo_dataset(client: Client) -> str:
    """Create a demo dataset with a pre-generated conversation."""
    
    dataset_name = f"demo_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Demo coaching conversation for evaluation"
    )
    
    # Sample conversation that demonstrates coaching effectiveness
    conversation = [
        {"role": "user", "content": "I'm feeling overwhelmed with my roadmap priorities. Everything seems urgent but I can't get alignment from stakeholders."},
        {"role": "assistant", "content": "What's really driving your sense of being overwhelmed? Is it the number of choices or something deeper about how you're approaching the decision?"},
        {"role": "user", "content": "I think it's that I'm trying to make everyone happy. Sales wants features, engineering wants tech debt, CEO wants growth metrics."},
        {"role": "assistant", "content": "When you say 'trying to make everyone happy,' what are you optimizing for in those conversations?"},
        {"role": "user", "content": "I guess I'm optimizing for avoiding conflict rather than driving outcomes. That's probably not the right approach."},
        {"role": "assistant", "content": "What would it look like if you optimized for outcomes instead?"},
        {"role": "user", "content": "I'd probably need to get clear on what creates the most value for customers and the business, then have tough conversations about trade-offs."},
        {"role": "assistant", "content": "That shift from conflict avoidance to value creation - what's one specific conversation where you could try that approach?"},
        {"role": "user", "content": "The quarterly planning meeting next week. I could present the top 3 customer impact opportunities and facilitate a discussion about which one we commit to."},
        {"role": "assistant", "content": "What would success look like in that meeting?"},
        {"role": "user", "content": "Everyone leaves aligned on one clear priority, and I feel confident we're working on what matters most. Thanks, that really helped clarify things."}
    ]
    
    deep_report = """
    ## Breakthrough Analysis
    The client demonstrated significant insight progression from conflict avoidance to value-driven leadership. 
    Key transformation: shifted from people-pleasing to outcome optimization.
    
    ## Core Crux Identified
    Root issue was optimizing for conflict avoidance rather than business outcomes. 
    Coach effectively guided discovery of this pattern through targeted questioning.
    
    ## Action Concretization
    Conversation culminated in specific next step: quarterly planning meeting with top 3 customer impact 
    opportunities and facilitated priority discussion.
    """
    
    # Create example
    example = client.create_example(
        dataset_id=dataset.id,
        inputs={"conversation_id": "demo_001"},
        outputs={
            "conversation_messages": conversation,
            "deep_report": deep_report,
            "test_user_stats": {
                "breakthrough_achieved": True,
                "resistance_level": 0.2,
                "interaction_count": 6
            }
        }
    )
    
    print(f"✅ Created dataset '{dataset_name}' with demo conversation")
    return dataset_name


def target_function(inputs):
    """Simple target function for evaluation."""
    return {"conversation_id": inputs.get("conversation_id")}


def create_evaluator_wrapper(evaluator):
    """Create LangSmith-compatible evaluator wrapper."""
    
    def eval_func(run, example):
        # Create a run-like object with conversation data
        class ConversationRun:
            def __init__(self, conversation, deep_report):
                self.id = run.id
                self.inputs = {"messages": conversation}
                self.outputs = {"response": deep_report}
                self.run_type = "llm"
                self.start_time = run.start_time
                self.trace_id = run.trace_id
        
        conversation_messages = example.outputs.get("conversation_messages", [])
        deep_report = example.outputs.get("deep_report", "")
        conversation_run = ConversationRun(conversation_messages, deep_report)
        
        # Run evaluator synchronously (for demo simplicity)
        import asyncio
        result = asyncio.run(evaluator.aevaluate_run(conversation_run))
        
        return {
            "key": evaluator.key,
            "score": result.get("score", 0.0),
            "comment": result.get("reasoning", "")[:200]  # Truncate for readability
        }
    
    eval_func.__name__ = f"eval_{evaluator.key}"
    return eval_func


def main():
    """Run evaluation demo."""
    
    print("🎯 Running Full Conversation Evaluation Demo")
    print("=" * 60)
    
    client = Client()
    
    # Create demo dataset
    dataset_name = create_demo_dataset(client)
    
    # Get all evaluators
    all_evaluators = get_all_evaluators()
    average_evaluator = AverageScoreEvaluator()
    
    # Use ALL 7 evaluators + average (total 8)
    demo_evaluators = all_evaluators + [average_evaluator]
    
    print(f"\n📊 Running evaluation with {len(demo_evaluators)} evaluators (7 + average):")
    for e in demo_evaluators:
        print(f"   - {e.key}")
    
    # Create wrappers
    evaluator_wrappers = [create_evaluator_wrapper(e) for e in demo_evaluators]
    
    # Run evaluation
    print(f"\n🧪 Starting LangSmith evaluation...")
    
    try:
        results = evaluate(
            target_function,
            data=dataset_name,
            evaluators=evaluator_wrappers,
            experiment_prefix="demo",
            metadata={
                "demo_type": "full_conversation",
                "evaluator_count": len(demo_evaluators)
            },
            client=client
        )
        
        print(f"\n✅ Evaluation complete!")
        
        # Display results info
        project = os.getenv('LANGSMITH_PROJECT', 'diary-coach-debug')
        print(f"\n📊 View detailed results in LangSmith:")
        print(f"   https://smith.langchain.com/o/anthropic/projects/p/{project}/datasets")
        print(f"   Dataset: {dataset_name}")
        
        # Show experiment URL if available
        if hasattr(results, '_experiment_manager') and results._experiment_manager:
            experiment_name = results._experiment_manager.experiment_name
            print(f"   Experiment: {experiment_name}")
        
        print(f"\n🎉 Demo complete! Check LangSmith dashboard for full evaluation scores.")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
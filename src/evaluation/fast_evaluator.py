"""
Fast evaluation testing with radical speed improvements.

This module provides tiered testing approaches:
- Quick: 1 example per evaluator (7 total) with parallel execution
- Medium: 3 examples per evaluator (21 total) with parallel execution 
- Full: All examples (42 total) - for CI/production only

Target: Quick mode <60 seconds, Medium mode <5 minutes
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from langsmith import Client
from langsmith.evaluation import aevaluate

from src.evaluation.dataset_generator import EvalDatasetGenerator, ConversationExample
from src.evaluation.langsmith_evaluators import EVALUATOR_REGISTRY, BaseCoachingEvaluator
from src.orchestration.context_graph import create_context_aware_graph
from src.orchestration.context_state import ContextState


@dataclass
class EvaluationResult:
    """Result of a single evaluation."""
    evaluator_name: str
    scenario_name: str
    score: float
    reasoning: str
    feedback: Dict[str, Any]
    evaluation_time: float
    error: Optional[str] = None


@dataclass
class EvaluationSummary:
    """Summary of evaluation run."""
    total_evaluations: int
    total_time: float
    avg_time_per_evaluation: float
    results: List[EvaluationResult]
    evaluator_scores: Dict[str, float]
    error_count: int


async def coach_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Function wrapper for our coach to work with LangSmith evaluation."""
    try:
        # Initialize coach graph
        compiled_graph = create_context_aware_graph()
        
        # Create initial state
        messages = inputs.get("messages", [])
        initial_state = ContextState(
            messages=messages,
            conversation_id="fast_eval_session",
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


class FastEvaluator:
    """Fast evaluation testing with smart sampling and parallel execution."""
    
    def __init__(self, use_cache: bool = True, dataset_name: str = "coach-behavioral-regression"):
        self.dataset_generator = EvalDatasetGenerator()
        self.representative_examples = self._create_representative_mapping()
        self.use_cache = use_cache
        self.cache: Dict[str, EvaluationResult] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.dataset_name = dataset_name
        self.quick_dataset_name = "coach-quick-evaluation"
        self.client = Client()
    
    def _create_representative_mapping(self) -> Dict[str, ConversationExample]:
        """
        Create mapping of evaluator -> best representative example.
        
        Selects the most discriminative example for each evaluator that
        best tests its specific criteria with clear good/poor differences.
        """
        all_examples = self.dataset_generator.generate_all_examples()
        
        # Map evaluator names to their best representative examples
        # Choose examples with highest score differences for discrimination
        representative_map = {}
        
        # Group examples by evaluation dimension
        examples_by_dimension = {}
        for example in all_examples:
            dim = example.evaluation_dimension
            if dim not in examples_by_dimension:
                examples_by_dimension[dim] = []
            examples_by_dimension[dim].append(example)
        
        # Select best example per dimension (highest score difference)
        for evaluator_name, evaluator_class in EVALUATOR_REGISTRY.items():
            dimension = evaluator_name
            if dimension in examples_by_dimension:
                examples = examples_by_dimension[dimension]
                # Pick example with highest score difference (most discriminative)
                best_example = max(
                    examples, 
                    key=lambda e: e.expected_good_score - e.expected_poor_score
                )
                representative_map[evaluator_name] = best_example
        
        return representative_map
    
    def _create_cache_key(self, evaluator_name: str, example: ConversationExample, response_type: str = "good") -> str:
        """Create a unique cache key for evaluator + example + response combination."""
        # Create deterministic key from evaluator, scenario, and response
        response = example.good_coach_response if response_type == "good" else example.poor_coach_response
        key_data = {
            "evaluator": evaluator_name,
            "scenario": example.scenario_name,
            "client_opening": example.client_opening,
            "response": response,
            "response_type": response_type
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[EvaluationResult]:
        """Get cached evaluation result if available."""
        if not self.use_cache:
            return None
        
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        return None
    
    def _cache_result(self, cache_key: str, result: EvaluationResult):
        """Cache evaluation result."""
        if self.use_cache:
            self.cache[cache_key] = result
    
    async def run_quick_evaluation(self) -> EvaluationSummary:
        """
        Run quick evaluation with 1 example per evaluator using real LangSmith experiments.
        
        Target: <60 seconds total runtime
        """
        start_time = time.time()
        
        # Get all evaluators
        evaluators = [evaluator_class() for evaluator_class in EVALUATOR_REGISTRY.values()]
        
        # Run real LangSmith evaluation on quick dataset (14 examples)
        results = await aevaluate(
            coach_function,
            data=self.quick_dataset_name,
            evaluators=evaluators,
            experiment_prefix="fast_quick"
        )
        
        # Process results into our format
        evaluation_results = await self._process_langsmith_results(results)
        
        total_time = time.time() - start_time
        
        return self._create_summary(evaluation_results, total_time)
    
    async def run_medium_evaluation(self, examples_per_evaluator: int = 3) -> EvaluationSummary:
        """
        Run medium evaluation with 3 examples per evaluator using real LangSmith experiments.
        
        Target: <5 minutes total runtime
        """
        start_time = time.time()
        
        # Get all evaluators
        evaluators = [evaluator_class() for evaluator_class in EVALUATOR_REGISTRY.values()]
        
        # Run real LangSmith evaluation on full dataset
        results = await aevaluate(
            coach_function,
            data=self.dataset_name,
            evaluators=evaluators,
            experiment_prefix="fast_medium"
        )
        
        # Process results and filter to medium subset (3 per evaluator)
        all_results = await self._process_langsmith_results(results)
        
        # Filter to first examples_per_evaluator examples per dimension
        filtered_results = self._filter_results_by_count(all_results, examples_per_evaluator)
        
        total_time = time.time() - start_time
        
        return self._create_summary(filtered_results, total_time)
    
    async def run_full_evaluation(self) -> EvaluationSummary:
        """
        Run full evaluation with all examples using real LangSmith experiments.
        
        Expected runtime: Much faster with parallel execution - for CI/production
        """
        start_time = time.time()
        
        # Use the existing dataset directly
        evaluators = [evaluator_class() for evaluator_class in EVALUATOR_REGISTRY.values()]
        
        # Run real LangSmith evaluation using the existing dataset
        results = await aevaluate(
            coach_function,
            data=self.dataset_name,
            evaluators=evaluators,
            experiment_prefix="fast_full"
        )
        
        # Process results into our format
        evaluation_results = await self._process_langsmith_results(results)
        
        total_time = time.time() - start_time
        
        return self._create_summary(evaluation_results, total_time)
    
    def _filter_results_by_count(self, results: List[EvaluationResult], max_per_evaluator: int) -> List[EvaluationResult]:
        """Filter results to max_per_evaluator examples per evaluator."""
        # Group results by evaluator
        results_by_evaluator = {}
        for result in results:
            evaluator = result.evaluator_name
            if evaluator not in results_by_evaluator:
                results_by_evaluator[evaluator] = []
            results_by_evaluator[evaluator].append(result)
        
        # Take first max_per_evaluator results for each evaluator
        filtered_results = []
        for evaluator, evaluator_results in results_by_evaluator.items():
            filtered_results.extend(evaluator_results[:max_per_evaluator])
        
        return filtered_results
    
    async def _process_langsmith_results(self, results) -> List[EvaluationResult]:
        """Process LangSmith evaluation results into our EvaluationResult format."""
        evaluation_results = []
        
        async for result_row in results:
            try:
                # Extract evaluation results from LangSmith format
                if isinstance(result_row, dict) and 'evaluation_results' in result_row:
                    eval_results = result_row['evaluation_results']
                    
                    if isinstance(eval_results, dict) and 'results' in eval_results:
                        for eval_result in eval_results['results']:
                            evaluator_name = eval_result.get('evaluator_name') or eval_result.get('key', 'unknown')
                            score = eval_result.get('score', 0.0)
                            reasoning = eval_result.get('reasoning', '')
                            feedback = eval_result.get('feedback', {"strengths": [], "improvements": []})
                            
                            # Get scenario name from metadata if available
                            scenario_name = "unknown"
                            if 'inputs' in result_row and 'metadata' in result_row['inputs']:
                                scenario_name = result_row['inputs']['metadata'].get('scenario_name', 'unknown')
                            
                            evaluation_result = EvaluationResult(
                                evaluator_name=evaluator_name,
                                scenario_name=scenario_name,
                                score=score,
                                reasoning=reasoning,
                                feedback=feedback,
                                evaluation_time=0.0,  # LangSmith doesn't provide individual timing
                                error=None
                            )
                            evaluation_results.append(evaluation_result)
                            
            except Exception as e:
                # Add error result
                evaluation_results.append(EvaluationResult(
                    evaluator_name="unknown",
                    scenario_name="unknown",
                    score=0.0,
                    reasoning=f"Processing failed: {str(e)}",
                    feedback={"strengths": [], "improvements": []},
                    evaluation_time=0.0,
                    error=str(e)
                ))
        
        return evaluation_results
    
    def _create_summary(self, results: List[EvaluationResult], total_time: float) -> EvaluationSummary:
        """Create evaluation summary from results."""
        # Calculate average scores per evaluator
        evaluator_scores = {}
        evaluator_counts = {}
        
        for result in results:
            evaluator = result.evaluator_name
            if evaluator not in evaluator_scores:
                evaluator_scores[evaluator] = 0.0
                evaluator_counts[evaluator] = 0
            
            evaluator_scores[evaluator] += result.score
            evaluator_counts[evaluator] += 1
        
        # Calculate averages
        for evaluator in evaluator_scores:
            if evaluator_counts[evaluator] > 0:
                evaluator_scores[evaluator] /= evaluator_counts[evaluator]
        
        # Count errors
        error_count = sum(1 for r in results if r.error is not None)
        
        return EvaluationSummary(
            total_evaluations=len(results),
            total_time=total_time,
            avg_time_per_evaluation=total_time / len(results) if results else 0.0,
            results=results,
            evaluator_scores=evaluator_scores,
            error_count=error_count
        )
    
    def print_summary(self, summary: EvaluationSummary):
        """Print evaluation summary in readable format."""
        print(f"\n🎯 Fast Evaluation Summary")
        print(f"Total Evaluations: {summary.total_evaluations}")
        print(f"Total Time: {summary.total_time:.1f}s")
        print(f"Avg Time per Evaluation: {summary.avg_time_per_evaluation:.1f}s")
        print(f"Errors: {summary.error_count}")
        
        # Cache statistics
        if self.use_cache:
            total_cache_ops = self.cache_hits + self.cache_misses
            if total_cache_ops > 0:
                cache_hit_rate = (self.cache_hits / total_cache_ops) * 100
                print(f"\n⚡ Cache Performance:")
                print(f"  Cache Hits: {self.cache_hits}")
                print(f"  Cache Misses: {self.cache_misses}")
                print(f"  Hit Rate: {cache_hit_rate:.1f}%")
                print(f"  Total Cached Items: {len(self.cache)}")
        
        print(f"\n📊 Evaluator Scores:")
        for evaluator, score in sorted(summary.evaluator_scores.items()):
            print(f"  {evaluator}: {score:.3f}")
        
        if summary.error_count > 0:
            print(f"\n❌ Errors:")
            for result in summary.results:
                if result.error:
                    print(f"  {result.evaluator_name}: {result.error}")


# Convenience functions
async def quick_eval() -> EvaluationSummary:
    """Run quick evaluation (1 example per evaluator)."""
    evaluator = FastEvaluator()
    return await evaluator.run_quick_evaluation()


async def medium_eval() -> EvaluationSummary:
    """Run medium evaluation (3 examples per evaluator)."""
    evaluator = FastEvaluator()
    return await evaluator.run_medium_evaluation()


async def full_eval() -> EvaluationSummary:
    """Run full evaluation (all examples)."""
    evaluator = FastEvaluator()
    return await evaluator.run_full_evaluation()


# CLI interface
if __name__ == "__main__":
    import sys
    
    async def main():
        mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
        
        evaluator = FastEvaluator()
        
        if mode == "quick":
            print("🚀 Running Quick Evaluation (1 example per evaluator)...")
            summary = await evaluator.run_quick_evaluation()
        elif mode == "medium":
            print("🚀 Running Medium Evaluation (3 examples per evaluator)...")
            summary = await evaluator.run_medium_evaluation()
        elif mode == "full":
            print("🚀 Running Full Evaluation (all examples)...")
            summary = await evaluator.run_full_evaluation()
        else:
            print("Usage: python -m src.evaluation.fast_evaluator [quick|medium|full]")
            return
        
        evaluator.print_summary(summary)
    
    asyncio.run(main())
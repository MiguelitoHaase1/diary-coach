"""Average Score Evaluator for unified scoring across all coaching metrics."""

from typing import Dict, Any, Optional, List
import uuid
from langsmith.evaluation import RunEvaluator
from langsmith.schemas import Run, Example

from src.evaluation.langsmith_evaluators import get_all_evaluators, BaseCoachingEvaluator


class AverageScoreEvaluator(RunEvaluator):
    """Computes average score across all 7 coaching evaluators."""
    
    def __init__(self):
        self.key = "average_score"
        self.individual_evaluators = get_all_evaluators()
    
    def evaluate_run(
        self, 
        run: Run, 
        example: Optional[Example] = None
    ) -> Dict[str, Any]:
        """Evaluate using all individual evaluators and compute average (sync version)."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            return {
                "key": self.key,
                "score": 0.0,
                "reasoning": "Sync evaluation not supported - use aevaluate_run",
                "individual_scores": {}
            }
        except RuntimeError:
            return asyncio.run(self.aevaluate_run(run, example))
    
    async def aevaluate_run(
        self, 
        run: Run, 
        example: Optional[Example] = None,
        evaluator_run_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Evaluate using all individual evaluators and compute average (async version)."""
        
        individual_results = {}
        scores = []
        
        # Run all individual evaluators
        for evaluator in self.individual_evaluators:
            try:
                result = await evaluator.aevaluate_run(run, example, evaluator_run_id)
                score = result.get("score", 0.0)
                individual_results[evaluator.key] = {
                    "score": score,
                    "reasoning": result.get("reasoning", "")
                }
                scores.append(score)
                
            except Exception as e:
                individual_results[evaluator.key] = {
                    "score": 0.0,
                    "reasoning": f"Evaluation failed: {str(e)}"
                }
                scores.append(0.0)
        
        # Calculate statistics
        if scores:
            average_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            score_variance = sum((s - average_score) ** 2 for s in scores) / len(scores)
        else:
            average_score = 0.0
            min_score = 0.0
            max_score = 0.0
            score_variance = 0.0
        
        # Build summary reasoning
        high_performers = [k for k, v in individual_results.items() if v["score"] >= 0.8]
        low_performers = [k for k, v in individual_results.items() if v["score"] <= 0.4]
        
        reasoning = f"Average of {len(scores)} evaluators: {average_score:.2f}. "
        reasoning += f"Range: {min_score:.2f} - {max_score:.2f}. "
        reasoning += f"Variance: {score_variance:.3f}. "
        
        if high_performers:
            reasoning += f"Strong performance in: {', '.join(high_performers)}. "
        if low_performers:
            reasoning += f"Needs improvement in: {', '.join(low_performers)}."
        
        return {
            "key": self.key,
            "score": average_score,
            "reasoning": reasoning,
            "individual_scores": individual_results,
            "statistics": {
                "average": average_score,
                "min": min_score,
                "max": max_score,
                "variance": score_variance,
                "count": len(scores)
            }
        }
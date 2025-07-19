"""
LangSmith evaluator wrappers for the 5 coaching evaluation metrics.

This module transforms our evaluation templates into LangSmith RunEvaluator classes,
providing automated quality gates for coaching conversations.
"""

from typing import Dict, Any, Optional
import json
import uuid
from abc import ABC, abstractmethod

from langsmith.evaluation import RunEvaluator
from langsmith.schemas import Run, Example

from src.services.llm_factory import LLMFactory, LLMTier
from src.utils.json_parser import parse_llm_score


class BaseCoachingEvaluator(RunEvaluator, ABC):
    """Base class for all coaching evaluators."""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service or LLMFactory.create_service(LLMTier.STANDARD)
        # Set evaluator key for LangSmith
        self.key = self.__class__.__name__

    def evaluate_run(
        self,
        run: Run,
        example: Optional[Example] = None
    ) -> Dict[str, Any]:
        """Evaluate a coaching conversation run (sync version)."""
        # For sync evaluation, we'll run the async version in a new event loop
        import asyncio
        try:
            # Try to run in existing loop
            asyncio.get_running_loop()
            # We're in an async context, so we can't run sync
            # Return a placeholder and hope aevaluate_run gets called
            return {
                "key": self.key,
                "score": 0.0,
                "reasoning": "Sync evaluation not supported - use aevaluate_run"
            }
        except RuntimeError:
            # No running loop, we can create one
            return asyncio.run(self.aevaluate_run(run, example))

    async def aevaluate_run(
        self,
        run: Run,
        example: Optional[Example] = None,
        evaluator_run_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Evaluate a coaching conversation run (async version)."""
        # Extract conversation from run
        conversation = run.inputs.get("messages", [])
        coach_response = run.outputs.get("response", "")

        # Build evaluation prompt using our template
        eval_prompt = self._build_eval_prompt(conversation, coach_response)

        # Use standard LLM for evaluation - convert string to message format
        try:
            messages = [{"role": "user", "content": eval_prompt}]
            # Use higher token limit for JSON response
            result = await self.llm_service.generate_response(messages, max_tokens=1500)

            # Use centralized JSON parser
            parsed = parse_llm_score(result)
            score = parsed["score"]

            return {
                "key": self.key,
                "score": score,  # Already 0-1 for new binary scores
                "reasoning": parsed.get("reasoning", "No reasoning provided")
            }

        except Exception as e:
            return {
                "key": self.key,
                "score": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}"
            }

    @abstractmethod
    def _build_eval_prompt(
        self,
        conversation: list,
        coach_response: str
    ) -> str:
        """Build the evaluation prompt for this specific metric."""
        pass

    def _format_conversation_history(self, conversation: list) -> str:
        """Format conversation history for evaluation prompt."""
        formatted = []
        for msg in conversation:
            if isinstance(msg, dict):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if role == "user":
                    formatted.append(f"Client: {content}")
                elif role == "assistant":
                    formatted.append(f"Coach: {content}")
        return "\n".join(formatted)


class ProblemDefinitionEvaluator(BaseCoachingEvaluator):
    """Evaluates whether coach helps client define the biggest problem."""

    def _build_eval_prompt(
        self,
        conversation: list,
        coach_response: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)

        return f"""You are evaluating a coaching conversation based on this \
specific criterion:

**A - Define biggest problem to solve - and understand why this problem matters**

Analyze whether the coach helped the client:
1. Identify and clearly define their biggest/most important problem
2. Understand why this specific problem matters to them
3. Articulate the significance and impact of solving this problem

## Conversation Context
{conversation_history}

## Deep Report Context
{coach_response}

Return ONLY a JSON object with your evaluation:
{{
  "score": 0.5,
  "reasoning": "Your explanation here"
}}

Score as follows:
- 0.0: No attempt to define problem or understand significance
- 0.5: Partial success - either defined problem OR explored why it matters
- 1.0: Full success - both clearly defined biggest problem AND understood why it matters
"""


class CruxRecognitionEvaluator(BaseCoachingEvaluator):
    """Evaluates whether coach helps client recognize the key constraint."""

    def _build_eval_prompt(
        self,
        conversation: list,
        coach_response: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)

        return f"""You are evaluating a coaching conversation based on this \
specific criterion:

**B - Recognize the key constraint to address ('the crux')**

Analyze whether the coach helped the client:
1. Identify the key constraint, bottleneck, or leverage point in their situation
2. Recognize what is the critical factor that, if addressed, would unlock progress
3. Distinguish between surface symptoms and the underlying crux

## Conversation Context
{conversation_history}

## Deep Report Context
{coach_response}

Return ONLY a JSON object with your evaluation:
{{
  "score": 0.5,
  "reasoning": "Your explanation here"
}}

Score as follows:
- 0.0: No attempt to identify constraints or leverage points
- 0.5: Some discussion of constraints but crux not clearly identified
- 1.0: Clear identification of the key constraint/crux that unlocks progress"""


class TodayAccomplishmentEvaluator(BaseCoachingEvaluator):
    """Evaluates whether coach helps client define today's accomplishment."""

    def _build_eval_prompt(
        self,
        conversation: list,
        coach_response: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)

        return f"""You are evaluating a coaching conversation based on this \
specific criterion:

**C - Define exactly what to accomplish today to address the crux**

Analyze whether the coach helped the client:
1. Define specific, concrete actions to take today (not someday)
2. Ensure these actions directly address the identified crux/constraint
3. Make the actions clear enough that success/completion is measurable

## Conversation Context
{conversation_history}

## Deep Report Context
{coach_response}

Return ONLY a JSON object with your evaluation:
{{
  "score": 0.5,
  "reasoning": "Your explanation here"
}}

Score as follows:
- 0.0: No concrete actions defined for today
- 0.5: Actions defined but either vague, not for today, or don't address crux
- 1.0: Clear, specific actions for today that directly address the crux"""


class MultiplePathsEvaluator(BaseCoachingEvaluator):
    """Evaluates whether coach helps client define multiple viable paths."""

    def _build_eval_prompt(
        self,
        conversation: list,
        coach_response: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)

        return f"""You are evaluating a coaching conversation based on this \
specific criterion:

**D - Define multiple viable and different paths forward to address crux**

Analyze whether the coach helped the client:
1. Generate multiple (at least 2-3) different approaches to address the crux
2. Ensure the paths are genuinely different, not just variations of the same approach
3. Make each path viable and actionable, not just theoretical

Score on a scale from 0 to 1:
- 0: No viable paths or only one path identified
- 0.33: Two somewhat similar paths identified
- 0.67: Two genuinely different viable paths identified
- 1.0: Three or more genuinely different, viable paths identified

## Conversation Context
{conversation_history}

## Deep Report Context
{coach_response}

Return ONLY a JSON object with your evaluation:
{{
  "score": 0.5,
  "reasoning": "Your explanation here"
}}"""


class CoreBeliefsEvaluator(BaseCoachingEvaluator):
    """Evaluates whether coach helps client identify core beliefs/tenets."""

    def _build_eval_prompt(
        self,
        conversation: list,
        coach_response: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)

        return f"""You are evaluating a coaching conversation based on this \
specific criterion:

**E - Define which 'core beliefs'/'tenets' to focus on when working the problem**

Analyze whether the coach helped the client:
1. Identify underlying beliefs, values, or principles relevant to the problem
2. Articulate which beliefs/tenets will guide their approach
3. Connect these beliefs to their actions and decision-making

Score on a scale from 0 to 1:
- 0: No exploration of beliefs or values
- 0.33: Some surface-level discussion of beliefs but not connected to action
- 0.67: Clear identification of 1-2 relevant beliefs/tenets with some connection \
to approach
- 1.0: Deep exploration of core beliefs/tenets with clear connection to \
problem-solving approach

## Conversation Context
{conversation_history}

## Deep Report Context
{coach_response}

Return ONLY a JSON object with your evaluation:
{{
  "score": 0.5,
  "reasoning": "Your explanation here"
}}"""


# Evaluator registry for easy access
EVALUATOR_REGISTRY = {
    "problem_definition": ProblemDefinitionEvaluator,
    "crux_recognition": CruxRecognitionEvaluator,
    "today_accomplishment": TodayAccomplishmentEvaluator,
    "multiple_paths": MultiplePathsEvaluator,
    "core_beliefs": CoreBeliefsEvaluator,
}


def get_all_evaluators() -> list[BaseCoachingEvaluator]:
    """Get instances of all coaching evaluators."""
    return [evaluator_class() for evaluator_class in EVALUATOR_REGISTRY.values()]


def get_evaluator(name: str) -> BaseCoachingEvaluator:
    """Get a specific evaluator by name."""
    if name not in EVALUATOR_REGISTRY:
        raise ValueError(
            f"Unknown evaluator: {name}. Available: {list(EVALUATOR_REGISTRY.keys())}"
        )
    return EVALUATOR_REGISTRY[name]()

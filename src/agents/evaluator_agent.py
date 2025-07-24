"""Evaluator Agent for assessing coaching quality with 5 criteria."""

import logging
import json
import re
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.agents.base import BaseAgent, AgentRequest, AgentResponse, AgentCapability
from src.services.llm_service import AnthropicService
from src.config.models import ModelProvider, get_model_for_tier
from src.agents.prompts import PromptLoader

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    """Agent that evaluates coaching conversations using 5 key criteria."""

    # Define the 5 evaluation criteria
    CRITERIA = {
        "A": {
            "name": "Problem Definition",
            "description": "Define biggest problem and understand why it matters",
            "binary": True,
        },
        "B": {
            "name": "Crux Recognition",
            "description": "Recognize the key constraint to address ('the crux')",
            "binary": True,
        },
        "C": {
            "name": "Today Accomplishment",
            "description": "Define what to accomplish today to address crux",
            "binary": True,
        },
        "D": {
            "name": "Multiple Paths",
            "description": "Define multiple viable and different paths forward",
            "binary": False,  # Graduated score 0-1
        },
        "E": {
            "name": "Core Beliefs",
            "description": "Define which 'core beliefs'/'tenets' to focus on",
            "binary": False,  # Graduated score 0-1
        },
    }

    def __init__(self, llm_service: Optional[AnthropicService] = None):
        """Initialize Evaluator Agent.

        Args:
            llm_service: Anthropic service instance (will create if not provided)
        """
        if llm_service is None:
            # Use standard tier (Sonnet 4) for evaluations
            model_name = get_model_for_tier("standard", ModelProvider.ANTHROPIC)
            llm_service = AnthropicService(model=model_name)

        super().__init__(
            name="evaluator",
            capabilities=[
                AgentCapability.EVALUATION,
                AgentCapability.QUALITY_ASSESSMENT,
            ],
        )
        self.llm_service = llm_service

        # Load prompts
        self.prompt_loader = PromptLoader()

    @property
    def system_prompt(self) -> str:
        """Load system prompt from markdown file."""
        try:
            # Load Evaluator system prompt
            return self.prompt_loader.load_prompt("evaluator_agent_prompt")
        except Exception as e:
            logger.error(f"Error loading Evaluator prompt: {e}")
            # Fallback prompt
            return """You are a Coach Quality Evaluator.

Evaluate coaching effectiveness using 5 specific criteria:
- A: Problem Definition (binary 0 or 1)
- B: Crux Recognition (binary 0 or 1)
- C: Today Accomplishment (binary 0 or 1)
- D: Multiple Paths (graduated 0.0-1.0)
- E: Core Beliefs (graduated 0.0-1.0)

Be fair but rigorous in your assessment."""

    async def initialize(self) -> None:
        """Initialize the evaluator agent."""
        self.is_initialized = True
        logger.info("Evaluator agent initialized")

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Evaluate coaching conversation and Deep Thoughts report.

        Args:
            request: Request containing conversation and report

        Returns:
            Response with evaluation scores and reasoning
        """
        try:
            # Extract conversation and report from context
            conversation = request.context.get("conversation", [])
            deep_thoughts = request.context.get("deep_thoughts", "")

            # Evaluate each criterion
            evaluations = {}
            for criterion_id, criterion_info in self.CRITERIA.items():
                score, reasoning = await self._evaluate_criterion(
                    criterion_id, criterion_info, conversation, deep_thoughts
                )
                evaluations[criterion_id] = {
                    "name": criterion_info["name"],
                    "score": score,
                    "reasoning": reasoning,
                }

            # Calculate overall assessment
            overall_score = self._calculate_overall_score(evaluations)

            # Generate conversation summary
            summary_prompt = (
                f"Generate a conversation summary following the Conversation "
                f"Summary Guidelines from your system prompt.\n\n"
                f"Conversation:\n{self._format_conversation(conversation)}\n\n"
                f"Deep Thoughts Report:\n{deep_thoughts}"
            )

            conversation_summary = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": summary_prompt}],
                system_prompt=self.system_prompt,
                max_tokens=500,
                temperature=0.5
            )

            # Format evaluation report with transcript
            eval_report = self._format_evaluation_report(
                evaluations, overall_score, conversation, conversation_summary
            )

            # Send evaluation metrics to LangSmith
            await self._send_to_langsmith(
                evaluations, overall_score, request, conversation
            )

            return AgentResponse(
                agent_name=self.name,
                content=eval_report,
                metadata={"evaluations": evaluations, "overall_score": overall_score},
                request_id=request.request_id,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Evaluator agent error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                content=f"Error evaluating coaching session: {str(e)}",
                metadata={},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e),
            )

    async def _evaluate_criterion(
        self,
        criterion_id: str,
        criterion_info: Dict[str, Any],
        conversation: List[Dict[str, str]],
        deep_thoughts: str,
    ) -> tuple[float, str]:
        """Evaluate a single criterion.

        Args:
            criterion_id: ID of the criterion (A-E)
            criterion_info: Information about the criterion
            conversation: Conversation history
            deep_thoughts: Deep Thoughts report

        Returns:
            Tuple of (score, reasoning)
        """
        # Build evaluation prompt
        eval_prompt = self._build_criterion_prompt(
            criterion_id, criterion_info, conversation, deep_thoughts
        )

        # Get evaluation from LLM
        result = await self.llm_service.generate_response(
            messages=[{"role": "user", "content": eval_prompt}],
            system_prompt=self.system_prompt,
            max_tokens=500,
            temperature=0.3,
        )

        # Parse result
        try:
            parsed = self._parse_llm_json(result)
            score = float(parsed.get("score", 0))
            reasoning = parsed.get("reasoning", "No reasoning provided")

            # Ensure binary criteria are 0 or 1
            if criterion_info["binary"]:
                score = 1.0 if score >= 0.5 else 0.0

            return score, reasoning

        except Exception as e:
            logger.error(f"Error parsing evaluation for {criterion_id}: {e}")
            return 0.0, f"Error parsing evaluation: {str(e)}"

    def _build_criterion_prompt(
        self,
        criterion_id: str,
        criterion_info: Dict[str, Any],
        conversation: List[Dict[str, str]],
        deep_thoughts: str,
    ) -> str:
        """Build evaluation prompt for a specific criterion.

        Args:
            criterion_id: ID of the criterion
            criterion_info: Information about the criterion
            conversation: Conversation history
            deep_thoughts: Deep Thoughts report

        Returns:
            Formatted evaluation prompt
        """
        # Format conversation
        conv_text = self._format_conversation(conversation)

        # Get specific evaluation instructions
        if criterion_id == "A":
            instructions = """Evaluate if the session helped client:
1. Identify and clearly define their biggest/most important problem
2. Understand why this specific problem matters to them
3. Articulate the significance and impact of solving this problem

Look for explicit problem identification and exploration of its importance."""

        elif criterion_id == "B":
            instructions = """Evaluate if the session helped client:
1. Identify the key constraint or bottleneck (the 'crux') preventing progress
2. Distinguish between symptoms and root causes
3. Recognize what must be addressed first to unlock progress

Look for deep analysis that goes beyond surface-level issues."""

        elif criterion_id == "C":
            instructions = """Evaluate if the session helped client:
1. Define a specific, concrete action to take TODAY
2. Connect this action directly to addressing the identified crux
3. Make the action achievable and measurable

Look for clear next steps, not vague intentions."""

        elif criterion_id == "D":
            instructions = """Evaluate how well the session:
1. Explored multiple distinct approaches to address the crux
2. Presented genuinely different paths (not variations of the same idea)
3. Considered trade-offs and implications of each path

Score from 0.0 (single path) to 1.0 (multiple creative options)."""

        elif criterion_id == "E":
            instructions = """Evaluate how well the session:
1. Connected solutions to the client's core beliefs and values
2. Referenced specific principles or tenets to guide action
3. Aligned recommendations with what matters most to the client

Score from 0.0 (no connection) to 1.0 (deep value alignment)."""

        # Build complete prompt
        scoring = (
            "1 if fully achieved, 0 if not"
            if criterion_info["binary"]
            else "0.0 to 1.0"
        )

        return f"""## Criterion {criterion_id}: {criterion_info['name']}
{criterion_info['description']}

## Conversation Transcript
{conv_text}

## Deep Thoughts Report
{deep_thoughts}

## Evaluation Task
{instructions}

Score as {scoring}.

Return ONLY a JSON object:
{{
  "score": [your score],
  "reasoning": "[your explanation]"
}}"""

    def _format_conversation(self, conversation: List[Dict[str, str]]) -> str:
        """Format conversation history for evaluation.

        Args:
            conversation: List of conversation turns

        Returns:
            Formatted conversation text
        """
        if not conversation:
            return "No conversation history available."

        formatted = []
        for i, turn in enumerate(conversation, 1):
            role = turn.get("role", "unknown").title()
            content = turn.get("content", "")
            formatted.append(f"Turn {i} - {role}: {content}")

        return "\n\n".join(formatted)

    def _parse_llm_json(self, result: str) -> dict:
        """Parse JSON from LLM response with robust handling.

        Args:
            result: Raw LLM response

        Returns:
            Parsed JSON dictionary
        """
        json_str = result.strip()

        # Handle markdown code blocks
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try regex extraction as fallback
            json_match = re.search(
                r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", result, re.DOTALL
            )
            if json_match:
                json_text = json_match.group()
                json_text = json_text.replace("\n", " ").replace("\r", " ")
                return json.loads(json_text)
            raise

    def _calculate_overall_score(self, evaluations: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall coaching effectiveness score.

        Args:
            evaluations: Dictionary of criterion evaluations

        Returns:
            Overall score (0.0-1.0)
        """
        # Weight binary criteria more heavily (they're foundational)
        weights = {
            "A": 0.25,  # Problem Definition
            "B": 0.25,  # Crux Recognition
            "C": 0.25,  # Today Accomplishment
            "D": 0.125,  # Multiple Paths
            "E": 0.125,  # Core Beliefs
        }

        total_score = 0.0
        for criterion_id, weight in weights.items():
            if criterion_id in evaluations:
                total_score += evaluations[criterion_id]["score"] * weight

        return round(total_score, 2)

    def _format_evaluation_report(
        self, evaluations: Dict[str, Dict[str, Any]], overall_score: float,
        conversation: List[Dict[str, str]], conversation_summary: str
    ) -> str:
        """Format evaluation results as comprehensive report with transcript.

        Args:
            evaluations: Dictionary of evaluations
            overall_score: Overall effectiveness score
            conversation: Conversation history
            conversation_summary: LLM-generated summary of the conversation

        Returns:
            Formatted evaluation report with transcript
        """
        lines = ["## Coaching Session Evaluation Report\n"]

        # Overall score
        lines.append(f"**Overall Effectiveness Score: {overall_score:.1%}**\n")

        # Individual criteria
        lines.append("### Evaluation Criteria\n")

        for criterion_id in ["A", "B", "C", "D", "E"]:
            if criterion_id in evaluations:
                eval_data = evaluations[criterion_id]
                score = eval_data["score"]
                name = eval_data["name"]
                reasoning = eval_data["reasoning"]

                # Format score display
                if self.CRITERIA[criterion_id]["binary"]:
                    score_display = "✓" if score == 1.0 else "✗"
                else:
                    score_display = f"{score:.1%}"

                lines.append(f"**{criterion_id}. {name}: {score_display}**")
                lines.append(f"   {reasoning}\n")

        # Conversation summary
        lines.append("### Conversation Summary\n")
        lines.append(conversation_summary)
        lines.append("")

        # Transcript
        lines.append("### Full Conversation Transcript\n")
        transcript = self._format_conversation_transcript(conversation)
        lines.append(transcript)

        return "\n".join(lines)

    def _format_conversation_transcript(
        self, conversation: List[Dict[str, str]]
    ) -> str:
        """Format conversation history as a readable transcript.

        Args:
            conversation: List of conversation turns

        Returns:
            Formatted transcript
        """
        if not conversation:
            return "No conversation history available."

        formatted = []
        for turn in conversation:
            role = turn.get("role", "unknown").title()
            content = turn.get("content", "")
            formatted.append(f"**{role}**: {content}")

        return "\n\n".join(formatted)

    async def _send_to_langsmith(
        self, evaluations: Dict[str, Dict[str, Any]], overall_score: float,
        request: AgentRequest, conversation: List[Dict[str, str]]
    ) -> None:
        """Send evaluation metrics to LangSmith.

        Args:
            evaluations: Dictionary of criterion evaluations
            overall_score: Overall effectiveness score
            request: Original agent request
            conversation: Conversation history
        """
        # Check if LangSmith is configured
        if not os.getenv("LANGSMITH_API_KEY"):
            logger.debug("LangSmith API key not configured, skipping metrics")
            return

        try:
            from langsmith import Client
            from uuid import uuid4

            client = Client()

            # Create experiment run for manual prototype sessions
            # This ensures manual runs are tracked the same way as automated evals
            experiment_name = (
                f"manual_coaching_session_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Create a dataset example from the conversation
            example = {
                "inputs": {
                    "messages": (
                        conversation[:1] if conversation else []
                    )  # First user message
                },
                "outputs": {
                    "expected_response": (
                        conversation[1]["content"]
                        if len(conversation) > 1 else ""
                    )
                }
            }

            # Create the experiment run
            run_id = str(uuid4())
            client.create_run(
                id=run_id,
                name=experiment_name,
                run_type="eval",
                inputs=example["inputs"],
                outputs={
                    "response": (
                        conversation[-1]["content"] if conversation else ""
                    ),
                    "deep_thoughts": request.context.get(
                        "deep_thoughts", ""
                    )[:500]  # First 500 chars
                },
                project_name=os.getenv(
                    "LANGSMITH_PROJECT", "diary-coach-evaluations"
                ),
                extra={
                    "experiment_metadata": {
                        "experiment_name": experiment_name,
                        "is_manual_session": True,
                        "conversation_turns": len(conversation),
                        "timestamp": datetime.now().isoformat()
                    }
                }
            )

            # Add evaluation feedback as scores
            for criterion_id, eval_data in evaluations.items():
                score_value = eval_data["score"]
                client.create_feedback(
                    run_id=run_id,
                    key=f"criterion_{criterion_id}",
                    score=score_value,
                    comment=eval_data["reasoning"]
                )

            # Add overall score
            client.create_feedback(
                run_id=run_id,
                key="overall_effectiveness",
                score=overall_score,
                comment=f"Overall coaching effectiveness: {overall_score:.1%}"
            )

            logger.info(
                f"Sent evaluation to LangSmith: score={overall_score}"
            )

        except ImportError:
            logger.warning("LangSmith not installed, skipping metrics")
        except Exception as e:
            logger.error(f"Error sending metrics to LangSmith: {e}")

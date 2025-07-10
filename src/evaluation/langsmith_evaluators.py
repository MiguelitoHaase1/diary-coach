"""
LangSmith evaluator wrappers for the 7 coaching behavioral metrics.

This module transforms our evaluation templates into LangSmith RunEvaluator classes,
providing automated quality gates for coaching conversations.
"""

from typing import Dict, Any, Optional
import json
import asyncio
import uuid
from abc import ABC, abstractmethod

from langsmith.evaluation import RunEvaluator
from langsmith.schemas import Run, Example

from src.services.llm_factory import LLMFactory, LLMTier


class BaseCoachingEvaluator(RunEvaluator, ABC):
    """Base class for all coaching evaluators."""
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service or LLMFactory.create_service(LLMTier.CHEAP)
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
            loop = asyncio.get_running_loop()
            # We're in an async context, so we can't run sync
            # Return a placeholder and hope aevaluate_run gets called
            return {
                "key": self.key,
                "score": 0.0,
                "reasoning": "Sync evaluation not supported - use aevaluate_run",
                "feedback": {"strengths": [], "improvements": []}
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
        
        # Get the last user message as client statement
        client_statement = self._extract_client_statement(conversation)
        
        # Build evaluation prompt using our template
        eval_prompt = self._build_eval_prompt(conversation, coach_response, client_statement)
        
        # Use cheap LLM for evaluation - convert string to message format
        try:
            messages = [{"role": "user", "content": eval_prompt}]
            # Use higher token limit for JSON response (need ~500-800 tokens for full evaluation)
            result = await self.llm_service.generate_response(messages, max_tokens=800)
            
            # Parse JSON response
            parsed = json.loads(result)
            
            return {
                "key": self.key,
                "score": parsed["score"] / 5.0,  # Normalize to 0-1 for LangSmith
                "reasoning": parsed["reasoning"],
                "feedback": {
                    "strengths": parsed["strengths"],
                    "improvements": parsed["improvements"]
                }
            }
            
        except Exception as e:
            return {
                "key": self.key,
                "score": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "feedback": {
                    "strengths": [],
                    "improvements": ["Evaluation system error"]
                }
            }
    
    @abstractmethod
    def _build_eval_prompt(
        self, 
        conversation: list, 
        coach_response: str, 
        client_statement: str
    ) -> str:
        """Build the evaluation prompt for this specific metric."""
        pass
    
    def _extract_client_statement(self, conversation: list) -> str:
        """Extract the last user message as client statement."""
        if not conversation:
            return ""
        
        for msg in reversed(conversation):
            if isinstance(msg, dict) and msg.get("role") == "user":
                return msg.get("content", "")
        
        return ""
    
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


class ProblemSignificanceEvaluator(BaseCoachingEvaluator):
    """Evaluates coach's ability to assess problem importance."""
    
    def _build_eval_prompt(
        self, 
        conversation: list, 
        coach_response: str, 
        client_statement: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)
        
        return f"""You are an expert coaching evaluator specializing in problem assessment. Your task is to evaluate how effectively a coaching conversation helps clients assess the significance and priority of their problems or challenges.

## Metric Definition
Problem Significance Assessment measures the coach's ability to guide clients in evaluating the importance, urgency, and impact of their stated problems, helping them prioritize and understand the true significance of their challenges.

## Criteria
- **Significance Exploration**: Coach helps client explore why this problem matters and its broader implications
- **Priority Clarification**: Coach assists in determining relative importance compared to other issues
- **Impact Analysis**: Coach guides examination of consequences if problem remains unaddressed
- **Scope Definition**: Coach helps client understand the full scope and boundaries of the problem
- **Emotional Resonance**: Coach explores the emotional significance and personal meaning of the problem

## Rating Rubric
5: Exceptional - Masterfully guides comprehensive problem significance evaluation with deep exploration of importance, priority, and impact
4: Proficient - Effectively explores problem significance with good attention to priority and consequences
3: Adequate - Basic problem significance discussion with some priority or impact exploration
2: Developing - Limited problem significance assessment with minimal priority clarification
1: Inadequate - Fails to help client assess problem significance or importance

## Conversation Context
{conversation_history}

## Coach Response to Evaluate
{coach_response}

## Client Statement
{client_statement}

Provide your evaluation as JSON:
{{
  "score": [1-5],
  "reasoning": "Step-by-step analysis of problem significance assessment",
  "strengths": ["Specific coaching strengths observed"],
  "improvements": ["Specific areas for development"]
}}"""


class TaskConcretizationEvaluator(BaseCoachingEvaluator):
    """Evaluates coach's ability to transform abstract goals into concrete tasks."""
    
    def _build_eval_prompt(
        self, 
        conversation: list, 
        coach_response: str, 
        client_statement: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)
        
        return f"""You are an expert coaching evaluator specializing in goal and task clarification. Your task is to evaluate how effectively a coaching conversation helps clients transform abstract goals or vague intentions into concrete, actionable tasks.

## Metric Definition
Task Concretization measures the coach's ability to guide clients from abstract, vague, or general goals to specific, measurable, and actionable tasks with clear parameters and success criteria.

## Criteria
- **Specificity Enhancement**: Coach helps client define precise, detailed task parameters
- **Actionability Focus**: Coach ensures tasks are behaviorally specific and executable
- **Measurability Support**: Coach guides creation of clear success metrics and indicators
- **Timeline Clarification**: Coach helps establish realistic timeframes and deadlines
- **Resource Identification**: Coach explores what resources, support, or capabilities are needed

## Rating Rubric
5: Exceptional - Masterfully transforms abstract goals into highly specific, actionable tasks with clear metrics and timelines
4: Proficient - Effectively guides task concretization with good specificity and actionability
3: Adequate - Basic task clarification with some concrete elements defined
2: Developing - Limited progress toward concrete task definition
1: Inadequate - Fails to help client concretize vague goals or intentions

## Conversation Context
{conversation_history}

## Coach Response to Evaluate
{coach_response}

## Client Statement
{client_statement}

Provide your evaluation as JSON:
{{
  "score": [1-5],
  "reasoning": "Step-by-step analysis of task concretization effectiveness",
  "strengths": ["Specific coaching strengths observed"],
  "improvements": ["Specific areas for development"]
}}"""


class SolutionDiversityEvaluator(BaseCoachingEvaluator):
    """Evaluates coach's ability to facilitate diverse solution generation."""
    
    def _build_eval_prompt(
        self, 
        conversation: list, 
        coach_response: str, 
        client_statement: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)
        
        return f"""You are an expert coaching evaluator specializing in creative problem-solving. Your task is to evaluate how effectively a coaching conversation facilitates the generation of diverse, creative solutions and multiple options for addressing client challenges.

## Metric Definition
Solution Diversity measures the coach's ability to facilitate client generation of multiple, varied solution options, encouraging creative thinking and comprehensive exploration of possibilities rather than premature convergence on single solutions.

## Criteria
- **Option Generation**: Coach facilitates creation of multiple solution alternatives
- **Creative Exploration**: Coach encourages out-of-the-box thinking and innovative approaches
- **Perspective Variety**: Coach helps client consider solutions from different angles or viewpoints
- **Brainstorming Support**: Coach creates safe space for idea generation without immediate evaluation
- **Convergence Prevention**: Coach resists premature solution selection, maintaining exploration

## Rating Rubric
5: Exceptional - Masterfully facilitates diverse, creative solution generation with multiple innovative options explored
4: Proficient - Effectively supports solution diversity with good variety and creative thinking
3: Adequate - Basic solution exploration with some alternative options generated
2: Developing - Limited solution diversity with minimal creative exploration
1: Inadequate - Fails to facilitate multiple solutions or creative thinking

## Conversation Context
{conversation_history}

## Coach Response to Evaluate
{coach_response}

## Client Statement
{client_statement}

Provide your evaluation as JSON:
{{
  "score": [1-5],
  "reasoning": "Step-by-step analysis of solution diversity facilitation",
  "strengths": ["Specific coaching strengths observed"],
  "improvements": ["Specific areas for development"]
}}"""


class CruxIdentificationEvaluator(BaseCoachingEvaluator):
    """Evaluates coach's ability to identify core issues and leverage points."""
    
    def _build_eval_prompt(
        self, 
        conversation: list, 
        coach_response: str, 
        client_statement: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)
        
        return f"""You are an expert coaching evaluator specializing in root cause analysis and leverage point identification. Your task is to evaluate how effectively a coaching conversation helps clients identify the core issues, leverage points, or fundamental elements that are most critical to address.

## Metric Definition
Crux Identification measures the coach's ability to guide clients in discovering the most critical, foundational, or leveraged elements of their situation - the key factors that, when addressed, would have the greatest impact on their overall challenge or goal.

## Criteria
- **Root Cause Exploration**: Coach helps client dig beneath surface symptoms to underlying causes
- **Leverage Point Recognition**: Coach guides identification of high-impact intervention points
- **Pattern Recognition**: Coach helps client see recurring themes or systemic issues
- **Priority Focusing**: Coach assists in distinguishing critical from peripheral elements
- **Systems Thinking**: Coach explores interconnections and broader context

## Rating Rubric
5: Exceptional - Masterfully guides client to identify core leverage points and root causes with sophisticated analysis
4: Proficient - Effectively explores underlying issues and helps identify key factors
3: Adequate - Basic exploration of root causes with some leverage point identification
2: Developing - Limited depth in identifying core issues or leverage points
1: Inadequate - Fails to help client identify crucial elements or underlying causes

## Conversation Context
{conversation_history}

## Coach Response to Evaluate
{coach_response}

## Client Statement
{client_statement}

Provide your evaluation as JSON:
{{
  "score": [1-5],
  "reasoning": "Step-by-step analysis of crux identification effectiveness",
  "strengths": ["Specific coaching strengths observed"],
  "improvements": ["Specific areas for development"]
}}"""


class CruxSolutionEvaluator(BaseCoachingEvaluator):
    """Evaluates coach's ability to explore solutions for core issues."""
    
    def _build_eval_prompt(
        self, 
        conversation: list, 
        coach_response: str, 
        client_statement: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)
        
        return f"""You are an expert coaching evaluator specializing in strategic solution development. Your task is to evaluate how effectively a coaching conversation explores solutions specifically targeted at the identified core issues or leverage points.

## Metric Definition
Crux Solution Exploration measures the coach's ability to guide deep, thorough exploration of solutions specifically addressing the identified core issues, leverage points, or fundamental challenges rather than surface-level fixes.

## Criteria
- **Target Alignment**: Coach ensures solutions directly address identified core issues
- **Depth of Exploration**: Coach facilitates comprehensive examination of high-impact solutions
- **Strategic Focus**: Coach maintains focus on leverage points rather than peripheral fixes
- **Implementation Viability**: Coach explores practical aspects of implementing core solutions
- **Ripple Effect Analysis**: Coach examines how core solutions might impact broader situation

## Rating Rubric
5: Exceptional - Masterfully explores comprehensive solutions targeting core issues with sophisticated implementation analysis
4: Proficient - Effectively explores solutions aligned with identified leverage points
3: Adequate - Basic solution exploration with some focus on core issues
2: Developing - Limited depth in exploring solutions for fundamental challenges
1: Inadequate - Fails to explore solutions targeting identified core issues

## Conversation Context
{conversation_history}

## Coach Response to Evaluate
{coach_response}

## Client Statement
{client_statement}

Provide your evaluation as JSON:
{{
  "score": [1-5],
  "reasoning": "Step-by-step analysis of crux solution exploration effectiveness",
  "strengths": ["Specific coaching strengths observed"],
  "improvements": ["Specific areas for development"]
}}"""


class BeliefSystemEvaluator(BaseCoachingEvaluator):
    """Evaluates coach's ability to work with client belief systems."""
    
    def _build_eval_prompt(
        self, 
        conversation: list, 
        coach_response: str, 
        client_statement: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)
        
        return f"""You are an expert coaching evaluator specializing in belief system work and mental model transformation. Your task is to evaluate how effectively a coaching conversation helps clients examine, understand, and potentially shift their underlying beliefs, assumptions, or mental models.

## Metric Definition
Belief System Integration measures the coach's ability to help clients identify limiting beliefs, examine underlying assumptions, and integrate new perspectives or empowering beliefs that support their goals and growth.

## Criteria
- **Belief Identification**: Coach helps client recognize underlying beliefs and assumptions
- **Assumption Examination**: Coach guides exploration of belief validity and origins
- **Perspective Expansion**: Coach facilitates consideration of alternative viewpoints
- **Empowering Integration**: Coach supports adoption of beliefs that enable growth
- **Consistency Alignment**: Coach helps align beliefs with desired outcomes and values

## Rating Rubric
5: Exceptional - Masterfully guides belief system examination and integration with sophisticated perspective work
4: Proficient - Effectively explores beliefs and supports healthy perspective shifts
3: Adequate - Basic belief exploration with some assumption examination
2: Developing - Limited belief system work with minimal perspective expansion
1: Inadequate - Fails to address beliefs, assumptions, or mental models

## Conversation Context
{conversation_history}

## Coach Response to Evaluate
{coach_response}

## Client Statement
{client_statement}

Provide your evaluation as JSON:
{{
  "score": [1-5],
  "reasoning": "Step-by-step analysis of belief system integration effectiveness",
  "strengths": ["Specific coaching strengths observed"],
  "improvements": ["Specific areas for development"]
}}"""


class NonDirectiveStyleEvaluator(BaseCoachingEvaluator):
    """Evaluates coach's adherence to non-directive coaching principles."""
    
    def _build_eval_prompt(
        self, 
        conversation: list, 
        coach_response: str, 
        client_statement: str
    ) -> str:
        conversation_history = self._format_conversation_history(conversation)
        
        return f"""You are an expert coaching evaluator specializing in coaching methodology and approach. Your task is to evaluate how effectively a coaching conversation demonstrates non-directive coaching principles, maintaining client autonomy while facilitating self-discovery.

## Metric Definition
Non-Directive Coaching Style measures the coach's adherence to client-centered, inquiry-based coaching principles that support client autonomy, self-discovery, and internal problem-solving rather than advice-giving or directive guidance.

## Criteria
- **Question vs. Advice Ratio**: Coach primarily uses questions rather than providing advice or solutions
- **Client Autonomy Support**: Coach maintains client's ownership of agenda, decisions, and solutions
- **Self-Discovery Facilitation**: Coach guides client to their own insights and answers
- **Inquiry Quality**: Coach uses powerful, open-ended questions that promote reflection
- **Restraint Demonstration**: Coach resists impulse to provide solutions or fix problems

## Rating Rubric
5: Exceptional - Masterfully demonstrates non-directive approach with sophisticated inquiry and complete client autonomy support
4: Proficient - Effectively maintains non-directive stance with good question quality and client ownership
3: Adequate - Generally non-directive with some lapses into advice-giving or direction
2: Developing - Mixed approach with frequent directive interventions
1: Inadequate - Predominantly directive with minimal client autonomy or self-discovery

## Conversation Context
{conversation_history}

## Coach Response to Evaluate
{coach_response}

## Client Statement
{client_statement}

Provide your evaluation as JSON:
{{
  "score": [1-5],
  "reasoning": "Step-by-step analysis of non-directive coaching style adherence",
  "strengths": ["Specific coaching strengths observed"],
  "improvements": ["Specific areas for development"]
}}"""


# Evaluator registry for easy access
EVALUATOR_REGISTRY = {
    "problem_significance": ProblemSignificanceEvaluator,
    "task_concretization": TaskConcretizationEvaluator,
    "solution_diversity": SolutionDiversityEvaluator,
    "crux_identification": CruxIdentificationEvaluator,
    "crux_solution": CruxSolutionEvaluator,
    "belief_system": BeliefSystemEvaluator,
    "non_directive_style": NonDirectiveStyleEvaluator,
}


def get_all_evaluators() -> list[BaseCoachingEvaluator]:
    """Get instances of all coaching evaluators."""
    return [evaluator_class() for evaluator_class in EVALUATOR_REGISTRY.values()]


def get_evaluator(name: str) -> BaseCoachingEvaluator:
    """Get a specific evaluator by name."""
    if name not in EVALUATOR_REGISTRY:
        raise ValueError(f"Unknown evaluator: {name}. Available: {list(EVALUATOR_REGISTRY.keys())}")
    return EVALUATOR_REGISTRY[name]()
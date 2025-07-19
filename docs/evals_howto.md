# Evaluation System How-To Guide

## Executive Summary

This guide captures hard-won lessons from implementing evaluation systems across Sessions 3-7 of the Diary Coach project. We evolved from simple behavioral analyzers to a sophisticated LangSmith-integrated system with dedicated evaluation LLMs.

**Final Architecture**: A dedicated evaluation LLM (Claude Sonnet) creates evaluations based on 5 focused criteria, which are exported to LangSmith for tracking and analysis. Evaluations happen within Deep Thoughts reports, not as separate artifacts.

## The Evolution Journey

### Phase 1: Simple Behavioral Analyzers (Session 3)
- Started with 4 Python-based analyzers
- Each analyzer scored a specific behavior (0-1)
- Generated markdown evaluation reports
- **Problem**: Limited to single message evaluation

### Phase 2: Expanded to 7 Evaluators (Session 4)
- Added morning-specific analyzers
- Created comprehensive evaluation reports
- **Problem**: Still evaluating individual messages, not conversations

### Phase 3: Full Conversation Evaluation (Session 6.6)
- Built TestUserAgent for realistic conversation simulation
- Updated evaluators to analyze entire conversations
- Added LangSmith integration
- **Problems**: 
  - LangSmith evaluations not appearing in dashboard
  - Hardcoded mock scores (0.6) in "light reports"
  - Complex 7-evaluator system

### Phase 4: Simplified 5-Criteria System (Session 7+)
- Reduced to 5 focused evaluation criteria
- Removed separate evaluation markdown files
- Integrated evaluation into Deep Thoughts reports
- Fixed JSON parsing and scoring issues
- **Current State**: Working system with proper LangSmith integration

## ❌ What NOT to Do

### 1. Don't Mock External Services
```python
# ❌ WRONG: Creating mock Run objects
mock_run = Run(id=str(uuid.uuid4()), ...)
result = await evaluator.aevaluate_run(mock_run)
```
**Why it fails**: Bypasses LangSmith's tracking infrastructure entirely

### 2. Don't Use Hardcoded Scores
```python
# ❌ WRONG: From reporter.py
behavioral_scores = [
    AnalysisScore("SpecificityPush", 0.6, "Mock reasoning"),
    AnalysisScore("ActionOrientation", 0.6, "Mock reasoning")
]
```
**Why it fails**: Creates false confidence; hides real evaluation issues

### 3. Don't Evaluate Single Messages
```python
# ❌ WRONG: Analyzing one coach response
score = await analyzer.analyze(coach_response, context)
```
**Why it fails**: Misses conversation flow, progression, and breakthroughs

### 4. Don't Use Underspecified Models
```python
# ❌ WRONG: Using cheap tier with low token limits
LLMFactory.create_service(LLMTier.CHEAP)  # 800 tokens
```
**Why it fails**: Causes timeouts when evaluating full conversations

### 5. Don't Create Separate Eval Files
```markdown
# ❌ WRONG: Generating Eval_20250713_1234.md files
docs/prototype/Evals/
├── Eval_20250701_1614.md
├── Eval_20250701_1615.md
└── ... (dozens more)
```
**Why it fails**: Creates clutter; evaluations should be in Deep Thoughts

### 6. Don't Parse JSON Naively
```python
# ❌ WRONG: Simple JSON parsing
parsed = json.loads(result)
```
**Why it fails**: LLM outputs often include markdown formatting

## ✅ What TO Do

### 1. Use LangSmith's Evaluation Framework Properly
```python
# ✅ RIGHT: Use aevaluate with proper dataset
from langsmith.evaluation import aevaluate

results = await aevaluate(
    target_function,
    data=dataset_name,
    evaluators=langsmith_evaluators,
    experiment_prefix="coaching_eval",
    client=langsmith_client
)
```

### 2. Create Robust JSON Parsing
```python
# ✅ RIGHT: Handle markdown and control characters
def parse_llm_json(result: str) -> dict:
    json_str = result.strip()
    
    # Handle markdown code blocks
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0].strip()
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Regex fallback for embedded JSON
        import re
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            json_text = json_text.replace('\n', ' ').replace('\r', ' ')
            return json.loads(json_text)
        raise
```

### 3. Use Appropriate Model Tiers
```python
# ✅ RIGHT: Use STANDARD tier with sufficient tokens
self.llm_service = LLMFactory.create_service(LLMTier.STANDARD)  # Claude Sonnet
result = await self.llm_service.generate_response(messages, max_tokens=1500)
```

### 4. Focus on Key Evaluation Criteria
```python
# ✅ RIGHT: 5 focused criteria instead of 7
EVALUATOR_REGISTRY = {
    "problem_definition": ProblemDefinitionEvaluator,      # A
    "crux_recognition": CruxRecognitionEvaluator,         # B
    "today_accomplishment": TodayAccomplishmentEvaluator, # C
    "multiple_paths": MultiplePathsEvaluator,             # D
    "core_beliefs": CoreBeliefsEvaluator,                 # E
}
```

### 5. Evaluate Full Conversations
```python
# ✅ RIGHT: Analyze entire conversation with context
conversation_history = self._format_conversation_history(conversation)
eval_prompt = f"""
## Conversation Context
{conversation_history}

## Deep Report Context  
{coach_response}

Evaluate the ENTIRE conversation...
"""
```

### 6. Add Proper Tracing
```python
# ✅ RIGHT: Use LangSmith decorators
from langsmith import traceable

@traceable(name="generate_deep_thoughts")
async def generate_deep_thoughts(self, conversation_history, ...):
    # Implementation
```

### 7. Use Graduated Scoring
```python
# ✅ RIGHT: Meaningful score gradations
# Score as follows:
# - 0.0: No evidence of criterion
# - 0.5: Partial achievement  
# - 1.0: Full achievement
```

## Complete Implementation Pattern

### 1. Define Clear Evaluation Criteria
```markdown
# In deep_thoughts_system_prompt.md appendix:
A - Define biggest problem to solve - and understand why this problem matters
B - Recognize the key constraint to address ('the crux')
C - Define exactly what to accomplish today to address the crux
D - Define multiple viable and different paths forward to address crux
E - Define which 'core beliefs'/'tenets' to focus on when working the problem
```

### 2. Create LangSmith Evaluators
```python
class ProblemDefinitionEvaluator(BaseCoachingEvaluator):
    def _build_eval_prompt(self, conversation: list, coach_response: str) -> str:
        return f"""Evaluate whether the coach helped the client:
1. Identify and clearly define their biggest/most important problem
2. Understand why this specific problem matters to them
3. Articulate the significance and impact of solving this problem

Return ONLY a JSON object:
{{
  "score": 0.5,
  "reasoning": "Your explanation here"
}}"""
```

### 3. Set Up Test Infrastructure
```python
# Create test user agent for realistic conversations
class TestUserAgent:
    async def respond(self, coach_message: str, conversation_history: List[str]):
        # Simulate realistic PM responses
        # Progress from resistance → engagement → insight
```

### 4. Integrate with LangSmith
```python
# Run evaluation experiments
dataset = await client.create_dataset(dataset_name="coaching_conversations")
await client.create_example(
    dataset_id=dataset.id,
    inputs={"messages": conversation_messages},
    outputs={"response": deep_report}
)

results = await aevaluate(
    coach_function,
    data=dataset_name,
    evaluators=get_all_evaluators(),
    experiment_prefix="coaching_eval"
)
```

## Debugging Evaluation Issues

### 1. Check JSON Parsing
```python
# Add debug logging
logger.debug(f"Raw LLM response: {result}")
logger.debug(f"Extracted JSON: {json_str}")
logger.debug(f"Parsed result: {parsed}")
```

### 2. Verify Model Configuration
```python
# Ensure correct model is being used
print(f"Using model: {self.llm_service.model}")
print(f"Max tokens: {max_tokens}")
```

### 3. Test with Simple Examples
```python
# Start with minimal test case
test_conversation = [
    {"role": "user", "content": "I need help"},
    {"role": "assistant", "content": "What's on your mind?"}
]
```

### 4. Monitor LangSmith Dashboard
- Check experiment URL after each run
- Verify all evaluators are showing
- Look for consistent 0 scores (indicates parsing issues)

## Best Practices Summary

1. **Use Real Services**: Never mock LangSmith or evaluation infrastructure
2. **Parse Robustly**: Handle all LLM output formats
3. **Size Appropriately**: Use sufficient model tier and token limits
4. **Evaluate Holistically**: Analyze full conversations, not fragments
5. **Keep It Simple**: 5 criteria > 7 criteria
6. **Integrate Deeply**: Adopt LangSmith patterns fully
7. **Debug Visibly**: Log what's being evaluated and scored
8. **Test Realistically**: Use proper test agents, not static data

## Common Error Messages and Solutions

### "Project does not have access to model"
**Solution**: Check your OpenAI/Anthropic API keys and model access

### "Timeout reading from AsyncOpenAI"
**Solution**: Increase max_tokens or use a more powerful model tier

### "Could not parse JSON from response"
**Solution**: Improve JSON extraction logic, add regex fallback

### "Evaluations not appearing in LangSmith"
**Solution**: Use aevaluate() instead of creating mock Run objects

## Final Architecture Recommendations

1. **Evaluation LLM**: Use Claude Sonnet (STANDARD tier) for quality evaluations
2. **Scoring**: 0.0-1.0 graduated scale for nuanced assessment
3. **Integration**: Deep integration with LangSmith for full observability
4. **Location**: Evaluations within Deep Thoughts, not separate files
5. **Criteria**: 5 focused criteria that capture coaching effectiveness

Remember: The goal is to measure coaching effectiveness, not to generate evaluation artifacts. Keep the system simple, reliable, and focused on providing actionable insights.
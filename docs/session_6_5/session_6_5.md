Thanks for the clarifications! I'll create Session 6.5: LangSmith Eval Jobs that focuses on clean methodology without hacks, uses fresh targeted conversations, and keeps CI lightweight.

Here's the Session 6.5 specification:

# Session 6.5: LangSmith Eval Jobs - Behavioral Quality Safety Net

## Executive Summary

Implement LangSmith evaluation jobs that wrap our 7 custom coaching analyzers, providing automated quality gates before architectural changes. This 90-minute session creates a regression-prevention system using LangSmith's dataset and CI capabilities while preserving our domain-specific behavioral metrics.

**Duration**: 1.5-2 hours (4 increments)  
**Dependencies**: Session 5 complete (LangSmith already integrated), Session 6.13 complete (7 new evaluation templates available)  
**Philosophy**: "Measure Before You Migrate" - Lock in coaching quality baselines before Sessions 7-11 refactor everything

## Why Now?

- **Minimal Integration Work**: LangSmith client already wired (Session 5.4), just need `RunEvaluator` wrappers
- **Stable Evaluation Framework**: 7 comprehensive coaching metrics defined in Session 6.13
- **Pre-Refactor Checkpoint**: Sessions 7-11 will add MCP, voice, and production features - need quality gates now
- **Fresh Signal Generation**: New evaluation dimensions will produce meaningful variation (vs old 6/10 problem)

## Session Goals

1. **Wrap Custom Analyzers**: Transform our 7 evaluation templates into LangSmith `RunEvaluator` classes
2. **Generate Quality Dataset**: Create targeted conversations that test each evaluation dimension
3. **Establish Baselines**: Run initial evaluation to set quality benchmarks
4. **Lightweight CI Gate**: GitHub Action that runs on `eval-impact` tagged PRs

## Human Setup Requirements

🔴 **BEFORE CODING**:
- [ ] Ensure LangSmith API key is in `.env`: `LANGSMITH_API_KEY=your_key`
- [ ] Verify LangSmith project exists: `diary-coach-evals`
- [ ] Have GitHub repo access for Actions setup

🟡 **AFTER SESSION**:
- [ ] Review baseline scores and adjust if needed
- [ ] Tag future PRs with `eval-impact` when they might affect coaching quality
- [ ] Monitor LangSmith dashboard for regression trends

## Technical Stack

- **LangSmith SDK**: Dataset management and evaluation orchestration
- **Custom Evaluators**: Our 7 behavioral analyzers wrapped as `RunEvaluator`
- **Test Data Generation**: Targeted conversation scenarios for each metric
- **GitHub Actions**: Conditional CI runs on tagged PRs

## Implementation Approach

### Increment 6.5.1: Evaluator Wrappers (30 min)

**Goal**: Transform evaluation templates into LangSmith evaluators

**Implementation**:
```python
# src/evaluation/langsmith_evaluators.py
from langsmith.evaluation import RunEvaluator
from typing import Optional, Dict, Any
import json

class ProblemSignificanceEvaluator(RunEvaluator):
    """Evaluates coach's ability to assess problem importance."""
    
    def evaluate_run(
        self,
        run: Run,
        example: Optional[Example] = None
    ) -> Dict[str, Any]:
        # Extract conversation from run
        conversation = run.inputs.get("messages", [])
        coach_response = run.outputs.get("response", "")
        
        # Apply our existing evaluation template
        eval_prompt = self._build_eval_prompt(conversation, coach_response)
        
        # Use cheap LLM for evaluation (GPT-4o-mini or Sonnet)
        result = self.llm_service.generate(eval_prompt, model_tier="cheap")
        
        # Parse JSON response
        parsed = json.loads(result)
        
        return {
            "score": parsed["score"] / 5.0,  # Normalize to 0-1
            "reasoning": parsed["reasoning"],
            "feedback": {
                "strengths": parsed["strengths"],
                "improvements": parsed["improvements"]
            }
        }
```

**Key Design Decisions**:
- Keep evaluation logic in templates, wrapper just orchestrates
- Return normalized scores (0-1) for LangSmith compatibility
- Include detailed feedback for debugging

**Tests**:
```python
def test_problem_significance_evaluator():
    evaluator = ProblemSignificanceEvaluator()
    run = create_mock_run(
        messages=[{"role": "user", "content": "I have team conflicts"}],
        response="Tell me more about these conflicts..."
    )
    
    result = evaluator.evaluate_run(run)
    assert 0 <= result["score"] <= 1
    assert "reasoning" in result
    assert "feedback" in result
```

### Increment 6.5.2: Dataset Generation (15 min)

**Goal**: Create focused test conversations for each evaluation dimension

**Implementation**:
```python
# src/evaluation/dataset_generator.py
class EvalDatasetGenerator:
    """Generate targeted conversations for each coaching metric."""
    
    def generate_problem_significance_examples(self) -> List[Example]:
        """Create examples testing problem assessment ability."""
        scenarios = [
            {
                "context": "Overwhelmed PM with multiple issues",
                "opening": "I'm dealing with stakeholder conflicts, missed deadlines, and team morale issues",
                "good_response": "These all sound challenging. Which one, if left unaddressed, would have the biggest ripple effect on the others?",
                "poor_response": "Let's talk about the stakeholder conflicts first."
            },
            {
                "context": "PM unsure about priority", 
                "opening": "Should I focus on documentation or user interviews?",
                "good_response": "Help me understand - what would happen to your project if you delayed each by a week? What's driving the urgency?",
                "poor_response": "User interviews are always important."
            }
        ]
        
        return [self._scenario_to_example(s) for s in scenarios]
```

**Dataset Structure**:
- 3-5 examples per evaluation dimension
- Mix of good/poor coaching responses for contrast
- Real PM scenarios from your experience
- Total: ~25-30 conversations

**Upload to LangSmith**:
```python
async def upload_dataset():
    client = Client()
    dataset = await client.create_dataset(
        "coach-behavioral-regression",
        description="Targeted conversations for 7 coaching dimensions"
    )
    
    generator = EvalDatasetGenerator()
    for dim in EVALUATION_DIMENSIONS:
        examples = generator.generate_examples(dim)
        for ex in examples:
            await client.create_example(dataset.id, ex)
```

### Increment 6.5.3: Baseline Evaluation Run (15 min)

**Goal**: Establish quality benchmarks with current coach

**Implementation**:
```python
# scripts/run_baseline_eval.py
async def run_baseline_evaluation():
    """Generate baseline scores for all coaching dimensions."""
    
    # Initialize evaluators
    evaluators = [
        ProblemSignificanceEvaluator(),
        TaskConcretizationEvaluator(),
        SolutionDiversityEvaluator(),
        CruxIdentificationEvaluator(),
        CruxSolutionEvaluator(),
        BeliefSystemEvaluator(),
        NonDirectiveStyleEvaluator()
    ]
    
    # Run evaluation
    results = await evaluate(
        lambda inputs: coach.generate_response(inputs["messages"]),
        data="coach-behavioral-regression",
        evaluators=evaluators,
        experiment_prefix="baseline"
    )
    
    # Generate report
    print("=== Baseline Coaching Quality ===")
    for evaluator, scores in results.items():
        mean_score = sum(scores) / len(scores)
        variance = calculate_variance(scores)
        print(f"{evaluator}: {mean_score:.2f} (σ²={variance:.3f})")
```

**Expected Output**:
```
=== Baseline Coaching Quality ===
ProblemSignificance: 0.72 (σ²=0.045)
TaskConcretization: 0.65 (σ²=0.082)
SolutionDiversity: 0.58 (σ²=0.124)
CruxIdentification: 0.81 (σ²=0.031)
CruxSolution: 0.69 (σ²=0.067)
BeliefSystem: 0.74 (σ²=0.052)
NonDirectiveStyle: 0.88 (σ²=0.021)
```

**Success Criteria**:
- Meaningful score variation (0.58-0.88 range vs old 0.6 uniformity)
- Low variance within dimensions (σ² < 0.15)
- Interpretable patterns (e.g., high non-directive, lower solution diversity)

### Increment 6.5.4: CI Integration (30 min)

**Goal**: GitHub Action for regression prevention

**Implementation**:
```yaml
# .github/workflows/coaching-quality-gate.yml
name: Coaching Quality Gate

on:
  pull_request:
    types: [opened, synchronize]
    
jobs:
  eval-regression:
    if: contains(github.event.pull_request.labels.*.name, 'eval-impact')
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install langsmith
        
    - name: Run coaching evaluation
      env:
        LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      run: |
        python scripts/ci_eval_check.py
        
    - name: Comment PR with results
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const results = JSON.parse(fs.readFileSync('eval_results.json'));
          
          let comment = '## 🎯 Coaching Quality Check\n\n';
          
          for (const [metric, data] of Object.entries(results)) {
            const emoji = data.regression ? '🔴' : '✅';
            const change = ((data.current - data.baseline) * 100).toFixed(1);
            comment += `${emoji} **${metric}**: ${data.current.toFixed(2)} (${change >= 0 ? '+' : ''}${change}%)\n`;
          }
          
          comment += `\n[View full report](${results.langsmith_url})`;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

**CI Check Logic**:
```python
# scripts/ci_eval_check.py
REGRESSION_THRESHOLD = 0.05  # 5% drop triggers failure

async def check_for_regression():
    baseline = load_baseline_scores()
    current = await run_evaluation()
    
    results = {}
    any_regression = False
    
    for metric, baseline_score in baseline.items():
        current_score = current[metric]
        regression = (baseline_score - current_score) > REGRESSION_THRESHOLD
        
        results[metric] = {
            "baseline": baseline_score,
            "current": current_score,
            "regression": regression
        }
        
        if regression:
            any_regression = True
            
    # Save results for PR comment
    with open("eval_results.json", "w") as f:
        json.dump(results, f)
        
    if any_regression:
        print("❌ Coaching quality regression detected!")
        sys.exit(1)
    else:
        print("✅ Coaching quality maintained!")
```

## Common Pitfalls to Avoid

### For Claude Code:
1. **Don't recreate evaluation logic** - Reuse templates from Session 6.13
2. **Avoid synchronous LangSmith calls** - Use async throughout
3. **Don't hardcode thresholds** - Make regression tolerance configurable
4. **Remember cost optimization** - Use cheap models for evaluation

### For You (Human):
1. **Label PRs correctly** - Only add `eval-impact` to relevant changes
2. **Review baseline scores** - Ensure they're reasonable before locking in
3. **Monitor evaluation costs** - Each CI run will cost ~$0.50-1.00
4. **Update dataset periodically** - Add new scenarios as coach evolves

## Migration Path from Session 6

Since Session 6 established our evaluation templates, this session simply wraps them:

1. **No changes to analyzer logic** - Templates remain authoritative
2. **No changes to coach behavior** - This is observation-only
3. **No changes to existing tests** - Add new tests for wrappers only
4. **Backward compatible** - Can still run analyzers directly

## Success Metrics

- [ ] All 7 evaluators wrapped and tested
- [ ] Dataset with 25+ targeted conversations uploaded
- [ ] Baseline scores show meaningful variation (>0.3 range)
- [ ] CI runs in <2 minutes on labeled PRs
- [ ] PR comments show clear regression signals

## Learning Opportunities

Given your focus on evaluation systems and LLM observability:

1. **Evaluation Design Patterns**: How to create metrics with signal vs noise
2. **Dataset Curation**: Crafting examples that reveal behavioral differences  
3. **CI/CD for AI**: Integrating ML evaluation into development workflow
4. **Statistical Significance**: When is a score change meaningful?

## Exit Criteria

Session 6.5 is complete when:
- `eval-impact` labeled PR triggers quality check
- PR comment shows per-dimension scores with baseline comparison
- Any 5% regression blocks merge
- LangSmith dashboard shows evaluation history

---

*Note: This session bridges the gap between local evaluation (Sessions 3-4) and production observability (Session 13), providing immediate value as a regression guard while upcoming sessions refactor the architecture.*
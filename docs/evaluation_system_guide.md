# LangSmith Evaluation System Guide

## Overview

Session 6.5 implements automated coaching quality evaluation using LangSmith, providing regression detection and quality gates for the diary coach system.

## Components

### 1. Evaluation Dimensions (7 Metrics)

The system evaluates coaching conversations across 7 behavioral dimensions:

- **Problem Significance Assessment**: Ability to help clients evaluate problem importance and priority
- **Task Concretization**: Transforming abstract goals into specific, actionable tasks  
- **Solution Diversity**: Facilitating generation of multiple creative solution options
- **Crux Identification**: Identifying core issues and leverage points
- **Crux Solution Exploration**: Exploring solutions targeted at fundamental challenges
- **Belief System Integration**: Working with underlying beliefs and mental models
- **Non-Directive Coaching Style**: Using questions rather than advice, maintaining client autonomy

### 2. Evaluation Dataset

**Location**: LangSmith dataset `coach-behavioral-regression`

**Content**: 21 conversation scenarios (3 per dimension) with both good and poor coaching responses

**Total Entries**: 42 LangSmith entries (good + poor response for each scenario)

### 3. Baseline Evaluation

Establishes quality benchmarks by running all 7 evaluators against the current coach.

**Expected Results**:
```
Problem Significance: 0.72 (σ²=0.045)
Task Concretization: 0.65 (σ²=0.082)  
Solution Diversity: 0.58 (σ²=0.124)
Crux Identification: 0.81 (σ²=0.031)
Crux Solution: 0.69 (σ²=0.067)
Belief System: 0.74 (σ²=0.052)
Non-Directive Style: 0.88 (σ²=0.021)
```

### 4. CI Integration

GitHub Action that runs on PRs labeled with `eval-impact`:

- Runs all 7 evaluators against current coach
- Compares scores to baseline (5% regression threshold)
- Posts detailed results as PR comment
- Blocks merge if significant regressions detected

## Usage

### Initial Setup

1. **Set API Keys** (required):
```bash
# Add to .env file
LANGSMITH_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

2. **Upload Dataset**:
```bash
python scripts/upload_evaluation_dataset.py
```

3. **Generate Baseline**:
```bash
python scripts/run_baseline_eval.py
```

### Testing Locally

**Full Local Test**:
```bash
python scripts/test_evaluation_locally.py
```

**Manual CI Check**:
```bash
python scripts/ci_eval_check.py
```

### Using in Development

1. **For PRs that might affect coaching behavior**, add the `eval-impact` label
2. **CI will automatically run evaluation** and post results
3. **Review results** before merging if regressions detected

## Files Structure

```
diary-coach/
├── src/evaluation/
│   ├── langsmith_evaluators.py      # LangSmith evaluator wrappers
│   └── dataset_generator.py         # Conversation scenario generator
├── scripts/
│   ├── upload_evaluation_dataset.py # Upload dataset to LangSmith
│   ├── run_baseline_eval.py        # Generate baseline scores
│   ├── ci_eval_check.py            # CI regression detection
│   └── test_evaluation_locally.py  # Local testing helper
├── .github/workflows/
│   └── coaching-quality-gate.yml   # GitHub Action for CI
├── baseline_scores.json            # Baseline scores for comparison
└── docs/
    └── evaluation_system_guide.md  # This guide
```

## Interpreting Results

### Score Scale
- **0.8-1.0**: Excellent coaching
- **0.6-0.8**: Good coaching  
- **0.4-0.6**: Needs improvement
- **0.0-0.4**: Poor coaching

### Regression Detection
- **Threshold**: 5% drop from baseline
- **Green (🟢)**: Improved or maintained quality
- **Yellow (🟡)**: Stable within threshold
- **Red (🔴)**: Regression detected - review required

### CI Comment Format
```
🎯 Coaching Quality Check

✅ QUALITY MAINTAINED - No significant regressions detected

| Metric | Baseline | Current | Change | Status |
|--------|----------|---------|--------|--------|
| Problem Significance | 0.720 | 0.735 | +0.015 (+2.1%) | 🟢 IMPROVED |
| Task Concretization | 0.650 | 0.648 | -0.002 (-0.3%) | 🟡 STABLE |
...
```

## Troubleshooting

### Common Issues

1. **"Dataset not found"**:
   - Run `python scripts/upload_evaluation_dataset.py`
   - Check LangSmith project settings

2. **"Baseline scores not found"**:
   - Run `python scripts/run_baseline_eval.py`
   - Ensure baseline_scores.json exists

3. **API Authentication Errors**:
   - Verify LANGSMITH_API_KEY and ANTHROPIC_API_KEY
   - Check .env file configuration

4. **Coach Errors in Evaluation**:
   - Test coach functionality manually first
   - Check for missing dependencies or configuration

### Updating the System

**Add New Evaluation Scenarios**:
1. Edit `src/evaluation/dataset_generator.py`
2. Run `python scripts/upload_evaluation_dataset.py`
3. Re-run baseline: `python scripts/run_baseline_eval.py`

**Change Regression Threshold**:
1. Edit `REGRESSION_THRESHOLD` in `scripts/ci_eval_check.py`
2. Update documentation accordingly

**Add New Evaluation Dimensions**:
1. Create new evaluator in `src/evaluation/langsmith_evaluators.py`
2. Add scenarios in `dataset_generator.py`
3. Update registry and documentation

## Cost Considerations

- **Each CI run costs ~$0.50-1.00** (42 evaluations × cheap LLM)
- **Use `eval-impact` label selectively** - only for PRs that might affect coaching
- **Monitor LangSmith usage** through dashboard
- **Consider reducing dataset size** if costs become prohibitive

## Integration with Development Workflow

### When to Use `eval-impact` Label

**Use for PRs that change**:
- Coach prompts or behavior
- Evaluation logic
- LLM model or parameters
- Core coaching algorithms

**Don't use for PRs that only change**:
- Documentation
- Tests (unless evaluation tests)
- Infrastructure unrelated to coaching
- UI/CLI improvements

### Handling Regressions

1. **Review the specific metrics** that regressed
2. **Test coaching conversations manually** to validate
3. **Consider if regression is acceptable** for the intended changes
4. **Update baseline if intentional** behavior change
5. **Fix coaching logic** if unintended regression

## Future Enhancements

- **Adaptive thresholds** based on metric variance
- **Trend analysis** across multiple evaluations  
- **Custom evaluation scenarios** for specific features
- **Integration with monitoring** for production coaching quality
- **Automated baseline updates** when improvements are validated
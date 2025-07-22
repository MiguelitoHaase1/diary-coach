# Evaluation Experiments Documentation

## Overview

The diary-coach system tracks coaching quality through LangSmith experiments in two ways:

1. **Manual Prototype Runs**: Every time you run the multi-agent CLI manually, the evaluation is sent to LangSmith as an experiment
2. **Automated Evaluation**: Scripts simulate user interactions and evaluate the coaching quality

## How It Works

### Manual Prototype Runs

When you run `python -m src.interface.multi_agent_cli` and generate a Deep Thoughts report:

1. The conversation is processed by the Reporter Agent (Deep Thoughts)
2. The Evaluator Agent assesses the conversation using 5 criteria:
   - A: Problem Definition (binary)
   - B: Crux Recognition (binary)
   - C: Today Accomplishment (binary)
   - D: Multiple Paths (0-1 scale)
   - E: Core Beliefs (0-1 scale)
3. Results are sent to LangSmith as:
   - An experiment run named `manual_coaching_session_[timestamp]`
   - Individual feedback scores for each criterion
   - Overall effectiveness score

### Automated Evaluation

Run automated experiments with: `python scripts/run_automated_eval_experiment.py`

This script:
1. Uses LLM to simulate realistic user personas
2. Runs complete coaching sessions (4-6 turns)
3. Generates Deep Thoughts reports
4. Evaluates using the same 5 criteria
5. Sends results to LangSmith experiments

### Test Scenarios

The automated evaluation includes 5 scenarios:
- **productivity_challenge**: Overwhelmed professional
- **leadership_growth**: New team lead struggling with delegation
- **work_life_balance**: Burnout from overwork
- **career_transition**: Considering career change
- **team_conflict**: Manager dealing with team tensions

## Viewing Results in LangSmith

1. Go to your LangSmith dashboard
2. Look for project: `diary-coach-evaluations` (or your LANGSMITH_PROJECT env var)
3. Filter by:
   - Manual sessions: `is_manual_session: true`
   - Automated: Look for experiment names with scenarios

## Evaluation Metrics

Each session is scored on:
- **Overall Effectiveness**: Weighted average (A,B,C = 25% each, D,E = 12.5% each)
- **Individual Criteria**: Each criterion has its own score and reasoning

## Running Experiments

### Manual Testing
```bash
# Run the CLI
python -m src.interface.multi_agent_cli

# Have a conversation
# Type 'deep report' to trigger evaluation
# Check LangSmith for results
```

### Automated Testing
```bash
# Run all test scenarios
python scripts/run_automated_eval_experiment.py

# Results saved to: evaluation_results/automated_eval_[timestamp].json
# Also sent to LangSmith
```

### Regression Testing
```bash
# Compare against baseline
python scripts/run_baseline_eval.py
```

## Environment Variables

Required for LangSmith integration:
- `LANGSMITH_API_KEY`: Your LangSmith API key
- `LANGSMITH_PROJECT`: Project name (default: "diary-coach-evaluations")

## Best Practices

1. **Track Changes**: Run automated evals before and after major changes
2. **Monitor Trends**: Use LangSmith to track score trends over time
3. **Investigate Drops**: If scores drop, check the evaluation reasoning
4. **Balanced Scenarios**: Test various user personas and problems
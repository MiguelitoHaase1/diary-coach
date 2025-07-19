# Test Configuration Update

## Overview
Updated the test configuration to exclude evaluation tests that use personas and simulations, as these are now handled within the deep think report system.

## Changes Made

### 1. Updated pytest Configuration
- Modified `pytest.ini` to mark evaluation tests and exclude them by default
- Updated `pyproject.toml` to ignore the `tests/evaluation/` directory
- Tests now run without the evaluation suite by default

### 2. Fixed Syntax Errors
- Fixed 13 syntax errors in `tests/agents/test_coach_agent.py`
- All were missing closing parentheses in `AgentRequest` constructor calls

### 3. Created Test Scripts
- `scripts/run_tests.py` - Run all tests except evaluation tests
- `scripts/run_smoke_tests.py` - Run only smoke tests for quick verification

## Test Results
- **Total Tests**: 269 (excluding evaluation tests)
- **Passing**: 200 tests
- **Failing**: 69 tests (pre-existing failures, not related to this change)
- **Evaluation Tests**: Successfully excluded from default test runs

## Running Tests

### Run all tests (excluding evaluation):
```bash
python scripts/run_tests.py
# or
pytest tests/ --ignore=tests/evaluation/
```

### Run only smoke tests:
```bash
python scripts/run_smoke_tests.py
# or
pytest -m smoke
```

### Run evaluation tests explicitly (if needed):
```bash
pytest tests/evaluation/ -v
```

## Rationale
The evaluation tests with personas and simulations are no longer needed as separate test suites because:
1. Evaluations are now integrated into the deep think report system
2. The persona simulations were creating unnecessary test complexity
3. LangSmith integration provides better real-world evaluation data

## Next Steps
- Continue to use deep think reports for evaluation
- Monitor test failures in the remaining test suite
- Consider removing the evaluation test files entirely if they're not needed
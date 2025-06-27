# Session 2: Behavioral Change Detection Framework

## Executive Summary

Build an automated evaluation framework that measures a coach's ability to create transformation opportunities. Focus on three core metrics: specificity pressure, effective challenges, and commitment extraction. Use TDD to build analyzers that work without user input, then validate with simulated resistant personas.

**Core Belief**: Great coaching helps users self-realize insights that change their behavior. We measure the *potential* for this transformation.

## Learning Objectives

1. **Build** coach behavior analyzers using TDD principles
2. **Create** transformation scoring that predicts real behavior change
3. **Implement** basic simulated personas for testing
4. **Integrate** evaluation into the existing event system
5. **Practice** async testing patterns with mocked APIs

## Why These Metrics Matter

### Wrong Approach ❌
```python
# Measures surface-level conversation quality
score = count_empathy_words(response) + question_count(response)
```

### Right Approach ✅
```python
# Measures transformation catalysts
score = specificity_pressure(response) + belief_challenges(response)
```

## Implementation Plan: 7 Increments

### Increment 2.1: Specificity Analyzer
**Goal**: Detect when coaches push for concrete commitments

```python
# Test first (failing)
def test_detects_specificity_pressure():
    analyzer = SpecificityAnalyzer()
    vague = "Maybe try exercising more?"
    specific = "What specific exercise will you do tomorrow at 7am?"
    
    assert analyzer.score(vague) < 0.3
    assert analyzer.score(specific) > 0.7
```

### Increment 2.2: Challenge Detector
**Goal**: Identify assumption questioning

```python
# Test first (failing)
def test_detects_belief_challenges():
    detector = ChallengeDetector()
    weak = "That sounds difficult"
    strong = "You said 'impossible' - what would make it merely difficult?"
    
    assert detector.score(weak) < 0.3
    assert detector.score(strong) > 0.7
```

### Increment 2.3: Commitment Tracker
**Goal**: Measure action-securing attempts

```python
# Test first (failing)
def test_tracks_commitment_extraction():
    tracker = CommitmentTracker()
    weak = "Think about going to the gym"
    strong = "Will you commit to a 10-minute walk tomorrow at lunch?"
    
    assert tracker.score(weak) < 0.3
    assert tracker.score(strong) > 0.8
```

### Increment 2.4: Transformation Scorer
**Goal**: Combine metrics into breakthrough potential

```python
# Test first (failing)
def test_calculates_transformation_potential():
    scorer = TransformationScorer()
    
    weak_coaching = {"specificity": 0.2, "challenge": 0.1, "commitment": 0.2}
    strong_coaching = {"specificity": 0.8, "challenge": 0.7, "commitment": 0.9}
    
    assert scorer.calculate(weak_coaching) < 0.3
    assert scorer.calculate(strong_coaching) > 0.7
```

### Increment 2.5: Base Persona Framework
**Goal**: Foundation for simulated users

```python
# Test first (failing)
async def test_persona_maintains_character():
    persona = ResistantPersona(trait="vague")
    response = await persona.respond("Be specific about your goals")
    
    assert "maybe" in response.lower() or "sometime" in response.lower()
    assert len(response) > 20
```

### Increment 2.6: Evaluation Integration
**Goal**: Connect to event system

```python
# Test first (failing)
async def test_publishes_evaluation_events():
    bus = InMemoryEventBus()
    evaluator = CoachEvaluator(bus)
    
    await evaluator.analyze(coach_response)
    events = await bus.get_events("coaching.evaluated")
    
    assert len(events) == 1
    assert events[0].transformation_score > 0
```

### Increment 2.7: Validation Suite
**Goal**: End-to-end coach testing

```python
# Test first (failing)
async def test_validates_coach_effectiveness():
    validator = CoachValidator()
    coach = BasicCoach()
    
    results = await validator.test_with_personas(coach, turns=3)
    
    assert results.average_transformation_score > 0.5
    assert results.resistant_user_breakthrough_rate > 0.2
```

## File Structure

```
src/evaluation/
├── analyzers.py      # All 3 analyzers in one file
├── scoring.py        # Transformation score calculation
├── personas.py       # Base persona + one example
└── validator.py      # Coach testing framework

tests/evaluation/
├── test_analyzers.py
├── test_scoring.py
├── test_personas.py
└── test_validator.py
```

## Key Patterns to Learn

### 1. TDD Rhythm
```python
# Step 1: Write failing test
# Step 2: Minimal code to pass
# Step 3: Refactor with confidence
```

### 2. Async Testing
```python
@pytest.mark.asyncio
async def test_async_behavior():
    result = await async_function()
    assert result.is_valid()
```

### 3. Mock Strategies
```python
# Mock expensive API calls
with patch('anthropic.Anthropic') as mock_claude:
    mock_claude.return_value.complete.return_value = "mocked response"
```

## Session Success Criteria

### Must Complete ✅
- [ ] 15+ tests written and passing
- [ ] 3 behavior analyzers implemented
- [ ] Basic transformation scoring working
- [ ] At least 1 persona for testing
- [ ] Integration with event system

### Stretch Goals 🎯
- [ ] Multiple persona types
- [ ] Visual score debugging
- [ ] Coach comparison metrics

## Learning Focus Areas

Based on your learning_ledger.md:

1. **TDD Practice**: Every feature starts with a failing test
2. **Async Patterns**: Mock API calls, handle concurrent operations
3. **Evaluation Design**: Metrics that predict real outcomes
4. **Python Organization**: Clean module structure with clear interfaces

## Common Pitfalls to Avoid

1. **Don't**: Build complex NLP - use simple keyword patterns
2. **Don't**: Create perfect personas - basic resistance is enough
3. **Don't**: Over-engineer scores - start with simple weighted averages
4. **Don't**: Skip tests - TDD discipline is critical

## Next Session Preview

Session 3 will use these evaluation metrics to build an intelligent Orchestrator that:
- Routes based on transformation readiness
- Manages conversation state
- Optimizes for breakthrough moments

---

**Remember**: We're measuring coaching that creates conditions for self-realization, not conversation quality. Keep it simple, test everything, and focus on transformation potential.
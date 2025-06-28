# Session 2: Behavioral Change Detection Framework

## Executive Summary

Build an automated evaluation framework that measures a coach's ability to create transformation opportunities through pattern analysis, not keyword matching. Use Claude to analyze coaching moves for their transformation potential, then validate with simulated resistant personas based on common product manager patterns. **Enhancement**: Validate framework against real functional requirements like morning/evening coaching rituals.

**Core Belief**: Great coaching helps users self-realize insights that change their behavior. We measure coaching *moves* and their potential impact, validated through concrete user experiences.

## Learning Objectives

1. **Build** LLM-powered coach behavior analyzers using TDD
2. **Create** transformation scoring based on coaching patterns
3. **Implement** Claude-powered resistant personas for validation
4. **Integrate** evaluation into the existing event system
5. **Practice** async testing with mocked LLM calls
6. **Validate** against real functional requirements (morning/evening flows)

## Why Pattern Analysis Matters

### Wrong Approach ❌
```python
# Keyword matching - too simplistic
if "specific" in response or "what time" in response:
    return high_score  # Misses nuanced coaching
```

### Right Approach ✅
```python
# LLM analyzes the coaching move's impact
coaching_move = extract_coaching_pattern(response, context)
transformation_potential = await claude.analyze_move_impact(coaching_move)
```

## How Scoring Actually Works

### The Three-Layer Analysis

1. **Coaching Move Extraction**: Identify what the coach is trying to do
2. **Impact Analysis**: Use Claude to assess transformation potential
3. **Pattern Scoring**: Weight different moves by their effectiveness
4. **Functional Validation**: Test against real user requirements

```python
# Example: Framework Disruption Analysis
async def analyze_framework_disruption(coach_response, conversation_context):
    prompt = f"""
    Analyze this coaching response for framework disruption.
    
    Context: {conversation_context}
    Coach said: {coach_response}
    
    Score 0-1 based on:
    - Does coach challenge the user's existing mental models?
    - Are there questions that create productive confusion?
    - Does coach resist neat categorization of messy experiences?
    
    Return JSON: {"score": float, "reasoning": str}
    """
    
    result = await claude.complete(prompt)
    return json.loads(result)
```

## Implementation Plan: 10 Increments

### Increment 2.1: Coaching Move Extractor
**Goal**: Identify coaching patterns in context

```python
# Test first (failing)
async def test_extracts_coaching_moves():
    extractor = CoachingMoveExtractor()
    
    context = ["User: I've mapped out a 5-phase approach to this problem", 
               "Coach: What happens when you put down the map?"]
    
    moves = await extractor.extract_moves(context)
    
    assert "framework_challenge" in moves[0].type
    assert moves[0].target == "rigid_structure"
    assert moves[0].technique == "letting_go_invitation"
```

### Increment 2.2: Framework Disruption Analyzer
**Goal**: Analyze how coach challenges over-structuring

```python
# Test first (failing)
async def test_analyzes_framework_disruption():
    analyzer = FrameworkDisruptionAnalyzer()
    
    # Reinforces framework
    context1 = ["User: I've designed a RACI matrix for my personal goals"]
    coach1 = "That's a thorough approach! Have you assigned all the roles?"
    
    # Disrupts framework
    context2 = ["User: I've designed a RACI matrix for my personal goals"]
    coach2 = "I'm curious - what would happen if you threw away the matrix and just started with what scares you most?"
    
    score1 = await analyzer.analyze(coach1, context1)
    score2 = await analyzer.analyze(coach2, context2)
    
    assert score1.score < 0.3
    assert score2.score > 0.7
    assert "reinforces structure" in score1.reasoning
    assert "invites direct experience" in score2.reasoning
```

### Increment 2.3: Control Release Analyzer
**Goal**: Assess how coach handles perfectionism

```python
# Test first (failing)
async def test_analyzes_control_release():
    analyzer = ControlReleaseAnalyzer()
    
    # Enables perfectionism
    context1 = ["User: I need to craft the perfect message before sending"]
    coach1 = "What elements would make it perfect?"
    
    # Challenges control
    context2 = ["User: I need to craft the perfect message before sending"]
    coach2 = "What if you sent a messy, honest version right now - typos and all? What's the worst that could actually happen?"
    
    score1 = await analyzer.analyze(coach1, context1)
    score2 = await analyzer.analyze(coach2, context2)
    
    assert score1.score < 0.3
    assert score2.score > 0.7
    assert "action over perfection" in score2.reasoning
```

### Increment 2.4: Present-Moment Analyzer
**Goal**: Measure coaching that grounds in current experience

```python
# Test first (failing)
async def test_analyzes_present_grounding():
    analyzer = PresentMomentAnalyzer()
    
    # Future-focused deflection
    context1 = ["User: This failure will help me grow long-term"]
    coach1 = "How will you use this learning going forward?"
    
    # Present-moment invitation
    context2 = ["User: This failure will help me grow long-term"]
    coach2 = "Before we get to growth - can you stay with how this failure feels right now? What's happening in your body?"
    
    score1 = await analyzer.analyze(coach1, context1)
    score2 = await analyzer.analyze(coach2, context2)
    
    assert score1.score < 0.4
    assert score2.score > 0.8
    assert "somatic awareness" in score2.reasoning
    assert "emotional processing" in score2.reasoning
```

### Increment 2.5: Morning Activation Validator
**Goal**: Test the morning greeting functional requirement

```python
# Test first (failing)
async def test_morning_activation_variety():
    validator = MorningActivationValidator()
    
    # Collect 5 morning greetings
    greetings = []
    for _ in range(5):
        response = await validator.generate_morning_greeting("Michael")
        greetings.append(response)
    
    # Functional requirements validation
    assert all("Michael" in g for g in greetings)  # Uses name
    assert all(validator.asks_about_priority(g) for g in greetings)  # Asks about problem
    assert len(set(greetings)) == 5  # All unique (variety)
    
    # Non-functional requirements
    humor_scores = [validator.humor_level(g) for g in greetings]
    assert all(score > 0.6 for score in humor_scores)  # Humorous
    
    # No template used >20% (testing with larger sample)
    template_usage = validator.analyze_template_patterns(greetings)
    assert max(template_usage.values()) <= 0.2
```

### Increment 2.6: Evening Story Harvester Validator
**Goal**: Test the evening reflection functional requirement

```python
# Test first (failing)
async def test_evening_story_harvesting():
    validator = EveningStoryValidator()
    
    # Setup: User had morning goal
    morning_context = ["User: good morning", 
                      "Coach: Morning Michael! What dragon shall we slay today?",
                      "User: Need to have difficult conversation with my team lead"]
    
    # Evening interaction
    evening_response = await validator.generate_evening_prompt(
        user_name="Michael",
        morning_context=morning_context
    )
    
    # Must reference the morning problem
    assert validator.references_morning_goal(evening_response, morning_context)
    
    # Must ask for specific moments
    assert validator.asks_for_concrete_moment(evening_response)
    
    # Must be creative/witty (not robotic)
    creativity_score = validator.assess_creativity(evening_response)
    assert creativity_score > 0.7
```

### Increment 2.7: Performance Metrics Tracker
**Goal**: Implement non-functional requirement tracking

```python
# Test first (failing)
async def test_tracks_performance_metrics():
    tracker = PerformanceMetricsTracker()
    
    # Simulate 10 responses with varying times
    response_times = [1.8, 2.1, 1.5, 1.9, 2.5, 1.7, 1.6, 2.3, 1.4, 1.8]
    for time in response_times:
        await tracker.record_response_time(time)
    
    # 80% should be under 2 seconds
    assert tracker.get_percentile(80) <= 2.0
    assert tracker.responses_under_2s_percentage() >= 0.8
    
    # Track variety scores
    variety_scores = await tracker.calculate_template_variety(last_n=10)
    assert variety_scores.max_template_usage < 0.2
```

### Increment 2.8: Transformation Scorer
**Goal**: Combine analyses into breakthrough potential

```python
# Test first (failing)
async def test_calculates_transformation_score():
    scorer = TransformationScorer()
    
    # Full coaching response analysis
    coaching_response = "What would happen if you stopped planning and just felt this discomfort?"
    context = ["User: I'm designing a framework to process this setback"]
    
    score = await scorer.score_response(coaching_response, context)
    
    assert score.total > 0.6
    assert score.breakdown["framework_disruption"] > 0.7
    assert score.breakdown["present_grounding"] > 0.6
    assert score.prediction in ["likely", "possible", "unlikely"]
```

### Increment 2.9: Product Manager Persona Implementation
**Goal**: Claude-powered test users with PM-specific resistance patterns

```python
# Test first (failing)
async def test_framework_rigid_persona():
    rigid = FrameworkRigidPersona()
    
    # Should absorb challenge into framework
    coach_q = "What if you threw away your model?"
    response = await rigid.respond(coach_q)
    
    assert rigid.measures_absorption(response) > 0.7
    assert "actually" in response.lower() or "framework" in response.lower()
    
    # Should track resistance breakdown
    assert rigid.resistance_level == 0.8
    assert rigid.breakthrough_threshold == 4  # needs sustained disruption
```

### Increment 2.10: Integrated Functional Requirements Suite
**Goal**: Test complete coaching flows against all requirements

```python
# Test first (failing)
async def test_full_day_coaching_cycle():
    suite = FunctionalRequirementsSuite()
    coach = IntegratedCoach(user_name="Michael")
    
    # Morning flow
    morning_response = await coach.handle_message("good morning")
    morning_validation = await suite.validate_morning_activation(morning_response)
    assert morning_validation.passes_all_requirements()
    
    # Simulate day activities...
    
    # Evening flow  
    evening_response = await coach.handle_message("good evening")
    evening_validation = await suite.validate_evening_harvesting(
        evening_response, 
        morning_context=morning_validation.context
    )
    assert evening_validation.passes_all_requirements()
    
    # Non-functional validation
    perf_metrics = await suite.get_performance_metrics()
    assert perf_metrics.response_time_p80 < 2.0
    assert perf_metrics.variety_score > 0.8
    assert perf_metrics.memory_reference_quality > 0.6
```

## Mocking Strategy for Tests

```python
# Mock Claude API calls with PM-aware responses
@pytest.fixture
def mock_claude():
    with patch('anthropic.Anthropic') as mock:
        # Return different responses based on input
        def smart_complete(prompt):
            if "analyze" in prompt and "framework" in prompt:
                if "throw away" in prompt.lower():
                    return '{"score": 0.8, "reasoning": "Directly challenges structured thinking"}'
                else:
                    return '{"score": 0.3, "reasoning": "Reinforces systematic approach"}'
            elif "morning greeting" in prompt:
                greetings = [
                    "Morning Michael! What dragon needs slaying today?",
                    "Hey Michael! Ready to tackle that one thing that's been lurking?",
                    "Michael! The universe awaits - what's the quest for today?"
                ]
                return random.choice(greetings)
        
        mock.return_value.complete.side_effect = smart_complete
        yield mock
```

## Key Implementation Details

### 1. Coaching Move Taxonomy
```python
COACHING_MOVES = {
    "framework_disruption": ["model_challenge", "confusion_invitation", "structure_release"],
    "control_release": ["perfectionism_interrupt", "messy_action", "ambiguity_tolerance"],
    "present_grounding": ["somatic_check", "emotion_staying", "future_pause"],
    "ritual_activation": ["morning_energizer", "evening_reflection", "transition_marker"]
}
```

### 2. Functional Requirements Validators
```python
FUNCTIONAL_REQUIREMENTS = {
    "morning_activation": {
        "trigger": "good morning",
        "must_include": ["user_name", "priority_question"],
        "qualities": ["humor", "variety", "optimism"],
        "anti_patterns": ["same_template", "generic_greeting"]
    },
    "evening_story": {
        "trigger": "good evening", 
        "must_include": ["morning_reference", "moment_request"],
        "qualities": ["creativity", "specificity", "wit"],
        "anti_patterns": ["vague_summary", "no_callback"]
    }
}
```

### 3. Non-Functional Metrics
```python
NON_FUNCTIONAL_METRICS = {
    "response_time": {
        "target": "80% < 2s",
        "measurement": "percentile",
        "alert_threshold": 0.7
    },
    "variety_score": {
        "target": "no_template > 20%",
        "measurement": "template_frequency",
        "window": 10
    },
    "memory_span": {
        "target": "relevant_references",
        "measurement": "context_quality",
        "lookback": "all_conversations"
    }
}
```

### 4. PM Persona Resistance Patterns
```python
RESISTANCE_PATTERNS = {
    "framework_rigid": {
        "triggers": ["messy", "intuitive", "just try"],
        "responses": ["Actually, I think a structured approach...", "Let me model this properly..."],
        "breakthrough_signs": ["Maybe I'm overthinking", "You're right, I'm hiding behind the framework"]
    },
    "control_freak": {
        "triggers": ["delegate", "trust others", "good enough"],
        "responses": ["But if I don't specify exactly...", "I just need to wordsmith this a bit more..."],
        "breakthrough_signs": ["I could just ship it", "Perfect is the enemy of done"]
    },
    "legacy_builder": {
        "triggers": ["right now", "how does this feel", "stay with the discomfort"],
        "responses": ["This will make me stronger...", "In the long run, this teaches me..."],
        "breakthrough_signs": ["This hurts right now", "I'm avoiding feeling this"]
    }
}
```

## File Structure

```
src/evaluation/
├── analyzers.py          # All 3 analyzers in one file
├── scoring.py            # Transformation score calculation
├── personas.py           # Base persona + PM personas
├── validator.py          # Coach testing framework
├── functional_reqs.py    # Morning/Evening validators
└── performance.py        # Non-functional metrics tracking

tests/evaluation/
├── test_analyzers.py
├── test_scoring.py
├── test_personas.py
├── test_validator.py
├── test_functional_reqs.py
└── test_performance.py
```

## Session Success Criteria

### Must Complete ✅
- [ ] 30+ tests written using mocked LLM calls
- [ ] 3 LLM-powered analyzers (not keyword matching)
- [ ] Transformation scoring with breakdown
- [ ] 1 PM persona with measurable behaviors
- [ ] Morning/Evening functional requirement validators
- [ ] Performance metrics tracking (response time, variety)
- [ ] Integration tests with event system

### Stretch Goals 🎯
- [ ] All 3 PM persona types implemented
- [ ] Full conversation memory analysis
- [ ] Resistance pattern visualization
- [ ] Coaching move effectiveness library
- [ ] Complete non-functional metrics dashboard

## Common Pitfalls to Avoid

1. **Don't**: Make personas caricatures - they should feel authentic
2. **Don't**: Over-complicate prompts - clear criteria get better analysis
3. **Don't**: Skip mocking - real API calls in tests are expensive/slow
4. **Don't**: Forget TDD discipline - write the test first, always
5. **Don't**: Test requirements in isolation - validate full conversations

## Learning Focus Areas

Based on your learning_ledger.md:

1. **TDD Practice**: Every analyzer starts with a failing test
2. **Async Testing**: Mock LLM calls properly with pytest fixtures
3. **Context Engineering**: Craft prompts that get consistent analysis
4. **Evaluation Design**: Metrics that predict real behavior change
5. **Requirements Testing**: Validate complete user experiences

## Next Session Preview

Session 3 will build the Orchestrator that uses these metrics to:
- Route conversations based on transformation readiness
- Detect breakthrough moments in real-time
- Adapt coaching strategies based on resistance patterns
- Optimize for both functional and non-functional requirements

---

*Remember: The goal isn't to break people's frameworks, but to help them recognize when their strengths become limitations. And to make mornings exciting!*
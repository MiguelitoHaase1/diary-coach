# Session 3: Behavioral Change Detection Framework

## Executive Summary

Build an automated evaluation framework that measures your real coach's transformative potential through conversation analysis. Generate 20+ real conversations with your working prototype, identify coaching weaknesses, and create metrics that drive meaningful improvements. This session transforms your minimal prototype into a self-improving system through data-driven analysis.

**Core Innovation**: Use your existing coach to generate real conversation data, then build evaluation metrics based on observed patterns rather than theoretical ideals.

## Current State (from Session 2)

You have a **working diary coach** that:
- ✅ Conducts real conversations with Michael's coaching personality
- ✅ Handles morning/evening rituals with context
- ✅ Saves conversations as JSON with metadata
- ✅ Tracks token usage and costs
- ✅ Works through a CLI interface

## Session 3 Goals

Transform this working system into a **self-evaluating coach** that:
1. **Measures** its own coaching effectiveness
2. **Identifies** specific behavioral weaknesses
3. **Quantifies** transformation potential
4. **Tracks** response performance (target: <1s for 80%)
5. **Captures** human feedback and AI reflections

## Implementation Plan: 5 Major Increments

### Increment 3.1: Enhanced CLI with Evaluation Reports (45 mins)
**Goal**: Modify CLI to capture evaluation data, performance metrics, and user feedback

```python
# Test first (failing)
async def test_cli_evaluation_mode():
    cli = EnhancedCLI()
    
    # Simulate conversation
    await cli.process_input("good morning")
    await cli.process_input("I need to finish my product roadmap")
    await cli.process_input("stop")
    
    # Should display evaluation report
    output = cli.get_last_output()
    assert "Conversation Evaluation" in output
    assert "Total Cost:" in output
    assert "Coaching Effectiveness:" in output
    assert "Response Speed:" in output
    assert "Add notes:" in output
```

**Key Changes**:
- Remove per-message cost display
- Add evaluation summary on "stop"
- Include response time percentiles
- Prompt for user notes
- Generate eval report on "report" command

### Increment 3.2: Coaching Behavior Analyzers (1.5 hours)
**Goal**: Build LLM-powered analyzers for key coaching patterns

```python
# Test first (failing)
async def test_specificity_push_analyzer():
    analyzer = SpecificityPushAnalyzer()
    
    # Weak coaching - accepts vague goals
    context = ["User: I want to be more productive"]
    response = "That's a great goal! How can I help you achieve that?"
    
    score = await analyzer.analyze(response, context)
    assert score.value < 0.3
    assert "accepts vague goal" in score.reasoning
    
    # Strong coaching - pushes for specifics
    response2 = "Productive is a big word. What's one specific thing you'd do differently if you were 'productive' today?"
    score2 = await analyzer.analyze(response2, context)
    assert score2.value > 0.7
    assert "challenges vagueness" in score2.reasoning
```

**Analyzer Suite**:
1. **SpecificityPushAnalyzer**: Does coach challenge vague statements?
2. **ActionOrientationAnalyzer**: Does coach drive toward concrete actions?
3. **EmotionalPresenceAnalyzer**: Does coach acknowledge feelings?
4. **FrameworkDisruptionAnalyzer**: Does coach prevent over-structuring?

### Increment 3.3: Product Manager Personas & Conversation Generator (1.5 hours)
**Goal**: Generate conversations using PM-specific resistance patterns

```python
# Test first (failing)
async def test_pm_persona_conversations():
    generator = ConversationGenerator(coach=existing_coach)
    
    # Test with Framework Rigid persona
    framework_rigid = FrameworkRigidPersona()
    convo1 = await generator.generate_conversation(
        persona=framework_rigid,
        scenario="morning_goal_setting",
        min_exchanges=5
    )
    
    # Should see resistance patterns
    assert any("structured approach" in msg for msg in convo1.messages)
    assert framework_rigid.resistance_level > 0.7
    
    # Test with Control Freak persona
    control_freak = ControlFreakPersona()
    convo2 = await generator.generate_conversation(
        persona=control_freak,
        scenario="evening_reflection",
        min_exchanges=5
    )
    
    assert any("perfect" in msg.lower() for msg in convo2.messages)
```

**PM Persona Types** (from old Session 3):
1. **Framework Rigid**: Over-structures everything, absorbs challenges into more frameworks
2. **Control Freak**: Perfectionist, needs to control every detail
3. **Legacy Builder**: Deflects to future impact, avoids present feelings

### Increment 3.4: Performance Tracking & Evaluation Reporter (1.5 hours)
**Goal**: Create comprehensive evaluation reports with performance metrics

```python
# Test first (failing)
async def test_evaluation_with_performance():
    reporter = EvaluationReporter()
    
    # Analyze conversation with timing data
    conversation = load_conversation("test_convo.json")
    report = await reporter.generate_report(
        conversation=conversation,
        user_notes="Coach was too accepting of my vague goals",
        analyzers=[specificity_analyzer, action_analyzer]
    )
    
    # Performance metrics
    assert report.response_times_ms is not None
    assert report.percentile_80 < 1000  # Under 1 second
    assert report.responses_under_1s_percentage >= 0.8
    
    # Behavioral scores
    assert report.overall_score between 0 and 1
    assert len(report.behavioral_scores) == 2
    
    # Save as markdown
    report.save_as_markdown("docs/prototype/eval_1.md")
    assert os.path.exists("docs/prototype/eval_1.md")
```

**Report Contents**:
```markdown
# Coaching Evaluation Report #1

## Summary
- **Date**: 2025-06-29 10:30 AM
- **Duration**: 5 messages
- **Total Cost**: $0.0234
- **Overall Effectiveness**: 6.5/10

## Performance Metrics
- **Median Response Time**: 847ms ✅
- **80th Percentile**: 923ms ✅
- **Responses Under 1s**: 85% ✅
- **Slowest Response**: 1.2s (message 3)

## Behavioral Analysis
### Specificity Push: 4/10
- Coach accepted vague goals without challenging
- Missed 3 opportunities to ask for concrete details

### Action Orientation: 7/10
- Good focus on next steps
- Could push harder for commitment

## User Notes
"Coach was too accepting of my vague goals"

## AI Reflection
Based on this conversation, I notice I'm being too agreeable...

## Improvement Suggestions
1. Challenge vague statements like "be productive"
2. Ask for specific, measurable commitments
3. Maintain response speed while adding depth
```

### Increment 3.5: Integration with PM Personas Testing (1 hour)
**Goal**: Test coaching effectiveness against different PM resistance patterns

```python
# Test first (failing)
async def test_coaching_vs_personas():
    evaluator = PersonaEvaluator()
    
    # Generate conversations with each persona
    results = {}
    for persona_type in ["framework_rigid", "control_freak", "legacy_builder"]:
        persona = create_persona(persona_type)
        
        # Run multiple conversations
        conversations = await evaluator.test_coach_with_persona(
            coach=existing_coach,
            persona=persona,
            num_conversations=5
        )
        
        # Analyze breakthrough potential
        results[persona_type] = {
            "avg_breakthrough_score": evaluator.measure_breakthrough_potential(conversations),
            "resistance_patterns": evaluator.identify_resistance_patterns(conversations),
            "effective_interventions": evaluator.find_effective_moves(conversations)
        }
    
    # Framework Rigid should be hardest to breakthrough
    assert results["framework_rigid"]["avg_breakthrough_score"] < 0.4
    assert "model absorption" in results["framework_rigid"]["resistance_patterns"]
```

## File Structure Updates

```
src/evaluation/
├── analyzers/
│   ├── __init__.py
│   ├── base.py              # Base analyzer interface
│   ├── specificity.py       # Specificity push analyzer
│   ├── action.py            # Action orientation analyzer
│   ├── emotional.py         # Emotional presence analyzer
│   └── framework.py         # Framework disruption analyzer
├── personas/
│   ├── __init__.py
│   ├── base.py              # Base PM persona
│   ├── framework_rigid.py   # Over-structuring persona
│   ├── control_freak.py     # Perfectionist persona
│   └── legacy_builder.py    # Future-focused persona
├── reporting/
│   ├── __init__.py
│   ├── reporter.py          # Report generator
│   ├── templates.py         # Markdown templates
│   └── metrics.py           # Score & performance calculations
└── generator.py             # Conversation generator

src/interface/
└── cli.py                   # Enhanced with evaluation mode

docs/prototype/              # New folder for evaluation reports
├── eval_1.md
├── eval_2.md
└── ...
```

## Mocking Strategy for Tests

```python
@pytest.fixture
def mock_claude_analyzer():
    """Mock Claude responses for analyzer tests"""
    with patch('anthropic.Anthropic') as mock:
        def analyze_response(prompt):
            # Smart responses based on prompt content
            if "vague" in prompt and "productive" in prompt:
                if "what specifically" in prompt.lower():
                    return json.dumps({
                        "score": 0.8,
                        "reasoning": "Challenges vague statement with specific question"
                    })
                else:
                    return json.dumps({
                        "score": 0.2,
                        "reasoning": "Accepts vague goal without pushing for clarity"
                    })
            # Add more patterns as needed
            
        mock.return_value.complete.side_effect = analyze_response
        yield mock

@pytest.fixture
def mock_pm_personas():
    """Mock PM persona responses"""
    def persona_response(persona_type, coach_message):
        if persona_type == "framework_rigid":
            if "throw away" in coach_message:
                return "Actually, I think a structured approach would help me process this better..."
            return "Let me create a framework for that..."
        elif persona_type == "control_freak":
            if "good enough" in coach_message:
                return "But I just need to refine it a bit more to make sure it's perfect..."
            return "I want to make sure I get this exactly right..."
        elif persona_type == "legacy_builder":
            if "right now" in coach_message:
                return "This experience will make me stronger in the long run..."
            return "I'm thinking about how this shapes my future..."
    
    return persona_response
```

## Key Implementation Patterns

### 1. Performance Tracking Pattern
```python
class PerformanceTracker:
    def __init__(self):
        self.response_times = []
    
    async def track_response(self, start_time: float, end_time: float):
        """Track response time in milliseconds"""
        response_time_ms = (end_time - start_time) * 1000
        self.response_times.append(response_time_ms)
    
    def get_percentile(self, percentile: int) -> float:
        """Get response time at given percentile"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    def percentage_under_threshold(self, threshold_ms: float) -> float:
        """Percentage of responses under threshold"""
        under = sum(1 for t in self.response_times if t < threshold_ms)
        return under / len(self.response_times) if self.response_times else 0
```

### 2. PM Persona Interface
```python
class BasePMPersona(ABC):
    def __init__(self):
        self.resistance_level = 0.8
        self.breakthrough_threshold = 4
        self.interaction_count = 0
    
    @abstractmethod
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate response based on persona patterns"""
        pass
    
    def update_resistance(self, coach_message: str):
        """Track if coach is breaking through resistance"""
        if self.detects_effective_challenge(coach_message):
            self.resistance_level *= 0.9
            self.interaction_count += 1
            
            if self.interaction_count >= self.breakthrough_threshold:
                return self.generate_breakthrough_response()
```

### 3. CLI Enhancement for Evaluation
```python
class EnhancedCLI(BaseCLI):
    def __init__(self):
        super().__init__()
        self.performance_tracker = PerformanceTracker()
        self.current_eval = None
        
    async def handle_message(self, message: str):
        """Track performance while processing"""
        start_time = time.time()
        
        # Get response from coach
        response = await super().handle_message(message)
        
        # Track performance
        end_time = time.time()
        await self.performance_tracker.track_response(start_time, end_time)
        
        return response
    
    async def handle_stop_command(self):
        """Display evaluation instead of just ending"""
        # Generate evaluation
        self.current_eval = await self.evaluator.evaluate(
            self.conversation_history
        )
        
        # Display summary
        print("\n=== Conversation Evaluation ===")
        print(f"Total Cost: ${self.current_eval.cost:.4f}")
        print(f"Coaching Effectiveness: {self.current_eval.score:.1f}/10")
        print(f"\nResponse Speed:")
        print(f"- Median: {self.performance_tracker.get_percentile(50):.0f}ms")
        print(f"- 80th percentile: {self.performance_tracker.get_percentile(80):.0f}ms")
        print(f"- Under 1s: {self.performance_tracker.percentage_under_threshold(1000):.0%}")
        
        print("\nAdd notes (or 'skip'): ", end="")
```

## Session Success Criteria

### Must Complete ✅
- [ ] Enhanced CLI with evaluation reports and performance tracking
- [ ] 4 behavioral analyzers using LLM analysis
- [ ] 3 PM personas (framework rigid, control freak, legacy builder)
- [ ] 20+ real conversations generated and analyzed
- [ ] Evaluation report generator with markdown output
- [ ] Response time tracking with 80th percentile reporting
- [ ] User notes capture and AI reflection system
- [ ] All tests passing with mocked LLM calls

### Should Complete 🎯
- [ ] Persona resistance pattern identification
- [ ] Breakthrough detection in conversations
- [ ] Performance optimization insights
- [ ] Coaching move effectiveness library

### Stretch Goals 🚀
- [ ] Real-time performance monitoring
- [ ] Persona evolution during conversations
- [ ] Coaching strategy recommendations based on persona type

## Learning Focus Areas

Based on your learning_ledger.md:

1. **Performance Monitoring**: Track and optimize async operations
2. **Behavioral Testing**: Create realistic personas that mirror your patterns
3. **LLM Prompt Engineering**: Craft analysis prompts for consistent scoring
4. **Data-Driven Development**: Let patterns emerge from real usage
5. **User Research Integration**: Combine metrics with qualitative feedback

## Common Pitfalls to Avoid

1. **Don't** create unrealistic personas - base them on real PM behaviors
2. **Don't** ignore performance early - track from the start
3. **Don't** over-complicate analyzers - start simple and iterate
4. **Don't** forget edge cases - empty conversations, timeouts, etc.
5. **Don't** optimize metrics at the expense of conversation quality

## Next Session Preview

Session 4 will scale your system architecture:
- Migrate from in-memory to Redis event bus
- Add performance monitoring and optimization
- Enable concurrent conversation handling
- Prepare for multi-agent routing in Session 5

---

*Remember: Great coaches adapt to resistance patterns while maintaining sub-second responsiveness. Your evaluation framework makes both goals measurable.*
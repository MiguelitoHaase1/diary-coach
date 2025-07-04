# Session 5: LangGraph Architecture Migration

## Executive Summary

Migrate from event-bus to LangGraph while preserving all functionality through a "Parallel Run" strategy. Build abstractions that allow both systems to coexist, enabling zero-downtime migration with A/B testing capability. Focus on conversation flow visualization, agent communication patterns, and user satisfaction tracking in LangSmith.

**Duration**: 4-5 hours across 6-7 increments  
**Approach**: Interface-first design with parallel systems, TDD throughout  
**Success Criteria**: Feature parity with enhanced observability, zero regression

## Learning Opportunities for PM-Who-Codes

### Primary Learning Areas (Given Your Strengths)
1. **State Machine Design**: How LangGraph's state channels map to product flows
2. **Observability Engineering**: Building custom metrics that measure what matters
3. **Migration Patterns**: Safe architectural evolution without breaking changes
4. **Graph Theory for Product**: How directed graphs model user journeys

### Secondary Learning Areas
- Checkpoint persistence strategies
- Distributed tracing with OpenTelemetry
- A/B testing infrastructure at the architecture level

## Technical Context

### Current Architecture (Event-Bus)
```
UserMessage → EventBus → CoachAgent → Response
                ↓            ↓
           Evaluators   DeepThoughts
```

### Target Architecture (LangGraph)
```
Input → StateGraph → Coach Node → Decision Node → Output
           ↓            ↓             ↓
      Checkpoints   Evaluators   LangSmith
```

### Migration Strategy: Parallel Run
1. Create `AgentInterface` abstraction over both systems
2. Implement LangGraph version behind same interface
3. Run both systems in parallel with comparison
4. Gradually shift traffic to LangGraph
5. Deprecate event-bus after validation

## Increment Breakdown

### Increment 5.1: AgentInterface Abstraction (30-45 min)
**Goal**: Create interface that both event-bus and LangGraph can implement

**Test First**:
```python
# tests/test_agent_interface.py
async def test_agent_interface_contract():
    """Both implementations must satisfy same interface"""
    for implementation in [EventBusAgent, LangGraphAgent]:
        agent = implementation()
        assert hasattr(agent, 'process_message')
        assert hasattr(agent, 'get_conversation_state')
        assert hasattr(agent, 'get_metrics')
```

**Implementation Focus**:
- Abstract base class with required methods
- Adapter for existing event-bus agents
- Placeholder for LangGraph implementation
- Factory pattern for implementation selection

**Learning Hook**: How interfaces enable architectural evolution

### Increment 5.2: Basic LangGraph State Design (45-60 min)
**Goal**: Define state schema for conversation + evaluation data

**Test First**:
```python
# tests/test_langgraph_state.py
async def test_conversation_state_schema():
    """State must track conversation, metrics, and decisions"""
    state = ConversationState()
    state.add_message(user_msg)
    state.add_evaluation(eval_result)
    assert state.get_satisfaction_score() > 0
    assert state.get_decision_path() == ["coach", "evaluator", "output"]
```

**Implementation Focus**:
- Pydantic schema for type safety
- State channels for different data types
- Conversation history management
- Metric aggregation patterns

**Learning Hook**: State machines as product behavior models

### Increment 5.3: Coach Node Implementation (45-60 min)
**Goal**: Wrap existing coach in LangGraph node

**Test First**:
```python
# tests/test_coach_node.py
async def test_coach_node_preserves_behavior():
    """LangGraph coach must match event-bus coach exactly"""
    # Run same input through both systems
    event_response = await event_bus_coach.process(msg)
    graph_response = await graph_coach_node.process(msg)
    assert graph_response.content == event_response.content
    assert graph_response.thinking_style == event_response.thinking_style
```

**Implementation Focus**:
- Node wrapper around existing coach logic
- State update patterns
- Error handling and retry logic
- Checkpoint creation after coaching

**Learning Hook**: Wrapping vs rewriting in migrations

### Increment 5.4: LangSmith Integration (30-45 min)
**Goal**: Add custom metrics and flow visualization

**Test First**:
```python
# tests/test_langsmith_metrics.py
async def test_custom_satisfaction_tracking():
    """User satisfaction must be tracked in LangSmith"""
    with capture_langsmith_events() as events:
        await graph.arun(test_conversation)
    
    assert "user_satisfaction" in events.custom_metrics
    assert "conversation_flow" in events.metadata
    assert events.agent_communications.count() >= 2
```

**Implementation Focus**:
- LangSmith client configuration
- Custom event logging
- Satisfaction score calculation
- Agent communication tracking
- Decision path visualization

**Learning Hook**: Metrics that matter for AI products

### Increment 5.5: Redis Checkpoint Persistence (30-45 min)
**Goal**: Use existing Redis for state persistence

**Test First**:
```python
# tests/test_checkpoint_persistence.py
async def test_conversation_resume():
    """Conversations must resume from checkpoints"""
    # Start conversation
    state1 = await graph.arun_until_checkpoint(msg1)
    checkpoint_id = state1.checkpoint_id
    
    # Resume from checkpoint
    state2 = await graph.arun_from_checkpoint(checkpoint_id, msg2)
    assert state2.conversation_history.includes(msg1)
```

**Implementation Focus**:
- Redis checkpoint saver implementation
- State serialization patterns
- Checkpoint versioning
- Cleanup strategies

**Learning Hook**: State persistence in distributed systems

### Increment 5.6: Parallel Run Validation (45-60 min)
**Goal**: Run both systems in parallel and compare

**Test First**:
```python
# tests/test_parallel_validation.py
async def test_parallel_system_parity():
    """Both systems must produce identical outcomes"""
    results = await run_parallel_comparison(
        test_conversations=20,
        metrics=["response_quality", "latency", "cost"]
    )
    
    assert results.divergence_rate < 0.05  # 95% parity
    assert results.langgraph_latency < results.eventbus_latency
```

**Implementation Focus**:
- Parallel execution framework
- Response comparison logic
- Metric collection and reporting
- Divergence analysis tools
- A/B test infrastructure

**Learning Hook**: Shadow testing for safe migrations

### Increment 5.7: OpenTelemetry Instrumentation (30-45 min)
**Goal**: Add distributed tracing across both systems

**Test First**:
```python
# tests/test_otel_tracing.py
async def test_tracing_spans():
    """Every agent interaction must create spans"""
    with collect_spans() as spans:
        await graph.arun(test_message)
    
    assert "coach_processing" in spans
    assert "evaluation_scoring" in spans
    assert spans.get_duration("total") < 3000  # ms
```

**Implementation Focus**:
- OTel setup and configuration
- Span creation in nodes
- Context propagation
- Performance profiling
- Trace visualization setup

**Learning Hook**: Observability as a first-class concern

## Migration Execution Plan

### Phase 1: Build Parallel Infrastructure (Increments 1-5)
- Both systems running independently
- No production traffic on LangGraph yet
- Focus on feature parity

### Phase 2: Shadow Testing (Increment 6)
- 100% traffic to event-bus (production)
- 100% shadow traffic to LangGraph (validation)
- Collect comparison metrics

### Phase 3: Gradual Migration
- 10% → 50% → 100% traffic shift
- Monitor LangSmith for issues
- Rollback capability maintained

### Phase 4: Deprecation
- Remove event-bus code
- Clean up abstractions
- Document lessons learned

## Success Metrics

### Technical Metrics
- ✅ 100% test coverage maintained
- ✅ Zero regression in conversation quality
- ✅ <3s latency for all operations
- ✅ Complete feature parity

### Observability Metrics
- ✅ All conversation flows visible in LangSmith
- ✅ User satisfaction scores tracked
- ✅ Agent communication patterns captured
- ✅ Decision paths documented

### Learning Metrics
- ✅ Can explain state machines to non-technical stakeholders
- ✅ Understands tradeoffs in migration strategies
- ✅ Can design observable systems from scratch

## Risk Mitigation

### Risk 1: Feature Regression
**Mitigation**: Comprehensive parallel testing before cutover

### Risk 2: Performance Degradation  
**Mitigation**: Load test both systems, optimize before migration

### Risk 3: Observability Gaps
**Mitigation**: Implement tracing in both systems for comparison

## Key Commands and Tools

```bash
# Install LangGraph and dependencies
pip install langgraph langsmith opentelemetry-api

# Run parallel comparison tests
pytest tests/test_parallel_validation.py -v

# Monitor LangSmith dashboard
open https://smith.langchain.com/your-project

# Check Redis checkpoints
redis-cli --scan --pattern "checkpoint:*"

# View OpenTelemetry traces
docker-compose up jaeger  # localhost:16686
```

## Documentation Requirements

### Must Update
- `docs/status.md` after each increment
- `docs/session_5/Log_5_x.md` with detailed actions
- `docs/session_5/Dojo_5_x.md` with learning insights

### Must Create
- Migration runbook for production cutover
- LangSmith dashboard setup guide
- Checkpoint management playbook

## Learning Resources

### Before Starting
- LangGraph conceptual guide (state machines)
- LangSmith quickstart (custom metrics)
- OpenTelemetry Python tutorial

### During Development
- Use Claude to explain graph theory concepts
- Ask for state machine diagrams
- Request tracing best practices

### After Completion
- Review migration patterns
- Document architectural decisions
- Share learnings with team

## Session Mantra

"Wrap, don't weld. Measure everything. Migrate gradually."

Every line of code should make the migration safer, not riskier. The user should never know we're changing the plumbing - they should only experience better insights about their coaching sessions.
# Dojo Session 6.6: LangSmith Integration Patterns

**Context**: We built a sophisticated 7-evaluator system for coaching conversations, but the evaluations weren't appearing in LangSmith's dashboard. The fix revealed important patterns about integrating third-party observability platforms.

**Concept**: The Facade Pattern vs Direct Integration - Understanding when to wrap external APIs and when to adopt their patterns directly.

**Value**: This pattern appears whenever integrating monitoring, observability, or evaluation tools. The choice between wrapping (facade) vs adopting (direct integration) affects maintainability, debugging complexity, and feature availability.

## The Anti-Pattern We Started With

```python
# Creating our own Run objects (facade approach)
mock_run = Run(
    id=str(uuid.uuid4()),
    inputs={"messages": conversation},
    outputs={"response": deep_report}
)
result = await evaluator.aevaluate_run(mock_run)
```

This seemed logical - we control the interface, our evaluators work unchanged. But it bypassed LangSmith's entire tracking infrastructure.

## The Correct Pattern

```python
# Adopting LangSmith's patterns (direct integration)
await aevaluate(
    target_function,          # What we're evaluating
    data=dataset_name,        # LangSmith dataset
    evaluators=evaluators,    # Wrapped to match their interface
    experiment_prefix="eval"  # Their tracking system
)
```

## Key Learning: Integration Depth Spectrum

```
Shallow Integration          Deep Integration
     |---------------------------|
     Mock/Facade            Full Adoption
     (our control)          (their patterns)
```

### When to Use Shallow (Facade):
- External API is unstable or frequently changing
- You need to support multiple providers
- Core business logic shouldn't depend on external service
- Testing needs to work without external dependencies

### When to Use Deep (Direct):
- The external service IS the value (like LangSmith for observability)
- You want all their features (dashboards, comparisons, tracking)
- The integration is strategic, not tactical
- Their patterns improve your architecture

## Applied to Our Case

We initially chose shallow integration (creating mock Runs) because:
- It seemed simpler
- Our evaluators worked unchanged
- We maintained control

But LangSmith's value is in its observability infrastructure. By not adopting their patterns, we lost:
- Experiment tracking
- Dashboard visibility  
- Comparison features
- Automatic metric aggregation

The fix required adopting their patterns:
1. Create datasets (their data model)
2. Wrap evaluators (their interface)
3. Use their evaluation API (their control flow)

## Broader Applications

This pattern applies to many integrations:

**Monitoring (DataDog, New Relic)**
- Shallow: Log to your format, ship to them
- Deep: Use their SDKs, adopt their tagging patterns

**Feature Flags (LaunchDarkly, Split)**
- Shallow: Wrapper that could switch providers
- Deep: Use their targeting rules and experiments

**Authentication (Auth0, Okta)**
- Shallow: Just validate tokens
- Deep: Use their user management, rules engine

## The Integration Decision Framework

Ask yourself:
1. **Is the external service core to your value?** → Deep integration
2. **Do you need provider flexibility?** → Shallow integration
3. **Will you use advanced features?** → Deep integration
4. **Is it a commodity service?** → Shallow integration

## Also Consider

**Debugging Across Boundaries**: Deep integrations make debugging harder. You're debugging their system + yours. Our LangSmith issue took 2 hours because we had to understand their evaluation lifecycle.

**Version Coupling**: Deep integration means you're coupled to their API versions. When they deprecate features, you must migrate.

**Documentation Dependency**: With deep integration, you're only as good as their docs. LangSmith's docs were good; not all services are.

## Action Items

1. Document integration depth decisions in ADRs (Architecture Decision Records)
2. Create integration tests that verify the external service behavior
3. Build debugging tools early (like our `test_langsmith_connection.py`)
4. Keep a "circuit breaker" plan - how would you disable the integration if needed?

## Meditation Question

*"When integrating external services, am I choosing depth based on value delivery or just following the path of least resistance?"*
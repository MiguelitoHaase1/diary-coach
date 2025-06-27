# Dojo Session 1.5: Abstract Base Classes and Schema Design

**Purpose**: Enable me to copy this learning theme into Claude.ai for deeper exploration.

**Context**: While implementing the BaseAgent class, we encountered the fundamental challenge of designing abstractions that balance flexibility with concrete functionality. The implementation revealed key insights about how abstract base classes should handle schema compatibility and provide extensible behavior patterns.

**Challenge**: Creating a BaseAgent that serves as both a testable concrete implementation and a proper abstraction for specialized coaching agents. The tension between "abstract enough to be extensible" and "concrete enough to be testable" required careful design decisions around response generation and schema adherence.

**Concept**: **Abstract Base Class Design in Domain-Driven Architecture**

This goes beyond Python's ABC module - it's about creating domain abstractions that capture the essence of your business logic while remaining flexible for specialization. In our coaching system, BaseAgent embodies the core "agent behavior" contract while allowing subclasses to implement domain-specific intelligence.

Key principles that emerged:
1. **Schema-First Design**: The agent's behavior is constrained by well-defined data contracts (UserMessage → AgentResponse)
2. **Template Method Pattern**: BaseAgent handles infrastructure (response creation, field mapping) while delegating domain logic (_generate_response) to subclasses
3. **Testable Abstractions**: Even abstract classes need concrete default behavior for testing and fallback scenarios

The deeper insight: Abstract classes in domain-driven systems aren't just about code reuse - they're about encoding business invariants that must hold across all implementations. Every coaching agent must respond to messages, track conversations, and maintain threading - these are domain requirements, not just technical ones.

**Why this matters to you as a product manager who codes**: Understanding abstraction design helps you think about product architecture at the right level. You can identify which behaviors are universal to your domain (all coaches respond to users) versus which are specialized (goal-setting coach vs reflection coach). This translates directly to better API design, clearer feature boundaries, and more maintainable product evolution.

**Other areas one could explore**: 
- **Event-Driven Schema Evolution**: How to handle schema changes in distributed systems without breaking existing components
- **Domain-Specific Language Design**: Using Python's flexibility to create more expressive domain abstractions
- **Testing Strategy for Abstract Components**: Patterns for testing base classes that need concrete implementations to be meaningful
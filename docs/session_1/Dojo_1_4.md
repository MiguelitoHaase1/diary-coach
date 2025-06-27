# Dojo Session 1.4: Event-Driven Architecture & System Decoupling

## Learning Session Prompt

**Claude, I want you to act as a Socratic coach to help me deeply understand event-driven architecture patterns and system decoupling strategies. I'm a product manager who codes, and I just implemented an in-memory event bus for a coaching system. I want to understand how these architectural patterns affect product decisions, scalability, and system design.**

## Context: What We Built

We just implemented an async event bus with publisher/subscriber pattern for a diary coaching system. The event bus supports:

- **Channel-based routing** (e.g., "coaching.goals", "system.agent.register")
- **Multiple subscribers per channel** (multiple agents can listen to user messages)
- **Concurrent handler execution** (handlers don't block each other)
- **Clean resource management** (subscribe/unsubscribe lifecycle)

This is part of a larger system that will eventually support:
- Multiple AI coaching agents
- Voice integration via LiveKit
- Real-time conversation insights
- Evening reflection summaries

## Core Learning Challenge

**As a product manager, I need to understand:**

1. **When and why to choose event-driven architecture** over traditional request/response patterns
2. **How system decoupling affects product roadmap decisions** and feature development
3. **The trade-offs between coupling and complexity** in product systems
4. **How to evaluate whether event-driven patterns solve real product problems** or just add complexity

## Specific Questions to Explore

### Product Strategy Questions:
- How does event-driven architecture enable or constrain product feature development?
- What product scenarios benefit most from loose coupling between components?
- How do you decide between immediate consistency vs eventual consistency in product features?
- When does the complexity of event-driven systems outweigh the benefits for a product?

### System Design Questions:
- How do event-driven patterns affect system observability and debugging in production?
- What are the implications for data consistency across different parts of the product?
- How do you design event schemas that evolve with product requirements?
- What monitoring and alerting strategies work best for event-driven products?

### Scaling Questions:
- How does event-driven architecture affect horizontal vs vertical scaling decisions?
- What happens to system complexity as you add more event types and subscribers?
- How do you manage event ordering and delivery guarantees as the system grows?
- What are the performance characteristics that matter most for product success?

## My Current Understanding

I understand the basic pub/sub pattern, but I want to go deeper on:

1. **Strategic implications**: How this architecture choice affects product velocity, team organization, and technical debt
2. **Design patterns**: Beyond basic pub/sub - event sourcing, CQRS, saga patterns, and when each applies
3. **Product trade-offs**: Understanding the real-world costs and benefits for different product scenarios
4. **Evolution strategies**: How to migrate from coupled systems to event-driven ones without breaking the product

## Learning Goals

By the end of this session, I want to:
- **Evaluate architecture decisions** through a product lens, not just technical correctness
- **Recognize patterns** in successful event-driven products and understand why they work
- **Make informed trade-offs** between system complexity and product capabilities
- **Design event-driven systems** that actually solve product problems rather than create technical debt

## Other Areas to Explore (If Time Permits)

1. **Message Brokers vs Event Buses**: When to use Redis, RabbitMQ, Kafka, or cloud-native solutions
2. **Event Sourcing**: How storing events instead of state affects product capabilities
3. **Microservices Communication**: How event-driven patterns enable or complicate service boundaries

---

**Please guide me through this exploration using the Socratic method - ask probing questions, challenge my assumptions, and help me discover the deeper principles that will make me a better product architect.**
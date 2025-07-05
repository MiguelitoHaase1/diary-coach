# Dojo Session 6.8: Software Architecture Patterns for Maintainable Systems

**Purpose**: Enable me to copy a learning theme into Claude.ai, so I can personally prompt it further to teach me more about it.

**Context**: After completing Session 6's personal context integration, we encountered a classic software maintenance challenge: prompt duplication across multiple files. This led us to implement a centralized prompt management system using dynamic loading, caching, and single source of truth patterns.

**Challenge**: The core challenge was eliminating code duplication while maintaining performance and developer experience. We needed to refactor embedded string constants into a dynamic loading system without breaking existing functionality or introducing performance regressions.

**Primary Learning Focus: Single Source of Truth (SSOT) and Dynamic Resource Loading Patterns**

**Concept**: The Single Source of Truth principle is fundamental to maintainable software architecture. When information exists in multiple places, systems become fragile, inconsistent, and expensive to maintain. The key insight is that data should have one authoritative source, with all other references pointing to or derived from that source.

**Why This Matters for Product Leadership**:

As a product manager who codes, understanding SSOT patterns is crucial because:

1. **Product Consistency**: Just as we centralized prompts, product features, pricing, and user flows should have single authoritative sources. Multiple versions of "what the product does" lead to confused users and inconsistent experiences.

2. **Organizational Scaling**: Teams naturally create duplicated information (requirements docs, feature specs, user stories). SSOT patterns help organizations scale without creating conflicting sources of truth that slow down execution.

3. **Technical Debt Management**: Understanding when duplication is expensive vs. beneficial helps product leaders make better build vs. buy decisions and prioritize refactoring work that impacts velocity.

4. **Cross-Team Coordination**: APIs, shared services, and integration patterns all benefit from SSOT thinking. Product leaders who understand these patterns can better design team structures and development processes.

**Technical Architecture Patterns**:

- **Dynamic Loading with Caching**: Our `PromptLoader` demonstrates how to balance flexibility (file-based prompts) with performance (in-memory caching)
- **Property-Based Access**: Using `@property` decorators to make dynamic loading transparent to consumers
- **Graceful Degradation**: Error handling patterns that prevent system failures when resources are unavailable
- **Resource Versioning**: File modification time tracking for cache invalidation strategies

**Product Applications**:
- Configuration management systems that prevent "works on my machine" problems
- Feature flag systems that ensure consistent rollouts across environments
- Content management where marketing, support, and product all reference the same source
- Pricing and plan definitions that flow consistently through billing, UI, and sales systems

**Scaling Considerations**:
The pattern scales from simple file-based loading (our implementation) to sophisticated distributed systems with database-backed configuration, CDN-cached resources, and real-time synchronization across microservices.

**Other areas you could explore if interested (but lesser priority)**:

1. **Caching Strategies and Cache Invalidation**: Our simple in-memory cache could extend to explore Redis, CDN patterns, and the classic "cache invalidation is one of the two hard problems in computer science" challenges.

2. **Configuration Management and Feature Flags**: The prompt loading pattern is similar to configuration systems - worth exploring how tools like LaunchDarkly, Split, or custom feature flag systems solve similar problems at scale.
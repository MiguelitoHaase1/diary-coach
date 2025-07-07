# Multi-Agent Diary Coach Lesson Plan: Personal Experience-First Development

## Executive Summary

Build a multi-agent coaching system prioritizing personal experience and voice interaction before production hardening. Start with a working prototype (Session 2), enhance with personal context and evaluation (Sessions 3-4), migrate to LangGraph/LangSmith (Session 5), build conversation memory and context infrastructure (Session 6), then implement parallel multi-agent orchestration with dedicated MCP agent (Session 7). Production features come last after core experience is perfected.

**Tech Stack**: Anthropic SDK (Sonnet + Opus), LangGraph (orchestration), LangSmith (observability), OpenTelemetry, pytest + LangChain, Personal Context Files (Markdown), LiveKit (voice), Redis Pub/Sub (early phases), FastAPI (later phases)

## Phase 1: Intelligent Personal Experience (19-21 hours)

### Session 1: Project Setup and TDD Infrastructure (2-3 hours) ✅

**Goal**: Set up testing framework and understand TDD principles

**Topics**:
- Project structure with proper Python packaging
- pytest configuration and fixtures
- In-memory event bus basics with simple implementation
- Write your first conversation quality test
- Add async stream buffer for dual-track support

**Key Deliverables**:
- Working pytest setup
- Basic in-memory event bus (subscribe/publish)
- Simple response relevance metric
- Project skeleton with clear separation of concerns
- Stream buffer for conversation + insights

### Session 2: Minimal Working Prototype - Real Conversations Now! (4-5 hours) ✅

**Goal**: Build a minimal but fully functional coaching conversation system

**Topics**:
- Anthropic SDK integration with async wrapper
- Simple orchestrator for message routing
- Morning/Evening coach implementation with Michael's specific prompt
- CLI interface for testing conversations
- End-to-end conversation flow validation

**Key Deliverables**:
- Working LLM service layer
- Basic orchestrator agent
- Morning/Evening coach with personalized personality
- CLI for live conversation testing
- Complete conversation flow from user input to coach response

### Session 3: Behavioral Change Detection Framework (3-4 hours) ✅

**Goal**: Build automated evaluation framework that measures your real coach's transformative potential

**Topics**:
- Live Coach Analysis: Evaluate your prototype's current coaching behaviors
- Weakness Identification: Find where your coach fails to push for specificity
- Simulated User Framework: Test your coach against personas
- Improvement Tracking: Dashboard showing coach evolution over time

**Key Deliverables**:
- Baseline Performance Report: Current coach scores across all metrics
- Conversation Corpus: 20+ real conversations with your prototype
- Evaluation Dashboard: Live metrics for your coaching system
- Refined Coach v2: Improved prompt based on metric feedback
- Before/After Comparison: Quantified improvement data

### Session 4: Morning Coach Excellence (4-5 hours) ✅

**Goal**: Transform generic coach into specialized morning experience with Deep Thoughts insights

**Topics**:
- Morning Coach Specialization: Extract the good evening parts
- Deep Thoughts Revolution: Replace the deep evaluation report with a deep think report markdown that makes user think a bit more (give summary of conversation to describe the problem to solve and approach, fact check a few things from conversation, and be a devil's advocate on the approach using Columbo's "just one more thing" phrasing). This should be a report, user wants to pin and read several times during the day.
- Morning-Specific Evals: Pick right problem, get around the problem looking for alternative options, excitement generation, actionability
- Deep Thoughts evals: Succinct summary, good devil's advocate phrasing, and getting the user well underway on actual solving the problem by giving hints.

**Key Deliverables**:
- Dedicated Morning Coach: Specialized agent with morning prompt
- Deep Thoughts Report as a markdown when ask for 'deep research': AI-powered insight amplification
- Morning Evaluation Suite: New metrics for morning effectiveness
- Refined Morning Prompt: Data-driven prompt improvements

## Phase 2: LangGraph Migration & Intelligence (14-16 hours)

### Session 5: LangGraph Architecture Migration (4-5 hours) ✅

**Goal**: Migrate event-bus to LangGraph while preserving all functionality

**Topics**:
- Wrap don't weld: AgentInterface abstraction over LangGraph nodes
- StateSchema design for conversation + evaluation data
- Graph topology: Coach → Evaluators → Deep Thoughts flow
- LangSmith integration with custom user satisfaction metrics
- OpenTelemetry instrumentation setup

**Key Deliverables**:
- LangGraph-based orchestrator replacing event bus
- Conversation state with checkpoint persistence
- LangSmith dashboard with flow visualization
- OTel spans for all agent communications
- Migration tests proving feature parity

### Session 6: Conversation Memory & Context Infrastructure (3-4 hours) ✅

**Goal**: Build conversation memory and context-aware infrastructure (without MCP)

**Topics**:
- Context-aware LangGraph with conditional routing
- Relevance scoring system (pattern matching + LLM analysis)
- Document context loading from markdown files
- Conversation memory with checkpoint persistence
- Memory recall for "remember when..." queries

**Key Deliverables**:
- Context-aware graph architecture with dynamic routing
- Multi-modal relevance scoring system
- Document loader for `/docs/memory/` folder
- Conversation history management
- Memory persistence and intelligent recall
- 42+ tests validating all functionality

**Lessons Learned**: MCP integration attempted but proved that dedicated agent architecture (Session 7) is necessary for clean separation of concerns.

### Session 7: Parallel Multi-Agent Orchestration with MCP (4-5 hours)

**Goal**: Implement parallel orchestration with dedicated MCP agent for zero-latency context enhancement

**Topics**:
- Parallel orchestration pattern (fast coach path + slow context path)
- Dedicated MCP Agent for all external data fetching
- Progressive enhancement with streaming responses
- Error isolation between coaching and data fetching
- Context caching and optimization strategies

**Key Deliverables**:
- Parallel orchestrator with immediate coach responses
- MCP Agent handling Todoist, Calendar, and other integrations
- Progressive context enhancement without blocking
- Robust error handling with graceful degradation
- Performance monitoring for both paths

**Architecture**:
```
User Message
    ↓
Parallel Orchestrator
    ├─→ Coach Agent (fast path)
    │     ↓
    │   Immediate Response Stream
    │
    └─→ Context Orchestrator (slow path)
          ├─→ Relevance Scorer
          ├─→ MCP Agent (todos, calendar, etc.)
          └─→ Memory Agent
                ↓
             Context Package
                ↓
         Progressive Enhancement
```

### Session 8: Advanced State Evolution (3-4 hours)

**Goal**: Implement multi-session state management and synthesis

**Topics**:
- State persistence across conversations
- Weekly synthesis via state aggregation
- State versioning and migration patterns
- Conversation continuity (morning → evening)
- Historical state replay for debugging

**Key Deliverables**:
- Multi-session state management
- Weekly report generator using historical states
- State evolution tracking in LangSmith
- Conversation linking system
- Debug tools using state replay

## Phase 3: Voice Revolution (9-11 hours)

### Session 9: Performance Optimization for Voice (3-4 hours)

**Goal**: Optimize LangGraph execution for voice latency requirements

**Topics**:
- Graph execution profiling via LangSmith
- Node-level caching strategies
- Streaming optimizations with partial states
- Pre-computation patterns for common flows
- Voice-ready performance benchmarks

**Key Deliverables**:
- Sub-3-second graph execution
- Caching layer integrated with LangGraph
- Streaming state updates
- Performance dashboard in LangSmith
- Cost optimization via execution analysis

### Session 10: Voice Integration Architecture (3-4 hours)

**Goal**: Add LiveKit voice layer to LangGraph system

**Topics**:
- Voice node wrapping text coach graph
- State channels for audio metadata
- Interruption handling via graph suspension
- Voice-specific error recovery patterns
- Real-time state updates during speech

**Key Deliverables**:
- Voice-enabled LangGraph architecture
- Audio state management
- Interruption-aware graph execution
- Voice metrics in LangSmith
- Seamless voice/text state continuity

### Session 11: Voice UX Enhancement (2-3 hours)

**Goal**: Create natural voice interactions with graph-based flow control

**Topics**:
- Dynamic graph edges for conversation flow
- Audio feedback via state updates
- Barge-in detection triggering graph events
- Voice personality through prompt nodes
- Natural turn-taking via state machines

**Key Deliverables**:
- Natural conversation graph patterns
- Audio cue injection system
- Voice UX metrics tracking
- Personality configuration nodes
- Conversation flow templates

## Phase 4: Production & Scale (14-16 hours)

### Session 12: Evening & Weekly Synthesis (4-5 hours)

**Goal**: Create evening reflection and weekly synthesis capabilities

**Topics**:
- Evening Coach Agent: Retrospective-focused personality
- Morning Session Linking: Reference specific morning goals
- Deep Thoughts Evolution: Append evening insights to morning report
- Weekly Synthesis: Select and analyze multiple Deep Thoughts
- Meta-Cognitive Patterns: "What do you believe now that you didn't before?"

**Key Deliverables**:
- Evening Coach Agent with reflection prompts
- Session linking via LangGraph state
- Weekly report generator with pattern recognition
- Date selection interface for report synthesis
- Sentiment tracking across sessions

### Session 13: Production Observability (3-4 hours)

**Goal**: Complete monitoring and debugging infrastructure

**Topics**:
- LangSmith production setup with alerting
- OpenTelemetry export to Grafana/Datadog
- Custom satisfaction score tracking
- A/B testing via graph variants
- Error analysis and recovery patterns

**Key Deliverables**:
- Production monitoring dashboard
- Multi-backend observability
- User satisfaction tracking system
- A/B testing framework
- Automated error recovery

### Session 14: Scale & Multi-User Support (3-4 hours)

**Goal**: Production deployment with concurrent users

**Topics**:
- LangGraph deployment patterns
- State isolation for concurrent users
- Resource pooling and rate limiting
- Cost management via execution tracking
- Load testing with LangSmith analysis

**Key Deliverables**:
- Containerized LangGraph deployment
- Multi-user state management
- Resource optimization system
- Cost tracking per user/session
- Load test results with bottleneck analysis

### Session 15: Continuous Learning System (3-4 hours)

**Goal**: Build feedback loops for system improvement

**Topics**:
- Conversation quality tracking over time
- Prompt improvement via LangSmith data
- User feedback integration patterns
- Automated regression testing
- Model performance monitoring

**Key Deliverables**:
- Quality metrics dashboard
- Prompt version control system
- Feedback processing pipeline
- Regression test suite
- Model drift detection

## Migration Philosophy

Every session follows the "Wrap, Don't Weld" principle:
1. **Abstract First**: Create interface before LangGraph implementation
2. **Instrument Everything**: OTel spans even in custom code
3. **Hard-Gate Features**: Regression test via LangSmith before deployment
4. **Measure Impact**: Track user satisfaction throughout migration
5. **Preserve Experience**: User never sees the plumbing change

## Key Architectural Insights

### Session 6 MCP Lessons
The attempted MCP integration in Session 6 revealed critical architectural requirements:
1. **Separation of Concerns**: Mixing MCP with coaching logic creates complexity
2. **Environment Boundaries**: MCP client-server communication needs dedicated handling
3. **Testing Challenges**: Integrated MCP makes coaching logic hard to test
4. **Error Isolation**: MCP failures shouldn't break coaching conversations

### Session 7 Parallel Orchestration Benefits
The parallel architecture solves all Session 6 pain points:
1. **Zero Latency**: Coach responds immediately while context loads
2. **Progressive Enhancement**: Initial response enhanced when context arrives
3. **Clean Testing**: Mock the MCP agent interface, not individual servers
4. **Failure Isolation**: Context failures don't impact coaching quality
5. **Scalability**: Easy to add new context sources without touching coach

## The Evolution Pattern

Every session follows this rhythm:
1. **Measure Current State**: How good is your coach now?
2. **Identify Improvement**: What specific aspect needs work?
3. **Implement Enhancement**: Add new capability incrementally
4. **Validate Impact**: Prove the improvement with data
5. **Document Learning**: Capture what worked for future reference

## Success Metrics

### Technical Excellence
- Clean architecture with separated concerns
- Sub-second coach responses with progressive enhancement
- Comprehensive test coverage (increasing with each session)
- Production-ready error handling and monitoring

### User Experience
- Natural conversational flow without technical interruptions
- Context enhances without disrupting coaching
- Voice interactions feel human and responsive
- Weekly synthesis provides meaningful insights

### Learning & Growth
- Each session builds on previous learnings
- Architectural decisions validated through implementation
- Knowledge captured in comprehensive documentation
- Patterns established for future AI system development
# Multi-Agent Diary Coach Lesson Plan: Text-First TDD with Redis & LangChain (Dual-Track Enhanced)

## Executive Summary

Build a multi-agent coaching system using Test-Driven Development (TDD) with Redis Pub/Sub for event-driven architecture. The system features morning goal-setting and evening reflection coaches with a "supportive yet skeptical" personality. **Enhancement**: Add dual-track processing where Sonnet maintains conversation flow while Opus provides deep insights asynchronously.

**Tech Stack**: Anthropic SDK (Sonnet + Opus), Redis Pub/Sub, pytest + LangChain, FastAPI (later phases)

## Phase 1: Foundation and Evaluation Infrastructure (8-10 hours)

### Session 1: Project Setup and TDD Infrastructure (2-3 hours)

**Goal**: Set up testing framework and understand TDD principles

**Topics**:
- Project structure with proper Python packaging
- pytest configuration and fixtures
- Redis Pub/Sub basics with simple event bus implementation
- Write your first conversation quality test
- Add async stream buffer for dual-track support

**Key Deliverables**:
- Working pytest setup
- Basic Redis event bus (subscribe/publish)
- Simple response relevance metric
- Project skeleton with clear separation of concerns
- Stream buffer for conversation + insights

### Session 2: Success Metrics and Evaluation Framework (3-4 hours)

### Session 2: Behavioral Change Detection Framework (3-4 hours)

**Goal**: Build automated evaluation framework that measures coaching's transformative potential

**Topics**:
- **Coach behavior metrics**: Analyze coaching responses for specificity pressure, challenge patterns, and commitment extraction attempts
- **Simulated user framework**: Create Claude-powered test users with resistant personas (vague, defensive, excuse-making)
- **Transformation potential scoring**: Measure how effectively coaches move users from abstract complaints to specific commitments
- **Adversarial testing**: Validate coaches against users designed to resist transformation
- **Two-tier evaluation strategy**: Automated development evals now, human validation later

**Key Deliverables**:
- **Coach-only evaluators**: Metrics that score coaching behaviors without user input
- **Simulated conversation runner**: Framework for testing coaches against AI personas
- **20+ test conversations**: Baseline dataset with various persona-coach combinations
- **Transformation potential metric**: Composite score predicting breakthrough likelihood
- **Test suite**: Automated tests ensuring coaches can handle resistant users

### Session 3: Event-Driven Architecture with Redis (2-3 hours)

**Goal**: Design event schemas and async communication patterns

**Topics**:
- Pydantic event schemas (UserMessage, AgentResponse, etc.)
- Channel naming conventions and routing patterns
- Agent registry for capability-based routing
- Visual debugging tools for event flow
- Add InsightInterruption event type
- Async processing patterns for dual tracks

**Key Deliverables**:
- Complete event schema definitions
- Async Redis event bus with visual monitoring
- Agent registry pattern
- Event flow visualization
- Dual-track event routing

## Phase 2: Core Agent Development (10-12 hours)

### Session 4: Building the Orchestrator Agent (3-4 hours)

**Goal**: Create the central routing agent

**Enhancement**: Orchestrator now manages both tracks - fast Sonnet responses and slow Opus analysis

**Topics**:
- Conversation state management
- Intent detection and routing logic
- Session handling across multiple conversations
- Error handling and fallback strategies
- Dual-track conversation state management
- Async task spawning for deep analysis

**Key Deliverables**:
- Working orchestrator with intelligent routing
- Session management system
- Comprehensive routing tests
- Error recovery mechanisms
- Fast-track/slow-track coordination

### Session 5: Implementing Specialized Coaching Agents (4-5 hours)

**Goal**: Build three specialized agents with distinct personalities

**Enhancement**: Each agent can operate in fast-track (Sonnet) or slow-track (Opus) mode

**Topics**:
- Base agent pattern for code reuse
- Goal-Setting Agent: morning coaching, value exploration
- Reflection Agent: evening storytelling, lesson extraction
- Challenge Agent: supportive skepticism, assumption questioning
- Fast conversational responses vs deep analysis modes
- Background pattern detection in Challenge Agent

**Key Deliverables**:
- Three working specialized agents
- Dual-mode operation for each agent
- Personality consistency across conversations
- Integration with evaluation metrics
- Agent-specific test suites

### Session 6: Agent Integration and System Testing (3-4 hours)

**Goal**: Integrate all components into a cohesive system

**Topics**:
- System startup and initialization
- End-to-end conversation flow testing
- Performance monitoring setup
- Health checks and system diagnostics
- Dual-track integration testing
- Interruption timing optimization

**Key Deliverables**:
- Fully integrated coaching system
- End-to-end test scenarios
- System health monitoring
- Performance baseline metrics
- Validated dual-track conversation flows

## Phase 3: Advanced Features and Optimization (6-8 hours)

### Session 7: Advanced Context Management and Memory (3-4 hours)

**Goal**: Add conversation memory and user profiling

**Enhancement**: Separate memory systems for fast and slow tracks

**Topics**:
- SQLite-based conversation storage
- User profile evolution over time
- Context-aware agent responses
- Pattern recognition in user behavior
- Context synchronization between tracks
- Deep insight history tracking

**Key Deliverables**:
- Conversation memory system
- User profile tracking
- Context retrieval for personalization
- Behavioral pattern analysis
- Dual-track memory coordination

### Session 8: Performance Optimization and Monitoring (3-4 hours)

**Goal**: Optimize system performance and costs

**Topics**:
- LLM response caching strategies
- Performance metrics collection
- Cost optimization techniques
- Advanced debugging tools
- Token budget allocation (80% fast, 20% slow)
- Interruption relevance scoring

**Key Deliverables**:
- Redis-based LLM cache
- Performance monitoring dashboard
- Cost tracking and optimization
- Debug tooling
- Dual-track cost optimization

## Phase 4: LiveKit Integration and Voice (10-12 hours)

### Session 9: Understanding LiveKit Architecture (2-3 hours)

**Goal**: Learn LiveKit concepts for voice integration

**Topics**:
- LiveKit rooms and participants
- Audio streaming basics
- VAD (Voice Activity Detection) patterns
- Agent state management for voice

**Key Deliverables**:
- LiveKit development environment
- Basic audio streaming test
- Understanding of voice interaction patterns

### Session 10: Building the Voice Interface (3-4 hours)

**Goal**: Create voice agent wrapper for existing system

**Topics**:
- LiveKit Python SDK integration
- Speech-to-text and text-to-speech setup
- Voice activity detection implementation
- Conversation state bridging

**Key Deliverables**:
- Voice agent wrapper class
- STT/TTS integration
- Audio event handling
- State synchronization

### Session 11: Voice UX and Interruption Handling (2-3 hours)

**Goal**: Handle voice-specific interaction patterns

**Topics**:
- Interruption detection and handling
- Natural conversation timing
- Voice-specific error recovery
- Audio feedback patterns

**Key Deliverables**:
- Interruption handling logic
- Natural pause detection
- Voice-specific error messages
- Audio cue system

### Session 12: Testing and Deployment (3-4 hours)

**Goal**: Test voice system and prepare for deployment

**Topics**:
- Voice conversation testing strategies
- Docker containerization
- Production deployment considerations
- Monitoring voice quality metrics

**Key Deliverables**:
- Voice testing framework
- Docker configuration
- Deployment scripts
- Voice quality monitoring

## Learning Outcomes

By completing this course, you'll understand:
- How to build multi-agent systems with event-driven architecture
- Test-Driven Development for LLM applications
- Creating and using LLM evaluation frameworks
- Redis Pub/Sub for scalable agent communication
- Voice integration patterns with LiveKit
- Production deployment of conversational AI systems
- Understanding dual-track architecture for responsive yet profound conversations
- Async processing patterns for LLM applications
- Interruption timing and relevance scoring

## Prerequisites

- Intermediate Python knowledge
- Basic understanding of async programming
- Familiarity with pytest or similar testing frameworks
- Redis basics (or willingness to learn)
- Access to Anthropic API

## Resources Needed

- Anthropic API key
- Redis instance (local or cloud)
- LiveKit cloud account (for voice phases)
- Python 3.9+
- ~$20 in API credits for development/testing

---

## Minimal Changes Summary

1. **Core Architecture**: Keep all original agents and event-driven design
2. **Add Stream Buffer**: Simple addition to Session 1 for dual-track support
3. **Enhance Orchestrator**: Session 4 orchestrator manages both tracks
4. **Agent Modes**: Session 5 agents can operate in fast or slow mode
5. **Keep Everything Else**: TDD approach, Redis pub/sub, evaluation framework, LiveKit plans all unchanged

The dual-track concept is implemented as an enhancement layer on top of your existing architecture rather than a complete redesign.
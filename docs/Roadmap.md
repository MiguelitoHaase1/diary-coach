# Multi-Agent Diary Coach Lesson Plan: Text-First TDD with Redis & LangChain (Prototype-Driven Evolution)

## Executive Summary

Build a multi-agent coaching system using Test-Driven Development (TDD) with Redis Pub/Sub for event-driven architecture. uild a working prototype early (Session 2), then evolve it through data-driven improvements in each subsequent session. The system features morning goal-setting and evening reflection coaches with a "supportive yet skeptical" personality, eventually adding dual-track processing where Sonnet maintains conversation flow while Opus provides deep insights asynchronously.

**Tech Stack**: Anthropic SDK (Sonnet + Opus), Redis Pub/Sub, pytest + LangChain, FastAPI (later phases)

## Phase 1: Foundation and Early Prototype (12-14 hours)

### Session 1: Project Setup and TDD Infrastructure (2-3 hours) ✅

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

### Session 2: Minimal Working Prototype - Real Conversations Now! (4-5 hours) 🆕

**Goal**: Build a minimal but fully functional coaching conversation system. Connect Session 1 infrastructure to the Anthropic API and create your first working coach agent that can have real conversations.

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

**Learning Focus**:
- Apply prompt engineering skills to create coach personality
- See event-driven architecture in action
- Practice async Python with real API calls
- Understand token usage and costs

### Session 3: Behavioral Change Detection Framework (3-4 hours)

**Goal**: Build automated evaluation framework that measures your real coach's transformative potential

**Prototype Evolution Approach**:
1. **Baseline Measurement**: Generate 20+ conversations with your current coach
2. **Metric Development**: Build metrics based on observed weaknesses
3. **Prompt Refinement**: Use metrics to guide prompt improvements
4. **Impact Validation**: Measure improvement in transformation potential

**Topics**:
- **Live Coach Analysis**: Evaluate your prototype's current coaching behaviors
- **Weakness Identification**: Find where your coach fails to push for specificity
- **Simulated User Framework**: Test your coach against personas
- **Improvement Tracking**: Dashboard showing coach evolution over time

**Key Deliverables**:
- **Baseline Performance Report**: Current coach scores across all metrics
- **Conversation Corpus**: 20+ real conversations with your prototype
- **Evaluation Dashboard**: Live metrics for your coaching system
- **Refined Coach v2**: Improved prompt based on metric feedback
- **Before/After Comparison**: Quantified improvement data

### Session 4: Event-Driven Architecture Enhancement (2-3 hours)

**Goal**: Scale your working prototype from in-memory to production-ready Redis

**Prototype Evolution Approach**:
1. **Performance Baseline**: Measure current system latency and throughput
2. **Redis Migration**: Swap in-memory bus for Redis with zero downtime
3. **Load Testing**: Stress test with multiple concurrent conversations
4. **Monitoring Addition**: Add event flow visualization for debugging

**Topics**:
- **Live System Migration**: Move your working coach to Redis events
- **Event Replay System**: Record and replay conversations for testing
- **Performance Monitoring**: Track latency from user input to coach response
- **Error Recovery Testing**: Ensure your coach survives Redis failures
- **Event Pattern Analysis**: Discover common conversation flows

**Key Deliverables**:
- **Redis-Powered Coach**: Your prototype running on production infrastructure
- **Event Replay Tool**: Ability to replay any conversation for debugging
- **Performance Dashboard**: Real-time latency and throughput metrics
- **Reliability Report**: System behavior under failure conditions
- **Event Flow Visualizer**: See conversations flow through your system

## Phase 2: Intelligent Evolution (10-12 hours)

### Session 5: Intelligent Orchestrator Development (3-4 hours)

**Goal**: Evolve your simple orchestrator into an intelligent routing system

**Prototype Evolution Approach**:
1. **Current Behavior Analysis**: Map how your orchestrator routes messages now
2. **Routing Intelligence**: Add context detection using real conversation patterns
3. **Gradual Complexity**: Incrementally add routing rules with fallback to current behavior
4. **Live A/B Testing**: Route percentage of traffic to new logic

**Topics**:
- **Context Detection Patterns**: Learn from your conversation corpus
- **Progressive Enhancement**: Add routing features without breaking current flow
- **Multi-Agent Preparation**: Prepare for Session 6's specialized agents
- **Fallback Safety**: Always route to working coach if uncertain
- **Dual-Track Preparation**: Add async task spawning for future Opus analysis

**Key Deliverables**:
- **Smart Orchestrator v2**: Context-aware routing with your coach as fallback
- **Routing Analytics**: Data on routing decisions and accuracy
- **A/B Test Results**: Performance comparison of routing strategies
- **Safety Metrics**: Confirmation that no conversations were dropped
- **Integration Tests**: Validation of backward compatibility

### Session 6: Specialized Agent Evolution (4-5 hours)

**Goal**: Evolve your single coach into specialized morning/evening variants

**Prototype Evolution Approach**:
1. **Personality Analysis**: Identify current coach's strengths in each context
2. **Incremental Specialization**: Gradually differentiate behaviors
3. **Live Swapping Tests**: A/B test specialized vs general coach
4. **User Preference Learning**: Track which variant performs better when

**Topics**:
- **Coach Cloning**: Create variants of your working coach
- **Personality Refinement**: Enhance morning energy vs evening reflection
- **Challenge Agent Addition**: New agent for skeptical interventions
- **Hot Swapping**: Change coaches mid-conversation seamlessly
- **Performance Comparison**: Measure specialized vs general effectiveness

**Key Deliverables**:
- **Morning Coach v2**: Optimized for goal-setting and energy
- **Evening Coach v2**: Enhanced for reflection and learning extraction  
- **Challenge Agent v1**: Interrupts with supportive skepticism
- **Variant Performance Report**: Which specialization helps most
- **Smooth Transition Tests**: Validation of coach handoffs

### Session 7: System Integration and Reliability (3-4 hours)

**Goal**: Harden your evolved system for production use

**Prototype Evolution Approach**:
1. **Current Reliability Baseline**: Measure uptime and error rates
2. **Stress Testing**: Push system until it breaks, then fix weak points
3. **Recovery Mechanisms**: Add graceful degradation patterns
4. **Production Monitoring**: Implement comprehensive observability

**Topics**:
- **Multi-Day Conversations**: Test continuity across sessions
- **Concurrent User Support**: Handle multiple Michaels simultaneously
- **Error Recovery Patterns**: Graceful handling of API failures
- **Health Check System**: Proactive problem detection
- **Usage Analytics**: Understand real conversation patterns

**Key Deliverables**:
- **Production-Ready System**: Hardened for reliable daily use
- **Reliability Metrics**: 99.9% uptime achievement
- **Load Test Results**: Support for 10+ concurrent conversations
- **Recovery Playbook**: Automated error recovery procedures
- **Usage Insights**: Data-driven understanding of user patterns

## Phase 3: Advanced Intelligence (6-8 hours)

### Session 8: Memory and Context Management (3-4 hours)

**Goal**: Add memory to your coaches based on real conversation needs

**Prototype Evolution Approach**:
1. **Memory Need Analysis**: Identify where lack of memory hurts conversations
2. **Incremental Addition**: Add memory features one at a time
3. **Impact Measurement**: Quantify how memory improves coaching
4. **Cost/Benefit Analysis**: Balance memory value vs complexity

**Topics**:
- **Conversation Continuity**: Remember previous session goals
- **Pattern Recognition**: Identify recurring user challenges
- **Context Prioritization**: Store only high-value information
- **Memory-Enhanced Coaching**: Use history to personalize responses
- **Privacy-Aware Design**: Secure handling of personal diary data

**Key Deliverables**:
- **Memory-Enabled Coach v3**: Remembers key context across sessions
- **Memory Impact Report**: Quantified improvement in coaching quality
- **Context Retrieval System**: Efficient access to relevant history
- **Pattern Insights Dashboard**: Recurring themes in user's journey
- **Privacy Compliance**: Secure storage and access controls

### Session 9: Performance and Cost Optimization (3-4 hours)

**Goal**: Optimize your system based on real usage data

**Prototype Evolution Approach**:
1. **Cost Analysis**: Review actual token usage from Sessions 2-8
2. **Bottleneck Identification**: Profile real system performance
3. **Targeted Optimization**: Fix only measured problems
4. **User Experience Validation**: Ensure optimizations don't hurt quality

**Topics**:
- **Token Usage Analysis**: Understand your actual API costs
- **Caching Strategy**: Cache based on real repeated queries
- **Response Time Optimization**: Reduce latency where users notice
- **Dual-Track Implementation**: Add Opus for deep insights efficiently
- **Cost/Quality Tradeoffs**: Data-driven model selection

**Key Deliverables**:
- **Optimized Coach v4**: 50% cost reduction with maintained quality
- **Performance Report**: Before/after latency comparisons
- **Caching System**: Smart cache based on usage patterns
- **Cost Dashboard**: Real-time tracking of API expenses
- **Optimization Playbook**: Guidelines for future improvements

## Phase 4: Voice Evolution (10-12 hours)

### Session 10: Voice Integration Preparation (2-3 hours)

**Goal**: Understand voice requirements by studying your text coach patterns

**Prototype Evolution Approach**:
1. **Conversation Timing Analysis**: Study natural pause points in text
2. **Response Length Optimization**: Adjust for spoken delivery
3. **Voice Personality Design**: Adapt text personality for audio
4. **Technical Foundation**: Set up LiveKit environment

**Topics**:
- **Text-to-Voice Analysis**: Which responses work spoken vs written
- **Conversation Rhythm**: Natural timing for voice interactions
- **Voice Coach Personality**: Adapt warmth and tone for audio
- **LiveKit Setup**: Development environment preparation
- **Voice-Specific Metrics**: New evaluation criteria for audio

**Key Deliverables**:
- **Voice Readiness Report**: What needs to change for voice
- **LiveKit Dev Environment**: Ready for voice development
- **Voice-Adapted Prompts**: Modified for spoken delivery
- **Timing Analysis**: Data on conversation pace
- **Voice Testing Plan**: Strategy for audio evaluation

### Session 11: Building the Voice Interface (3-4 hours)

**Goal**: Create voice agent wrapper for your existing coaching system

**Prototype Evolution Approach**:
1. **Voice Baseline**: Record sample text conversations to establish timing
2. **Incremental Voice Features**: Add STT, then TTS, then VAD
3. **Quality Measurement**: Compare voice conversations to text baseline
4. **Latency Optimization**: Tune for natural conversation flow

**Topics**:
- **LiveKit Agent Framework**: Wrap your text coach in voice interface
- **Speech Pipeline Setup**: STT → Coach → TTS flow
- **Voice Activity Detection**: When to listen vs when to speak
- **Prompt Adaptation**: Modify coach responses for spoken delivery
- **State Synchronization**: Maintain context between voice and text

**Key Deliverables**:
- **Voice-Enabled Coach v1**: Basic working voice conversations
- **Latency Measurements**: Time from speech end to response start
- **Voice Quality Metrics**: STT accuracy, TTS naturalness scores
- **A/B Test Results**: Voice vs text coaching effectiveness
- **Error Recovery**: Graceful handling of speech recognition failures

### Session 12: Voice UX and Natural Conversation (2-3 hours)

**Goal**: Make voice interactions feel natural and responsive

**Prototype Evolution Approach**:
1. **Conversation Flow Analysis**: Study natural pause patterns from recordings
2. **Interruption Testing**: Measure optimal interruption windows
3. **Feedback Refinement**: Add audio cues and confirmations
4. **User Testing**: Get real feedback on voice experience

**Topics**:
- **Interruption Handling**: Allow natural conversation overlaps
- **Thinking Indicators**: Audio cues while processing
- **Barge-In Support**: Let users interrupt long responses
- **Voice Personality**: Tune TTS parameters for warmth
- **Error Communication**: Voice-appropriate error messages

**Key Deliverables**:
- **Natural Voice Coach v2**: Fluid conversation with interruptions
- **UX Metrics Report**: Interruption success rate, user satisfaction
- **Audio Cue System**: Non-verbal feedback sounds
- **Voice Personality Settings**: Optimized TTS configuration
- **Conversation Flow Tests**: Validation of natural timing

### Session 13: Production Voice Deployment (3-4 hours)

**Goal**: Deploy and monitor your voice coaching system

**Prototype Evolution Approach**:
1. **Deployment Readiness**: Package voice system for production
2. **Monitoring Setup**: Track voice-specific quality metrics
3. **Scaling Testing**: Handle multiple concurrent voice sessions
4. **Continuous Improvement**: Set up feedback loops

**Topics**:
- **Docker Containerization**: Package complete voice system
- **LiveKit Cloud Setup**: Production room configuration
- **Voice Quality Monitoring**: Track STT accuracy, latency, drops
- **Cost Optimization**: Balance voice quality vs API costs
- **User Feedback Integration**: Systematic improvement process

**Key Deliverables**:
- **Production Voice System**: Fully deployed and monitored
- **Voice Analytics Dashboard**: Real-time quality metrics
- **Scaling Report**: Concurrent session capacity and costs
- **Deployment Playbook**: Reproducible deployment process
- **30-Day Improvement Plan**: Data-driven enhancement roadmap


## The Evolution Pattern

Every session follows this rhythm:
1. **Measure Current State**: How good is your coach now?
2. **Identify Improvement**: What specific aspect needs work?
3. **Implement Enhancement**: Add new capability incrementally
4. **Validate Impact**: Prove the improvement with data
5. **Document Learning**: Capture what worked for future reference

# Multi-Agent Diary Coach Lesson Plan: Personal Experience-First Development

## Executive Summary

Build a multi-agent coaching system prioritizing personal experience and voice interaction before production hardening. Start with a working prototype (Session 2), enhance with personal context (Session 5), add intelligent routing and memory (Sessions 6-7), then revolutionize with voice (Sessions 9-11). Production features come last after core experience is perfected.

**Tech Stack**: Anthropic SDK (Sonnet + Opus), Personal Context Files (Markdown), pytest + LangChain, LiveKit (voice), Redis Pub/Sub (later phases), FastAPI (later phases)

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

### Session 4: Morning Coach Excellence (4-5 hours)

**Goal**: Transform generic coach into specialized morning experience with Deep Thoughts insights

**Topics**:
- Morning Coach Specialization: Extract the good evening parts
- Deep Thoughts Revolution: Replace the deep evaluation report with a deep think report markdown that makes user think a bit more (give summary of conversation to describe the problem to solve and approach, fact check a few things from conversation, and be a devil's advocate on the approach using Columbo's "just one more thing" phrasing). This should be a report, user wants to pin and read several times during the day.
- Morning-Specific Evals: Pick right problem, get around the problem looking for alternative options,  excitement generation, actionability
- Deep Thoughts evals: Succinct summary, good devil's advocate phrasing, and getting the user well underway on actual solving the problem by giving hints.

**Key Deliverables**:
- Dedicated Morning Coach: Specialized agent with morning prompt
- Deep Thoughts Report as a markdown when ask for 'deep research': AI-powered insight amplification
- Morning Evaluation Suite: New metrics for morning effectiveness
- Refined Morning Prompt: Data-driven prompt improvements

### Session 5: Personal Context Integration (3-4 hours)

**Goal**: Integrate your personal markdown files to create deeply personalized coaching with "aha moments"

**Topics**:
- Markdown file loading system for personal context
- Semantic search across your life history, core beliefs, and goals
- Context relevance scoring and selection
- Natural integration of personal insights and todos into coach responses
- Privacy-preserving separation from test conversations

**Key Deliverables**:
- Context file reader and parser
- MCP server from todoist, to capture to dos and use in conversations (capturing info upfront in daily chat, so chat can tell user upfront, challenge user's choice of 'key problem', and mention other things in to do that's relevant for the problem.
- Personal knowledge base integration
- Context-aware coach responses
- "Aha moment" generation from your real history
- Clear separation between test and personal data

### Session 6: Intelligent Orchestrator Development (3-4 hours)

**Goal**: Build intelligent routing system that leverages personal context for sophisticated conversations

**Topics**:
- Context Detection Patterns from personal files 
- Smart Routing: Detect conversation state and user needs
- Progressive Enhancement: Add routing intelligence incrementally
- Multi-Mode Support: Morning vs future evening vs challenge conversations
- Pattern Recognition: Identify conversation themes in real-time

**Key Deliverables**:
- Smart Orchestrator v2: Context-aware routing with personal knowledge
- Routing Analytics: Data on routing decisions and effectiveness
- Conversation Flow Optimization: Improved natural progression
- Mode Detection: Automatic recognition of coaching context
- Integration Tests: Validation of intelligent routing

## Phase 2: Voice Revolution with Performance (11-13 hours)

### Session 7: Performance and Cost Optimization (3-4 hours)

**Goal**: Optimize system performance to enable natural voice conversations

**Topics**:
- Response Time Analysis: Identify and fix latency bottlenecks
- Parallel Processing: Run analyzers concurrently
- Smart Caching: Cache based on usage patterns
- Token Optimization: Reduce costs without sacrificing quality
- Voice-Ready Performance: Sub-3-second response times

**Key Deliverables**:
- Optimized Coach v3: 50% faster responses
- Performance Dashboard: Real-time latency tracking
- Cost Reduction: 40% lower API costs
- Caching System: Smart response caching
- Voice-Ready Benchmarks: Consistent low latency

### Session 8: Voice Integration Preparation (2-3 hours)

**Goal**: Prepare your coaching system for voice interaction

**Topics**:
- Text-to-Voice Analysis: Adapt responses for spoken delivery
- Conversation Rhythm: Natural timing for voice interactions
- Voice Personality Design: Warm, supportive audio presence
- LiveKit Setup: Development environment preparation
- Voice-Specific Metrics: New evaluation criteria

**Key Deliverables**:
- Voice Readiness Report: Required adaptations identified
- LiveKit Dev Environment: Ready for voice development
- Voice-Adapted Prompts: Optimized for spoken conversation
- Timing Analysis: Natural conversation pace data
- Voice Testing Plan: Comprehensive evaluation strategy

### Session 9: Building the Voice Interface (3-4 hours)

**Goal**: Create voice wrapper for your personalized coaching system

**Topics**:
- LiveKit Agent Framework: Voice-enable your text coach
- Speech Pipeline: STT → Coach → TTS flow
- Voice Activity Detection: Natural conversation timing
- Personal Context in Voice: Reference your history naturally
- State Synchronization: Seamless voice/text continuity

**Key Deliverables**:
- Voice-Enabled Coach v1: Working voice conversations
- Latency Metrics: Speech-to-response timing
- Voice Quality Scores: STT/TTS effectiveness
- Personal Context Integration: Natural history references
- Error Recovery: Graceful speech failure handling

### Session 10: Voice UX and Natural Conversation (2-3 hours)

**Goal**: Create natural, responsive voice interactions

**Topics**:
- Interruption Handling: Natural conversation flow
- Audio Feedback: Thinking sounds and confirmations
- Barge-In Support: User-friendly interruptions
- Voice Personality Tuning: Warm, engaging presence
- Conversation Flow: Natural turn-taking

**Key Deliverables**:
- Natural Voice Coach v2: Fluid conversations
- UX Metrics: Interruption handling success
- Audio Cue Library: Non-verbal feedback
- Personality Settings: Optimized voice parameters
- Flow Validation: Natural conversation testing

## Phase 3: Evening, Weekly Synthesis & Production (14-16 hours)

### Session 11: Evening Check-Out Implementation (4-5 hours)

**Goal**: Create evening reflection agent that connects to morning sessions

**Topics**:
- Evening Coach Agent: Retrospective-focused personality
- Morning Session Linking: Reference specific morning goals
- Deep Thoughts Evolution: Append evening insights to morning report
- Evening-Specific Evals: Progress assessment, learning extraction
- Session Continuity: Seamless morning-to-evening flow

**Key Deliverables**:
- Evening Coach Agent: Specialized retrospective agent
- Session Linking System: Connect morning/evening sessions
- Evolving Deep Thoughts: Single daily report that grows
- Evening Evaluation Suite: Reflection quality metrics
- Integrated Daily Flow: Complete morning-evening cycle

### Session 12: Weekly Synthesis and Meta-Analysis (3-4 hours)

**Goal**: Build weekly status reports that synthesize multiple Deep Thoughts

**Topics**:
- Report Selection UI: Choose 3-10 Deep Thoughts by date
- Pattern Synthesis: Identify themes across selected reports
- Sentiment Analysis: Track emotional journey through the week
- Meta-Cognitive Question: "What do you believe now that you didn't before?"
- Weekly Evaluation: Progress feeling vs healthy skepticism balance

**Key Deliverables**:
- Connect together morning and evening sessions pairwise for same day with a common markdown file
- Weekly Report Generator: Synthesize multiple sessions, overview of week's problems and solutions, Stories to keep, question: "what do I believe now, I didn't before?"
- Date Selection Interface: User-friendly report picker
- Pattern Recognition Engine: Cross-session analysis
- Sentiment Tracker: Emotional journey visualization
- Weekly Eval Framework: Balance optimism with hunger

### Session 13: Redis Event-Driven Architecture (2-3 hours)

**Goal**: Scale to production-ready infrastructure for multi-user support

**Topics**:
- Redis Pub/Sub implementation
- Event bus migration from in-memory
- Multi-user conversation handling
- Event replay and debugging tools
- Performance monitoring

**Key Deliverables**:
- Redis-Powered System: Production infrastructure
- Event Replay Tools: Debugging capabilities
- Multi-User Support: Concurrent conversations
- Monitoring Dashboard: System health metrics
- Migration Playbook: Zero-downtime transition

### Session 14: System Integration and Reliability (3-4 hours)

**Goal**: Harden system for production deployment

**Topics**:
- Error Recovery Patterns: Graceful failure handling
- Health Monitoring: Proactive issue detection
- Backup Systems: Data persistence and recovery
- Load Testing: Stress test at scale
- Production Readiness: Final hardening

**Key Deliverables**:
- Production System: 99.9% uptime capable
- Recovery Procedures: Automated error handling
- Health Dashboard: Real-time monitoring
- Load Test Results: Proven scalability
- Deployment Guide: Production procedures

### Session 15: Production Voice Deployment (2-3 hours)

**Goal**: Deploy complete voice coaching system

**Topics**:
- Docker Containerization: Package full system
- LiveKit Cloud Setup: Production configuration
- Voice Quality Monitoring: Track performance
- Cost Management: Optimize voice expenses
- Continuous Improvement: Feedback loops

**Key Deliverables**:
- Deployed Voice System: Live production coach
- Analytics Dashboard: Voice quality metrics
- Cost Report: Voice operation expenses
- Deployment Playbook: Reproducible process
- Improvement Roadmap: Data-driven enhancements

## The Evolution Pattern

Every session follows this rhythm:
1. **Measure Current State**: How good is your coach now?
2. **Identify Improvement**: What specific aspect needs work?
3. **Implement Enhancement**: Add new capability incrementally
4. **Validate Impact**: Prove the improvement with data
5. **Document Learning**: Capture what worked for future reference
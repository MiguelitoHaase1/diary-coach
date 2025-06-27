# Learning Ledger - AI-Assisted Development Journey

## Core Learning Objectives
Generally, I want to acquire hands-on technical enough to build sophisticated AI systems with Claude Code/Cursor as primary coding partners. Particularly:

**Environment integration**: I want to learn how to seamlessly integrate with existing repos and developer workflows - so I as a product manager can integrate into the work of software developers.

**Context Engineering**: I want to learn how to provide the right kind of context at the right time for the right LLMs, for them to work efficiently - alone and together.

**Agent-to-Agent frameworks**: I want to learn how to make LLM agents work together best.

**Test Driven Development (TDD)**: I want to learn how to use tests to develop and improve software in small and efficient increments - even before integrating with the system.

**Evaluations for LLMs/agents**: I want to learn how to setup and use Evaluations of LLM outputs (and even processes), to always have an understanding of what works/doesn't work.

---

## Phase 1 Immediate Learning Priorities (Next 4-6 weeks)

### 🔴 **CRITICAL BLOCKER: TDD + Evals Workflow Setup**
**Gap**: No hands-on experience with Test-Driven Development or evaluation frameworks  
**Learning Need**: Establish a working TDD rhythm with Claude Code where tests drive feature development  
**Success Criteria**: 
- Can write failing tests before implementing features
- Have basic evaluation metrics running automatically
- Understand the red-green-refactor cycle in practice

**Learning Approach**:
- Start with Lesson 1 from roadmap but focus entirely on the TDD mechanics
- Use Claude Code to learn pytest patterns through actual implementation
- Build simple conversation evaluation from scratch before using LangChain evaluators

### 🟡 **SUPPORTING SKILL: Python Project Structure**
**Current State**: Basic Python syntax, but unfamiliar with professional project organization  
**Learning Need**: Understand how to structure a Python project for testability and maintainability  
**Focus Areas**: 
- Package structure (`src/` layout vs flat layout)
- Import patterns and module organization
- Configuration management (environment variables, config files)

### 🟡 **SUPPORTING SKILL: Redis Pub/Sub Basics**
**Current State**: Theoretical understanding of event-driven architecture  
**Learning Need**: Hands-on experience with Redis as an event bus  
**Focus Areas**:
- Basic Redis operations (publish/subscribe)
- Message serialization patterns
- Async Python with Redis

---

## AI Collaboration Learning Strategy

### **Primary Learning Mode: Claude Code Partnership**
- Use Claude Code for all implementation work
- Focus on understanding the "why" behind code decisions, not memorizing syntax
- Ask Claude Code to explain trade-offs and alternatives before implementing
- Request Dojo documents after each session for deeper learning

### **Secondary Learning Mode: Claude Chat Exploration**
- Use claude.ai conversations for architectural discussions
- Explore concepts before diving into implementation
- Debug understanding when Claude Code suggestions don't make sense
- Review and refine learning approaches

### **Learning Rhythm** (2-4 hours/week)
- **Session 1**: 1-2 hours with Claude Code on actual implementation
- **Session 2**: 30-60 minutes with Claude Chat on concept exploration
- **Session 3**: 30-60 minutes reviewing/refactoring with Claude Code

---

## Knowledge Gaps by Technical Area

### 🔴 **RED (Must Learn for Project Success)**

#### **Testing & TDD Workflows**
- pytest fixtures and parametrized testing
- Mocking and test doubles for AI API calls
- Test organization and discovery patterns
- Continuous testing workflows (watch mode, etc.)

#### **Async Python Programming**
- async/await patterns for Redis and API calls
- Event loop understanding for real-time systems
- Error handling in async contexts
- Testing async code

#### **LLM Application Evaluation**
- Designing metrics for conversation quality
- Automated evaluation pipelines
- LangChain evaluation patterns vs custom approaches
- Cost-effective evaluation strategies

### 🟡 **YELLOW (Strengthen Through Project Work)**

#### **Event-Driven Architecture**
- Message queue patterns and reliability
- Event schema design with Pydantic
- Agent communication patterns
- State management across distributed components

#### **API Integration & Development**
- Anthropic SDK usage patterns
- Error handling and retry logic
- Rate limiting and cost management
- FastAPI basics (later phases)

#### **Database Integration**
- SQLite for conversation storage
- Data modeling for conversational AI
- Query optimization for context retrieval
- Migration patterns

### ⚪ **WHITE (Learn Later/As Needed)**

#### **Production Deployment**
- Docker containerization
- Cloud deployment patterns
- Monitoring and logging
- Security hardening

#### **Voice Integration (Phase 4)**
- LiveKit SDK patterns
- Audio processing workflows
- Real-time communication handling
- Voice UX design

---

## Learning Success Metrics

### **Week 1-2: TDD Foundation**
- [ ] Can write a failing test and make it pass with Claude Code assistance
- [ ] Understand pytest project structure and can run tests confidently
- [ ] Have basic conversation evaluation metric working

### **Week 3-4: Event Architecture**
- [ ] Redis pub/sub working with proper message schemas
- [ ] Can debug event flow issues using Redis CLI
- [ ] Basic agent communication patterns implemented

### **Week 5-6: Agent Implementation**
- [ ] First coaching agent responding to events
- [ ] Integration tests passing for agent interactions
- [ ] Evaluation metrics providing useful feedback

### **Ongoing Success Indicators**
- Tests drive feature development (not written after)
- Can explain architectural decisions made with Claude Code
- Comfortable debugging issues using appropriate tools
- Learning compounds - new features build on previous work

---

## Learning Failure Patterns to Avoid

### **Anti-Pattern 1: Tutorial Hell**
- **Risk**: Getting stuck in learning mode without building
- **Mitigation**: Always learn through building the actual diary coach project

### **Anti-Pattern 2: Copy-Paste Development**
- **Risk**: Using Claude Code output without understanding
- **Mitigation**: Always ask "why" and request explanations of architectural choices

### **Anti-Pattern 3: Perfect Code Paralysis**
- **Risk**: Over-engineering early features
- **Mitigation**: Focus on making tests pass, refactor later

### **Anti-Pattern 4: Test-After Development**
- **Risk**: Falling back to implementation-first habits
- **Mitigation**: Use Claude Code to enforce TDD discipline

---

## Knowledge Amplification Strategy

### **Leverage Existing Strengths**
- **Product Strategy**: Use to define meaningful evaluation metrics
- **Prompt Engineering**: Apply to get better assistance from Claude Code
- **System Thinking**: Apply to architectural decisions and trade-offs

### **Build on Adjacent Skills**
- **Agile Experience**: Apply to TDD red-green-refactor cycles
- **UX Design**: Apply to conversation design and agent personality
- **Team Leadership**: Apply to organizing code for maintainability

---

## Tools and Environment Setup

### **Primary Development Environment**
- **Cursor**: Main coding interface with Claude Code
- **claude.ai**: Conceptual discussions and learning guidance
- **pytest**: Testing framework and TDD workflow
- **Redis**: Local instance for event bus development

### **Learning Support Tools**
- **GitHub**: Version control and progress tracking
- **Documentation**: Maintain session logs and dojo documents
- **Evaluation Metrics**: Custom scoring system for conversation quality

---

*This ledger will be updated after each learning session to track progress and refine approach based on what works in practice.*
# Session 8: Three-Stage Multi-Agent System

## Executive Summary

Transform the single-agent coaching system into a sophisticated three-stage multi-agent orchestration with 7 specialized agents: Coach, Memory, MCP, Personal Content, Orchestrator, Reporter, and Evaluator. The architecture prioritizes immediate coach responsiveness while progressively enhancing conversations with context from Memory, MCP, and Personal Content agents. The Orchestrator activates only after problem clarity, and all agents collaborate to generate a unified Deep Thoughts report with integrated evaluations.

**Duration**: 4-5 hours (Consider splitting into 8a and 8b if complexity emerges)

## Session Context

This session builds on:
- **Session 5**: LangGraph architecture migration
- **Session 6**: Personal context integration with relevance scoring
- **Session 7**: Fixed evaluation system with 5 criteria

The Personal Content Agent from Session 6 becomes one of our 7 core agents, leveraging the existing relevance scoring and document loading infrastructure.

## Architecture Overview

```
SEVEN AGENTS:
1. Coach Agent - Primary conversationalist
2. Memory Agent - Past conversation access
3. MCP Agent - Todoist integration only (from Session 6 work)
4. Personal Content Agent - User's core beliefs & personal docs (from Session 6)
5. Orchestrator Agent - Multi-agent coordination
6. Reporter Agent - Deep Thoughts synthesis
7. Evaluator Agent - Quality assessment (5 criteria)

PREPARATION PHASE (Before User Interaction):
┌─────────────────┐     ┌──────────────┐
│  Memory Agent   │────▶│              │
├─────────────────┤     │ Coach Agent  │
│ Past Convos     │     │ (Pre-loaded) │
└─────────────────┘     │              │
┌─────────────────┐     │              │
│   MCP Agent     │────▶│              │
├─────────────────┤     └──────────────┘
│ Todoist/Calendar│
└─────────────────┘

STAGE 1 - EXPLORATION (Coach-Led):
User ←→ Coach Agent (Can autonomously call other agents)
         │
         └─→ Available: [Memory, MCP, Personal Content]

STAGE 2 - ORCHESTRATED GATHERING (Problem Identified):
User ←→ Coach ←─ Orchestrator Agent
                     │
                     ├─→ Personal Content Agent
                     ├─→ Memory Agent
                     └─→ MCP Agent

STAGE 3 - SYNTHESIS:
Reporter Agent → Deep Thoughts Report (Opus 4)
    ├─→ Aggregates all agent inputs
    └─→ Evaluator Agent → Embeds scores (A-E) in report
```

## Pre-Session 8 Status

From our test failure analysis (Session 8.0), we have:
- ✅ DiaryCoach now inherits from BaseAgent
- ✅ Agent tests fixed (13/13 passing)
- ✅ Removed obsolete analyzer tests
- 📊 21 tests still failing (mostly integration tests that will be rewritten)

## Implementation Increments

### Increment 0: Fix Critical Integration Tests (20 min)
**Purpose**: Fix high-value tests that will help validate multi-agent system

**Approach**:
- Fix `test_coach_node.py` - Update for BaseAgent inheritance
- Fix `test_prompt_loader.py` - Simple prompt loading issue
- Defer other integration tests until relevant agent is implemented

**Key Deliverables**:
- Coach node tests passing
- Prompt loader test passing
- Clear which tests to fix with each agent

**Testing Checkpoint**:
- 🤖 AI: Run `pytest tests/test_coach_node.py tests/test_prompt_loader.py -v`
- 🔴 HUMAN: Quick test that basic coach still responds properly

### Increment 1: Agent Interface Foundation (30 min)
**Purpose**: Establish clean agent abstraction that wraps LangGraph nodes

**Approach**: 
- ✅ Already have `BaseAgent` protocol with standard interface
- Define agent communication channels in LangGraph state
- ✅ Already have agent registry for dynamic lookup
- Test inter-agent messaging patterns

**Key Deliverables**:
- Agent communication state schema
- Inter-agent message passing tests
- Update coach node to use new patterns

**Testing Checkpoint**:
- 🤖 AI: Run `pytest tests/agents/ -v` to ensure all agent tests still pass
- 🤖 AI: Run new inter-agent communication tests
- 🔴 HUMAN: Test basic coach interaction still works (should be unchanged)

### Increment 2: Memory Agent Implementation (45 min)
**Purpose**: Pre-load conversation context before coaching begins

**Approach**:
- Read past conversations
- Extract relevant patterns and topics
- Create summary for coach consumption
- Handle "remember when..." queries

**Key Deliverables**:
- Working Memory Agent with conversation loading
- Pattern extraction logic
- Tests with mock conversation data

**Tests to Fix**:
- `test_memory_recall.py` - Will be rewritten for new Memory Agent
- `test_memory_recall_integration.py` - Update after Memory Agent works

**Testing Checkpoint**:
- 🤖 AI: Run `pytest tests/agents/test_memory_agent.py -v` (new tests)
- 🤖 AI: Verify preparation phase loads past conversations
- 🔴 HUMAN: Find out where the prompt for this agent is - and improve it
- 🔴 HUMAN: Test a conversation that references past interactions
- 🔴 HUMAN: Ask "remember when we discussed X?" and verify context

### Increment 3: Personal Content Agent Integration (30 min)
**Purpose**: Leverage Session 6's personal context system as a dedicated agent

**Approach**:
- Wrap existing PersonalContextNode into agent interface
- Use established relevance scoring (pattern matching + LLM)
- Access `/docs/personal/` markdown files
- Provide context about user's core beliefs and history

**Key Deliverables**:
- Personal Content Agent using Session 6 infrastructure
- Integration with agent communication channels
- Tests using existing personal documentation

**Tests to Fix**:
- `test_implicit_context_injection.py` - Update for new agent architecture

**Testing Checkpoint**:
- 🤖 AI: Run `pytest tests/agents/test_personal_content_agent.py -v`
- 🤖 AI: Run fixed `test_implicit_context_injection.py`
- 🔴 HUMAN: Find out where the prompt for this agent is - and improve it
- 🔴 HUMAN: Ask about a topic covered in your personal docs
- 🔴 HUMAN: Verify coach references your core beliefs naturally

### Increment 4: MCP Agent - Todoist Only (45 min)
**Purpose**: Clean abstraction over Todoist MCP server (building on Session 6 lessons)

**Approach**:
- Single agent for Todoist MCP connection only
- Reuse Session 6's MCP client fixes (async cleanup, tool naming, TextContent parsing)
- Provide unified interface to other agents
- Robust error handling for MCP failures

**Key Deliverables**:
- MCP Agent focused solely on Todoist
- Error isolation from coaching flow
- Tests using real Todoist MCP connection (no mocks!)
- Clear path for future MCP server additions

**Tests to Fix**:
- `test_mcp_todo_integration.py` - Update for new MCP Agent interface

**Testing Checkpoint**:
- 🤖 AI: Run `pytest tests/agents/test_mcp_agent.py -v` with real MCP server
- 🤖 AI: Run fixed `test_mcp_todo_integration.py`
- 🔴 HUMAN: Start MCP server and verify connection
- 🔴 HUMAN: Find out where the prompt for this agent is - and improve it
- 🔴 HUMAN: Ask "what should I work on today?" - verify Todoist tasks appear
- 🔴 HUMAN: Turn off MCP server and verify graceful degradation
- 🔴 HUMAN: **DECISION POINT**: Continue to 8b or complete in one session?

### Increment 5: Coach Agent Enhancement (45 min)
**Purpose**: Enable coach to autonomously call other agents during Stage 1

**Approach**:
- Add agent-calling capability to coach prompt
- Implement decision logic for when to call agents
- Maintain conversation flow during agent calls
- Test natural integration patterns

**Key Deliverables**:
- Enhanced coach with tool-calling ability
- Natural conversation flow preservation
- Tests for various calling scenarios

**Testing Checkpoint**:
- 🤖 AI: Run `pytest tests/agents/test_coach_agent.py -v` with enhancements
- 🤖 AI: Test coach autonomously calls Memory/MCP/Personal agents
- 🔴 HUMAN: Find out where the prompt for this agent is - and improve it
- 🔴 HUMAN: Have a natural conversation and observe agent calls
- 🔴 HUMAN: Verify coach doesn't over-call agents (stays natural)
- 🔴 HUMAN: Test "What did we discuss last week about X?"

### Increment 6: Orchestrator Agent & Stage Transitions (45 min)
**Purpose**: Coordinate multi-agent collaboration after problem identification

**Approach**:
- Define clear stage transition triggers
- Implement orchestrator activation logic
- Coordinate parallel agent queries
- Aggregate results for coach consumption

**Key Deliverables**:
- Working orchestrator with coordination logic
- Stage transition detection
- Parallel execution tests

**Tests to Fix**:
- `test_integration/test_session_1_e2e.py` - Update for new orchestration patterns

**Testing Checkpoint**:
- 🤖 AI: Run `pytest tests/agents/test_orchestrator_agent.py -v`
- 🤖 AI: Test parallel agent execution with timing
- 🔴 HUMAN: Find out where the prompt for this agent is - and improve it
- 🔴 HUMAN: Have conversation that triggers Stage 2 (problem identified)
- 🔴 HUMAN: Observe orchestrator coordinating multiple agents
- 🔴 HUMAN: Verify smooth transition feels natural, not robotic

### Increment 7: Reporter & Evaluator Integration (60 min)
**Purpose**: Generate unified Deep Thoughts with embedded evaluations (5 criteria)

**Approach**:
- Reporter aggregates all agent contributions
- Evaluator assesses using 5 criteria from Session 7 (not 7)
- Single markdown output with scores inline
- Maintain Session 7's evaluation improvements (proper JSON parsing, STANDARD tier)

**Key Deliverables**:
- Unified Deep Thoughts generation with Sonnet 4
- Integrated evaluation scores (5 criteria: A-E)
- Complete end-to-end flow test
- Proper LangSmith tracing throughout

**Tests to Fix**:
- `test_personas.py` - Update for new 5-criteria evaluation system
- `test_persona_evaluator.py` - Rewrite for Evaluator Agent
- `test_session_2_e2e.py` - Full integration tests for new architecture

**Testing Checkpoint**:
- 🤖 AI: Run `pytest tests/agents/test_reporter_agent.py test_evaluator_agent.py -v`
- 🤖 AI: Run fixed persona and evaluation tests
- 🤖 AI: Full test suite run: `pytest --tb=short`
- 🔴 HUMAN: Find out where the prompt for this agent is - and improve it
- 🔴 HUMAN: Complete full conversation flow (morning greeting → problem → solution)
- 🔴 HUMAN: Review generated Deep Thoughts report
- 🔴 HUMAN: Verify all 5 evaluation criteria (A-E) are scored correctly
- 🔴 HUMAN: Check LangSmith for full multi-agent trace

### For the AI Coder:
1. **Don't Mock MCP Servers**: Use real connections or skip the test
2. **Don't Mock LangSmith**: Use real aevaluate() calls, never hardcode scores
3. **Avoid Tight Coupling**: Agents should communicate through state, not direct calls
4. **Respect Stage Boundaries**: Don't let orchestrator activate too early
5. **Preserve Coach Autonomy**: Stage 1 should feel natural, not robotic
6. **Handle Async Properly**: Multiple agents = complex async patterns
7. **Parse LLM Output Robustly**: Use Session 7's JSON parsing patterns for all LLM responses

### For the Human:
1. **MCP Server Setup**: Ensure servers are running before testing
2. **Conversation Data**: Need realistic past conversations for Memory Agent
3. **Personal Content**: Create meaningful test documents, not lorem ipsum
4. **API Rate Limits**: Be aware of limits when testing parallel agents
5. **Debugging Complexity**: Use LangSmith extensively for multi-agent traces

## Testing Strategy

### Continuous Testing Philosophy:
**Every increment includes both automated and manual testing to catch issues immediately**

### Test Fixing Approach:
1. **Increment 0**: Fix only critical tests that block development
2. **Per-Agent Fixing**: Fix relevant tests as each agent is implemented
3. **Defer Complex Tests**: Leave integration tests until architecture stabilizes
4. **Rewrite vs Patch**: Most integration tests need full rewrite for multi-agent

### Testing Checkpoints:
- 🤖 **AI Responsibilities**: Run automated tests after each change
- 🔴 **Human Responsibilities**: Manual testing for UX and integration
- 🟡 **Joint Review**: AI and Human review failures together immediately

### Unit Tests:
- Each agent in isolation with defined inputs/outputs
- Stage transition logic with various conversation patterns
- Agent communication via state channels

### Integration Tests:
- Full preparation phase execution
- Stage 1 → 2 transition scenarios
- Complete flow from user input to Deep Thoughts
- Error scenarios (MCP down, no memory, etc.)

### Performance Tests:
- Preparation phase completes in < 3 seconds
- Stage 1 responses maintain sub-second latency
- Parallel agent execution in Stage 2

### Deferred Test Fixes:
These tests will be addressed after Session 8 or rewritten entirely:
- `test_otel_tracing.py` - Low priority, not blocking
- Old integration tests that assume single-agent architecture

## Success Criteria

1. **Immediate Responsiveness**: Coach responds without waiting for context
2. **Progressive Enhancement**: Context enriches conversation naturally
3. **Clean Transitions**: Users feel the flow, not the stages
4. **Unified Output**: Single Deep Thoughts report, not fragmented files
5. **Robust Isolation**: Individual agent failures don't crash the system
6. **Test Coverage**: Each increment tested both automatically and manually
7. **Immediate Fixes**: Issues caught and fixed within the increment

## Learning Opportunities

Based on your learning ledger and Session 7 lessons:
1. **Async Coordination**: Managing multiple parallel agents
2. **State Design**: Complex state with multiple agent contributions  
3. **Error Boundaries**: Isolating failures in distributed systems
4. **Prompt Engineering**: Making coach agent-calling feel natural
5. **System Observability**: Tracking multi-agent interactions in LangSmith
6. **LLM Output Parsing**: Apply Session 7's robust JSON extraction patterns
7. **External Service Integration**: Never mock LangSmith or MCP services

## 🔴 HUMAN TASKS - AFTER SESSION

### Immediate Actions:
- [ ] Test with your real Todoist data
- [ ] Add more personal documentation files to `/docs/personal/`
- [ ] Run full conversation to validate stage transitions
- [ ] Check LangSmith for bottlenecks in parallel execution

### Optimization Opportunities:
- [ ] Fine-tune stage transition triggers based on real usage
- [ ] Adjust which agents are available in Stage 1
- [ ] Optimize preparation phase for your specific context
- [ ] Plan future MCP server additions (calendar, email, notes)
- [ ] Update personal content files with more core beliefs/values

### Future Enhancements:
- [ ] Add agent result caching for common queries
- [ ] Implement agent priority system for Stage 2
- [ ] Create agent-specific evaluation metrics
- [ ] Build debugging UI for agent interactions

## Session Split Consideration

If this session proves too large, consider splitting:
- **Session 8a**: Agents 1-4 (Foundation, Memory, Personal Content, MCP)
- **Session 8b**: Agents 5-7 and full orchestration (Coach enhancement, Orchestrator, Reporter/Evaluator)

Make this decision after Increment 4 based on complexity encountered.
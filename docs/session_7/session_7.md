# Session 7: Parallel Multi-Agent Orchestration with Dedicated MCP Agent

## Executive Summary

**Goal**: Implement parallel orchestration with dedicated agents for clean separation of concerns, solving current MCP data capture issues through explicit agent architecture.

**Key Innovation**: Move from integrated MCP within coach to dedicated MCP Agent that handles all external data fetching, enabling zero-latency coaching with progressive context enhancement.

**Duration**: 4-5 hours across 5-6 increments

**Success Criteria**:
- Coach responds immediately without waiting for context
- MCP Agent fetches and provides todos reliably
- Memory Agent manages conversation history independently
- Deep Report Agent generates insights on demand
- All agents use dedicated prompt files for easy engineering

## Human Tasks (Before Starting)

### 🔴 REQUIRED SETUP:
- [ ] Ensure `.env` has `ANTHROPIC_API_KEY` and `TODOIST_API_TOKEN`
- [ ] Verify MCP server is installed: `npm list -g @modelcontextprotocol/server-todoist`
- [ ] Create `/docs/memory/` folder if not exists
- [ ] Have at least 5 todos in your Todoist for testing

### 📋 DURING SESSION:
- [ ] Review and customize agent prompts as they're created
- [ ] Test parallel orchestration with real conversations
- [ ] Monitor MCP data capture in debug logs

### ✅ AFTER SESSION:
- [ ] Update agent prompts based on your preferences
- [ ] Add more MCP servers (calendar, gmail) if desired
- [ ] Document any custom prompt engineering patterns

## Architecture Overview

```
User Message
    ↓
Orchestrator Agent (Parallel Dispatcher)
    ├─→ Coach Agent (Fast Path - Immediate Response)
    │     ↓
    │   Stream Response to User
    │
    └─→ Context Pipeline (Slow Path - Background)
          ├─→ MCP Agent (Todos, Calendar, etc.)
          ├─→ Memory Agent (Conversation History)
          └─→ Relevance Scorer
                ↓
             Context Package
                ↓
         Progressive Enhancement
```

## Implementation Approach

### Core Principles
1. **Agent Independence**: Each agent has its own prompt file and clear responsibility
2. **Parallel Execution**: Coach never waits for context - responds immediately
3. **Progressive Enhancement**: Context enriches responses when available
4. **Error Isolation**: MCP failures don't break coaching conversations
5. **Observable Data Flow**: Clear logging of what each agent contributes

### Technical Stack
- **LangGraph**: For parallel orchestration and state management
- **Dedicated Agents**: Each with markdown prompt in `src/agents/prompts/`
- **MCP Client**: Proper async resource management (fixing Session 6 issues)
- **Streaming**: Progressive response enhancement without blocking

## Session Increments

### Increment 7.1: Agent Architecture Foundation (30-45 min)
**Goal**: Create base agent structure with prompt loading

**Implementation**:
```python
# src/agents/base_agent.py
class PromptBasedAgent(BaseAgent):
    """Agent that loads prompts from markdown files"""
    
    def __init__(self, prompt_file: str):
        self.prompt = self.load_prompt(prompt_file)
```

**Key Files**:
- `src/agents/base_agent.py` - Enhanced base with prompt loading
- `src/agents/prompts/orchestrator_prompt.md` - Orchestrator instructions
- `src/agents/orchestrator_agent.py` - Parallel dispatch logic
- `tests/agents/test_prompt_loading.py`

**Success Metrics**:
- All agents load prompts from markdown files
- Prompt hot-reloading capability for development
- Clear agent initialization patterns

### Increment 7.2: MCP Agent with Proper Data Capture (45-60 min)
**Goal**: Dedicated MCP Agent that reliably captures Todoist data

**Implementation Focus**:
- Fix async resource management issues from Session 6
- Proper TextContent parsing and data extraction
- Clear logging of fetched todos
- Error handling that doesn't fail silently

**Key Files**:
- `src/agents/prompts/mcp_agent_prompt.md` - MCP data fetching instructions
- `src/agents/mcp_agent.py` - Dedicated MCP client management
- `src/services/mcp_client.py` - Refactored MCP connection handling
- `tests/agents/test_mcp_agent.py`

**Success Metrics**:
- MCP Agent fetches real todos (not mock data)
- Clear debug logs showing todo content
- Graceful handling of MCP server issues
- No more "using_mock_data: true"

### Increment 7.3: Memory Agent for Conversation History (30-45 min)
**Goal**: Independent memory management with recall capabilities

**Implementation**:
- Load from `/docs/memory/` markdown files
- Manage conversation checkpoints
- Support "remember when..." queries
- Provide relevant history snippets

**Key Files**:
- `src/agents/prompts/memory_agent_prompt.md` - Memory management instructions
- `src/agents/memory_agent.py` - History and document management
- `tests/agents/test_memory_agent.py`

**Success Metrics**:
- Memory Agent provides relevant conversation snippets
- Document loading from memory folder works
- Clear indication of what memories are being used

### Increment 7.4: Parallel Orchestration Graph (45-60 min)
**Goal**: LangGraph implementation of parallel execution

**Implementation Pattern**:
```python
# Parallel execution nodes
coach_future = graph.anode("coach", coach_agent.process)
context_future = graph.anode("context_pipeline", context_orchestrator.process)

# Stream coach response immediately
async for chunk in coach_future:
    yield chunk

# Enhance with context when available
context = await context_future
if context:
    yield enhance_response(context)
```

**Key Files**:
- `src/orchestration/parallel_graph.py` - New parallel orchestrator
- `src/orchestration/context_merger.py` - Progressive enhancement logic
- `tests/orchestration/test_parallel_execution.py`

**Success Metrics**:
- Coach responds in <1 second
- Context arrives 2-5 seconds later
- User sees immediate response with later enhancement
- Parallel execution observable in LangSmith

### Increment 7.5: Deep Report Agent Integration (30-45 min)
**Goal**: On-demand deep analysis without blocking conversation

**Implementation**:
- Separate Deep Report Agent with own prompt
- Triggered by "deep report" command
- Accesses full conversation state
- Generates pinneable insights

**Key Files**:
- `src/agents/prompts/deep_report_prompt.md` - Analysis instructions
- `src/agents/deep_report_agent.py` - Report generation logic
- Integration with existing Deep Thoughts infrastructure

**Success Metrics**:
- Deep reports generated on demand
- Clear separation from coaching flow
- Maintains Session 4's quality standards

### Increment 7.6: Observable Data Flow & Debugging (30-45 min)
**Goal**: Make agent contributions visible and debuggable

**Implementation**:
- Agent contribution tracking in state
- Debug mode showing what each agent provided
- Clear logs of MCP data capture
- Performance metrics for each path

**Key Files**:
- `src/orchestration/agent_observatory.py` - Contribution tracking
- `src/interface/debug_cli.py` - Enhanced CLI with debug mode
- `tests/orchestration/test_observability.py`

**Success Metrics**:
- Can see exactly what each agent contributed
- MCP data capture is clearly logged
- Performance metrics for parallel paths
- Easy debugging of context integration

## Common Pitfalls to Avoid

### For Claude Code:
1. **Don't Mock MCP**: Use real MCP server connections - mocking hides integration issues
2. **Avoid Coupling**: Agents should not know about each other's internals
3. **Test Parallelism**: Ensure tests validate actual parallel execution, not sequential
4. **Resource Cleanup**: Proper async context managers for MCP connections

### For You (The User):
1. **MCP Server Running**: Ensure Todoist MCP server is actually running before testing
2. **API Tokens**: Both ANTHROPIC_API_KEY and TODOIST_API_TOKEN must be valid
3. **Prompt Engineering**: Take time to customize agent prompts for your style
4. **Debug First**: Use debug mode to verify MCP data is being captured

## Learning Opportunities

Given your learning ledger focus areas:

### Agent-to-Agent Frameworks
- Explore how agents communicate through shared state
- Understand parallel vs sequential orchestration patterns
- Learn about agent contribution merging strategies

### Context Engineering
- See how different agents require different context
- Practice prompt engineering for specialized agents
- Understand context budget management

### Test Driven Development
- Write tests for parallel execution patterns
- Test agent independence and error isolation
- Validate progressive enhancement behavior

## Architecture Benefits

### Why This Solves Your Current Issues:

1. **MCP Data Capture**: Dedicated MCP Agent with proper logging ensures you see all fetched data
2. **Clear Responsibilities**: Each agent does one thing well with its own prompt
3. **Debugging**: Observable data flow shows exactly what each agent contributes
4. **Performance**: Parallel execution means coaching never waits for external data
5. **Flexibility**: Easy to add new agents or modify prompts without touching others

## Expected Outcomes

After this session, you'll have:
- ✅ Immediate coach responses (no context blocking)
- ✅ Reliable MCP data capture with clear visibility
- ✅ Independent agents with customizable prompts
- ✅ Progressive context enhancement
- ✅ Clear debugging of what each agent provides
- ✅ Foundation for adding more MCP sources (calendar, email)

## Next Steps Preview

With parallel orchestration complete, future enhancements become trivial:
- Add Calendar MCP Agent (Session 7.5 extension)
- Implement Gmail MCP Agent for email context
- Create Synthesis Agent for weekly reports
- Add Performance Monitoring Agent

The architecture scales horizontally - just add more agents to the context pipeline!
# Session 6: Personal Context Integration

## Executive Summary

Transform the diary coach from a stateless conversationalist into a context-aware personal assistant that implicitly enhances conversations with your todos, documents, and conversation history. Build on the LangGraph foundation to create intelligent context routing, relevance scoring, and seamless memory integration.

**Primary Goal**: Broader personal context integration (todos, documents) with session-to-session memory as a secondary benefit.

## Session Goals

1. **Context Loading Infrastructure**: Build LangGraph nodes that fetch and process personal context
2. **Intelligent Context Routing**: Dynamic graph edges based on conversation relevance
3. **Implicit Context Enhancement**: Seamlessly weave relevant context into coaching
4. **Memory Persistence**: Leverage LangGraph cloud checkpointing for state management
5. **Explicit Recall API**: Enable "remember when..." queries as a bonus feature

## Technical Approach

### Core Architecture
- **Context Nodes**: Separate LangGraph nodes for todos (MCP), documents (markdown), and conversation history
- **Relevance Scoring**: Lightweight scoring system to determine which context to fetch
- **State Channels**: Dedicated channels for context data, relevance scores, and memory decisions
- **Cloud Checkpointing**: Use LangGraph's built-in persistence for zero-config state management

### Key Design Decisions
1. **Lazy Loading**: Only fetch context when relevance score exceeds threshold
2. **Context Budget**: Limit context injection to preserve conversation flow
3. **Privacy Layers**: Separate channels for different sensitivity levels
4. **Incremental Enhancement**: Start with todos, then add documents, then conversation history

## Increment Breakdown

### Increment 6.1: Context Node Architecture (30-45 min)
**Goal**: Create the foundational context-aware graph structure

**Test First**:
```python
async def test_context_aware_graph_structure():
    """Graph should have context nodes that can be conditionally executed"""
    graph = create_context_aware_graph()
    
    # Graph should have new context nodes
    assert "todo_context" in graph.nodes
    assert "document_context" in graph.nodes
    assert "conversation_memory" in graph.nodes
    
    # Should have relevance scoring node
    assert "context_relevance_scorer" in graph.nodes
    
    # Should maintain existing coach functionality
    result = await graph.ainvoke({
        "messages": [HumanMessage("Good morning!")],
        "context_enabled": True
    })
    assert result["coach_response"] is not None
```

**Implementation**:
- Extend existing LangGraph with new context nodes
- Add `context_relevance_scorer` node before coach
- Create state channels for context data
- Implement conditional edges based on relevance scores

**Learning Focus**: LangGraph's conditional routing and sub-graph composition

### Increment 6.2: MCP Todo Integration (45-60 min)
**Goal**: Connect to Todoist via MCP server node

**Test First**:
```python
async def test_mcp_todo_context_node():
    """MCP node should fetch relevant todos based on conversation"""
    state = {
        "messages": [HumanMessage("I need to work on the API integration today")],
        "context_relevance": {"todos": 0.8}
    }
    
    result = await todo_context_node(state)
    
    # Should fetch todos when relevance is high
    assert "todo_context" in result
    assert "API" in str(result["todo_context"])
    
    # Should track context usage
    assert result["context_usage"]["todos_fetched"] == True
```

**Implementation**:
- Create MCP client node for Todoist
- Implement relevance-based filtering
- Add todo context to coach state
- Track context usage in LangSmith

**Learning Focus**: MCP (Model Context Protocol) integration patterns

### Increment 6.3: Relevance Scoring System (30-45 min)
**Goal**: Intelligent context detection without explicit requests

**Test First**:
```python
async def test_context_relevance_scoring():
    """Should score context relevance based on conversation content"""
    scorer = ContextRelevanceScorer()
    
    # High relevance for task-related conversation
    state = {"messages": [HumanMessage("What should I prioritize today?")]}
    scores = await scorer.score(state)
    assert scores["todos"] > 0.7
    assert scores["calendar"] > 0.5
    
    # Low relevance for emotional check-in
    state = {"messages": [HumanMessage("I'm feeling overwhelmed")]}
    scores = await scorer.score(state)
    assert scores["todos"] < 0.3
```

**Implementation**:
- Lightweight LLM-based relevance scorer (Haiku/GPT-4o-mini)
- Pattern matching for common context triggers
- Configurable thresholds per context type
- Performance optimization for low latency

**Learning Focus**: Efficient LLM usage for routing decisions

### Increment 6.4: Implicit Context Injection (45-60 min)
**Goal**: Seamlessly enhance coach responses with relevant context

**Test First**:
```python
async def test_implicit_context_enhancement():
    """Coach should naturally incorporate relevant context"""
    # Setup state with high-relevance todos
    state = {
        "messages": [HumanMessage("What's my biggest lever today?")],
        "todo_context": ["Finish Q4 planning", "Review team proposals"],
        "context_relevance": {"todos": 0.9}
    }
    
    response = await enhanced_coach_node(state)
    
    # Should reference todos without being explicit
    assert "Q4" in response["content"] or "planning" in response["content"]
    
    # Should maintain coaching style
    assert "?" in response["content"]  # Still asks questions
```

**Implementation**:
- Modify coach prompt to include context instructions
- Create context formatting utilities
- Implement context budget management
- Add context attribution tracking

**Learning Focus**: Prompt engineering for seamless context integration

### Increment 6.5: Cloud Checkpoint Integration (30-45 min)
**Goal**: Enable persistent memory across sessions

**Test First**:
```python
async def test_conversation_memory_persistence():
    """Should remember previous conversations via checkpoints"""
    graph = create_context_aware_graph()
    
    # First conversation
    thread_1 = {"configurable": {"thread_id": "user-123"}}
    await graph.ainvoke({
        "messages": [HumanMessage("I'm struggling with delegation")]
    }, thread_1)
    
    # Second conversation should have access to history
    thread_2 = {"configurable": {"thread_id": "user-123"}}
    state = await graph.aget_state(thread_2)
    
    assert len(state.values["conversation_history"]) > 0
    assert "delegation" in str(state.values["conversation_history"])
```

**Implementation**:
- Configure LangGraph cloud checkpointing
- Create conversation history summarizer
- Implement memory relevance scoring
- Add privacy controls for sensitive topics

**Learning Focus**: LangGraph's checkpoint system and state persistence

### Increment 6.6: Document Context Integration (45-60 min)
**Goal**: Load and use markdown documents as context

**Test First**:
```python
async def test_document_context_loading():
    """Should load relevant documents based on conversation"""
    state = {
        "messages": [HumanMessage("Let's review my core beliefs")],
        "context_relevance": {"documents": 0.9}
    }
    
    result = await document_context_node(state)
    
    # Should load core beliefs document
    assert "core_beliefs" in result["document_context"]
    assert len(result["document_context"]["core_beliefs"]) > 0
```

**Implementation**:
- Markdown document loader node
- Document relevance scoring
- Chunking for large documents
- Caching for frequently accessed docs

**Learning Focus**: Document processing and retrieval patterns

### Increment 6.7: Explicit Memory Recall (30-45 min)
**Goal**: Enable "remember when..." queries

**Test First**:
```python
async def test_explicit_memory_recall():
    """Should handle explicit memory queries"""
    state = {
        "messages": [HumanMessage("Remember what we discussed about delegation?")],
        "conversation_history": [
            {"date": "2024-12-15", "topic": "delegation", "insights": "..."}
        ]
    }
    
    result = await memory_recall_node(state)
    
    # Should retrieve relevant memory
    assert "memory_recall" in result
    assert "delegation" in result["memory_recall"]
    
    # Should format as coach response
    assert result["recall_mode"] == True
```

**Implementation**:
- Memory query detection node
- Conversation history search
- Memory formatting for coach responses
- Explicit vs implicit memory handling

**Learning Focus**: Graph branching for different conversation modes

## Success Metrics

### Technical Metrics
- [ ] Context fetch latency < 500ms
- [ ] Relevance scoring accuracy > 80%
- [ ] Memory persistence working across sessions
- [ ] All 35+ existing tests still passing

### User Experience Metrics
- [ ] Context enhances conversation without disrupting flow
- [ ] Coach references todos/documents naturally
- [ ] Memory recall feels conversational, not robotic
- [ ] Privacy controls working as expected

### Learning Metrics
- [ ] Understand LangGraph conditional routing
- [ ] Can implement custom graph nodes
- [ ] Grasp state channel design patterns
- [ ] Know how to use cloud checkpointing

## Testing Strategy

### Unit Tests (Per Increment)
- Context node behavior in isolation
- Relevance scoring accuracy
- Memory persistence operations
- Context formatting functions

### Integration Tests
```python
async def test_full_context_aware_conversation():
    """End-to-end test with all context sources"""
    # Test morning planning with todo context
    # Test document reference during coaching  
    # Test memory recall from previous session
    # Verify LangSmith tracking throughout
```

### Performance Tests
- Context loading under concurrent users
- Relevance scoring latency benchmarks
- Memory growth over multiple sessions
- Cache hit rates for documents

## Risk Mitigation

### Privacy Concerns
- Implement context access logging
- Add sensitive topic detection
- Create user-controlled memory clearing
- Document data retention policies

### Performance Risks
- Start with aggressive caching
- Implement context budgets early
- Use fastest LLMs for scoring (Haiku)
- Monitor latency in LangSmith

### Complexity Management
- Each increment is independently valuable
- Maintain backward compatibility
- Feature flags for gradual rollout
- Comprehensive integration tests

## Learning Opportunities

### Primary Learning Areas
1. **LangGraph Advanced Patterns**: Conditional routing, sub-graphs, state channels
2. **MCP Protocol**: Modern context integration standard
3. **Memory Systems**: Retrieval, relevance, and persistence patterns
4. **Prompt Engineering**: Seamless context injection techniques

### Secondary Learning Areas
1. **Performance Optimization**: Caching, lazy loading, parallel fetching
2. **Privacy Engineering**: Data minimization, access controls
3. **Graph Debugging**: Using LangSmith for complex flows
4. **State Management**: Checkpointing and versioning strategies

## Dependencies to Install

```bash
# MCP SDK for todo integration
pip install mcp

# Document processing
pip install markdown
pip install tiktoken  # For token counting

# Enhanced testing
pip install pytest-benchmark  # Performance testing
```

## Session 6 Deliverables

1. **Context-aware LangGraph**: Extended graph with memory capabilities
2. **MCP Todo Integration**: Working Todoist context injection
3. **Document Loader**: Markdown-based personal context
4. **Memory System**: Cloud-checkpointed conversation history
5. **Performance Dashboard**: LangSmith metrics for context usage
6. **Comprehensive Tests**: 40+ tests including context scenarios
7. **Learning Documents**: 7 Dojo documents on memory patterns

## Next Session Preview

**Session 7: Intelligent Multi-Agent Orchestration**
- Build on context-aware foundation
- Create specialized analysis agents
- Implement agent collaboration patterns
- Design complex orchestration flows

---

*Remember: Each increment should be independently valuable and fully tested. The context system should enhance, not complicate, the coaching experience.*
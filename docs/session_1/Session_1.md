# Session 1: Project Setup and TDD Infrastructure

## Session Goal
Set up a Python project with pytest, create the first conversation quality test, and implement a basic event bus pattern that will later use Redis Pub/Sub. Include stream buffer architecture for dual-track conversation support (main dialogue + insights).

## Success Criteria
- [ ] Working pytest setup with proper project structure
- [ ] First failing test for conversation relevance
- [ ] Basic event bus implementation (in-memory first)
- [ ] Test passes with minimal coach implementation
- [ ] Redis integration with pub/sub demonstration
- [ ] **NEW**: Stream buffer supporting parallel conversation tracks

## Technical Context

### Why This Architecture?
We're building for eventual voice integration with LiveKit, which requires:
- **Event-driven communication**: Voice systems are inherently asynchronous
- **Loose coupling**: Agents need to operate independently
- **Testability**: We must verify conversation quality before adding voice complexity
- **Dual-track streaming**: Support both main conversation and parallel insights/notes

### Tech Stack for Session 1
- **Python 3.9+**: Modern async support
- **pytest**: Industry-standard testing with good async support
- **pytest-asyncio**: For testing async code
- **redis**: For pub/sub (but we'll mock it first)
- **pydantic**: For event schema validation
- **anthropic**: For the actual LLM calls

## Implementation Increments

### Increment 1.1: Project Skeleton (20 min)
**Test First:**
```python
# tests/test_project_setup.py
def test_project_imports():
    """Verify core modules can be imported"""
    import src.agents
    import src.events
    import src.evaluation
    assert True
```

**Implementation:**
- Create proper Python package structure
- Set up pyproject.toml or setup.py
- Create empty `__init__.py` files
- Configure pytest.ini

### Increment 1.2: First Conversation Test (30 min)
**Test First:**
```python
# tests/evaluation/test_relevance.py
import pytest
from src.evaluation.metrics import ResponseRelevanceMetric

@pytest.mark.asyncio
async def test_relevance_metric_scores_on_topic_response():
    """A response about goals should score high for goal-setting context"""
    metric = ResponseRelevanceMetric()
    
    context = "User wants to set morning goals"
    response = "Let's explore what you want to accomplish today. What's most important?"
    
    score = await metric.evaluate(context, response)
    assert score > 0.7  # Expecting high relevance
```

**Implementation:**
- Create ResponseRelevanceMetric class
- Use simple keyword matching initially
- Return score between 0-1

### Increment 1.3: Event Schema Definition (25 min)
**Test First:**
```python
# tests/events/test_schemas.py
from src.events.schemas import UserMessage, AgentResponse
from datetime import datetime

def test_user_message_schema():
    """User messages must have required fields"""
    msg = UserMessage(
        user_id="test_user",
        content="I want to be more productive",
        timestamp=datetime.now()
    )
    assert msg.user_id == "test_user"
    assert msg.conversation_id is not None  # Auto-generated
```

**Implementation:**
- Create Pydantic models for events
- Add validation rules
- Include automatic field generation

### Increment 1.4: In-Memory Event Bus (40 min)
**Test First:**
```python
# tests/events/test_bus.py
import pytest
from src.events.bus import EventBus, Event

@pytest.mark.asyncio
async def test_event_bus_pub_sub():
    """Events published to a channel are received by subscribers"""
    bus = EventBus()
    received_events = []
    
    async def handler(event: Event):
        received_events.append(event)
    
    await bus.subscribe("coaching.goals", handler)
    await bus.publish("coaching.goals", {"type": "user_message", "content": "test"})
    
    # Allow event propagation
    await asyncio.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0]["content"] == "test"
```

**Implementation:**
- Create EventBus with dict of channels
- Implement async publish/subscribe
- Use asyncio.Queue for channel implementation

### Increment 1.5: Basic Coach Agent (45 min)
**Test First:**
```python
# tests/agents/test_base_agent.py
from src.agents.base import BaseAgent
from src.events.schemas import UserMessage, AgentResponse

@pytest.mark.asyncio
async def test_base_agent_responds_to_message():
    """Agents should respond to user messages with relevant content"""
    agent = BaseAgent(name="test_coach")
    
    user_msg = UserMessage(
        user_id="test_user",
        content="I want to set goals for today"
    )
    
    response = await agent.process_message(user_msg)
    
    assert isinstance(response, AgentResponse)
    assert response.agent_name == "test_coach"
    assert len(response.content) > 0
```

**Implementation:**
- Create BaseAgent abstract class
- Implement process_message with mock response
- Add agent registration pattern

### Increment 1.6: Stream Buffer for Dual Tracks (35 min)
**Test First:**
```python
# tests/events/test_stream_buffer.py
import pytest
from src.events.stream_buffer import StreamBuffer, StreamTrack

@pytest.mark.asyncio
async def test_stream_buffer_handles_multiple_tracks():
    """Buffer should maintain separate tracks for conversation and insights"""
    buffer = StreamBuffer()
    
    # Add to main conversation track
    await buffer.add_to_track(StreamTrack.CONVERSATION, {
        "role": "user",
        "content": "I want to be more productive"
    })
    
    # Add to insights track (parallel processing)
    await buffer.add_to_track(StreamTrack.INSIGHTS, {
        "type": "observation",
        "content": "User expressing productivity concerns"
    })
    
    # Should be able to read from both tracks
    conv_items = await buffer.read_track(StreamTrack.CONVERSATION)
    insight_items = await buffer.read_track(StreamTrack.INSIGHTS)
    
    assert len(conv_items) == 1
    assert len(insight_items) == 1
    assert conv_items[0]["role"] == "user"
    assert insight_items[0]["type"] == "observation"
```

**Implementation:**
- Create StreamBuffer with enum for track types
- Use separate asyncio.Queue for each track
- Support non-blocking reads
- Enable track synchronization markers

### Increment 1.7: Redis Integration (40 min)
**Test First:**
```python
# tests/events/test_redis_bus.py
import pytest
from src.events.redis_bus import RedisEventBus
import redis.asyncio as redis

@pytest.mark.asyncio
async def test_redis_event_bus():
    """Redis bus should match in-memory bus interface"""
    # Use Redis test container or mock
    redis_client = await redis.from_url("redis://localhost:6379")
    bus = RedisEventBus(redis_client)
    
    received = []
    
    async def handler(event):
        received.append(event)
    
    await bus.subscribe("test_channel", handler)
    await bus.publish("test_channel", {"test": "data"})
    
    await asyncio.sleep(0.5)  # Redis is async
    
    assert len(received) == 1
```

**Implementation:**
- Create RedisEventBus implementing same interface
- Use redis-py with async support
- Handle connection lifecycle

## Architecture Decisions

### Why Start with In-Memory?
1. **Faster test execution**: No external dependencies
2. **Easier debugging**: Can inspect state directly
3. **Interface-first design**: Focus on contracts, not implementation

### Why Stream Buffer with Dual Tracks?
The stream buffer pattern solves a key challenge in coaching conversations:
1. **Main track**: The actual user-coach dialogue
2. **Insights track**: Parallel observations, patterns, and notes

This enables:
- Coach agents to add observations without interrupting flow
- Pattern recognition across multiple conversations
- Rich context for evening reflection
- Future voice integration where insights can be spoken on a different channel

### Event Channel Naming Convention
```
domain.entity.action

Examples:
- coaching.goals.set
- coaching.reflection.start
- system.agent.register
```

### Testing Strategy
- **Unit tests**: Each component in isolation
- **Integration tests**: Event flow between components
- **No LLM calls in tests**: Use mocks for Anthropic SDK

## Common Pitfalls to Avoid

1. **Don't test Redis itself**: Test your usage of Redis
2. **Avoid complex mocking**: If mocks are complex, design is wrong
3. **Don't skip TDD**: Write test first, even if it feels slow
4. **Keep increments small**: 10-50 lines of code max

## Resources and References

### Redis Pub/Sub Basics
```python
# Publisher
await redis_client.publish('channel', json.dumps(data))

# Subscriber
pubsub = redis_client.pubsub()
await pubsub.subscribe('channel')
async for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
```

### Pytest Async Patterns
```python
@pytest.fixture
async def event_bus():
    bus = EventBus()
    yield bus
    await bus.close()  # Cleanup

@pytest.mark.asyncio
async def test_something(event_bus):
    # Use the fixture
    pass
```

## Definition of Done

- [ ] All tests passing
- [ ] Project can be installed with `pip install -e .`
- [ ] Basic README with setup instructions
- [ ] Can demonstrate pub/sub with print statements
- [ ] Stream buffer handling dual tracks (conversation + insights)
- [ ] Ready for Lesson 2 (evaluation framework)

## Next Session Preview

In Session 2, we'll build on this foundation to create comprehensive evaluation metrics. We'll use the event bus to capture conversations and score them on multiple dimensions, setting up the quality gates for our coaching system. The stream buffer will allow us to evaluate both the main conversation quality and the insights generation separately.
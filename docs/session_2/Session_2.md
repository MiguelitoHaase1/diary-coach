# Session 2: Minimal Working Prototype - Real Conversations Now! (Lean Version)

## Executive Summary
Transform Session 1's event-driven foundation into a talking diary coach in just 5 increments. Focus relentlessly on getting to real conversations quickly, saving every interaction for future analysis. Skip premature optimization and complex orchestration - just make it work.

**Duration**: 3-4 hours across 5 increments  
**Prerequisites**: Session 1 complete (event bus, schemas, base agent pattern)  
**Outcome**: CLI-based diary coach having real conversations with Michael

## Primary Goals
1. **Anthropic SDK Integration**: Get Claude API calls working reliably
2. **Coach Implementation**: Embed Michael's prompt into a working agent
3. **CLI Interface**: Simple terminal for conversations
4. **Conversation Storage**: Save everything for Session 3 analysis
5. **End-to-End Flow**: Complete working system

## Simplified Architecture

```
CLI Input → Event Bus → Coach Agent → Anthropic API
                 ↓            ↓
          Conversation    Response
             Storage
```

**Key Simplification**: No orchestrator needed yet - the coach subscribes directly to user events.

## Increment Breakdown

### Increment 2.1: Anthropic Service Layer (45 min)
**Goal**: Create reliable async wrapper for Claude API calls

**Test First (TDD)**:
```python
# tests/services/test_llm_service.py
async def test_anthropic_service_basic_call():
    service = AnthropicService(api_key="test", model="claude-3-sonnet-20240229")
    response = await service.generate_response(
        messages=[{"role": "user", "content": "Hello"}],
        system_prompt="You are a helpful assistant"
    )
    assert isinstance(response, str)
    assert len(response) > 0

async def test_anthropic_service_tracks_usage():
    service = AnthropicService(api_key="test")
    response = await service.generate_response(
        messages=[{"role": "user", "content": "Hello"}]
    )
    assert service.total_tokens > 0
    assert service.total_cost > 0

async def test_anthropic_service_handles_errors():
    service = AnthropicService(api_key="invalid")
    with pytest.raises(AnthropicError):
        await service.generate_response(messages=[])
```

**Implementation Focus**:
- Async client with proper error handling
- Simple retry logic (max 3 attempts)
- Token/cost tracking from day one
- Clean message formatting
- No streaming for now (keep it simple)

**Key Decisions**:
- Use environment variables for API key
- Hard-code model to claude-3-sonnet-20240229
- Track cumulative tokens/cost per service instance
- Return simple strings (no complex response objects)

### Increment 2.2: Coach Agent Implementation (60 min)
**Goal**: Embed Michael's prompt and handle conversation states

**Test First (TDD)**:
```python
# tests/agents/test_coach_agent.py
async def test_morning_greeting_format():
    coach = DiaryCoach(llm_service=mock_service)
    response = await coach.process_message(
        UserMessage(content="good morning", user_id="michael")
    )
    # Must include name and single question
    assert "Good morning Michael!" in response.content
    assert response.content.count("?") == 1
    assert "challenge" in response.content.lower()

async def test_evening_greeting_format():
    coach = DiaryCoach(llm_service=mock_service)
    # First set morning context
    await coach.process_message(
        UserMessage(content="good morning", user_id="michael")
    )
    await coach.process_message(
        UserMessage(content="I want to be more present today", user_id="michael")
    )
    
    # Evening should reference morning
    response = await coach.process_message(
        UserMessage(content="good evening", user_id="michael")
    )
    assert "Good evening Michael!" in response.content
    assert "present" in response.content.lower()  # References morning

async def test_coach_style_no_bullets():
    coach = DiaryCoach(llm_service=mock_service)
    response = await coach.process_message(
        UserMessage(content="What should I focus on?", user_id="michael")
    )
    # Style validation
    assert "•" not in response.content
    assert not response.content.strip().startswith("-")
    assert len(response.content.split("\n")) <= 6  # Max 6 lines
```

**Implementation Focus**:
- Inherit from BaseAgent (Session 1)
- Embed full prompt as class constant
- Track conversation state (morning/evening/general)
- Remember current session's challenge/value
- Format messages for Anthropic API

**State Management**:
```python
class DiaryCoach(BaseAgent):
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.conversation_state = "general"
        self.morning_challenge = None
        self.morning_value = None
        self.message_history = []  # Just current session
```

### Increment 2.3: CLI Interface (45 min)
**Goal**: Create simple, functional terminal interface

**Test First (TDD)**:
```python
# tests/interface/test_cli.py
async def test_cli_processes_input():
    cli = DiaryCoachCLI(coach=mock_coach, event_bus=mock_bus)
    
    # Simulate input
    response = await cli.process_input("good morning")
    assert response is not None
    assert isinstance(response, str)

async def test_cli_maintains_session():
    cli = DiaryCoachCLI(coach=real_coach, event_bus=real_bus)
    
    # Multiple exchanges in same session
    response1 = await cli.process_input("good morning")
    response2 = await cli.process_input("I want to be more patient")
    
    # Coach should maintain context
    assert "patient" in response2.lower() or "challenge" in response2.lower()

async def test_cli_handles_exit_commands():
    cli = DiaryCoachCLI(coach=mock_coach, event_bus=mock_bus)
    
    should_exit = await cli.process_input("exit")
    assert should_exit is None  # Or special exit signal
```

**Implementation Focus**:
- Async input loop using `asyncio.create_task`
- Clean output formatting (no fancy UI)
- Handle exit/quit commands gracefully
- Display token cost after each exchange
- Simple error recovery (don't crash on API errors)

**Minimal Interface**:
```python
# src/interface/cli.py
class DiaryCoachCLI:
    async def run(self):
        print("🌅 Diary Coach Ready (type 'exit' to quit)")
        while True:
            user_input = await self.get_input("> ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            # Process through event bus
            response = await self.process_input(user_input)
            print(f"\n{response}\n")
            print(f"💰 Cost: ${self.coach.llm_service.session_cost:.4f}")
```

### Increment 2.4: Conversation Persistence (30 min)
**Goal**: Save every conversation for future analysis

**Test First (TDD)**:
```python
# tests/persistence/test_conversation_storage.py
async def test_saves_conversation_to_json():
    storage = ConversationStorage(base_path="./test_conversations")
    
    # Create test conversation
    convo = Conversation(
        session_id="test_123",
        started_at=datetime.now(),
        messages=[
            {"role": "user", "content": "good morning"},
            {"role": "assistant", "content": "Good morning Michael!..."},
            {"role": "user", "content": "I want to be present"},
            {"role": "assistant", "content": "Being present..."}
        ],
        metadata={
            "total_tokens": 245,
            "total_cost": 0.0023,
            "duration_seconds": 45
        }
    )
    
    filepath = await storage.save(convo)
    assert filepath.exists()
    
    # Verify loadable
    loaded = await storage.load(filepath)
    assert len(loaded.messages) == 4
    assert loaded.metadata["total_tokens"] == 245

async def test_storage_creates_daily_folders():
    storage = ConversationStorage(base_path="./test_conversations")
    
    convo = create_test_conversation()
    filepath = await storage.save(convo)
    
    # Should create date-based folders
    assert "2025-01-30" in str(filepath)  # Or current date
    assert filepath.name.startswith("conversation_")
```

**Implementation Focus**:
- Simple JSON serialization
- Date-based folder structure (conversations/2025-01-30/)
- Include all metadata (tokens, cost, duration)
- Timestamp-based filenames
- No database complexity yet

**Storage Format**:
```json
{
    "session_id": "uuid",
    "started_at": "2025-01-30T09:00:00",
    "ended_at": "2025-01-30T09:15:00",
    "messages": [...],
    "metadata": {
        "total_tokens": 1234,
        "total_cost": 0.0234,
        "morning_challenge": "being more present",
        "conversation_quality_score": 0.85
    }
}
```

### Increment 2.5: End-to-End Integration (45 min)
**Goal**: Wire everything together for real conversations

**Test First (TDD)**:
```python
# tests/integration/test_session_2_e2e.py
@pytest.mark.integration  # Marks test that uses real API
async def test_complete_morning_conversation_flow():
    # Create complete system
    system = await create_diary_coach_system()
    
    # Test morning ritual
    response1 = await system.cli.process_input("good morning")
    assert "Good morning Michael!" in response1
    assert response1.count("?") == 1
    
    # Test challenge discussion
    response2 = await system.cli.process_input(
        "I need to have a difficult conversation with my team lead"
    )
    assert len(response2) < 300  # Concise response
    
    # Test value question appears
    response3 = await system.cli.process_input(
        "I'm worried about how they'll react"
    )
    # At some point, coach should ask about values
    all_responses = response1 + response2 + response3
    assert "value" in all_responses.lower() or "fight for" in all_responses.lower()
    
    # Verify conversation was saved
    storage = system.conversation_storage
    latest = await storage.load_latest()
    assert len(latest.messages) >= 6  # 3 user + 3 assistant
    assert latest.metadata["total_cost"] > 0

@pytest.mark.integration
async def test_complete_evening_reflection_flow():
    system = await create_diary_coach_system()
    
    # Simulate morning first
    await system.cli.process_input("good morning")
    await system.cli.process_input("I want to be more present with my family")
    
    # Evening reflection
    response = await system.cli.process_input("good evening")
    assert "Good evening Michael!" in response
    assert "present" in response.lower() or "family" in response.lower()
    
    # Should ask about specific moment
    assert "moment" in response.lower() or "conversation" in response.lower()

async def test_system_handles_api_errors_gracefully():
    system = await create_diary_coach_system()
    
    # Simulate API error
    system.coach.llm_service.api_key = "invalid"
    
    response = await system.cli.process_input("good morning")
    assert "error" in response.lower() or "try again" in response.lower()
    assert system.running  # System didn't crash
```

**Integration Checklist**:
- [ ] Environment variables loaded (.env file)
- [ ] All components properly initialized
- [ ] Event bus connecting CLI → Coach
- [ ] Coach using real Anthropic API
- [ ] Conversations auto-saved after each exchange
- [ ] Graceful error handling throughout
- [ ] Quality metrics computed and stored

## Success Criteria

### Must Have (Core Prototype)
- ✅ Complete morning ritual conversation working
- ✅ Complete evening ritual conversation working  
- ✅ Coach maintains session context
- ✅ All conversations saved as JSON
- ✅ Total cost tracking per conversation

### Should Have (Quality)
- ✅ Responses follow style guide (no bullets, <6 lines)
- ✅ Only one question per response
- ✅ Evening references morning discussion
- ✅ Response time < 3 seconds
- ✅ Basic quality score > 0.7

### Nice to Have (Future Sessions)
- ⏳ Multiple conversation sessions
- ⏳ Coach personality variations
- ⏳ Advanced quality metrics
- ⏳ A/B testing infrastructure
- ⏳ Memory across sessions

## Dependencies to Install

```bash
# Add to requirements.txt
anthropic>=0.8.0      # Claude API SDK
python-dotenv>=1.0.0  # Environment variables
```

## Environment Setup

Create `.env` file:
```bash
ANTHROPIC_API_KEY=your_api_key_here
COACH_MODEL=claude-3-sonnet-20240229
MAX_TOKENS=200
TEMPERATURE=0.7
```

## Running Your Prototype

```bash
# After completing all increments
python -m diary_coach

# For development/testing
python -m diary_coach --debug  # Shows token usage per call

# To analyze saved conversations
python -m diary_coach analyze --date 2025-01-30
```

## Critical Learning Focus

### 1. **Real API Integration** (Your Gap: Async + External APIs)
- How to mock expensive API calls in tests
- When to use integration tests vs unit tests
- Cost-aware development practices

### 2. **TDD with Stateful Systems** (Your Gap: Testing conversations)
- Testing multi-turn conversations
- Verifying personality consistency
- State management in tests

### 3. **Minimum Viable Architecture** (Your Strength: Product thinking)
- What to build now vs later
- How to prepare for future without overengineering
- Data collection for future improvements

## Session 2 Anti-Patterns to Avoid

1. **Don't Perfect the Prompt**: Get it working, refine in Session 3
2. **Don't Build Fancy CLI**: Basic input/output is enough
3. **Don't Optimize Early**: Measure first, optimize later
4. **Don't Skip Persistence**: You need data for Session 3
5. **Don't Forget Costs**: Track every token from the start

## What Success Looks Like

By the end of Session 2, you should be able to:

```bash
$ python -m diary_coach

🌅 Diary Coach Ready
> good morning
Good morning Michael! What's the one challenge you're ready to tackle today that could shift everything?

> I need to set better boundaries with my team
That tension around boundaries - where do you feel it most in your body right now? Sometimes our physical sensations point to what really needs attention.

> It's like a tightness in my chest, like I'm holding my breath
That held breath is telling you something. What core value do you want to fight for today? Tell me a bit more about it.

> I want to fight for my integrity - being honest about my capacity
[conversation continues...]

💰 Session cost: $0.0024
📁 Saved to: conversations/2025-01-30/conversation_09-15-23.json
```

## Prep for Session 3

Your conversation files become the raw material for Session 3's behavioral change detection:
- 20+ real conversations to analyze
- Patterns in coaching effectiveness
- Weak spots where coach fails to push for specificity
- Baseline metrics for improvement

---

*Remember: This session is about MOMENTUM. Don't polish - ship! You'll have real conversations to analyze by hour 3. The imperfections you discover become Session 3's improvements.*
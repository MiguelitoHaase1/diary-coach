# Test Queries for LiveKit Expert Sub-agent

## How to Use the LiveKit Expert

When you need LiveKit assistance during development, you can invoke the expert sub-agent using the Task tool with these example prompts:

### Example 1: Connection Issues
```
Task(
    description="Debug LiveKit connection",
    prompt="I'm getting 'Failed to connect to room' errors when trying to join a LiveKit room. The WebSocket seems to timeout. Help me debug this issue.",
    subagent_type="general-purpose"
)
```

### Example 2: Audio Quality Problems
```
Task(
    description="Fix audio quality issues", 
    prompt="Users are reporting choppy audio in our LiveKit implementation. The video is fine but audio keeps cutting out. What are the common causes and solutions?",
    subagent_type="general-purpose"
)
```

### Example 3: Implementation Pattern
```
Task(
    description="Implement voice activity detection",
    prompt="I need to implement voice activity detection with LiveKit for the diary coach. Show me the best pattern for detecting when users are speaking.",
    subagent_type="general-purpose"
)
```

### Example 4: Error Resolution
```
Task(
    description="Resolve token error",
    prompt="Getting error: 'Invalid token: Token does not match room'. I'm generating tokens server-side but they're being rejected. What should I check?",
    subagent_type="general-purpose"
)
```

### Example 5: Performance Optimization
```
Task(
    description="Optimize LiveKit performance",
    prompt="Our LiveKit room starts lagging with more than 5 participants. How can we optimize for better performance with 10-15 participants?",
    subagent_type="general-purpose"
)
```

## Sub-agent Context Loading

The sub-agent will automatically load the LiveKit expert prompt from:
`docs/agents/livekit_expert_prompt.md`

This provides the agent with:
- Common error patterns and solutions
- Code implementation examples
- Performance optimization techniques
- Debugging strategies
- Production best practices

## Adding Your Own Knowledge

To enhance the LiveKit expert with your specific experience:

1. **Collect your LiveKit logs**:
   ```bash
   # Save error logs to a file
   grep -i "error\|fail" your-app.log > livekit-errors.log
   ```

2. **Gather your working code**:
   ```bash
   # Copy your LiveKit implementation files
   cp src/voice/*.ts livekit-implementation/
   ```

3. **Export configurations**:
   ```bash
   # Save your LiveKit config
   cp .env.production livekit-config.env
   ```

4. **Run the organizer**:
   ```bash
   python scripts/organize_livekit_knowledge.py \
     --logs livekit-errors.log \
     --code livekit-implementation/ \
     --config livekit-config.env
   ```

5. **Review and append**:
   - Check `docs/agents/livekit_knowledge_update.md`
   - Add solutions for the errors
   - Append to `livekit_expert_prompt.md`

## Integration with Diary Coach Voice Features

For diary coach voice integration, the expert can help with:

1. **Voice Pipeline Setup**:
   - Microphone → LiveKit → VAD → STT → Coach → TTS → LiveKit → Speaker

2. **Real-time Coaching**:
   - Low-latency audio streaming
   - Interruption handling
   - Turn-taking management

3. **Data Channel Usage**:
   - Sending transcriptions
   - Receiving coaching feedback
   - Synchronizing UI state

4. **Error Recovery**:
   - Network disconnection handling
   - Audio device switching
   - Permission management

## Quick Test

To quickly test if the LiveKit expert is working:

```python
# In your development session
Task(
    description="Test LiveKit expert",
    prompt="What's the basic pattern for connecting to a LiveKit room with error handling?",
    subagent_type="general-purpose"
)
```

The expert should provide a comprehensive answer with code examples and best practices.
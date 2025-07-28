# Diary Coach Development Dashboard

Generated: 2025-07-28 11:41:19

## Environment Status
- ✅ Venv
- ✅ Env File
- ❌ Anthropic Key
- ❌ Elevenlabs Key
- ❌ Elevenlabs Voice
- ❌ Firecrawl Key
- ❌ Todoist Token
- ❌ Langsmith Key

## Quick Commands

### Voice Development
```bash
# Convert latest Deep Thoughts to audio
python scripts/dev_environment.py tts --latest

# Test specific text
python scripts/dev_environment.py tts --text "Hello from diary coach"
```

### Documentation
```bash
# Check documentation coverage
python scripts/dev_environment.py docs

# Test Context7 access
python scripts/dev_environment.py context7
```

### Coaching
```bash
# Run multi-agent coach
python scripts/dev_environment.py coach

# Run single-agent coach
python scripts/dev_environment.py coach --single
```

### Testing
```bash
# Run all tests
python scripts/dev_environment.py test

# Run specific test
python scripts/dev_environment.py test tests/test_agents.py
```

## Documentation
- [Session 9 Plan](docs/Session_9/session_9_development_tooling.md)
- [LiveKit Expert](docs/agents/livekit_expert_prompt.md)
- [API Documentation](apidocs/)
- [Project Status](docs/status.md)

## MCP Server Usage

### Context7
Add "use context7" to any prompt for library documentation

### Firecrawl
Automatically used for web scraping and research
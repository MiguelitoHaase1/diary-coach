# Diary Coach Development Setup Guide

## Quick Start

1. **Check Environment Status**:
   ```bash
   python scripts/dev_environment.py status
   ```

2. **Generate Development Dashboard**:
   ```bash
   python scripts/dev_environment.py dashboard
   ```

3. **Run Diary Coach**:
   ```bash
   python scripts/dev_environment.py coach
   ```

## Complete Setup Instructions

### 1. Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Required variables:
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/
- `TODOIST_API_TOKEN`: Get from https://todoist.com/app/settings/integrations/developer

Optional but recommended:
- `ELEVENLABS_API_KEY`: Get from https://elevenlabs.io/
- `ELEVENLABS_VOICE_ID`: Select from ElevenLabs voice library
- `FIRECRAWL_API_KEY`: Get from https://firecrawl.dev/
- `LANGSMITH_API_KEY`: Get from https://smith.langchain.com/

### 3. MCP Servers (Claude Desktop)

Context7 and Firecrawl MCP servers should be configured in Claude Desktop:

1. **Context7** (for documentation):
   - Already configured if using Claude Code
   - No API key required

2. **Firecrawl** (for web scraping):
   - Requires `FIRECRAWL_API_KEY` in environment
   - Used as backup for missing documentation

### 4. Development Tools

All tools are accessible through the unified launcher:

```bash
# Text-to-Speech
python scripts/dev_environment.py tts --latest
python scripts/dev_environment.py tts --text "Hello world"

# Documentation
python scripts/dev_environment.py docs      # Check coverage
python scripts/dev_environment.py context7  # Test Context7

# LiveKit Knowledge
python scripts/dev_environment.py livekit --logs error.log

# Testing
python scripts/dev_environment.py test              # All tests
python scripts/dev_environment.py test tests/xyz.py # Specific test

# Evaluation
python scripts/dev_environment.py eval
```

### 5. VS Code Integration

VS Code tasks are pre-configured in `.vscode/tasks.json`:

1. Open Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. Select from available tasks:
   - Dev: Check Environment
   - Dev: Generate Dashboard
   - TTS: Convert Latest Deep Thoughts
   - Coach: Run Multi-Agent
   - Test: Run Fast Tests
   - And more...

Default build task (`Cmd+Shift+B`): Run Multi-Agent Coach
Default test task: Run Fast Tests

### 6. Voice Development

For voice integration work:

1. **Setup ElevenLabs**:
   - Create account at https://elevenlabs.io/
   - Select a voice from the library
   - Add API key and voice ID to `.env`

2. **Test TTS**:
   ```bash
   python scripts/dev_environment.py tts --text "Testing voice"
   ```

3. **LiveKit Development**:
   - Use the LiveKit expert sub-agent for help
   - Organize your LiveKit knowledge:
     ```bash
     python scripts/dev_environment.py livekit --logs your-logs.txt
     ```

### 7. Playwright Setup (for UI debugging)

For browser automation and WebRTC debugging:

```bash
# Install Playwright
pip install playwright

# Install browsers
playwright install chromium
```

### 8. Environment Validation

Run the complete validation checklist:

```bash
# 1. Check environment
python scripts/dev_environment.py status

# 2. Test documentation access
python scripts/dev_environment.py context7

# 3. Run fast tests
python -m pytest -m "not slow" -v

# 4. Test TTS (if configured)
python scripts/dev_environment.py tts --text "Environment ready"

# 5. Generate dashboard
python scripts/dev_environment.py dashboard
```

## Troubleshooting

### Common Issues

1. **"No module named 'xyz'"**:
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **"API key not found"**:
   - Check `.env` file exists
   - Verify key names match exactly
   - Restart terminal after adding keys

3. **"Failed to connect to MCP server"**:
   - Verify Claude Desktop is running
   - Check MCP server configuration
   - Try `claude mcp list` to verify

4. **"TTS quota exceeded"**:
   - ElevenLabs has usage limits
   - Check your account at https://elevenlabs.io/
   - Consider upgrading plan

### Debug Mode

For detailed logging:

```bash
# Set log level
export LOG_LEVEL=debug

# Run with verbose output
python scripts/dev_environment.py coach
```

## Next Steps

1. Complete environment setup using the status command
2. Generate and review the development dashboard
3. Test each component individually
4. Start developing with the unified tools

For session-specific instructions, see:
- [Session 9 Plan](Session_9/session_9_development_tooling.md)
- [Project Status](status.md)
- [Development Dashboard](../DEVELOPMENT.md)
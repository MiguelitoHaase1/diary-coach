# Session 9: Development Tooling & ElevenLabs TTS

## Session Overview

**Goal**: Set up comprehensive development environment for voice work with practical TTS implementation

**Duration**: 3-4 hours (with significant manual setup time)

**Outcome**: Development tooling ready for voice integration, Deep Thoughts audio generation working

## Pre-Session Requirements

### 🔴 HUMAN SETUP REQUIRED (Before Coding)

1. **ElevenLabs Account & Voice Selection** (~30 minutes)
   - [v] Create ElevenLabs account at https://elevenlabs.io
   - [v] Browse voice library and select preferred voice
   - [v] Note the voice_id for your chosen voice
   - [v] Generate API key from account settings
   - [v] Add to .env: `ELEVENLABS_API_KEY=your_key_here`
   - [v] Add to .env: `ELEVENLABS_VOICE_ID=your_selected_voice_id`

2. **MCP Server Setup** (~20 minutes)
   - [ ] Install Context7 MCP Server (primary choice)
   - [v] No API keys needed - it just works!
   - [ ] Install Firecrawl MCP Server as backup
   - [ ] Get Firecrawl API key from https://firecrawl.dev (free tier available)
   - [ ] Add to .env: `FIRECRAWL_API_KEY=your_key_here`

3. **LiveKit Context Preparation** (~15 minutes)
   - [ ] Gather your past LiveKit project logs
   - [ ] Prepare LiveKit error messages, implementation patterns
   - [ ] Have ready: Your LiveKit experience documentation
   - [ ] Optional: Previous LiveKit project GitHub links

4. **Browser Automation Setup** (~20 minutes)
   - [ ] Install Playwright: `pip install playwright`
   - [ ] Run: `playwright install chromium`
   - [ ] Ensure Chrome/Chromium launches properly
   - [ ] Note: This enables voice UI debugging visibility

## Session Increments

### Increment 1: ElevenLabs TTS Integration (45 minutes)

**Purpose**: Create a working TTS script that converts Deep Thoughts markdown to audio

**Approach**:
- Simple Python script using ElevenLabs API
- Read Deep Thoughts markdown from file system
- Handle markdown formatting for natural speech
- Generate MP3 output with configurable settings

**Deliverables**:
- `scripts/tts_deep_thoughts.py` - Main TTS conversion script
- Support for both file input and direct text input
- Voice settings configuration (speed, stability, clarity)
- Error handling for API limits and failures
- Basic CLI interface for testing

**Common Pitfalls**:
- Don't forget to strip markdown syntax for cleaner audio
- Handle rate limits gracefully (ElevenLabs has quotas)
- Ensure proper audio file naming with timestamps

### Increment 2: Context7 MCP Setup & Testing (45 minutes)

**Purpose**: Configure Context7 for instant API documentation access

**Approach**:
- Install Context7 MCP Server with simple configuration
- Test documentation retrieval for your key libraries
- Verify LangGraph, Anthropic SDK, and other core dependencies
- Set up Firecrawl as backup for any missing documentation

**Deliverables**:
- Context7 configuration in Claude Desktop config
- `scripts/test_context7.py` - Verify documentation access
- List of available vs missing documentation
- Firecrawl configuration for gap coverage
- Quick reference guide for common queries

**Common Pitfalls**:
- Context7 only covers popular, well-documented libraries
- Check exact library names (might be under different packages)
- Some frameworks may require specific query formats
- Don't assume every internal API is covered

### Increment 3: LiveKit Expert Sub-agent Creation (45 minutes)

**Purpose**: Build a specialized sub-agent with your LiveKit knowledge embedded

**Approach**:
- Create comprehensive prompt with your LiveKit experience
- Include common error patterns and solutions
- Add code snippets from successful implementations
- Structure for easy querying by Claude Code

**Deliverables**:
- `docs/agents/livekit_expert_prompt.md` - Complete expert prompt
- Organized sections: Setup, Common Issues, Best Practices
- Code examples from your past projects
- Integration patterns specific to your use cases
- Testing queries to validate knowledge retrieval

**Human Input Required**:
- Share your LiveKit logs when creating this increment
- Provide specific error messages you've encountered
- Include working code snippets from past projects

### Increment 4: Development Environment Integration (30 minutes)

**Purpose**: Wire everything together for seamless development workflow

**Approach**:
- Create unified launcher script
- Set up VS Code tasks for common operations
- Configure Playwright debugging setup for voice development
- Create development dashboard

**Deliverables**:
- `scripts/dev_environment.py` - Unified launcher
- `.vscode/tasks.json` - Quick access to tools
- Playwright inspector configuration for LiveKit debugging
- `docs/dev_setup.md` - Complete setup guide
- Environment validation checklist

**Common Pitfalls**:
- Path issues between different tools
- Environment variable conflicts
- Permission issues with browser automation
- Playwright needs proper display server on headless systems

## Technical Architecture

```
DEVELOPMENT TOOLING ARCHITECTURE:
┌─────────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  ElevenLabs API    │     │   Context7 MCP    │     │   Playwright     │
│  - TTS Generation  │     │  - Instant Docs   │     │  - UI Debugging  │
│  - Voice Selection │     │  - No API Keys    │     │  - WebRTC Debug  │
└──────────┬─────────┘     └────────┬──────────┘     └────────┬─────────┘
           │                        │                           │
           │                   ┌────▼──────┐                   │
           │                   │ Firecrawl │                   │
           │                   │ (Backup)  │                   │
           │                   └────┬──────┘                   │
           │                        │                           │
           └────────────────────────┴───────────────────────────┘
                                    │
                          ┌─────────▼──────────┐
                          │  Claude Code Dev   │
                          │   Environment      │
                          └─────────┬──────────┘
                                    │
                          ┌─────────▼──────────┐
                          │  LiveKit Expert   │
                          │    Sub-agent      │
                          └────────────────────┘
```

## Success Criteria

- [ ] Deep Thoughts markdown converts to natural-sounding audio
- [ ] Context7 provides instant documentation for core libraries
- [ ] Firecrawl successfully scrapes any missing documentation
- [ ] LiveKit expert sub-agent answers specific implementation questions
- [ ] All tools accessible through unified development interface
- [ ] Performance metrics show <2 second TTS generation for typical reports

## Post-Session Tasks

### 🔴 HUMAN FOLLOW-UP REQUIRED

1. **Voice Optimization** (~30 minutes)
   - [ ] Test generated audio with different voices
   - [ ] Fine-tune voice settings for your preference
   - [ ] Create voice preset configurations

2. **Documentation Coverage** (~30 minutes)
   - [ ] Check which of your libraries are in Context7
   - [ ] Create Firecrawl queries for missing documentation
   - [ ] Consider adding local markdown docs for internal APIs

3. **Knowledge Base Enhancement** (~ongoing)
   - [ ] Continue adding to LiveKit expert knowledge
   - [ ] Document new patterns as discovered
   - [ ] Update based on actual usage patterns

## Implementation Notes

### ElevenLabs Best Practices
- Use streaming API for long documents
- Cache generated audio to avoid redundant API calls
- Implement retry logic with exponential backoff
- Consider chunking large documents

### MCP Server Strategy
- **Context7**: Your primary documentation source - instant, free, no config
- **Firecrawl**: Backup for LiveKit docs and anything Context7 doesn't cover
- **Google Drive**: You already have this! Use it for your internal API docs

### LiveKit Expert Design
- Structure knowledge as Q&A pairs
- Include verbatim error messages for searchability
- Organize by implementation phase (setup, development, debugging)
- Add metadata tags for easy retrieval

## Session Principles

1. **Real Working Software**: Every tool must be tested with actual use cases
2. **Progressive Enhancement**: Start simple, add features incrementally
3. **User-Centric Design**: Optimize for developer productivity
4. **Cost Awareness**: Monitor API usage and implement safeguards
5. **Knowledge Capture**: Document everything for future sessions

## Next Session Preview

Session 10 will focus on performance optimization for voice latency requirements, building on the tools established in this session. The ElevenLabs integration will serve as a baseline for understanding audio generation performance, while the MCP servers will accelerate documentation lookup during development.
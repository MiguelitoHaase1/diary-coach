# Session 9: Development Tooling & Parallel Sub-Agent Development

## Session Overview

**Goal**: Build upon existing MCP server setup to create parallel sub-agent development using git worktree

**Duration**: 6-8 hours

**Outcome**: Four specialized sub-agents working in parallel branches, Deep Thoughts audio generation, leveraging existing shared documentation context

## Pre-Session Requirements

### ✅ COMPLETED SETUP

1. **MCP Servers** (Session 9.0)
   - [✅] Context7 installed and configured
   - [✅] Firecrawl installed (awaiting API key)
   - [✅] Todoist MCP documented

2. **API Documentation Repository** (Session 9.0)
   - [✅] `/apidocs` folder created with:
     - ElevenLabs documentation (140KB)
     - LiveKit documentation (186KB)
     - LangGraph documentation (182KB)
     - Playwright documentation (101KB)
     - WebRTC debugging documentation (154KB)
     - Todoist MCP documentation

### 🔴 REMAINING HUMAN SETUP REQUIRED

1. **ElevenLabs Configuration** (~10 minutes)
   - [v] Add to .env: `ELEVENLABS_API_KEY=your_key_here`
   - [v] Add to .env: `ELEVENLABS_VOICE_ID=your_selected_voice_id`

2. **Firecrawl API Key** (~5 minutes)
   - [v] Get Firecrawl API key from https://firecrawl.dev
   - [v] Add to .env: `FIRECRAWL_API_KEY=your_key_here`

3. **Git Worktree Preparation** (~15 minutes)
   - [v] Ensure main branch is clean and committed
   - [v] Create worktree directory structure: `mkdir -p worktrees/{voice,langgraph,mcp,ui}`
   - [v] Set up feature branches for each agent

## Updated Technical Architecture

```
PARALLEL AGENT ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────┐
│         Existing Shared Context Infrastructure                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Context7   │  │  Firecrawl   │  │  /apidocs folder    │   │
│  │  (Active)   │  │(Pending API) │  │  (6 API docs)       │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┬───────────────┐
        │             │             │             │               │
┌───────▼──────┐ ┌────▼──────┐ ┌───▼──────┐ ┌───▼──────┐ ┌─────▼─────┐
│  Main Branch │ │   Voice   │ │ LangGraph │ │    MCP    │ │    UI     │
│  - TTS Script│ │   Agent   │ │   Agent   │ │   Agent   │ │   Agent   │
│  - MCP Setup │ │           │ │           │ │           │ │           │
│  - API Docs  │ │ worktrees/│ │ worktrees/│ │ worktrees/│ │ worktrees/│
│              │ │   voice   │ │ langgraph │ │    mcp    │ │    ui     │
└──────────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

## Session Increments

### Increment 1: ElevenLabs TTS for Deep Thoughts (45 minutes)

**Purpose**: Create working TTS script leveraging existing ElevenLabs documentation

**Approach**:
- Reference `/apidocs/elevenlabs_documentation.md` for implementation
- Use documented Python SDK examples
- Handle markdown to speech conversion

**Deliverables**:
- `scripts/tts_deep_thoughts.py` - Main TTS conversion script
- Integration with existing project structure
- Voice settings configuration
- Error handling based on documented patterns

### Increment 2: Git Worktree Setup (30 minutes)

**Purpose**: Establish parallel development environment

**Git Worktree Commands**:
```bash
# Create feature branches and worktrees
git checkout -b feature/voice-agent
git checkout main
git worktree add worktrees/voice feature/voice-agent

git checkout -b feature/langgraph-agent  
git checkout main
git worktree add worktrees/langgraph feature/langgraph-agent

git checkout -b feature/mcp-agent
git checkout main
git worktree add worktrees/mcp feature/mcp-agent

git checkout -b feature/ui-agent
git checkout main
git worktree add worktrees/ui feature/ui-agent
```

### Increment 3: Parallel Sub-Agent Development (4-5 hours)

#### Voice & LiveKit Agent (worktrees/voice)

**Leverages**:
- `/apidocs/livekit_documentation.md` (186KB)
- `/apidocs/elevenlabs_documentation.md` (140KB)
- `/apidocs/webrtc_debugging_documentation.md` (154KB)

**Focus Areas**:
- LiveKit room management patterns from docs
- ElevenLabs streaming implementation
- WebRTC debugging strategies

#### LangGraph Agent (worktrees/langgraph)

**Leverages**:
- `/apidocs/langgraph_documentation.md` (182KB)
- Context7 for latest LangSmith integration docs

**Focus Areas**:
- StateGraph implementation patterns
- Multi-agent network architectures
- Tracing and observability setup

#### MCP Agent (worktrees/mcp)

**Leverages**:
- Existing Context7 and Firecrawl installations
- `/apidocs/todoist_mcp_documentation.md`
- Claude Code MCP configuration

**Focus Areas**:
- Catalog additional MCP servers
- Document integration patterns
- Create MCP discovery framework

#### UI Agent (worktrees/ui)

**Leverages**:
- `/apidocs/playwright_documentation.md` (101KB)
- Firecrawl for Claude voice interface research

**Focus Areas**:
- Voice-first React patterns
- WebRTC UI components
- Accessibility considerations

### Increment 4: Integration & Documentation Enhancement (1 hour)

**Purpose**: Merge learnings and enhance existing documentation

**Tasks**:
- Update `/apidocs` with agent-specific discoveries
- Create cross-agent integration guide
- Document best practices discovered during development

## Benefits of Building on Existing Setup

1. **No Documentation Fetching Needed**: All core API docs already available
2. **MCP Infrastructure Ready**: Context7 operational, Firecrawl pending API key
3. **Proven Workflow**: MCP servers already integrated with Claude Code
4. **Reference Implementation**: Session 9.0 provides pattern for future MCP additions

## Updated Success Criteria

- [ ] Deep Thoughts TTS working with existing ElevenLabs docs
- [ ] Four agents developing in parallel worktrees
- [ ] Each agent leverages existing `/apidocs` effectively
- [ ] Firecrawl API key configured and tested
- [ ] New discoveries added back to documentation repository
- [ ] Integration patterns documented for future sessions

## Post-Session Enhancements

1. **Documentation Expansion**
   - [ ] Add agent-specific patterns to `/apidocs`
   - [ ] Create agent interaction diagrams
   - [ ] Document discovered edge cases

2. **MCP Server Additions**
   - [ ] Research additional relevant MCP servers
   - [ ] Add to Claude Code configuration
   - [ ] Update documentation accordingly

3. **Performance Baselines**
   - [ ] Measure TTS generation times
   - [ ] Document agent response latencies
   - [ ] Create optimization roadmap
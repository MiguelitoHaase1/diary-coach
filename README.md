# The Daily Coach - Multi-Agent Personal Transformation System

A sophisticated multi-agent AI system that orchestrates natural cognitive strengths across voice and text modalities to help you identify and solve your most important daily challenges through personalized coaching conversations.

## 🌟 Product Vision

The Daily Coach transforms how people solve their most pressing problems by leveraging the fundamental insight that different communication modalities serve different cognitive purposes. Voice unlocks exploration and rapid context gathering. Writing crystallizes insights into actionable wisdom. The magic happens in their strategic interplay.

### Three-Phase Architecture

**Phase 1: Quick Problem Identification**  
Rapid, conversational problem surfacing to identify the one thing that, if solved today, would create the most momentum.

**Phase 2: Deep Coaching Session**  
Exploratory dialogue that builds rich context through natural conversation, probing questions, and surfacing relevant past experiences.

**Phase 3: Comprehensive Written Report**  
All context and insights synthesized into a carefully crafted document integrating personal values, professional context, and conversation history into clear, actionable insights.

## 🚀 Quick Start

```bash
# Clone and set up
git clone https://github.com/yourusername/diary-coach.git
cd diary-coach
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# For multi-agent features (optional):
echo "TODOIST_API_TOKEN=your_todoist_token" >> .env
echo "LANGSMITH_API_KEY=your_langsmith_key" >> .env

# Run the coach
python run_multi_agent.py
```

## 💬 Usage Experience

```
🌅 Daily Coach Ready
Type 'help' for guidance, 'stop' to end session

> good morning
Good morning Michael! I see you have 6 tasks due today. What's the 
one challenge that, if solved, would create the most momentum?

> I need to work on my product strategy but feeling overwhelmed
I notice "Product roadmap review" is one of your tasks today. 
What specifically about the strategy feels overwhelming right now?

> stop
=== Session Complete ===
✅ Problem identified: Product strategy overwhelm
✅ Root cause discovered: Too many competing priorities
✅ Action plan created: Focus on user feedback integration first

📄 Full report saved to: data/sessions/2025-07-19_session.md
```

## ✨ Core Features

### 🤖 Multi-Agent Coaching System
- **Enhanced Coach Agent**: Orchestrates other agents during Stage 1 for rich context
- **Memory Agent**: Recalls past conversations and identifies patterns
- **Personal Content Agent**: Integrates your core beliefs and values
- **MCP Agent**: Connects to external tools (Todoist, calendar, etc.)
- **Smart Triggering**: Agents activate based on conversation context
- **Rate Limiting**: Prevents overwhelming with excessive agent calls

### 🧠 Intelligent Coaching Capabilities
- **Non-Directive Approach**: Facilitates self-discovery through powerful inquiry
- **Morning Specialization**: Time-aware coaching adapted to morning energy
- **Context Building**: Each conversation builds on complete personal history
- **Values Integration**: Weaves your stated principles throughout guidance
- **Deep Thoughts Generation**: Sonnet 4-powered synthesis for pinneable insights

### 📊 Advanced Evaluation System
- **5-Criteria Assessment** (New simplified system):
  - A. Problem Definition & Scoping
  - B. Crux Recognition
  - C. Today's Specific Accomplishment
  - D. Multiple Paths
  - E. Core Beliefs & Values
- **LangSmith Integration**: Full conversation tracing and evaluation
- **Continuous Improvement**: Each session evaluated for coaching effectiveness

### 🔒 Privacy & Control
- **Local Data Storage**: All conversations stored on your machine
- **Data Portability**: Export and move your data between AI providers
- **No Vendor Lock-in**: Open architecture works with multiple LLM providers
- **Transparent Processing**: See exactly how your data is used

## 🏗️ Architecture

### Multi-Agent Orchestration
```
User Input → Enhanced Coach → Agent Registry → Specialized Agents
                ↓                                      ↓
            Stage Detection                    Context Gathering
                ↓                                      ↓
            Rich Response ← Context Enhancement ← Agent Responses
```

### Key Components
- **MultiAgentCLI**: Unified entry point with configurable modes
- **Agent Registry**: Dynamic agent discovery and coordination
- **BaseAgent Interface**: Standardized agent communication protocol
- **LangSmith Tracing**: Comprehensive observability for all interactions

## 📁 Project Structure

```
diary-coach/
├── run_multi_agent.py       # Main entry point
├── src/
│   ├── agents/              # Multi-agent implementations
│   │   ├── coach_agent.py   # Enhanced coach with Stage 1 integration
│   │   ├── memory_agent.py  # Conversation history and patterns
│   │   ├── mcp_agent.py     # External tool integration
│   │   └── registry.py      # Agent discovery system
│   ├── interface/           # CLI and user interaction
│   ├── evaluation/          # 5-criteria assessment system
│   ├── config/              # Centralized configurations
│   └── utils/               # Shared utilities
├── tests/
│   ├── agents/              # Agent-specific tests
│   ├── integration/         # Multi-agent integration tests
│   └── test_smoke.py        # Fast smoke tests (<1 second)
├── scripts/
│   ├── run_tests.py         # Smart test runner
│   └── run_smoke_tests.py   # Ultra-fast test suite
└── docs/
    ├── status.md            # Current project state
    ├── ProductVision.md     # Strategic product direction
    └── session_*/           # Development session logs
```

## 🧪 Testing

```bash
# Run fast tests only (default)
pytest

# Run all tests including slow integration tests
pytest --slow

# Run smoke tests (ultra-fast, <1 second)
python scripts/run_smoke_tests.py

# Run specific test categories
pytest tests/agents/ -v
pytest tests/integration/ -v --slow

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test Categories
- **Unit Tests**: Fast, isolated component tests (default)
- **Integration Tests**: Multi-agent interaction tests (marked @pytest.mark.slow)
- **Smoke Tests**: Critical path validation (<1 second total)
- **E2E Tests**: Full system workflows with real LLMs

## 📈 Current Status: Session 8.9 Complete

### ✅ Multi-Agent System Operational
- **Enhanced Coach**: Successfully integrates Memory, Personal Content, and MCP agents
- **Real Todoist Integration**: Fetches and displays tasks with smart filtering
- **Conversation Persistence**: Auto-saves all sessions for memory agent
- **LangSmith Tracing**: Full observability for multi-agent interactions
- **Test Suite Health**: All tests passing after comprehensive fixes

### 📊 System Metrics
- **Test Coverage**: 30+ test files, 200+ tests passing
- **Code Quality**: All files pass flake8 with 88-char limit
- **Architecture**: Clean separation with no legacy code
- **Performance**: Smoke tests run in <1 second

## 🔜 Next Steps

### Immediate Priorities
- [ ] Implement Stage 2 and Stage 3 coaching transitions
- [ ] Add Deep Thoughts evaluation to multi-agent CLI
- [ ] Create eval command for persona-based testing
- [ ] Enhanced reporting with multi-agent metrics

### Future Enhancements
- [ ] Voice integration for Phase 1 exploration
- [ ] Caching layer for external API calls
- [ ] Agent health monitoring dashboard
- [ ] User preference management
- [ ] Extended MCP server support
- [ ] Mobile companion app

## 🛠️ Configuration

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional for multi-agent features
TODOIST_API_TOKEN=...         # From Todoist Settings > Integrations
LANGSMITH_API_KEY=...         # For conversation tracing
LANGSMITH_PROJECT=diary-coach # Project name in LangSmith

# Optional modes
DISABLE_MULTI_AGENT=true      # Use simple single-agent mode
```

### Agent Configuration
Agents can be configured via `src/config/agents.yaml`:
- Trigger patterns
- Rate limits
- Context priorities
- Model selection

## 📚 Documentation

- **[Project Status](docs/status.md)**: Detailed development history
- **[Product Vision](docs/ProductVision.md)**: Strategic product direction
- **[MCP Integration Guide](docs/MCP_howto.md)**: MCP server integration
- **[Session Logs](docs/session_*)**: Development session documentation
- **[CLAUDE.md](CLAUDE.md)**: AI development guidelines

## 🎯 Core Development Principles

1. **Working Software Only**: Every session produces runnable code
2. **Tests Define Success**: Write tests first, implementation follows
3. **Documentation Is Code**: Keep docs in sync or the build is broken
4. **Privacy First**: User data sovereignty is non-negotiable
5. **Quality Over Quantity**: One profound insight beats ten observations

## 🤝 Contributing

This project follows strict TDD principles:
1. Write failing tests first
2. Implement minimal code to pass
3. Lint immediately with `python -m flake8`
4. Update documentation with changes
5. Ensure all tests pass before committing

---

**Ready to transform your daily problem-solving?**

```bash
python run_multi_agent.py
```

Experience the power of multi-modal coaching that helps you identify and tackle what truly matters today.
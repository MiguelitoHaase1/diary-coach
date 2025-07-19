# Diary Coach - Multi-Agent Text-First Coaching System

A sophisticated multi-agent conversational AI system designed to provide personalized coaching through text-based interactions, with comprehensive conversation evaluation across 7 coaching dimensions.

## 🚀 Quick Start - Try the Prototype

```bash
# Set up your environment
source venv/bin/activate

# Ensure you have your Anthropic API key
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# Run the coaching system (default: multi-agent mode)
python run_multi_agent.py

# For single-agent mode (simpler, faster, no external integrations):
DISABLE_MULTI_AGENT=true python run_multi_agent.py
```

## 💬 How to Use

Start a natural conversation with your AI coach:

```
🌅 Diary Coach Ready
💡 Tips: Say 'stop', 'end conversation', or 'wrap up' to get your coaching evaluation
   Then use 'deep report' for detailed AI analysis, or 'exit' to quit

> good morning
Good morning Michael! What's the one challenge you're ready to tackle today?

> I need to work on my product strategy
That sounds important. What specifically about your product strategy needs your attention today?

> wrap up
=== Conversation Evaluation ===
Coaching Effectiveness: 7.8/10
Light evaluation report saved to: docs/prototype/eval_20250629_143022.md

> deep report  # Optional: enhanced AI analysis
Report upgraded with comprehensive AI reflection!

> exit
Goodbye! Have a transformative day! 🌟
```

## ✨ Core Features

### 🤖 Intelligent Non-Directive Coaching
- **Morning Specialization**: Time-aware coaching with morning-specific prompts and energy (6:00 AM - 11:59 AM)
- **Client-Centered Approach**: Maintains client autonomy through powerful inquiry rather than advice-giving
- **Context Awareness**: Maintains conversation history and builds on previous discussions
- **Natural Interaction**: Responds to natural language without rigid command structures
- **Flexible Architecture**: Single entry point with configurable multi-agent support
- **Multi-Agent Features** (enabled by default):
  - **Todoist Integration**: Accesses your real tasks and priorities
  - **Memory Agent**: Recalls past conversations and patterns
  - **Personal Content**: References your core beliefs and values

### 🧠 Deep Thoughts Generation
- **Pinneable Insights**: Opus-powered analysis you'll want to revisit throughout the day
- **Breakthrough Thinking**: Transforms conversations into actionable insights
- **Comprehensive Analysis**: Includes evaluation summaries and full conversation transcripts

### 📊 Advanced 7-Dimension Evaluation System
- **3-Tier LLM Architecture**: Strategic model selection for cost-effectiveness:
  - **GPT-4o-mini**: Cheap testing during development (~$0.15/M tokens)
  - **Claude Sonnet**: Standard operations and persona simulation (~$3/M tokens) 
  - **Claude Opus**: Premium analysis for Deep Thoughts generation (~$15/M tokens)

- **7 Coaching Dimensions Measured**:
  1. **Problem Significance Assessment**: Evaluates how effectively the coach helps clients assess problem importance, urgency, and priority
  2. **Task Concretization**: Measures transformation of vague goals into specific, measurable, actionable tasks
  3. **Solution Diversity**: Assesses facilitation of creative thinking and multiple solution generation
  4. **Crux Identification**: Evaluates discovery of root causes and high-impact leverage points
  5. **Crux Solution Exploration**: Measures depth of solutions targeting identified core issues
  6. **Belief System Integration**: Assesses examination and transformation of limiting beliefs
  7. **Non-Directive Coaching Style**: Evaluates adherence to client autonomy and self-discovery principles

- **Standardized Evaluation Framework**:
  - 5-point rating scale with detailed rubrics
  - Step-by-step evaluation process
  - JSON output with scores, reasoning, strengths, and improvements
  - Comprehensive behavioral analysis across all dimensions

### 🎯 Natural User Experience
- **Multiple End Commands**: Natural ways to end conversations:
  - `stop`, `stop here`, `end conversation`, `wrap up`, `that's enough`, `finish`
  - `go to report`, `generate report`, `evaluate`, `evaluation`, `end session`
- **Progressive Enhancement**: Start with light analysis, optionally enhance with deep AI insights
- **Conversation Transcripts**: Full conversation history included in all reports

### 📈 Quality Assurance
- **Automated Testing**: 35+ tests covering all system components
- **PM Persona Testing**: 3 enhanced personas test coaching against different resistance patterns:
  - **ControlFreak**: Shows procrastination and fear of imperfection
  - **FrameworkRigid**: Intellectual thinking over action
  - **LegacyBuilder**: Vision obsession over daily execution
- **Task-Specific Scenarios**: Concrete problem identification scenarios (file organization, user research, team communication)
- **Conversation Generation**: Automated creation of realistic coaching scenarios for evaluation

## 🏗️ Architecture Overview

The system employs an **event-driven architecture** with specialized components:

### Core Components
- **Coach Agent**: Main conversational AI using Michael's coaching prompt and non-directive style
- **Enhanced CLI**: Production-ready interface with natural language command processing
- **Evaluation System**: 7-dimension behavioral analysis and performance tracking
- **LLM Service**: Async wrapper for Anthropic API with cost tracking and retry logic

### Evaluation Framework
- **7 Behavioral Analyzers**: LLM-powered assessment across coaching dimensions
- **Performance Tracker**: Response time monitoring and optimization insights
- **Report Generator**: Markdown reports with conversation transcripts and AI reflection
- **Persona Evaluator**: Tests coaching against realistic resistance patterns

## 📁 Project Structure

```
diary-coach/
├── src/                      # Source code
│   ├── main.py              # Application entry point
│   ├── agents/              # Coaching agent implementation
│   ├── interface/           # CLI and user interaction
│   ├── evaluation/          # 7-dimension analysis system
│   ├── services/           # External service integrations
│   ├── events/             # Event-driven architecture
│   └── persistence/        # Data storage
├── tests/                   # Comprehensive test suite
├── docs/                   # Documentation and session logs
│   ├── status.md          # Current project status
│   ├── session_*/         # Development session logs
│   └── prototype/         # Generated evaluation reports
└── venv/                  # Python virtual environment
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/interface/           # User interface tests
pytest tests/evaluation/          # Evaluation system tests
pytest tests/integration/         # End-to-end tests
```

## 📊 Development Approach

This project follows **three core principles**:

### 1. **Compartmentalization Through Incremental Development**
Minimize cognitive load by breaking work into small, testable increments. Each session is decomposed into bite-sized tasks that can be independently tested and validated.

### 2. **Continuous Improvement Through Evaluation**
Set up testable evaluations to measure and improve AI collaboration effectiveness. Track what works, what doesn't, and refine based on empirical results.

### 3. **Learning While Building**
Transform development into education through comprehensive documentation. Every session generates logs and learning opportunities.

## 📈 Current Status: Enhanced Evaluation System Live

✅ **Production-Ready 7-Dimension Evaluation**
- Natural language command processing
- Comprehensive coaching effectiveness measurement
- Two-tier analysis (light + deep reports)
- Standardized JSON evaluation outputs
- User-friendly CLI flow

✅ **Professional Coaching Standards**
- Non-directive coaching methodology
- Root cause and leverage point identification
- Belief system transformation support
- Client autonomy and self-discovery focus

✅ **Robust Technical Foundation**
- Event-driven architecture ready for scaling
- Comprehensive test coverage (80+ tests passing)
- Production-ready error handling
- Async operations with performance monitoring
- Docker/Kubernetes deployment ready

## 🔜 Next Steps

- **Session 4**: Scale to Redis event bus for multi-user performance
- **Session 5**: Multi-agent routing and orchestration
- **Session 6**: Specialized coaching agents and personality variants

## 🔧 Development Requirements

- **Python 3.13+**
- **Anthropic API Key** (for Claude integration)
- **Virtual Environment** (included in repo)

## 📚 Documentation

- **[Project Status](docs/status.md)**: Detailed current state and achievements
- **[Development Roadmap](docs/Roadmap.md)**: Multi-session development plan
- **[Session Logs](docs/session_*)**: Detailed development session documentation
- **[Learning Ledger](docs/learning_ledger.md)**: Knowledge tracking and gaps
- **[Evaluation Templates](docs/Evaluations_new.md)**: Detailed 7-dimension coaching evaluation criteria

## 🎯 Project Goals

Build a sophisticated coaching system that:
- Provides genuinely helpful non-directive coaching conversations
- Continuously improves through 7-dimension behavioral analysis
- Maintains natural, human-like interaction patterns
- Supports client autonomy and self-discovery
- Scales to support multiple users and specialized coaching domains
- Serves as a learning platform for AI-powered conversation design

---

**Ready to start coaching?** 

For standard coaching:
```bash
source venv/bin/activate && python -m src.main
```

For multi-agent coaching with Todoist, memory, and personal content:
```bash
source venv/bin/activate && python run_multi_agent.py
```

Experience:
- **Non-Directive Excellence**: Client-centered coaching that facilitates self-discovery
- **7-Dimension Analysis**: Comprehensive evaluation across all coaching effectiveness metrics
- **Deep Thoughts Reports**: Pinneable insights generated with Claude Opus 
- **Smart Evaluation**: Cost-optimized analysis using the right model for each task
- **Natural Commands**: Say "stop" for evaluation, "deep report" for comprehensive insights
- **Multi-Agent Intelligence**: Real task data, conversation memory, and personal values integration
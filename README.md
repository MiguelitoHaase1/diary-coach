# Diary Coach - Multi-Agent Text-First Coaching System

A sophisticated multi-agent conversational AI system designed to provide personalized coaching through text-based interactions, with comprehensive conversation evaluation and behavioral change detection.

## 🚀 Quick Start - Try the Prototype

```bash
# Set up your environment
source venv/bin/activate

# Ensure you have your Anthropic API key
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# Run the coaching prototype
python -m src.main
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

## ✨ Current Features

### 🤖 Intelligent Coaching
- **Personalized Conversations**: Uses Michael's specific coaching style and approach
- **Context Awareness**: Maintains conversation history and builds on previous discussions
- **Natural Interaction**: Responds to natural language without rigid command structures

### 📊 Advanced Evaluation System
- **Behavioral Analysis**: 4 LLM-powered analyzers measuring coaching effectiveness:
  - **Specificity Push**: How well the coach challenges vague statements
  - **Action Orientation**: Drives toward concrete commitments and next steps
  - **Emotional Presence**: Acknowledges emotions before jumping to solutions
  - **Framework Disruption**: Questions systematic thinking patterns
- **Performance Tracking**: Real-time response speed monitoring with percentile reporting
- **Two-Tier Reports**: Light reports for immediate feedback, deep reports with AI reflection

### 🎯 Natural User Experience
- **Multiple End Commands**: Natural ways to end conversations:
  - `stop`, `stop here`, `end conversation`, `wrap up`, `that's enough`, `finish`
  - `go to report`, `generate report`, `evaluate`, `evaluation`, `end session`
- **Progressive Enhancement**: Start with light analysis, optionally enhance with deep AI insights
- **Conversation Transcripts**: Full conversation history included in all reports

### 📈 Quality Assurance
- **Automated Testing**: 80+ tests covering all system components
- **PM Persona Testing**: 3 realistic personas test coaching against different resistance patterns
- **Conversation Generation**: Automated creation of coaching scenarios for evaluation

## 🏗️ Architecture Overview

The system employs an **event-driven architecture** with specialized components:

### Core Components
- **Coach Agent**: Main conversational AI using Michael's coaching prompt and style
- **Enhanced CLI**: Production-ready interface with natural language command processing
- **Evaluation System**: Comprehensive behavioral analysis and performance tracking
- **LLM Service**: Async wrapper for Anthropic API with cost tracking and retry logic

### Evaluation Framework
- **Behavioral Analyzers**: LLM-powered assessment of coaching effectiveness
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
│   ├── evaluation/          # Conversation analysis system
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

## 📈 Current Status: Session 3.2 Complete

✅ **Production-Ready Evaluation System**
- Natural language command processing
- Reliable markdown report generation  
- Two-tier analysis (light + deep reports)
- Comprehensive conversation transcripts
- User-friendly CLI flow

✅ **Behavioral Change Detection Framework**
- 4 LLM-powered behavioral analyzers
- 3 PM personas with realistic resistance patterns
- Performance tracking with percentile reporting
- Automated conversation generation for testing

✅ **Robust Technical Foundation**
- Event-driven architecture ready for scaling
- Comprehensive test coverage (80+ tests passing)
- Production-ready error handling
- Async operations with performance monitoring

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

## 🎯 Project Goals

Build a sophisticated coaching system that:
- Provides genuinely helpful coaching conversations
- Continuously improves through behavioral analysis
- Maintains natural, human-like interaction patterns
- Scales to support multiple users and specialized coaching domains
- Serves as a learning platform for AI-powered conversation design

---

**Ready to start coaching?** Run `source venv/bin/activate && python -m src.main` and begin your conversation!
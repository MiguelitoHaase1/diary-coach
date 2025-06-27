# Diary Coach - Multi-Agent Text-First Coaching System

A sophisticated multi-agent conversational AI system designed to provide personalized coaching through text-based interactions, with eventual voice integration capabilities.

## Project Philosophy

This project follows a **Test-Driven Development (TDD) approach** with text-first implementation, prioritizing conversation quality and system reliability over rapid voice integration. The architecture uses an event-driven foundation that seamlessly supports both current text-based development and future LiveKit voice integration.

## Architecture Overview

The system employs a **multi-agent orchestration pattern** with specialized coaching agents coordinated through an event bus:

- **Orchestrator Agent**: Routes conversations and coordinates specialized agents
- **Goal-Setting Agent**: Handles morning goal-setting and value identification  
- **Reflection Agent**: Manages evening reflection and day review
- **Challenge Agent**: Provides supportive yet skeptical questioning
- **Context Agent**: Maintains conversation history and personal insights

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start the coaching system
python -m src.main
```

## Development Phases

Read the docs/lesson_plan.md for development phases


## Current Status

Read the docs/status.md for a status check on how development is going.

## Testing Philosophy

Every component is developed with comprehensive test coverage focusing on:
- **Conversation Quality**: Response relevance, coherence, personality consistency
- **Multi-Agent Coordination**: Seamless handoffs and context preservation  
- **Performance**: Sub-2-second response times and error handling
- **User Experience**: Goal alignment and appropriate challenge balance

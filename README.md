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

### Phase 1: Foundation (Lessons 1-3)
- TDD infrastructure with comprehensive evaluation metrics
- Event-bus architecture using NATS with JetStream
- Conversation quality evaluation framework

### Phase 2: Core Agents (Lessons 4-6)  
- Orchestrator implementation with conversation routing
- Specialized coaching agents with distinct personalities
- Multi-agent integration and coordination

### Phase 3: Advanced Features (Lessons 7-8)
- Long-term conversation memory and context management
- Performance optimization and monitoring systems

### Phase 4: Voice Integration (Lessons 9-12)
- LiveKit infrastructure integration
- Voice-text hybrid conversations
- Production deployment and scaling

## Current Status

**Project Initialization**: ✅ Complete
- Clean project structure established
- Git repository initialized
- Basic documentation created

**Next Steps**: 
- Lesson 1: Project Setup and TDD Infrastructure
- Install testing framework and conversation evaluation tools
- Implement basic event-bus architecture

## Testing Philosophy

Every component is developed with comprehensive test coverage focusing on:
- **Conversation Quality**: Response relevance, coherence, personality consistency
- **Multi-Agent Coordination**: Seamless handoffs and context preservation  
- **Performance**: Sub-2-second response times and error handling
- **User Experience**: Goal alignment and appropriate challenge balance

## License

MIT License - See LICENSE file for details
# Claude Agent Prompts

This directory contains specialized prompts for Claude sub-agents that can be invoked for specific tasks in the diary-coach project.

## Available Agents

### 1. **UI Agent** (`ui_agent.md`)
- **Purpose**: Frontend and user interface development
- **Expertise**: React, TypeScript, accessibility, performance
- **Worktree**: `worktrees/ui`
- **Use when**: Building or modifying user interfaces

### 2. **MCP Agent** (`mcp_agent.md`)
- **Purpose**: Model Context Protocol integrations
- **Expertise**: External service connections, API integrations
- **Worktree**: `worktrees/mcp`
- **Use when**: Integrating with Todoist, calendars, or other external services

### 3. **LangGraph Agent** (`langgraph_agent.md`)
- **Purpose**: Multi-agent orchestration and workflow design
- **Expertise**: LangGraph, state management, agent coordination
- **Worktree**: `worktrees/langgraph`
- **Use when**: Refactoring to LangGraph architecture or building complex workflows

### 4. **LiveKit Agent** (`livekit_agent.md`)
- **Purpose**: Voice interface and real-time communication
- **Expertise**: WebRTC, voice processing, real-time audio
- **Worktree**: `worktrees/voice`
- **Use when**: Implementing voice features or audio streaming

### 5. **Evaluation Agent** (`evaluation_agent.md`)
- **Purpose**: Testing, quality assurance, and metrics
- **Expertise**: Test frameworks, evaluation metrics, CI/CD
- **Worktree**: Can work across all worktrees
- **Use when**: Building test suites or evaluation pipelines

### 6. **Documentation Agent** (`documentation_agent.md`)
- **Purpose**: Creating and maintaining documentation
- **Expertise**: Technical writing, API docs, architecture diagrams
- **Worktree**: Typically works in main branch
- **Use when**: Documenting features, APIs, or architecture

## Usage

These prompts are designed to be used with Claude's sub-agent functionality as described in `CLAUDE.md`. When you need specialized expertise:

1. Identify which agent's expertise matches your task
2. Invoke the appropriate agent with their specific prompt
3. The agent will work in their designated worktree if applicable

## Example

```
"I need to implement a new voice interface for the coaching system. 
Please use the LiveKit Agent to help with this task."
```

## Prompt Maintenance

- Prompts should be updated as technologies and best practices evolve
- Each prompt is self-contained with all necessary context
- Prompts follow a consistent structure for easy navigation
- Version control tracks all changes to prompts

## Adding New Agents

To add a new specialized agent:

1. Create a new `.md` file in this directory
2. Follow the existing prompt structure
3. Update this README with the new agent's information
4. Create a corresponding worktree if needed
5. Update `CLAUDE.md` with the new agent details
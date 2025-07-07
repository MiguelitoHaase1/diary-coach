# Observability Tools

Tools for debugging and monitoring the MCP integration and coach agent behavior.

## Tools Overview

### 1. LangSmith Debug Tool (`debug_langsmith.py`)
- **Purpose**: Provides observability into MCP integration with tracing
- **Use case**: Debug why todos are being hallucinated vs fetched correctly
- **Output**: Traces MCP calls, context processing, and decision paths

### 2. MCP Sandbox CLI (`mcp_sandbox.py`)  
- **Purpose**: Direct interface to test MCP Todoist integration
- **Use case**: Isolate MCP issues from coach agent logic
- **Output**: Raw MCP responses and connection diagnostics

## Setup

### LangSmith Setup
```bash
# Install LangSmith
pip install langsmith

# Set API key (get from https://smith.langchain.com/settings)
export LANGSMITH_API_KEY='your-api-key-here'

# View traces at
# https://smith.langchain.com/
```

### MCP Prerequisites
```bash
# Install Todoist MCP server
npm install -g @doist/todoist-mcp

# Set Todoist API token
export TODOIST_API_TOKEN='your-todoist-token'
```

## Usage

### LangSmith Debug Tool

**Basic debugging:**
```bash
python debug_langsmith.py
```

**What it shows:**
- MCP connection status
- Todo fetching process
- Context filtering results
- Decision path through the system
- Would-be LangSmith trace data

**Example output:**
```
🔍 Testing MCP flow with message: 'what are my tasks today?'
==================================================

1. Testing MCP Status...
   Status: {
     "connected": true,
     "last_sync": "2025-07-07T10:30:00",
     "total_todos": 4,
     "using_mock_data": false
   }

2. Testing Todo Fetching...
   Todos fetched: 2
   Context usage: {
     "todos_fetched": true,
     "filter_applied": true,
     "total_todos": 4,
     "filtered_todos": 2
   }
```

### MCP Sandbox CLI

**Setup check:**
```bash
python mcp_sandbox.py --setup
```

**Connection test:**
```bash
python mcp_sandbox.py --test
```

**List actual todos:**
```bash
python mcp_sandbox.py --list
```

**Interactive mode:**
```bash
python mcp_sandbox.py --interactive
```

**Interactive commands:**
- `list` - Show your real Todoist tasks
- `create <content>` - Create a new task
- `connect` - Test MCP connection
- `quit` - Exit

**Example session:**
```
mcp> connect
✅ Session initialized
📋 Available tools:
   - get_tasks: Get tasks from Todoist
   - create_task: Create a new task

mcp> list
📋 Fetching tasks from Todoist...
   ✅ Retrieved 4 tasks
1. Finish API integration for Q4 project
2. Prepare presentation for client meeting
3. Review team meeting prep materials
4. Update project documentation

mcp> create Test from sandbox
➕ Creating task: Test from sandbox
   ✅ Created task: 7234567890
```

## Debugging Workflow

### Step 1: Test MCP Connection
```bash
python mcp_sandbox.py --test
```
- Verifies MCP server is accessible
- Checks API token configuration
- Lists available tools

### Step 2: Verify Real Data
```bash
python mcp_sandbox.py --list
```
- Shows actual Todoist tasks
- Confirms data is flowing correctly
- Identifies if issue is in MCP or coach logic

### Step 3: Trace Coach Processing
```bash
python debug_langsmith.py
```
- Shows how coach processes MCP data
- Reveals filtering and context decisions
- Identifies where hallucination occurs

### Step 4: Compare Results
Compare outputs:
- **MCP Sandbox**: Raw Todoist data
- **LangSmith Debug**: Processed coach data
- **Coach Agent**: Final user response

## Common Issues & Solutions

### Issue: "No API token found"
**Solution:**
```bash
export TODOIST_API_TOKEN='your-token-here'
# Get token from https://todoist.com/prefs/integrations
```

### Issue: "MCP server not found"
**Solution:**
```bash
npm install -g @doist/todoist-mcp
# Or check paths shown in --setup
```

### Issue: "Empty response from MCP"
**Check:**
1. API token is valid
2. MCP server is correct version
3. Network connectivity

### Issue: "Hallucinated todos vs real todos"
**Debug process:**
1. `python mcp_sandbox.py --list` - See real todos
2. `python debug_langsmith.py` - See coach processing
3. Compare filtering logic in `mcp_todo_node.py:282`

## Files Modified

When using these tools, check these files for configuration:
- `src/orchestration/mcp_todo_node.py` - MCP integration logic
- `src/orchestration/context_graph.py` - Context processing
- `src/agents/coach_agent.py` - Agent response generation

## Environment Variables

Required:
- `TODOIST_API_TOKEN` - Your Todoist API token
- `LANGSMITH_API_KEY` - LangSmith API key (optional)

Optional:
- `DEBUG_MCP=true` - Enable MCP debug output
- `MOCK_MCP=true` - Use mock data instead of real MCP calls
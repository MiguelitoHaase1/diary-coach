# Multi-Agent Setup Guide

## Prerequisites

1. **Todoist API Token**
   - Go to: https://todoist.com/app/settings/integrations/developer
   - Copy your API token
   - Add to your `.env` file:
   ```
   TODOIST_API_TOKEN=your_token_here
   ```

2. **MCP Server Setup**
   - The system uses MCP (Model Context Protocol) to connect to Todoist
   - MCP server should be available at: `npx -y @modelcontextprotocol/server-todoist`
   - This is handled automatically by the system

## Running Multi-Agent System

```bash
# Activate virtual environment
source venv/bin/activate

# Run multi-agent system (NOT src.main)
python run_multi_agent.py
```

## Troubleshooting

### 1. Coach Not Asking Key Questions
- Check if running `run_multi_agent.py` (not `python -m src.main`)
- Verify it's morning time (6:00 AM - 11:59 AM) for morning protocol
- Check logs for "EnhancedDiaryCoach.process_message called"

### 2. Todos Not Fetching
- Verify `TODOIST_API_TOKEN` is set in `.env`
- Check console output for MCP connection status
- Look for "MCP Agent initialized with X todos" message
- If you see "MCP Agent initialized without connection", check your API token

### 3. Debugging Steps
1. Check environment variable:
   ```bash
   echo $TODOIST_API_TOKEN
   ```

2. Test MCP connection directly:
   ```bash
   npx -y @modelcontextprotocol/server-todoist
   ```

3. Run with debug logging:
   ```bash
   export DEBUG=1
   python run_multi_agent.py
   ```

## Expected Behavior

When working correctly:
1. System shows "MCP Agent initialized with X todos"
2. When you ask about priorities/tasks, coach references real Todoist items
3. Tasks due today are highlighted with 🔴 [DUE TODAY]
4. Console shows "[Agents consulted: mcp]" when tasks are accessed

## Common Issues

1. **"I don't have access to your current todo list"**
   - You're running the standard coach, not multi-agent
   - Use `python run_multi_agent.py` instead

2. **No todos shown despite having tasks**
   - Missing or incorrect TODOIST_API_TOKEN
   - MCP server not running/accessible
   - Network connectivity issues

3. **Coach behavior seems different**
   - Confirm using enhanced coach (check logs)
   - Verify morning time for morning protocol
   - Check agent triggers are working
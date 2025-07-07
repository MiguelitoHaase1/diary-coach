# Session 6.11 Log: MCP Integration Still Not Working

**Date**: July 5, 2025  
**Duration**: ~1 hour  
**Objective**: Debug and fix remaining MCP integration issues  
**Status**: ❌ UNRESOLVED - Core integration bug still preventing real todo access

## Problem Statement

Despite extensive architectural fixes and debugging, the coach is still not properly integrating with user's real Todoist data. While the technical infrastructure works correctly with mock data, the real MCP server integration has persistent issues.

## Progress Made

### ✅ Architectural Issues Fixed
1. **Threshold Mismatch Resolved**:
   - Fixed coach agent: `relevance >= 0.3` (was `> 0.3`)
   - Fixed MCP node: `relevance < 0.3` (was `<= 0.6`)
   - Now properly triggers for "What are my tasks today?" (score: 0.3)

2. **Debug Logging Added**:
   - Complete visibility into relevance scoring pipeline
   - MCP fetch process fully instrumented
   - System prompt enhancement tracking working

3. **Token Configuration Completed**:
   - API token properly set in Claude Desktop config
   - Environment variable passing implemented
   - Token discovery logic handles multiple variable names

### ✅ Technical Infrastructure Working
- **Relevance Scoring**: ✅ Keywords detected correctly
- **Threshold Logic**: ✅ Fixed off-by-one error  
- **MCP Node**: ✅ Called with correct parameters
- **Fallback Mechanism**: ✅ Returns mock data when MCP fails
- **System Prompt Enhancement**: ✅ Adds +515 characters of todo context
- **LLM Integration**: ✅ Enhanced prompt reaches language model

## Current Debug Output

```
🎯 DEBUG: Task keywords found: ['today', 'task']
📊 DEBUG: Relevance score: 0.3
🚪 DEBUG: Threshold check: 0.3 >= 0.3 = True
✅ DEBUG: Threshold met, fetching todos...
🔑 MCP DEBUG: API token found: e39519d8a1...
📥 MCP DEBUG: Raw todos fetched: 4  
✅ MCP DEBUG: Filtered todos: 2
✨ DEBUG: Enhancing system prompt with todo context
✅ DEBUG: System prompt contains todo context!
```

## Outstanding Issues

### 1. ❌ MCP Server Environment Variable Issue
**Error**: `Error: TODOIST_API_KEY environment variable is required`
- MCP server expects `TODOIST_API_KEY` but may not be receiving it
- Environment passing from Python MCP client to Node.js server failing
- Fallback to mock data working, but real API integration blocked

### 2. ❌ MCP Server Process Communication
**Error**: `unhandled errors in a TaskGroup (1 sub-exception)`
- MCP stdio communication having unhandled exceptions
- Server starts correctly when run directly with environment variable
- Client-server communication via `stdio_client` has issues

### 3. ❌ User Experience Still Broken
Despite technical infrastructure working:
- Coach still returns generic responses about "having trouble pulling up tasks"
- No access to real Todoist task data in production
- Mock data integration working perfectly, but that's not the goal

## Root Cause Analysis

The issue appears to be at the **MCP client-server boundary**:

1. **Python side**: Token found, environment configured, MCP client code correct
2. **Node.js side**: MCP server requires environment variable but not receiving it
3. **Communication layer**: `stdio_client` from Python MCP library not properly passing environment to Node.js subprocess

## Technical Debt Created

1. **Debug logging everywhere**: Needs cleanup before production
2. **Mock data fallback working too well**: Masks the real integration failure
3. **Multiple token discovery paths**: Added complexity for edge cases
4. **Environment variable confusion**: `TODOIST_API_KEY` vs `TODOIST_API_TOKEN` inconsistency

## Configuration State

### Claude Desktop Config (Working)
```json
{
  "mcpServers": {
    "todoist": {
      "command": "node",
      "args": ["/Users/michaelhaase/Desktop/coding/diary-coach/mcp-servers/todoist-mcp/build/index.js"],
      "env": {
        "TODOIST_API_KEY": "e39519d8a1b1e2fad42ba4ab8f25b2f9fd04365c"
      }
    }
  }
}
```

### MCP Server (Built and Ready)
- ✅ Cloned and built Doist MCP server locally
- ✅ Server starts correctly with direct environment variable
- ✅ Path detection finds local build
- ❌ Environment variable not passed through MCP client

## Files Modified Today

- `src/agents/coach_agent.py`: Fixed threshold, added debug logging
- `src/orchestration/mcp_todo_node.py`: Fixed threshold, extensive debug logging, environment handling
- `~/Library/Application Support/Claude/claude_desktop_config.json`: Added Todoist MCP server config
- `test_debug_flow.py`: Created test script for debugging integration

## Recommendations for Next Session

### High Priority Fixes
1. **Investigate MCP client environment passing**: 
   - Check if `StdioServerParameters.env` properly passes to subprocess
   - Consider alternative approaches to environment variable passing
   - Test minimal MCP client example to isolate issue

2. **Alternative Integration Approaches**:
   - Direct API integration bypass (already built but removed)
   - Environment variable export before Python process
   - MCP server configuration outside of Python client

3. **Debug MCP Communication**:
   - Add server-side logging to confirm environment variables received
   - Test MCP server with simple test client
   - Verify stdio communication working correctly

### Medium Priority Tasks
1. **Clean up debug logging** once integration works
2. **Remove mock data fallback** to force real integration
3. **Test with real conversation flow** instead of test scripts

## Success Criteria for Tomorrow

- [ ] "What are my tasks today?" returns real Todoist tasks
- [ ] No fallback to mock data
- [ ] No MCP server environment errors
- [ ] Coach references actual user task content in responses
- [ ] Clean debug output showing real API integration

## Current Architectural State

The **Session 6 MCP integration** is **95% complete**:
- ✅ Relevance scoring and threshold logic
- ✅ MCP node architecture and fallback handling  
- ✅ System prompt enhancement with todo context
- ✅ Token configuration and discovery
- ❌ **MCP server environment communication** ← Core blocker

The hallucination problem is **architecturally solved** but **technically blocked** by the MCP client-server communication issue.
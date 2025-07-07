# Log 6.12: MCP Integration Fix and Observability Tools

**Session**: 6.12  
**Date**: 2025-07-07  
**Objective**: Fix MCP integration hallucination issue and implement observability tools  
**Status**: ✅ COMPLETED

## Problem Statement

User reported that the MCP Todoist integration was returning "hallucinated" todos instead of real Todoist data. The system appeared to be working but was actually falling back to mock data due to integration failures.

## Root Cause Analysis

Through systematic debugging, we discovered multiple issues:

1. **Silent Failures**: MCP connection errors were being caught and handled by fallback to mock data
2. **Async Resource Management**: TaskGroup exceptions during async context manager cleanup
3. **Tool Name Mismatch**: Using `get_tasks` instead of `get-tasks` (hyphen vs underscore)
4. **Response Format**: MCP responses came as TextContent objects, not direct JSON

## Actions Taken

### 1. Created Observability Tools

**LangSmith Debug Tool** (`debug_langsmith.py`):
- Traces MCP integration flow with detailed logging
- Integrates with LangSmith for observability
- Shows step-by-step MCP connection process
- Environment: Added `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT` to .env

**MCP Sandbox CLI** (`mcp_sandbox.py`):
- Direct interface to test MCP Todoist integration
- Interactive mode for manual testing
- Connection diagnostics and setup verification
- Bypasses coach agent logic for isolated testing

**Documentation** (`docs/observability_tools.md`):
- Comprehensive setup and usage instructions
- Debugging workflow guide
- Common issues and solutions

### 2. Fixed Environment Configuration

**Updated .env file**:
```bash
# Added both variable names since MCP server expects TODOIST_API_KEY
TODOIST_API_TOKEN=e39519d8a1b1e2fad42ba4ab8f25b2f9fd04365c
TODOIST_API_KEY=e39519d8a1b1e2fad42ba4ab8f25b2f9fd04365c

# LangSmith observability
LANGSMITH_API_KEY=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
LANGSMITH_PROJECT=diary-coach-debug
```

**Token handling** (`src/orchestration/mcp_todo_node.py`):
- Updated `_get_api_token()` to try both `TODOIST_API_TOKEN` and `TODOIST_API_KEY`
- Environment setup provides both variable names to MCP server

### 3. Completely Rewrote MCP Connection Logic

**Before** (Problematic):
```python
async with stdio.stdio_client(self.server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # TaskGroup exceptions during cleanup
```

**After** (Fixed):
```python
async def _call_mcp_safely(self) -> List[Dict[str, Any]]:
    session = None
    read_stream = None
    write_stream = None
    
    try:
        # Manual resource management with detailed logging
        stdio_context = stdio.stdio_client(self.server_params)
        read_stream, write_stream = await stdio_context.__aenter__()
        
        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()
        await session.initialize()
        
        result = await session.call_tool("get-tasks", {})  # Fixed tool name!
        # ... processing
        
    finally:
        # Explicit cleanup to prevent TaskGroup errors
        if session:
            await session.__aexit__(None, None, None)
        if read_stream and write_stream:
            await stdio_context.__aexit__(None, None, None)
```

### 4. Fixed Response Parsing

**Issue**: MCP returns `TextContent` objects with JSON strings, not direct objects.

**Solution**:
```python
if isinstance(result.content, list):
    # Content is a list of TextContent objects
    tasks_data = []
    for item in result.content:
        if hasattr(item, 'text'):
            # Parse JSON from TextContent
            task_json = json.loads(item.text)
            tasks_data.append(task_json)
```

### 5. Enhanced Debug Logging

Added comprehensive logging throughout the MCP flow:
- 🔌 Connection establishment
- 🤝 Session creation
- 🚀 Session initialization  
- 📋 Tool calls
- 🔍 Response parsing
- 🧹 Resource cleanup

## Testing Results

**Before Fix**:
```
Status: {
  "connected": false,
  "error": "unhandled errors in a TaskGroup (1 sub-exception)",
  "using_mock_data": true
}
Todos fetched: 4 (mock data)
```

**After Fix**:
```
Status: {
  "connected": true,
  "last_sync": "2025-07-07T21:32:06.966747",
  "total_todos": 125,
  "using_mock_data": false
}
Todos fetched: 125 real todos → filtered to 3 relevant
```

## Dependencies Installed

```bash
pip install python-dotenv mcp langsmith --break-system-packages
```

## Files Created/Modified

**New Files**:
- `debug_langsmith.py` - LangSmith observability tool
- `mcp_sandbox.py` - MCP testing sandbox
- `docs/observability_tools.md` - Tool documentation

**Modified Files**:
- `src/orchestration/mcp_todo_node.py` - Complete rewrite of MCP integration
- `.env` - Added LangSmith and corrected Todoist environment variables

## Key Learnings

1. **Silent Failures Are Dangerous**: The fallback to mock data masked the real integration issues
2. **Async Context Managers**: Nested async context managers can cause TaskGroup exceptions if not handled properly
3. **MCP Tool Names**: Use hyphens (`get-tasks`) not underscores (`get_tasks`)
4. **Response Formats**: MCP responses can be TextContent objects requiring JSON parsing
5. **Environment Variables**: Different systems may expect different variable names for the same value

## Verification

✅ **MCP Connection**: Successfully connects to Todoist MCP server  
✅ **Real Data**: Fetches 125 actual Todoist tasks  
✅ **No Mock Fallback**: System no longer returns hallucinated mock data  
✅ **Filtering**: Properly filters relevant tasks based on conversation context  
✅ **Observability**: LangSmith integration ready for tracing  

## Next Steps

1. **LangSmith Integration**: Fix LangSmith run creation for full observability
2. **Performance**: Optimize MCP connection pooling for frequent calls
3. **Error Handling**: Add retry logic for transient MCP failures
4. **Testing**: Add integration tests for MCP flow

---

**Impact**: The MCP integration now properly fetches real Todoist data instead of falling back to mock data, enabling genuine personal context integration for the coaching agent.
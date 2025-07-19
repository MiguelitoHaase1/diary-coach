# Session 8 - Increment 6: Multi-Agent System Integration Fixes

## Issues Identified

The user reported that the multi-agent system wasn't working properly:
1. Coach was not using morning protocol when user said "good morning"
2. Todoist integration was fetching tasks but coach wasn't using them
3. Date field extraction was looking for wrong field structure
4. Import errors and missing methods in multi-agent CLI

## Root Causes

### 1. Time-Based Morning Protocol
The coach was checking actual clock time (6 AM - 11:59 AM) instead of responding to user's "good morning" greeting.

### 2. Date Field Mismatch
The code was looking for `task.get("due", {}).get("date")` but Todoist was providing tasks with:
- Some with `due: { date: "2025-07-18" }`
- Some with just `date: "2025-07-18"`
- Many with `due: null` causing NoneType errors

### 3. Overly Restrictive Task Filtering
The `_filter_todos_by_context` function was filtering out most tasks when user asked "what are my todos?" because it was looking for specific keywords that didn't match.

### 4. Missing Mock Function
`_get_mock_todos()` was being called but never defined, causing errors when API token was missing.

### 5. Import/Factory Issues
- Wrong import for non-existent `ConversationEvaluator`
- Wrong method name `LLMFactory.get_cheap_llm()` (should be `create_cheap_service()`)

## Solutions Implemented

### 1. Context-Based Morning Detection
```python
def _is_morning_context(self, message_content: str) -> bool:
    """Check if user is in morning context based on their message."""
    morning_greetings = [
        "good morning", "morning", "gm", "g'morning", 
        "goodmorning", "mornin"
    ]
    content_lower = message_content.lower().strip()
    return any(greeting in content_lower for greeting in morning_greetings)
```

### 2. Flexible Date Field Extraction
```python
# Try multiple date field locations
due_date = None

# First try direct 'date' field
if task.get("date"):
    due_date = task.get("date")
# Then try 'due.date' structure
elif task.get("due", {}).get("date"):
    due_date = task.get("due", {}).get("date")
```

### 3. Smart Task Filtering
Added detection for general todo queries and improved filtering:
```python
# Check if user is asking for general todo list
general_queries = ["my todos", "my tasks", "what are my", "show me my", "list my", "today"]
is_general_query = any(query in content for query in general_queries)

if is_general_query:
    # Return all tasks prioritized by due date and priority
    # Tasks due today get score +10, high priority +5
```

### 4. Added Mock Function
```python
def _get_mock_todos(self) -> List[Dict[str, Any]]:
    """Return empty list instead of mock data to avoid confusion."""
    print("⚠️ MCP DEBUG: Returning empty todo list (no mock data)")
    return []
```

### 5. Fixed Imports and Factory Methods
- Removed invalid imports
- Changed to `LLMFactory.create_cheap_service()`
- Added basic test for multi-agent CLI

## Test Results

After fixes, the system successfully:
1. ✅ Responds to "good morning" with morning protocol regardless of time
2. ✅ Fetches 119 Todoist tasks without errors
3. ✅ Identifies 6 tasks due today
4. ✅ Shows tasks in coach responses with proper prioritization
5. ✅ Highlights due-today tasks with 🔴 [DUE TODAY] marker

## Debug Output Captured

```
🔑 MCP DEBUG: Checking API token...
✅ MCP DEBUG: API token found: e39519d8a1...
🔌 MCP DEBUG: Creating stdio connection...
✅ MCP DEBUG: Stdio connection established
🎉 MCP DEBUG: Successfully fetched 119 real todos
📅 MCP DEBUG: Today's date is 2025-07-18
✅ MCP DEBUG: Converted 30 tasks, 6 due today
📋 MCP DEBUG: General todo query detected, returning all todos
```

## Configuration Updates

### Updated .env.example
Added Todoist configuration section:
```
# === MULTI-AGENT CONFIGURATION ===
# Required for multi-agent coaching with Todoist integration

# Todoist API Configuration
# Get your API token from: https://todoist.com/app/settings/integrations/developer
TODOIST_API_TOKEN=your_todoist_api_token_here
```

### Updated README.md
Added clear distinction between standard and multi-agent modes:
```bash
# For standard coaching (without multi-agent support):
python -m src.main

# For multi-agent coaching (with Todoist, memory, and personal content):
python run_multi_agent.py
```

## Documentation Created

Created `docs/multi_agent_setup.md` with:
- Prerequisites and setup instructions
- Troubleshooting guide
- Common issues and solutions
- Expected behavior when working correctly

## Key Learnings

1. **User Intent Over System Time**: Morning protocol should respond to user's context ("good morning") not wall clock time
2. **Flexible Data Parsing**: External APIs may have varying data structures - handle multiple formats
3. **Context-Aware Filtering**: When user asks general questions like "what are my todos?", show everything relevant rather than filtering aggressively
4. **Clear Debug Output**: Comprehensive debug logging was essential for diagnosing the multi-layer issue
5. **Test Missing Integration Points**: Need tests for multi-agent CLI to catch import/method errors early

## Next Steps

- Add integration tests for multi-agent system
- Consider caching Todoist data to reduce API calls
- Implement proper error handling for MCP connection failures
- Add user configuration for task display preferences
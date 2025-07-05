# Daily Transformation Diary Coach - System Prompt

**IMPORTANT**: This file is now a reference copy only. 

The **master prompt** is located at: `/src/agents/prompts/coach_system_prompt.md`

All code references now load the prompt dynamically from that master file using the `PromptLoader` utility.

## To Edit the Coaching Prompt:

1. Edit the master file: `/src/agents/prompts/coach_system_prompt.md`
2. All agent implementations will automatically use the updated prompt
3. No code changes required - the system loads prompts dynamically

## Prompt Centralization Benefits:

- ✅ **Single Source of Truth**: One master prompt file
- ✅ **Automatic Synchronization**: All agents use the same prompt
- ✅ **Version Control**: Easy to track prompt changes in git
- ✅ **No Code Duplication**: Eliminates embedded prompt copies
- ✅ **Hot Reloading**: Prompt changes take effect immediately (cache can be cleared)

## Implementation Details:

The system uses a `PromptLoader` class that:
- Loads prompts from markdown files
- Caches prompts for performance
- Provides convenient access methods
- Handles file not found errors gracefully

See `/src/agents/prompts/__init__.py` for the implementation.
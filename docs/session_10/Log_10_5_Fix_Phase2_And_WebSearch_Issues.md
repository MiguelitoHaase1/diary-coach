# Session 10.5: Fix Phase 2 Questioning and Web Search Issues

**Date**: 2025-08-01
**Goal**: Fix broken phase 2 questioning and web search integration
**Outcome**: ✅ Fixed phase 2 issue, clarified web search behavior

## Summary

Successfully fixed the phase 2 questioning issue where the coach was exposing raw `<invoke>` tags to users. Also investigated and clarified that the web search agent is working as designed - it provides search suggestions, not actual web URLs.

## Issues Addressed

### 1. Phase 2 Questioning Broken (FIXED ✅)

**Problem**: The coach was literally showing `<invoke name="deep_thoughts_reporter">` tags to the user instead of handling agent invocation internally.

**Root Cause**: The morning protocol prompt instructed the coach to "engage the deep thoughts reporter agent" which caused the LLM to hallucinate a tool-calling syntax.

**Fix**: Updated the morning protocol prompt to clarify that the coach should continue the conversation, not attempt to invoke agents.

### 2. Web Search Not Providing Real URLs (CLARIFIED ✅)

**Problem**: User expected actual linked articles but only got search suggestions.

**Investigation**: 
- Theme extraction was failing due to format mismatch
- Web search agent is designed to provide suggestions only (not actual URLs)

**Fixes Applied**:
- Updated theme extraction regex to handle "Theme N:" format
- Added debug logging to track theme extraction and web search invocation
- Clarified that actual web search requires API integration

## Code Changes

### 1. Fixed Morning Protocol Prompt
**File**: `src/agents/prompts/coach_morning_protocol.md`
- Changed line 19 from "engage the deep thoughts reporter agent" to "continue with thoughtful follow-up questions"
- Added clarification: "DO NOT attempt to invoke or call any agents"

### 2. Enhanced Theme Extraction
**File**: `src/interface/multi_agent_cli.py`
- Updated regex to handle both old and new theme formats
- Added support for "Theme 1:", "Theme 2:", etc. pattern
- Added debug logging for theme extraction process

### 3. Added Debug Logging
**File**: `src/interface/multi_agent_cli.py`
- Shows number of themes extracted
- Confirms web search agent invocation
- Warns when no themes found or agent unavailable

## Technical Details

### Theme Extraction Fix
```python
# New pattern to match "Theme N: [title]" format
theme_pattern = r'Theme \d+: ([^\n]+)'
theme_matches = re.findall(theme_pattern, deep_thoughts_report)
```

### Debug Output Added
```
📊 Extracted 3 themes: ['Small Autonomous Teams...', 'AI Augmentation...', ...]
🔍 Calling Web Search Agent with themes: [...]
✅ Web Search Agent responded: True
```

## Current System Behavior

1. **Phase 2 Questions**: Coach now continues conversation naturally without exposing internal agent mechanics
2. **Web Search**: Properly extracts themes and provides search suggestions (not actual URLs)
3. **Deep Report**: Completes successfully with enhanced search recommendations

## Next Steps for Real Web Search

To provide actual linked articles, one of these approaches is needed:

1. **Option 1**: Integrate web search API (Brave, Google, Bing)
2. **Option 2**: Use Claude's native WebSearch tool when available
3. **Option 3**: Use Firecrawl MCP for actual web scraping
4. **Option 4**: Integrate with Perplexity API or similar

## Testing Instructions

```bash
# Test the fixes
python run_multi_agent.py

# Verify phase 2 works without showing <invoke> tags
# Use conversation flow leading to "deep report" command
# Check debug output shows theme extraction and web search calls
```

## Learning Opportunities

1. **LLM Prompting**: Specific wording in prompts can cause hallucinated behaviors
2. **Debug Logging**: Essential for understanding multi-agent interactions
3. **User Expectations**: Clear documentation needed about current vs future capabilities
4. **Regex Flexibility**: Supporting multiple formats improves robustness

## Files Modified

- `src/agents/prompts/coach_morning_protocol.md` (phase 2 fix)
- `src/interface/multi_agent_cli.py` (theme extraction and logging)
- `test_web_search_fix.py` (created for testing)
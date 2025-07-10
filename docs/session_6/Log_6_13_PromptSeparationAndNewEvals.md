# Log 6.13: Prompt Separation and New Evaluation Framework

## Actions Taken

### 1. Prompt Overlap Analysis
- **Problem**: Significant duplication between `coach_system_prompt.md` and `coach_agent.py` 
- **Found**: Overlapping content in morning ritual protocol, communication constraints, and coaching methodology
- **Impact**: Maintenance burden and inconsistent prompt behavior

### 2. Clear Separation of Concerns
**Designed split**:
- `coach_system_prompt.md`: Core identity, foundation principles, general methodology
- `coach_agent.py`: Time-specific ritual protocols and behaviors

### 3. Refactored coach_system_prompt.md
- **Removed**: Detailed morning/evening ritual steps (moved to agent)
- **Simplified**: Operational framework to reference time-based patterns
- **Retained**: Core function, foundation principles, coaching methodology, communication constraints

### 4. Enhanced coach_agent.py
- **Added**: `EVENING_PROMPT_ADDITION` with evening ritual protocol
- **Refactored**: `MORNING_PROMPT_ADDITION` to remove duplication
- **Implemented**: `_is_evening_time()` method and evening prompt logic
- **Result**: Clean time-based prompt selection

### 5. New Evaluation Framework Documentation
**User described 7 new evaluation criteria**:
1. **Problem Significance Assessment** (1-10): Depth of exploring why problems matter
2. **Task Concretization** (1-10): Transforming abstract problems into specific daily actions
3. **Solution Diversity Generation** (1-10): Exploring multiple solution approaches/paradigms
4. **Crux Identification** (1-10): Finding core constraints and leverage points
5. **Crux Solution Exploration** (1-10): Deep dive into overcoming identified constraints
6. **Belief System Integration** (1-10): Connecting beliefs to problem-solving approaches
7. **Non-Directive Coaching Style** (1-10): Question-first approach, avoiding premature advice

## Files Modified
- `/src/agents/prompts/coach_system_prompt.md`: Removed duplicated content, focused on core identity
- `/src/agents/coach_agent.py`: Enhanced with evening protocol, cleaned morning protocol

## Current State
- ✅ Prompt separation complete with clear responsibilities
- ✅ Evening protocol implemented alongside morning
- ✅ New evaluation framework documented
- ⏳ Evaluation integration planned for session 6.5

## Next Steps
- Update status.md with session 6 progress
- Implement new evaluation framework in session 6.5
- Test time-based prompt selection in prototype
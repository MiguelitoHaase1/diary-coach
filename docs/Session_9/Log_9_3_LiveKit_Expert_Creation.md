# Session 9.3: LiveKit Expert Sub-agent Creation

**Date**: 2025-07-28
**Duration**: ~45 minutes
**Focus**: Building a specialized sub-agent with LiveKit expertise

## Summary

This increment created a comprehensive LiveKit expert sub-agent framework, including the expert prompt template, knowledge organization tools, and testing documentation.

## Actions Taken

### 1. Created LiveKit Expert Prompt Template

**File**: `docs/agents/livekit_expert_prompt.md`
- Comprehensive LiveKit knowledge structure
- Common error patterns and solutions
- Implementation patterns with code examples
- Performance optimization techniques
- Production best practices
- Debugging strategies

**Key Sections**:
1. Core Expertise Areas (architecture, SDKs, patterns)
2. Common Issues and Solutions
3. Performance Optimization
4. Debugging Techniques
5. Production Best Practices
6. Integration Patterns
7. Error Pattern Library
8. Quick Troubleshooting Checklist

### 2. Built Knowledge Organization Tool

**File**: `scripts/organize_livekit_knowledge.py`
- Parses LiveKit error logs automatically
- Extracts code patterns from implementations
- Processes configuration files
- Generates formatted knowledge updates
- Groups similar patterns together

**Key Features**:
- Error log parsing with context extraction
- Code pattern recognition (connections, events, tracks)
- Configuration example collection
- Automated markdown generation
- Timestamp extraction from logs

### 3. Created Testing Documentation

**File**: `docs/agents/test_livekit_expert.md`
- Example queries for common LiveKit issues
- Sub-agent invocation patterns
- Knowledge enhancement workflow
- Integration guidance for diary coach
- Quick test examples

**Usage Examples**:
- Connection debugging
- Audio quality troubleshooting
- Implementation patterns
- Error resolution
- Performance optimization

## Technical Details

### Expert Prompt Structure

1. **Identity**: Specialized LiveKit expert with WebRTC knowledge
2. **Expertise Areas**: 
   - Architecture (rooms, tracks, data channels)
   - Client SDKs (JS/TS, React, Python)
   - Common patterns (connection, publishing, events)
   - Issue resolution (connection, quality, permissions)
   - Performance optimization
   - Production deployment

3. **Knowledge Format**:
   ```markdown
   ### Issue: [Problem Description]
   **Symptoms**: 
   - Specific error messages
   - Observable behavior
   
   **Solutions**:
   1. Step-by-step fixes
   2. Code examples
   3. Configuration changes
   ```

### Knowledge Organization Process

1. **Input Sources**:
   - Error logs (--logs)
   - Implementation code (--code)
   - Configuration files (--config)

2. **Processing**:
   - Pattern matching for errors
   - Function context extraction
   - Timestamp identification
   - Code pattern grouping

3. **Output**:
   - Structured markdown update
   - Grouped by pattern type
   - Limited examples per category
   - Ready to append to expert prompt

### Integration Points

1. **With Claude Code**:
   - Use Task tool with general-purpose agent
   - Expert prompt loaded as context
   - Provides specialized LiveKit assistance

2. **With Diary Coach**:
   - Voice pipeline architecture
   - Real-time coaching patterns
   - Data channel integration
   - Error recovery strategies

## Deliverables

1. ✅ **Expert Prompt**: `docs/agents/livekit_expert_prompt.md`
   - 300+ lines of LiveKit expertise
   - Structured knowledge sections
   - Code examples and patterns
   - Troubleshooting checklist

2. ✅ **Knowledge Organizer**: `scripts/organize_livekit_knowledge.py`
   - Automated log parsing
   - Pattern extraction
   - Configuration processing
   - Markdown generation

3. ✅ **Test Documentation**: `docs/agents/test_livekit_expert.md`
   - 5 example queries
   - Usage instructions
   - Knowledge enhancement guide
   - Integration patterns

4. ✅ **Directory Structure**: `docs/agents/`
   - Organized location for sub-agent prompts
   - Scalable for future agents
   - Easy to discover and maintain

## Human Input Required

To complete the LiveKit expert knowledge base:

1. **Provide Error Logs**:
   ```bash
   # From your LiveKit projects
   grep -i "error\|fail" app.log > livekit-errors.log
   python scripts/organize_livekit_knowledge.py --logs livekit-errors.log
   ```

2. **Share Implementation Code**:
   ```bash
   # Your working LiveKit code
   python scripts/organize_livekit_knowledge.py --code src/voice/
   ```

3. **Add Configurations**:
   ```bash
   # LiveKit server/client configs
   python scripts/organize_livekit_knowledge.py --config livekit.config.json
   ```

4. **Document Solutions**:
   - For each error pattern found
   - Add the solution that worked
   - Include any workarounds discovered

## Next Steps

1. **Populate with Real Data**:
   - [ ] Add actual error logs from LiveKit projects
   - [ ] Include working code implementations
   - [ ] Document specific solutions discovered

2. **Test the Expert**:
   - [ ] Run test queries through Task tool
   - [ ] Verify expert provides accurate solutions
   - [ ] Refine based on results

3. **Extend for Voice Integration**:
   - [ ] Add voice-specific patterns
   - [ ] Include VAD integration examples
   - [ ] Document audio pipeline setup

## Learning Opportunities

1. **Sub-agent Architecture**:
   - Specialized agents provide focused expertise
   - Structured prompts enable consistent responses
   - Knowledge organization improves over time

2. **Pattern Recognition**:
   - Error patterns are often repetitive
   - Code patterns reveal best practices
   - Configuration examples prevent mistakes

3. **Knowledge Management**:
   - Automated parsing saves manual effort
   - Structured format aids retrieval
   - Incremental updates build expertise

## Common Pitfalls Addressed

1. ✅ Created template structure before requiring logs
2. ✅ Built automation tools for knowledge extraction
3. ✅ Provided clear examples for usage
4. ✅ Included placeholder sections for human input

## Status

✅ LiveKit expert prompt template created
✅ Knowledge organization tool implemented
✅ Testing documentation provided
✅ Ready for human input to complete knowledge base
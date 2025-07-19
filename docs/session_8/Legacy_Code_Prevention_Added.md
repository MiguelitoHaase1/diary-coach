# Legacy Code Prevention Guidelines Added to CLAUDE.md

## Summary
Added comprehensive guidelines to CLAUDE.md to ensure Claude Code doesn't leave legacy code behind during architecture changes or refactoring.

## What Was Added

### 1. New Increment Discipline Rule
- Added "No legacy code left behind" to the core discipline principles
- References the new Legacy Code Prevention section

### 2. Legacy Code Prevention Section
Created "The Fourth Law: Clean Architecture Transitions" with:

**What to Clean Up:**
- Tests for deleted/changed functionality
- Database schemas (unused tables, columns, migrations)
- Config files with obsolete entries
- Documentation for changed features
- Dead imports and dependencies
- Old implementations (classes, functions, modules)
- Mock data and test fixtures

**Clean Transition Checklist:**
- Grep for all references to removed components
- Update or delete related tests
- Remove database artifacts
- Clean up configuration files
- Update documentation
- Run full test suite to catch stragglers
- Check for orphaned files in directory structure

**Proactive Cleanup Process:**
1. Ask: "What did I replace or remove?"
2. Search: Find all references to those items
3. Clean: Update or delete each reference
4. Test: Ensure nothing broke
5. Document: Note major deletions in commit message

### 3. Updated Remember Section
- Added "Clean transitions = no orphaned code" to core principles

## Why This Matters
During Session 7.3 refactoring, we saw the importance of cleaning up old code:
- Removed old analyzer modules
- Deleted obsolete tests
- Cleaned up evaluation system artifacts

This guideline ensures future refactoring maintains the same discipline, preventing:
- Confusion from orphaned code
- Test failures from missing dependencies
- Maintenance burden from dead code
- Documentation drift from outdated references

## Impact on Session 8
This is particularly relevant for Session 8's multi-agent transformation, where we'll be:
- Replacing single-agent patterns with multi-agent architecture
- Updating many integration tests
- Removing old orchestration code
- Cleaning up legacy node implementations

The new guidelines ensure each increment leaves the codebase cleaner than it found it.
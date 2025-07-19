# Claude Code: System Guide

## The Three Laws

### 1. Working Software Only
Every session produces software and tests that run in realistic settings. No mocks, mock-runs, no scaffolding without a sandbox test of functionality.

### 2. Tests Define Success  
Write tests first. Implementation follows. Red tests block progress.

### 3. Documentation Is Code
Stale docs = broken build. Update docs with every increment or session fails.

---

## Increment Discipline
- **Change only what the test requires** - resist the urge to refactor, unless I explicitly ask you to --- but feel free to ask me explicitly to refactor a part if you find it useful
- **Functions do one thing** - if you need "and" to describe it, split it
- **88 character line limit** - readability over cleverness
- **Lint continuously** - run `python -m flake8` after EVERY file creation/edit
- **No legacy code left behind** - see Legacy Code Prevention section below

### Linting Workflow
1. **After creating new file**: Immediately run `python -m flake8 <filename>`
2. **After editing file**: Run linter before any tests
3. **Fix all issues**: Don't proceed until lint passes
4. **Common fixes**:
   - Line too long: Split at logical points, use parentheses for continuation
   - Trailing whitespace: Remove with `sed -i '' 's/[[:space:]]*$//' <file>`
   - Missing newline: Add with `echo "" >> <file>`
   - Unused imports: Remove immediately

---

## Session Workflow

### Start Session
1. Read `docs/session_x/Session_x.md` 
2. Check `docs/status.md` for current state (potentially also check log markdowns under 'docs/session_x/...')
3. List human setup tasks upfront:
   ```
   🔴 HUMAN SETUP REQUIRED:
   - [ ] Create .env with: [keys]
   - [ ] Install: [dependencies]
   - [ ] Configure: [services]
   ```

### Execute Increments
For each ~10 line increment:
1. **Test First**: Write failing test
2. **Code Minimal**: Just enough to pass
3. **Lint Immediately**: Run `python -m flake8` on new/modified files
4. **Run Suite**: All tests must pass
5. **Log Actions**: Update `Log_x_y.md` only after lint + tests pass

### End Session
1. Update `docs/status.md` 
2. Commit with format: `feat(session-x): implement increment y`
3. Push to GitHub
4. List human improvement tasks thereafter:
   ```
   🔴 HUMAN SETUP REQUIRED:
   - [ ] Particular prompts to iterate on and improve: [link]
   - [ ] Particular classes to iterate on and improve: [link]
   - [ ] Other configurations to still adapt and improve: [xyz]
   ```


---

## Documentation Structure

```
project/
├── README.md              # User-facing: what & why
├── roadmap.md            # AI-facing: sessions & architecture  
├── docs/
│   ├── status.md         # Current state across all sessions
│   ├── learning_ledger.md # Your knowledge gaps/strengths
│   └── session_x/
│       ├── Session_x.md  # Session spec & approach
│       ├── Log_x_y.md    # Action-by-action record, including learning opportunities for me
```

### Update Rules
- **After EVERY increment**: Update status.md
- **When approach changes**: Update Session_x.md and roadmap.md  
- **When you struggle**: Note in learning_ledger.md


---

## Quick Reference

### Testing
```bash
# JavaScript
npm test -- --watch
npm run test:unit

# Python  
pytest tests/session_x/
pytest -k test_increment_y
```

### Git Commits
```bash
git commit -m "feat(session-x): implement increment y"
git commit -m "test(session-x): add tests for increment y"
git commit -m "docs(session-x): update status and logbook"
```

### Model Selection
```bash
claude --model opus      # Complex reasoning
claude --model sonnet    # Default
/model opus             # Switch mid-session
```

---

## Legacy Code Prevention

### The Fourth Law: Clean Architecture Transitions
When changing architecture or refactoring major components, **never leave orphaned code behind**.

### What to Clean Up
When you modify or replace code:
1. **Tests**: Update or remove tests for deleted/changed functionality
2. **Database schemas**: Remove unused tables, columns, or migrations
3. **Config files**: Delete obsolete configuration entries
4. **Documentation**: Update or remove docs for changed features
5. **Dead imports**: Remove unused imports and dependencies
6. **Old implementations**: Delete replaced classes, functions, modules
7. **Mock data**: Remove test fixtures for deleted features

### Clean Transition Checklist
For every major change:
- [ ] Grep for all references to removed components
- [ ] Update or delete related tests
- [ ] Remove database artifacts
- [ ] Clean up configuration files
- [ ] Update documentation
- [ ] Run full test suite to catch stragglers
- [ ] Check for orphaned files in directory structure

### Examples
```python
# ❌ WRONG: Leaving old code commented out
# class OldAnalyzer:  # Replaced by new system
#     def analyze(self):
#         pass

# ✅ RIGHT: Delete it completely
# If needed later, it's in git history

# ❌ WRONG: Keeping tests for deleted features
def test_old_analyzer():  # But OldAnalyzer is gone!
    pass

# ✅ RIGHT: Delete the test or rewrite for new system
```

### Proactive Cleanup
Before completing any increment:
1. Ask: "What did I replace or remove?"
2. Search: Find all references to those items
3. Clean: Update or delete each reference
4. Test: Ensure nothing broke
5. Document: Note major deletions in commit message

---

## MCP (Model Context Protocol) Integration
A more detailed description of MCP integration approaches is given in @docs/MCP_howto.md

### MCP Rules

1. **Use Real MCP Servers**: Never mock. Find established servers on GitHub first.
2. **Test in Isolation**: Create `mcp_sandbox.py` to verify connection before integration.
3. **Read Server Docs**: Tool names use hyphens (`get-tasks`), responses are TextContent objects.
4. **Ensure Injection**: Data must reach the LLM prompt, not just be fetched:
   ```python
   # ❌ WRONG
   todos = await mcp.get_todos()
   return llm.generate(prompt)  # Todos never used!
   
   # ✅ RIGHT  
   todos = await mcp.get_todos()
   enhanced_prompt = inject_context(prompt, todos)
   return llm.generate(enhanced_prompt)
   ```
5. **Build Debug Tools**: Add connection status logging and prompt injection verification.
6. **Fail Loudly**: No silent fallbacks to mock data.

### MCP Workflow
```bash
# 1. Clone and build server
# 2. Test with mcp_sandbox.py
# 3. Verify data reaches LLM
# 4. Add observability
```

---

## Evaluation System Principles

### Core Rules
1. **Never Mock External Services**: Always use real LangSmith/evaluation infrastructure
2. **Parse LLM Output Robustly**: Handle markdown, JSON blocks, and control characters
3. **Evaluate Full Conversations**: Never evaluate single messages in isolation
4. **Use Appropriate Model Tiers**: STANDARD tier (Sonnet) for evaluations, not CHEAP
5. **Keep Criteria Focused**: 5 clear criteria > 7 complex analyzers

### Implementation Pattern
```python
# ✅ RIGHT: Proper LangSmith integration
results = await aevaluate(
    target_function,
    data=dataset_name,
    evaluators=langsmith_evaluators,
    experiment_prefix="coaching_eval"
)

# ❌ WRONG: Mock Run objects or hardcoded scores
mock_run = Run(id=str(uuid.uuid4()), ...)  # Never do this
behavioral_scores = [("Specificity", 0.6, "Mock")]  # Never hardcode
```

### JSON Parsing Pattern
```python
# Always handle LLM formatting quirks
if "```json" in result:
    json_str = result.split("```json")[1].split("```")[0]
# Include regex fallback for embedded JSON
```

---

## Remember

- **No session ends without runnable software**
- **Documentation drift = technical debt**
- **Small increments compound into big features**
- **Your learning matters as much as the code**
- **Real services over mocks, always**
- **Clean transitions = no orphaned code**
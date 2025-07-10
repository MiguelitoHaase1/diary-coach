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

---

## Session Workflow

### Start Session
1. Read `docs/session_x/Session_x.md` 
2. Check `docs/status.md` for current state
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
3. **Log Actions**: Update `Log_x_y.md` 
4. **Run Suite**: All tests must pass

### End Session
1. Update `docs/status.md` 
2. Create `Dojo_x_y.md` for learning opportunities
3. Commit with format: `feat(session-x): implement increment y`
4. Push to GitHub
5. List human improvement tasks thereafter:
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
│       ├── Log_x_y.md    # Action-by-action record
│       └── Dojo_x_y.md   # Learning opportunity
```

### Update Rules
- **After EVERY increment**: Update status.md
- **When approach changes**: Update Session_x.md and roadmap.md  
- **When you struggle**: Note in learning_ledger.md

---

## Dojo Format

```markdown
# Dojo Session X.Y

**Context**: [What we built and what went wrong]
**Concept**: [The principle that would have helped]
**Value**: [Why this matters beyond this project]
**Also Consider**: [2-3 other topics from this increment]
```

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

## Remember

- **No session ends without runnable software**
- **Documentation drift = technical debt**
- **Small increments compound into big features**
- **Your learning matters as much as the code**
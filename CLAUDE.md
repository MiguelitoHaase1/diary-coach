# Claude Code: System Guide

## The Three Laws

### 1. Working Software Only
Every session produces software that runs. No mocks, no scaffolding, no "TODO: implement later".

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

## Remember

- **No session ends without runnable software**
- **Documentation drift = technical debt**
- **Small increments compound into big features**
- **Your learning matters as much as the code**
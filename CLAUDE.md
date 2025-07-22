# Claude Code: System Guide

## I. Core Philosophy

### The Four Laws

#### 1. Working Software Only

Every session produces software and tests that run in realistic settings. No mocks, mock-runs, no scaffolding without a sandbox test of functionality.

#### 2. Tests Define Success

Write tests first. Implementation follows. Red tests block progress.

#### 3. Documentation Is Code

Stale docs = broken build. Update docs with every increment or session fails.

#### 4. Clean Architecture Transitions

When changing architecture or refactoring major components, never leave orphaned code behind. Meanwhile, make sure to keep the most endearing aspects of the left-behind product - e.g., as defined in a product vision markdown in the repo!

---

## II. Operating Procedures

### A. Session Workflow

#### Starting a Session

1. **ALWAYS CHECK FOR VIRTUAL ENVIRONMENT FIRST**:
   ```bash
   # Check if venv exists
   ls -la | grep venv
   # If it exists, activate it:
   source venv/bin/activate
   # If not, create one:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Read `docs/session_x/Session_x.md`
3. Check `docs/status.md` for current state (potentially also check log markdowns under 'docs/session_x/...')
4. List human setup tasks upfront:
    
    ```
    🔴 HUMAN SETUP REQUIRED:
    - [ ] Create .env with: [keys]
    - [ ] Install: [dependencies]
    - [ ] Configure: [services]
    ```
    

#### Executing Increments

For each increment within a session:

1. **Test First**: Write failing test
2. **Code Minimal**: Just enough to pass
3. **Lint Immediately**: Run `python -m flake8` on new/modified files
4. **Run Suite**: All tests must pass
5. **Log Actions**: Update `Log_x_y.md` only after lint + tests pass
6. **Turn over the microphone**: Always, engage the user after each increment, before moving on to the next one

Also, at any point in an increment, turn over the microphone before making any major decisions, or if you are stuck on something for too many tries, e.g., API errors or similar difficulties that reoccur.

#### When Things Fail
1. **Fail Fast**: Broken increment = immediate stop
2. **Document Failure**: Log what broke and why
3. **Clean Rollback**: Never leave partial implementations

#### Ending a Session

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
    

#### Documentation Structure

```
project/
├── README.md              # User-facing: what & why
├── roadmap.md            # AI-facing: sessions & architecture  
├── docs/
│   ├── status.md         # Current state across all sessions
│   ├── learning_ledger.md # Your knowledge gaps/strengths
│   └── session_x/
│       ├── Session_x.md  # Session spec & approach
│       ├── Log_x_y.md    # Action-by-action record, including learning opportunities
```

**Update Rules:**

- After EVERY increment: Update status.md and write the log file (log_x_y.md)
- When approach changes: Update Session_x.md and roadmap.md

### B. Increment Discipline

#### Python Execution Protocol

**CRITICAL**: Before running ANY Python command:
1. **Check for venv**: `ls -la | grep venv`
2. **Activate it**: `source venv/bin/activate`
3. **Verify activation**: The prompt should show `(venv)` prefix
4. **Only then run Python commands**

Common commands after activation:
- `python run_multi_agent.py` - Run the multi-agent coaching system
- `python -m pytest` - Run tests
- `python -m flake8 <file>` - Lint a file
- `python scripts/run_automated_eval_experiment.py` - Run evaluations

#### Code Standards

- **Change only what the test requires** - resist the urge to refactor, unless explicitly asked
- **Functions do one thing** - if you need "and" to describe it, split it
- **88 character line limit** - readability over cleverness
- **No legacy code left behind** - see Clean Transitions below

#### Linting Protocol

1. **After creating new file**: Immediately run `python -m flake8 <filename>`
2. **After editing file**: Run linter before any tests
3. **Fix all issues**: Don't proceed until lint passes
4. **Common fixes**:
    - Line too long: Split at logical points, use parentheses for continuation
    - Trailing whitespace: Remove with `sed -i '' 's/[[:space:]]*$//' <file>`
    - Missing newline: Add with `echo "" >> <file>`
    - Unused imports: Remove immediately

#### Clean Transitions

When modifying or replacing code:

1. **Grep for all references** to removed components
2. **Update or delete** related tests
3. **Remove database artifacts** (unused tables, columns, migrations)
4. **Clean up configuration files** for obsolete entries
5. **Update documentation** for changed features
6. **Delete dead imports** and dependencies
7. **Remove old implementations** completely
8. **Write-up changes in the log file**, so one can know which aspects of the old code was dropped/de-prioritized

**Example:**

```python
# ❌ WRONG: Leaving old code commented out
# class OldAnalyzer:  # Replaced by new system
#     def analyze(self):
#         pass

# ✅ RIGHT: Delete it completely
# If needed later, it's in git history
```

#### Git Commit Standards

```bash
git commit -m "feat(session-x): implement increment y"
git commit -m "test(session-x): add tests for increment y"
git commit -m "docs(session-x): update status and logbook"
```

---

## III. Domain-Specific Guidance

### A. MCP (Model Context Protocol) Integration

#### The Seven MCP Laws

1. **Real Servers Only**: Never mock MCP data or bypass with direct API calls. Always use an actual MCP server.
    
2. **Research First**: Search for reputable MCP servers before building. Check GitHub stars, recent commits, and community adoption.
    
3. **Read, Then Code**: Study the MCP server's README thoroughly. Note:
    
    - Exact tool names (often use hyphens: `get-tasks` not `get_tasks`)
    - Response formats (TextContent objects vs direct JSON)
    - Environment variable names (API_KEY vs API_TOKEN)
4. **E2E Test Setup**: Start with a test that validates the complete flow - not just fetching, but ensuring data reaches the LLM.
    
5. **Sandbox Before Integration**: Create `mcp_sandbox.py` to verify connection, auth, and data retrieval BEFORE touching main codebase.
    
6. **Architecture First**: Map the data flow completely:
    
    ```
    MCP Server → Client → Agent → System Prompt → LLM
                                     ↑
                               INJECTION POINT
    ```
    
7. **Observability Required**: Build debug tools immediately - connection status, raw response logging, injection verification.
    
_Note: For detailed MCP integration approaches, see @docs/MCP_howto.md_

### B. Evaluation System Integration

#### Core Principles

1. **Never Mock External Services**: Always use real LangSmith/evaluation infrastructure
2. **Stay in the driver seat:** Generally, make our own evals via our own LLMs as judges, rather than delegating core logic to a service (e.g., LangSmith). Use the external services for monitoring and dashboarding, not the core logic of evals.
3. **Parse LLM Output Robustly**: Handle markdown, JSON blocks, and control characters
4. **Evaluate Full Product experiences**: Try to evaluate the totality - e.g., full conversation, not single messages in isolation
5. **Keep Criteria Focused**: 5 clear criteria maximum, ideally need to be clear if they fail or succeed
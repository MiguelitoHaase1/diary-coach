# Claude Code Assistant: System Guide

---

## Common Commands

### Testing Commands
```bash
# Run tests for current increment
npm test -- --watch

# Run specific test suites
npm run test:unit              # Unit tests only
npm run test:integration       # Integration tests only
npm run test:e2e              # End-to-end tests

# Python projects
pytest tests/session_x/        # Run tests for specific session
pytest -k test_increment_y     # Run specific increment tests
pytest --cov=src              # Run with coverage report

# Test debugging
npm test -- --verbose         # Detailed test output
pytest -vv                    # Very verbose output
```

### Git Commands
```bash
# Commit format for increments
git commit -m "feat(session-x): implement increment y"
git commit -m "test(session-x): add tests for increment y"
git commit -m "docs(session-x): update status and logbook"

# Branch management
git checkout -b feature/session-x-increment-y
git rebase develop            # Before PR
```

### Documentation Commands
```bash
# Generate documentation templates
touch docs/session_x/Log_x_y.md
touch docs/session_x/Dojo_x_y.md

# Check documentation status
ls docs/session_*/           # List all session folders
grep -n "TODO" docs/**/*.md  # Find pending updates across sessions
ls docs/session_x/*.md       # List files for specific session
```

### Development Commands
```bash
# Environment setup
cp .env.example .env         # Create local environment
source venv/bin/activate     # Python virtual environment
nvm use                      # Node version management

# Build and run
npm run build               # Build project
npm run dev                 # Development server
docker-compose up           # Full stack with Docker
```

### Claude Code Model Selection
```bash
# Start session with specific model
claude --model sonnet        # Use Sonnet (default)
claude --model opus          # Use Opus for complex reasoning
claude --model haiku         # Use Haiku for simple tasks

# Specific model versions
claude --model claude-3-opus-20240229
claude --model claude-3-5-sonnet-20241022

# Within a session - switch models
/model opus                  # Switch to Opus mid-session
/model sonnet               # Switch back to Sonnet
/model haiku                # Switch to Haiku

# Default model set in ~/.config/claude/settings.json
# API key configured for usage billing instead of Pro subscription
```

---

## Documentation Architecture

### Project Vision & Planning
- **README.md** - Product vision document
  - *Target:* End users and stakeholders
  - *Purpose:* Describes what we're building and why it matters
  
- **roadmap.md** - Development journey blueprint
  - *Target:* AI agents (Claude Code, Cursor, etc.)
  - *Purpose:* Breaks vision into testable sessions, proposes architecture, defines tech stack hypothesis

### Session Management
- **docs/session_x/Session_x.md** - Detailed session specification
  - *Target:* AI agents
  - *Purpose:* Deep dive into session x with TDD setup, refined tech stack considerations, and implementation approach
  
- **docs/status.md** - Project-wide status document
  - *Target:* AI agents and developers
  - *Purpose:* Documents overall project state, what's working, what failed, and current progress across all sessions

### Incremental Progress Tracking
- **docs/session_x/Log_x_y.md** - Granular action log
  - *Target:* AI agents
  - *Purpose:* Records specific actions in increment y of session x to prevent repeating mistakes
  - *Format:* Action-by-action breakdown with outcomes and learnings

### Learning & Development
- **docs/session_x/Dojo_x_y.md** - Session-specific learning recommendations
  - *Target:* Me, who will use it in an LLM conversation in claude.ai
  - *Purpose:* Propose one key topic for me to go learn about based docs/session_x/Log_x_y.md - and my knowledge as given in docs/learning_ledger.md. Pick a topic that is deep and valuable for me to learn as a product manager who can code. Also mention 2-3 other topics cursorily that could be covererd if I want.. but lesser priority.
  - *Format:* Just write the context and topic - I'll use Claude.ai myself to make it a learning session.
  
- **learning_ledger.md** - Knowledge inventory
  - *Target:* AI agents
  - *Purpose:* Tracks your software development knowledge gaps and strengths to inform Dojo creation

---

## Documentation Maintenance Principle

**IMPORTANT: You MUST keep docs/ current throughout development** - stale documentation creates more confusion than no documentation. 

**MANDATORY documentation updates:**
- **You MUST update docs/status.md after EVERY increment** before moving to the next task
- **You MUST keep docs/session_x/Session_x.md aligned with actual implementation** - no divergence allowed
- **You MUST refresh docs/roadmap.md** whenever scope or approach changes
- **You MUST maintain docs/learning_ledger.md** as knowledge gaps are discovered

This ensures documentation remains a reliable source of truth rather than a historical artifact.

---

## Persona and Core Directives

You are **Claude Code**, an expert-level AI coding assistant operating under the three core principles above. Your primary function is to provide simple, testable, incrementally-improvable code while capturing learning opportunities for a product manager who codes.

---

## Implementation Guidelines

### 1. Test-Driven Development (TDD) is MANDATORY
**ALWAYS write tests BEFORE implementation code**. This is non-negotiable. Tests define success and prevent scope creep.

### 2. Minimal Incremental Sessions
- **You MUST break features into 10-line sandbox exercises** with unit tests
- **NEVER proceed without passing tests** - red tests block progress
- Keep discomfort bite-sized and reward quick wins

### 3. Systematic Logging is REQUIRED
**At session end, you MUST generate:**
- **logbook_x_y.md**: Complete record of what we tried and learned
- **dojo_x_y.md**: Learning opportunities from this increment

---

## Session Workflow

1. **Start**: Review docs/session_x/Session_x.md and current docs/status.md
2. **Plan**: Break session into testable increments
3. **Execute**: For each increment:
   - Write tests first
   - Implement minimal code to pass
   - Log actions in docs/session_x/Log_x_y.md
4. **Test**: Run full test suite to ensure nothing breaks
   - Unit tests for the increment
   - Integration tests for affected components
   - Regression tests for existing functionality
5. **Reflect**: Update docs/status.md with progress
6. **Learn**: Generate docs/session_x/Dojo_x_y.md for learning opportunities
7. **Commit**: Push to version control. 

---

## Testing Strategy

- **Unit Tests**: 80%+ coverage for individual functions
- **Integration Tests**: Component interactions with minimal mocking
- **E2E Tests**: Critical user journey validation

---

## Project Structure

```
project_name/
├── docs/
│   ├── README.md              # Product vision
│   ├── roadmap.md            # Development blueprint
│   ├── status.md             # Project-wide status
│   ├── learning_ledger.md    # Knowledge inventory
│   ├── session_1/            # Session 1 complete artifacts
│   │   ├── Session_1.md      # Session 1 specification
│   │   ├── Log_1_[1-7].md    # Increment logbooks
│   │   └── Dojo_1_[1-7].md   # Learning exercises
│   ├── session_2/            # Session 2 artifacts (future)
│   │   ├── Session_2.md      # Session 2 specification
│   │   ├── Log_2_[1-N].md    # Increment logbooks
│   │   └── Dojo_2_[1-N].md   # Learning exercises
│   └── session_N/            # Future sessions follow same pattern
├── src/
├── tests/
├── pyproject.toml
├── docker-compose.yml
└── .env.example
```

---

## Development Best Practices

###Code Quality
- Keep changes minimal
- Type hints required for all code
- Public APIs must have docstrings
- Functions must be focused and small
- Follow existing patterns exactly
- Line length: 88 chars maximum


### Git Workflow
- Check git status before commits
- Feature branches: `feature/session-x-increment-y`
- Atomic commits with descriptive messages
- Update status_x.md before PRs
- For pull requests, create a detailed message of what changed. Focus on the high level description of the problem it tries to solve, and how it is solved. Don't go into the specifics of the code unless it adds clarity.

### Security
- Environment variables for all secrets
- Input validation and sanitization
- Parameterized database queries

### Debugging Approach
1. Read full error messages and stack traces
2. Use language-appropriate debugging tools
3. Verify assumptions with logging
4. Isolate problems through systematic elimination

---

## Learning Integration

### Dojo Document Format
Each dojo_x_y.md follows this template:

```markdown
# Dojo Session X.Y

**Purpose**: Enable me to copy a learning theme into Claude.ai, so I can personally prompt it further to teach me more about it.
**Context**: [What we were building and what we stumbled into]
**Challenge**: [The problem we solved]
**Concept**: [The underlying principle, and why it matters to me, even beyond this specific use case]
**Other areas one could explore**: Mention 2-3 other topics from the increment, I could also consider exploring if I have time and interest.

```

This structure ensures every coding session becomes a learning opportunity, transforming routine development into continuous education.

---

## Environment Variables

Always use .env files for secrets and keys. Never commit them to version control. Use .env.example as a template.

---



---

## Special Action

### Push Changes Action

When the user asks to "push changes" or complete a session, perform these steps in order:

1. **Create Session Documentation**:
   ```bash
   # Create/update session log
   touch docs/session_x/Log_x_y.md
   
   # Create/update session dojo
   touch docs/session_x/Dojo_x_y.md
   ```

2. **Update Project Status**:
   - Update `docs/status.md` with current project state
   - Update `README.md` with latest features and instructions
   - Update `docs/roadmap.md` if scope or direction changed

3. **Commit and Push**:
   ```bash
   # Check current state
   git status
   git diff
   
   # Add all changes
   git add .
   
   # Create descriptive commit message
   git commit -m "feat(session-x): Complete [session description]
   
   - Added [key feature 1]
   - Implemented [key feature 2]  
   - Fixed [important bug]
   - Updated documentation and status
   
   # Push to GitHub
   git push origin main
   ```

4. **Verify Completion**:
   ```bash
   # Confirm push succeeded
   git status
   git log --oneline -3
   ```

**Use this action** when:
- User requests to "push changes", "commit and push", or "complete session"
- Major session milestone is reached
- Documentation needs to be synchronized with code changes
- Ready to share progress with collaborators
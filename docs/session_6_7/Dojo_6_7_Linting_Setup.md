# Dojo Session 6.7: The Discovered Infrastructure

**Context**: Asked about linting, discovered black and flake8 were installed but no configuration existed. The 88-character limit in CLAUDE.md wasn't being enforced by tooling.

**Concept**: Documentation without automation is aspiration, not reality. A coding standard only exists if it's automatically checked. The gap between "what we say" and "what we enforce" breeds inconsistency.

**Value**: This pattern reveals organizational maturity - are standards documented, configured, automated, and enforced? Each level requires more discipline but yields more consistency. Finding half-implemented infrastructure is an opportunity.

**Also Consider**:
- The importance of .gitignore-style config files for tool consistency
- How Black and flake8 can conflict without proper configuration  
- Why character limits matter for code readability in team settings
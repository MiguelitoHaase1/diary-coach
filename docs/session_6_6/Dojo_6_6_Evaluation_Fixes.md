# Dojo Session 6.6: The Hidden Mock Pattern

**Context**: The manual evaluation system was showing 6/10 for every behavioral metric. Investigation revealed hardcoded scores masquerading as real analysis in the "light report" generation.

**Concept**: Mock data in production code creates false confidence. What appears to work perfectly may be completely fake. Always trace data flow from source to output.

**Value**: This pattern appears everywhere - placeholder implementations that become permanent, demo data that reaches production, and "temporary" workarounds that last forever. Finding these requires skepticism about suspiciously consistent results.

**Also Consider**:
- Test naming clarity (light vs deep reports had different behaviors)
- The cost of running real analysis vs the deception of fake data
- How incremental development can leave scaffolding in place
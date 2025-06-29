# Dojo Session 3.2: Advanced CLI Design Patterns and Error-Driven Development

**Purpose**: Enable me to copy a learning theme into Claude.ai, so I can personally prompt it further to teach me more about it.

**Context**: We just completed a major debugging and enhancement session for the evaluation system. What started as simple bug fixes revealed deeper patterns about CLI design, error-driven development, and user experience psychology that are valuable for any product manager building developer tools or user-facing software.

**Challenge**: We discovered that our evaluation system had multiple critical gaps: users couldn't remember commands, reports weren't actually being generated (silent failures), and the CLI forced a linear flow that didn't match user mental models. Fixing these issues required understanding both technical implementation details and user experience psychology.

**Concept**: **Error-Driven Development as a Product Management Philosophy**

This session demonstrated a powerful approach to product development that goes beyond traditional "feature-driven" development. Instead of just adding new capabilities, we used actual user errors and confusion as a guide to identify both technical debt and user experience gaps simultaneously.

The core insight: **Real user struggles reveal system design flaws that technical testing alone cannot uncover.** When users say "I can't remember the command" or "the report didn't generate," they're providing invaluable feedback about both interface design and implementation reliability.

Here's why this matters for product managers who code:

1. **Silent Failures Are Product Killers**: Our evaluation system claimed to generate reports but didn't actually create files. Users trusted the system was working, making the failure even more damaging. This teaches us that success messages must be tied to actual outcomes, not just code execution.

2. **Cognitive Load in Interface Design**: Users struggling to remember "stop" taught us that command-line interfaces need the same UX consideration as graphical interfaces. Natural language variations ("wrap up", "end conversation") dramatically reduce cognitive load without adding technical complexity.

3. **Progressive Enhancement vs. Forced Paths**: Our original design forced users down a linear path (chat → stop → exit). Users actually wanted flexibility (chat → stop → potentially enhance → exit when ready). This pattern applies to any software where users need control over their journey.

4. **Error-Driven Prioritization**: Rather than building new features, we focused on fixing what users actually struggled with. This resulted in higher user satisfaction than adding more capabilities would have.

5. **Testing What Actually Breaks**: Our comprehensive test suite emerged from real user pain points, not from theoretical edge cases. This makes tests more valuable because they prevent real-world problems.

**Learning Prompts for Claude.ai**:

*"I want to understand error-driven development as a product management methodology. Specifically, how do I use actual user errors and confusion to guide both technical architecture decisions and user experience improvements? Help me understand how to identify silent failures in software systems, design interfaces that reduce cognitive load, and create development processes that prioritize fixing user pain points over adding features. I'm particularly interested in patterns that apply across different types of software products, not just CLI tools."*

**Other areas one could explore** if you have time and interest:

- **CLI Design Psychology**: How command-line interfaces can learn from GUI usability principles while maintaining their power and efficiency advantages.

- **Progressive Enhancement in Software Architecture**: Design patterns that allow users to start with simple functionality and optionally access more advanced features without forcing upfront complexity decisions.

- **Silent Failure Detection**: Technical strategies for ensuring that user-facing success messages correspond to actual system success, including monitoring and validation patterns.
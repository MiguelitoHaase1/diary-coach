I'd like to give another try at getting web search agent to work. I suggest we:

1 - use Anthropic's native web search within the web search agent
2 - The existing orchestrator agent we already have should now get an active role in phase 3 to coordinate workflow, error handle, and manage retry logic (Route requests, monitor progress, coordinate agents).... e.g., ensuring that the web search agent gets guidance on what to look for and ensures the information comes back to the deep thoughts agen.
3 - This should offload the cognitive load for the deep thoughts agent ('reporter'), so it simply focuses on narrative structure, synthesis and writing while ensuring coherence --- and only called once for writing report... so the orchestrator can take care of rest.

### Agent Roles and Responsibilities

**Orchestrator Agent (Claude Sonnet)**

- Analyzes user requests and creates research strategies
- Generates specific, contextual search queries for the Web Search agent
- Manages retry logic and error handling (e.g., if critical information is missing: Generate new search queries - If results have errors: Implement retry with modified queries - If information is complete: Proceed to synthesis)
- Prepares structured briefs for the Deep Thoughts agent (e.g., Organized, deduplicated information grouped by theme - Clear context about the original request - Key facts, quotes, and data points - Source citations for credibility)
- Ensures single, focused call to Deep Thoughts agent

**Web Search Agent (Claude with Native Search)**

- Executes searches using Anthropic's native web search functionality
- Validates and quality-checks search results (e.g., if an error occurred in the search process. Analyze the error and determine the best recovery strategy: 1. Rate limit errors: Wait and retry with same query 2. No results found: Reformulate query with synonyms or broader terms 3. Timeout errors: Simplify query or break into smaller searches 4. Invalid query: Restructure following search syntax rules Create a recovery plan that ensures we still gather the needed information.)
- Reports back best results

**Deep Thoughts Agent (Claude Sonnet)**

- Receives pre-processed, validated information from Orchestrator
- Focuses exclusively on narrative structure and synthesis
- Creates coherent, well-structured reports
- Called only once per workflow with complete information

## Key Implementation Principles

1. **Single Responsibility**: Each agent has one clear job
2. **Single Deep Thoughts Call**: Brief must be complete and comprehensive
3. **Error Resilience**: Orchestrator handles most retry logic
4. **Quality Gates**: Orchestrator validates before proceeding
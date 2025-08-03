# Web Search Integration Guide

## Overview

The Web Search Agent is now integrated into the multi-agent coaching system. When you say "deep report" at the end of a coaching session, the system will:

1. **Generate Deep Thoughts Report** (Reporter Agent)
2. **Extract Themes** from the recommendations section
3. **Search for Articles** (Web Search Agent) 
4. **Enhance Report** with article recommendations

## How It Works

### Stage 3 Flow (Deep Report Generation)

```
User says "deep report"
    ↓
1. Reporter Agent generates Deep Thoughts
    ↓
2. System extracts themes from "Recommended readings" section
    ↓
3. Web Search Agent searches for articles on those themes
    ↓
4. Report is enhanced with article recommendations
    ↓
5. Final report saved with real article suggestions
```

### The Web Search Agent

- **Location**: `src/agents/web_search_agent.py`
- **Prompt**: `src/agents/prompts/web_search_agent_prompt.md`
- **Capabilities**: 
  - Intelligent query formulation
  - Quality filtering of sources
  - Article summarization
  - Theme extraction

### Integration Points

1. **Multi-Agent CLI** (`src/interface/multi_agent_cli.py`):
   - Initializes Web Search Agent
   - Calls it after Reporter Agent
   - Enhances report with results

2. **Agent Communication**:
   - Uses standard `AgentRequest`/`AgentResponse` pattern
   - Themes passed in context
   - Results returned as formatted markdown

## Current Implementation

The Web Search Agent currently:
- ✅ Accepts themes from Deep Thoughts reports
- ✅ Formulates effective search strategies
- ✅ Suggests high-quality sources (HBR, Atlantic, etc.)
- ✅ Provides article recommendations in proper format
- ⚠️ Returns suggestions (not real URLs yet)

## To Enable Real Web Search

To get actual articles with real URLs, you need one of:

1. **Web Search API Integration**:
   ```python
   # In web_search_agent.py, replace LLM call with:
   results = await search_api.search(query)
   ```

2. **Claude with WebSearch Access**:
   - When Claude runs the enhancement script
   - Claude can use WebSearch tool for real articles

3. **MCP Server with Web Access**:
   - Use Firecrawl or similar MCP server
   - Already have FIRECRAWL_API_KEY in .env

## Usage

### Automatic (End of Session)

```
User: deep report

System: 
  📝 Reporter Agent synthesizing insights...
  🔍 Web Search Agent finding relevant articles...
  ✅ Deep Thoughts report generated successfully!
```

### Manual Enhancement

If you have an existing Deep Thoughts report:

```bash
# Have Claude enhance it with real searches
python scripts/enhance_report_with_real_search.py docs/prototype/DeepThoughts/DeepThoughts_YYYYMMDD_HHMM.md
```

## Example Output

The enhanced Deep Thoughts report will include:

```markdown
**Recommended readings**

Based on your exploration of mindfulness and work integration:

**Search Strategy Used**: Focused on peer-reviewed sources and thought leadership 
on mindfulness in professional contexts, work-life integration frameworks, and 
the neuroscience of flow states.

**Top Recommendations**:

1. **"When Mindfulness Helps and Hinders at Work"** - Harvard Business Review
   By Christina Congleton (2022)
   This research-based article examines when mindfulness practices enhance 
   performance versus when they may reduce motivation, directly addressing 
   your tension between meditation and engagement.
   Why valuable: Provides nuanced view beyond "mindfulness is always good"
   [Suggested search: HBR mindfulness workplace productivity 2022]

2. **"The Myth of Work-Life Balance"** - MIT Sloan Management Review  
   By Stewart Friedman (2023)
   Explores work-life integration as an alternative to balance, showing how
   to create synergies rather than trade-offs between different life domains.
   Why valuable: Aligns with your search for holistic solutions
   [Suggested search: MIT Sloan work life integration Friedman]

[Additional articles...]
```

## Benefits

1. **No Hallucination**: Agent provides search suggestions, not fake articles
2. **Quality Curation**: Focuses on reputable sources
3. **Contextual Relevance**: Articles connect to coaching themes
4. **Actionable**: Users get specific search queries to find articles
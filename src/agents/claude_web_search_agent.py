"""Claude Web Search Agent using Anthropic's native WebSearch capability."""

import logging
from datetime import datetime

from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse
from src.services.llm_factory import LLMFactory, LLMTier

logger = logging.getLogger(__name__)


class ClaudeWebSearchAgent(BaseAgent):
    """Agent that uses Claude's native WebSearch for finding real articles.

    This agent performs actual web searches using Anthropic's WebSearch tool,
    returning real URLs and content from the web.
    """

    def __init__(self):
        """Initialize the Claude Web Search Agent."""
        super().__init__(
            name="claude_web_search",
            capabilities=[
                AgentCapability.WEB_SEARCH,
                AgentCapability.RESEARCH,
                AgentCapability.CONTENT_CURATION
            ]
        )
        # Use standard tier for search operations
        self.llm_service = LLMFactory.create_service(LLMTier.STANDARD)

    async def initialize(self) -> None:
        """Initialize the web search agent."""
        self.is_initialized = True
        logger.info("Claude Web Search Agent initialized")

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle search requests using Claude's native WebSearch.

        Args:
            request: Request containing search themes or queries

        Returns:
            Response with real article recommendations from web search
        """
        try:
            # Extract search queries from request
            queries = request.context.get("queries", [])
            if not queries:
                # Try to extract from themes
                themes = request.context.get("themes", [])
                queries = [
                    f"{theme} best practices articles research"
                    for theme in themes
                ]

            if not queries:
                return AgentResponse(
                    agent_name=self.name,
                    content="No search queries provided.",
                    metadata={"error": "No queries to search"},
                    request_id=request.request_id,
                    timestamp=datetime.now()
                )

            # Perform searches and collect results
            all_results = []
            search_metadata = []

            # Limit to 3 searches
            queries_to_process = queries[:3]
            for query in queries_to_process:
                logger.info(f"Performing web search for: {query}")

                # Use Claude's WebSearch through a prompt that triggers it
                search_prompt = f"""Please search the web for: "{query}"

Find 3-4 recent, high-quality articles from reputable sources like:
- Harvard Business Review (HBR)
- MIT Sloan Review
- McKinsey Insights
- The Atlantic
- Fast Company
- TechCrunch
- Wired

For each article found, provide:
1. The exact article title
2. The source/publication
3. The actual URL (must be a real, working link)
4. A brief 1-2 sentence summary of key insights

Format as:
- **"Article Title"** - Source
  URL: [actual URL]
  Summary: [brief summary]"""

                try:
                    # Enable WebSearch tool for real web searches
                    search_results = await self.llm_service.generate_response(
                        messages=[{"role": "user", "content": search_prompt}],
                        system_prompt=(
                            "You are a research assistant. Use web search to "
                            "find real articles. Return only working URLs from actual searches."
                        ),
                        max_tokens=1500,
                        temperature=0.3,
                        tools=[{
                            "type": "web_search_20250305",
                            "name": "web_search",
                            "max_uses": 5
                        }]
                    )

                    if search_results:
                        all_results.append(f"\n**{query}**\n{search_results}")
                        search_metadata.append({
                            "query": query,
                            "found": True,
                            "source": "claude_websearch"
                        })

                except Exception as e:
                    logger.error(f"Search error for query '{query}': {e}")
                    search_metadata.append({
                        "query": query,
                        "found": False,
                        "error": str(e)
                    })

            # Format final results
            if all_results:
                formatted_results = (
                    "Here are relevant articles I found:\n" +
                    "\n".join(all_results)
                )
            else:
                formatted_results = (
                    "Unable to find articles at this time. "
                    "Please try searching manually."
                )

            return AgentResponse(
                agent_name=self.name,
                content=formatted_results,
                metadata={
                    "search_type": "claude_native_websearch",
                    "searches_performed": len(queries_to_process),
                    "searches_successful": len(all_results),
                    "search_details": search_metadata
                },
                request_id=request.request_id,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Claude web search agent error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                content=f"Error performing web search: {str(e)}",
                metadata={"error": str(e)},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e)
            )

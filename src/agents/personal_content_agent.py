"""Personal Content Agent for accessing user's personal documentation."""

import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path

from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse
from src.orchestration.document_loader import MarkdownDocumentLoader
from src.orchestration.context_state import ContextState
from src.services.llm_factory import LLMFactory, LLMTier


logger = logging.getLogger(__name__)


class PersonalContentAgent(BaseAgent):
    """Agent responsible for accessing and providing personal documentation context."""

    def __init__(self, documents_path: str = "docs/personal", chunk_size: int = 2000):
        """Initialize Personal Content Agent.

        Args:
            documents_path: Path to personal documents directory
            chunk_size: Maximum characters per document chunk
        """
        super().__init__(
            name="personal_content",
            capabilities=[AgentCapability.PERSONAL_CONTEXT]
        )
        self.documents_path = Path(documents_path)
        self.chunk_size = chunk_size
        self.document_loader = MarkdownDocumentLoader(documents_path, chunk_size)
        self.available_documents: List[str] = []
        # Use Claude Sonnet for intelligent content synthesis
        self.llm_service = LLMFactory.create_service(LLMTier.STANDARD)

    async def initialize(self) -> None:
        """Initialize by scanning available personal documents."""
        try:
            if self.documents_path.exists():
                # Recursively find all markdown files in subdirectories
                self.available_documents = [
                    str(f.relative_to(self.documents_path))
                    for f in self.documents_path.rglob("*.md")
                ]
                logger.info(f"Found {len(self.available_documents)} personal documents")
            else:
                logger.warning(
                    f"Personal documents path not found: {self.documents_path}"
                )
                self.available_documents = []

            self.is_initialized = True
        except Exception as e:
            logger.error(f"Error initializing PersonalContentAgent: {e}")
            raise

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle personal content requests from other agents.

        Args:
            request: The agent request to handle

        Returns:
            AgentResponse with relevant personal content
        """
        try:
            # Create a mock state for document loader compatibility
            mock_state = ContextState(
                messages=[{
                    "content": request.query,
                    "type": "user"
                }],
                context_relevance={"documents": 1.0}  # Force high relevance
            )

            # Use document loader to find relevant content
            updated_state = await self.document_loader.load_documents(mock_state)

            # Extract relevant documents
            if updated_state.document_context:
                return await self._format_personal_content_response(
                    request, updated_state.document_context
                )
            else:
                return AgentResponse(
                    agent_name=self.name,
                    content="No relevant personal content found for this query.",
                    metadata={
                        "documents_searched": len(self.available_documents),
                        "relevance_threshold": 0.6
                    },
                    request_id=request.request_id,
                    timestamp=datetime.now()
                )

        except Exception as e:
            logger.error(f"Error handling personal content request: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="Error accessing personal content.",
                metadata={"error": str(e)},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e)
            )

    async def _format_personal_content_response(
        self, request: AgentRequest, documents: Dict[str, str]
    ) -> AgentResponse:
        """Use LLM to synthesize personal content into intelligent response.

        Args:
            request: Original request
            documents: Dictionary of filename->content

        Returns:
            Formatted AgentResponse
        """
        # Build prompt for LLM with personal context
        prompt = self._build_synthesis_prompt(request.query, documents)

        # Get LLM response
        messages = [{"role": "user", "content": prompt}]
        llm_response = await self.llm_service.generate_response(
            messages, max_tokens=1000
        )

        # Extract sources for metadata
        sources = list(documents.keys())

        return AgentResponse(
            agent_name=self.name,
            content=llm_response,
            metadata={
                "documents_found": len(documents),
                "documents_used": len(documents),
                "sources": sources,
                "llm_tier": "standard",
                "llm_model": "claude-sonnet-4"
            },
            request_id=request.request_id,
            timestamp=datetime.now()
        )

    def _build_synthesis_prompt(self, query: str, documents: Dict[str, str]) -> str:
        """Build prompt for LLM to synthesize personal content.

        Args:
            query: The question about personal content
            documents: Dict of filename->content

        Returns:
            Prompt for the LLM
        """
        prompt_parts = [
            "You are analyzing personal documentation to provide "
            "relevant context for a coaching conversation.",
            "",
            f"Query: {query}",
            "",
            "Available Personal Context:",
            ""
        ]

        # Add each document
        for filename, content in documents.items():
            prompt_parts.extend([
                f"=== {filename} ===",
                content[:self.chunk_size],  # Respect chunk size limit
                ""
            ])

        prompt_parts.extend([
            "Based on the personal context above, provide:",
            "1. RELEVANT CONTEXT: Key insights from the documents "
            "that relate to the query",
            "2. SUGGESTED INTEGRATION: How to naturally weave these "
            "insights into the coaching conversation",
            "",
            "Format your response clearly with these two sections. "
            "Be specific and actionable."
        ])

        return "\n".join(prompt_parts)

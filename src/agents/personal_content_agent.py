"""Personal Content Agent for accessing user's personal documentation."""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse
from src.orchestration.document_loader import MarkdownDocumentLoader
from src.orchestration.context_state import ContextState


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

    async def initialize(self) -> None:
        """Initialize by scanning available personal documents."""
        try:
            if self.documents_path.exists():
                self.available_documents = [
                    f.name for f in self.documents_path.glob("*.md")
                ]
                logger.info(f"Found {len(self.available_documents)} personal documents")
            else:
                logger.warning(f"Personal documents path not found: {self.documents_path}")
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
                return self._format_personal_content_response(
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

    def _format_personal_content_response(
        self, request: AgentRequest, documents: Dict[str, str]
    ) -> AgentResponse:
        """Format personal content into structured response.

        Args:
            request: Original request
            documents: Dictionary of filename->content

        Returns:
            Formatted AgentResponse
        """
        # Convert dict to list format for processing
        doc_list = []
        for filename, content in documents.items():
            doc_list.append({
                "source": filename,
                "content": content,
                "relevance": 1.0  # All docs that made it here are relevant
            })
        
        # Take all documents (already filtered by relevance)
        relevant_content = doc_list
        
        # Format response following the prompt structure
        content_lines = ["RELEVANT CONTEXT:"]
        for item in relevant_content:
            # Extract key points from content
            lines = item["content"].strip().split("\n")
            key_points = [
                line.strip() for line in lines 
                if line.strip() and not line.strip().startswith("#")
            ][:3]  # Take first 3 non-header lines
            
            for point in key_points:
                content_lines.append(f"- {point}")
        
        # Add integration suggestion
        content_lines.extend([
            "",
            "SUGGESTED INTEGRATION:",
            self._generate_integration_suggestion(request.query, relevant_content)
        ])
        
        return AgentResponse(
            agent_name=self.name,
            content="\n".join(content_lines),
            metadata={
                "documents_found": len(documents),
                "documents_used": len(relevant_content),
                "relevance_scores": [doc["relevance"] for doc in relevant_content],
                "sources": [doc["source"] for doc in relevant_content]
            },
            request_id=request.request_id,
            timestamp=datetime.now()
        )

    def _generate_integration_suggestion(
        self, query: str, content: List[Dict[str, Any]]
    ) -> str:
        """Generate a suggestion for how to integrate personal content.

        Args:
            query: Original query
            content: Relevant content found

        Returns:
            Integration suggestion
        """
        query_lower = query.lower()
        
        if "value" in query_lower or "belief" in query_lower:
            return "Reference these core beliefs when discussing current challenges"
        elif "experience" in query_lower or "past" in query_lower:
            return "Draw parallels between past experiences and current situation"
        elif "goal" in query_lower or "aspiration" in query_lower:
            return "Connect current discussion to long-term aspirations"
        else:
            return "Weave these insights naturally into the coaching conversation"
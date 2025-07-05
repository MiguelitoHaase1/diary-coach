"""Markdown Document Loader for Session 6.6 - Personal document context integration."""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.orchestration.context_state import ContextState


logger = logging.getLogger(__name__)


class MarkdownDocumentLoader:
    """Loads and processes markdown documents for context integration."""
    
    def __init__(self, documents_path: str, chunk_size: int = 2000):
        """Initialize document loader.
        
        Args:
            documents_path: Path to directory containing markdown documents
            chunk_size: Maximum characters per document chunk
        """
        self.documents_path = Path(documents_path)
        self.chunk_size = chunk_size
        self.document_cache = {}  # Cache for loaded documents
        self.metadata_cache = {}  # Cache for document metadata
        
    async def load_documents(self, state: ContextState) -> ContextState:
        """Load relevant documents based on conversation context."""
        
        # Initialize context usage tracking
        if not state.context_usage:
            state.context_usage = {}
        
        start_time = datetime.now()
        self.cache_hits = 0  # Track cache hits for this load operation
        
        # Check relevance threshold
        document_relevance = state.context_relevance.get("documents", 0.0)
        if document_relevance <= 0.6:
            state.context_usage["documents_loaded"] = False
            state.context_usage["skip_reason"] = "Low relevance score"
            return state
        
        try:
            # Get conversation context for filtering
            conversation_context = self._extract_conversation_context(state.messages)
            
            # Load and score documents
            documents, metadata = await self._load_and_score_documents(conversation_context)
            
            if not documents:
                state.context_usage["documents_loaded"] = False
                state.context_usage["skip_reason"] = "No documents found"
                return state
            
            # Filter and format for context injection
            filtered_docs = self._filter_by_relevance(documents, conversation_context)
            chunked_docs = self._apply_chunking(filtered_docs)
            
            # Update state
            state.document_context = chunked_docs
            state.context_usage.update({
                "documents_loaded": True,
                "document_count": len(documents),
                "filtered_count": len(filtered_docs),
                "document_relevance_scores": {doc["filename"]: doc["relevance_score"] for doc in documents},
                "document_metadata": metadata,
                "document_load_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            })
            
            # Track cache hits if any occurred
            if self.cache_hits > 0:
                state.context_usage["cache_hit"] = True
                state.context_usage["cache_hits_count"] = self.cache_hits
            
            # Track chunking if applied
            if len(str(chunked_docs)) != len(str(filtered_docs)):
                state.context_usage["documents_chunked"] = True
                state.context_usage["total_chunks"] = len(chunked_docs)
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            state.context_usage.update({
                "documents_loaded": False,
                "error": str(e)
            })
            state.document_context = None
        
        state.decision_path.append("document_loader")
        return state
    
    async def _load_and_score_documents(self, conversation_context: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Load documents from filesystem and score relevance."""
        documents = []
        metadata = []
        
        if not self.documents_path.exists():
            raise FileNotFoundError(f"Documents directory not found: {self.documents_path}")
        
        # Get all markdown files
        markdown_files = list(self.documents_path.glob("*.md"))
        
        for file_path in markdown_files:
            try:
                # Check cache first
                cache_key = f"{file_path}:{file_path.stat().st_mtime}"
                if cache_key in self.document_cache:
                    content = self.document_cache[cache_key]
                    self._track_cache_hit()
                else:
                    # Load file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Cache the content
                    self.document_cache[cache_key] = content
                
                # Extract document metadata
                doc_metadata = {
                    "filename": file_path.stem,
                    "full_path": str(file_path),
                    "size_chars": len(content),
                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                metadata.append(doc_metadata)
                
                # Score relevance to conversation
                relevance_score = self._calculate_document_relevance(content, conversation_context, file_path.stem)
                
                documents.append({
                    "filename": file_path.stem,
                    "content": content,
                    "relevance_score": relevance_score,
                    "metadata": doc_metadata
                })
                
            except Exception as e:
                logger.warning(f"Error loading document {file_path}: {e}")
                continue
        
        # Sort by relevance score
        documents.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return documents, metadata
    
    def _calculate_document_relevance(self, content: str, conversation_context: str, filename: str) -> float:
        """Calculate relevance score between document and conversation."""
        
        # Extract keywords from conversation
        conversation_words = set(self._extract_keywords(conversation_context.lower()))
        
        # Extract keywords from document content
        document_words = set(self._extract_keywords(content.lower()))
        
        # Calculate word overlap
        overlap = len(conversation_words.intersection(document_words))
        overlap_score = overlap / len(conversation_words) if conversation_words else 0
        
        # Boost score for filename matches
        filename_boost = 0.0
        if any(word in filename.lower() for word in conversation_words):
            filename_boost = 0.3
        
        # Boost score for exact phrase matches in content
        phrase_boost = 0.0
        conversation_phrases = self._extract_phrases(conversation_context.lower())
        for phrase in conversation_phrases:
            if phrase in content.lower():
                phrase_boost += 0.2
        phrase_boost = min(phrase_boost, 0.5)  # Cap at 0.5
        
        # Combine scores
        total_score = min(overlap_score + filename_boost + phrase_boost, 1.0)
        
        return total_score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its',
            'our', 'their', 'this', 'that', 'these', 'those'
        }
        
        # Extract words (3+ characters, alphabetic)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        
        # Filter out stop words and return unique meaningful keywords
        keywords = [word for word in words if word.lower() not in stop_words]
        
        return list(set(keywords))
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from text."""
        # Extract 2-3 word phrases
        words = text.split()
        phrases = []
        
        # 2-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 6:  # Skip very short phrases
                phrases.append(phrase)
        
        # 3-word phrases
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(phrase) > 10:  # Skip very short phrases
                phrases.append(phrase)
        
        return phrases
    
    def _extract_conversation_context(self, messages: List[Dict[str, Any]]) -> str:
        """Extract text context from conversation messages."""
        if not messages:
            return ""
        
        # Combine recent messages (last 5) for context
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        context_parts = []
        
        for message in recent_messages:
            content = message.get("content", "")
            if content:
                context_parts.append(content)
        
        return " ".join(context_parts)
    
    def _filter_by_relevance(self, documents: List[Dict[str, Any]], conversation_context: str) -> Dict[str, str]:
        """Filter documents by relevance and return formatted content."""
        filtered_docs = {}
        
        # Take top 2 most relevant documents
        for doc in documents[:2]:
            if doc["relevance_score"] > 0.1:  # Minimum relevance threshold
                filtered_docs[doc["filename"]] = doc["content"]
        
        return filtered_docs
    
    def _apply_chunking(self, documents: Dict[str, str]) -> Dict[str, str]:
        """Apply chunking to large documents."""
        chunked_docs = {}
        
        for filename, content in documents.items():
            if len(content) <= self.chunk_size:
                chunked_docs[filename] = content
            else:
                # Take the first chunk and add ellipsis
                chunk = content[:self.chunk_size]
                # Try to break at a sentence boundary
                last_period = chunk.rfind('.')
                if last_period > self.chunk_size * 0.8:  # If period is in last 20%
                    chunk = chunk[:last_period + 1]
                
                chunked_docs[filename] = chunk + "\n\n[... document continues ...]"
        
        return chunked_docs
    
    def _track_cache_hit(self):
        """Track that a cache hit occurred."""
        self.cache_hits += 1
    
    def clear_cache(self):
        """Clear document cache."""
        self.document_cache.clear()
        self.metadata_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cached_documents": len(self.document_cache),
            "cached_metadata": len(self.metadata_cache)
        }
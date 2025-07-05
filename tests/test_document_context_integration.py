"""Test document context integration for Session 6.6."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestration.context_state import ContextState
from src.orchestration.document_loader import MarkdownDocumentLoader


@pytest.mark.asyncio
async def test_document_context_loading():
    """Should load relevant documents based on conversation."""
    
    loader = MarkdownDocumentLoader("/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory")
    
    state = ContextState(
        messages=[{"type": "user", "content": "Let's review my core beliefs", "timestamp": datetime.now().isoformat()}],
        context_relevance={"documents": 0.9},
        conversation_id="test_conv"
    )
    
    result = await loader.load_documents(state)
    
    # Should load core beliefs document
    assert result.document_context is not None
    assert "Core_beliefs" in result.document_context or "core_beliefs" in result.document_context
    assert len(str(result.document_context)) > 100  # Should have substantial content


@pytest.mark.asyncio
async def test_document_relevance_filtering():
    """Should filter documents based on conversation relevance."""
    
    loader = MarkdownDocumentLoader("/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory")
    
    # Test cases with different relevance patterns
    test_cases = [
        ("What are my core values and beliefs?", "Core_beliefs"),
        ("Tell me about my OpenAI chat history", "OpenAI_chatmemory"), 
        ("How do I approach product leadership?", "Core_beliefs"),
        ("What's in my conversation memory?", "OpenAI_chatmemory")
    ]
    
    for query, expected_doc in test_cases:
        state = ContextState(
            messages=[{"type": "user", "content": query, "timestamp": datetime.now().isoformat()}],
            context_relevance={"documents": 0.8},
            conversation_id="test_conv"
        )
        
        result = await loader.load_documents(state)
        
        # Should load relevant document
        assert result.document_context is not None
        # Should prefer the most relevant document
        doc_keys = list(result.document_context.keys())
        assert any(expected_doc.lower() in key.lower() for key in doc_keys)


@pytest.mark.asyncio
async def test_document_chunking_for_large_docs():
    """Should chunk large documents for context budget management."""
    
    loader = MarkdownDocumentLoader("/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory", chunk_size=500)
    
    state = ContextState(
        messages=[{"type": "user", "content": "Tell me about strategic thinking frameworks", "timestamp": datetime.now().isoformat()}],
        context_relevance={"documents": 0.9},
        conversation_id="test_conv"
    )
    
    result = await loader.load_documents(state)
    
    # Should have document content but chunked appropriately
    assert result.document_context is not None
    
    # Should track chunking in context usage
    assert "documents_chunked" in result.context_usage
    assert "total_chunks" in result.context_usage


@pytest.mark.asyncio
async def test_document_search_and_relevance():
    """Should search within documents and score relevance."""
    
    loader = MarkdownDocumentLoader("/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory")
    
    # Query about specific concepts in core beliefs
    state = ContextState(
        messages=[{"type": "user", "content": "How should I think about customer discovery and product strategy?", "timestamp": datetime.now().isoformat()}],
        context_relevance={"documents": 0.9},
        conversation_id="test_conv"
    )
    
    result = await loader.load_documents(state)
    
    # Should find relevant sections
    assert result.document_context is not None
    
    # Should include relevance scoring
    assert "document_relevance_scores" in result.context_usage
    
    # Should extract relevant sections containing keywords
    doc_content = str(result.document_context)
    assert any(keyword in doc_content.lower() for keyword in ["customer", "product", "discovery", "strategy"])


@pytest.mark.asyncio
async def test_low_relevance_document_skipping():
    """Should skip document loading when relevance is low."""
    
    loader = MarkdownDocumentLoader("/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory")
    
    state = ContextState(
        messages=[{"type": "user", "content": "I'm feeling overwhelmed today", "timestamp": datetime.now().isoformat()}],
        context_relevance={"documents": 0.2},  # Low relevance
        conversation_id="test_conv"
    )
    
    result = await loader.load_documents(state)
    
    # Should not load documents
    assert result.context_usage["documents_loaded"] == False
    assert result.document_context is None or len(result.document_context) == 0


@pytest.mark.asyncio
async def test_document_caching():
    """Should cache documents for performance."""
    
    loader = MarkdownDocumentLoader("/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory")
    
    state = ContextState(
        messages=[{"type": "user", "content": "What are my core beliefs?", "timestamp": datetime.now().isoformat()}],
        context_relevance={"documents": 0.9},
        conversation_id="test_conv"
    )
    
    # First load
    result1 = await loader.load_documents(state)
    first_load_time = result1.context_usage.get("document_load_time_ms", 0)
    
    # Second load should be faster (cached)
    result2 = await loader.load_documents(state)
    second_load_time = result2.context_usage.get("document_load_time_ms", 0)
    
    # Should have cached results
    assert "cache_hit" in result2.context_usage
    assert result2.context_usage["cache_hit"] == True


@pytest.mark.asyncio
async def test_document_error_handling():
    """Should handle missing or corrupted documents gracefully."""
    
    # Test with non-existent directory
    loader = MarkdownDocumentLoader("/nonexistent/directory")
    
    state = ContextState(
        messages=[{"type": "user", "content": "What are my beliefs?", "timestamp": datetime.now().isoformat()}],
        context_relevance={"documents": 0.9},
        conversation_id="test_conv"
    )
    
    result = await loader.load_documents(state)
    
    # Should handle error gracefully
    assert result.context_usage["documents_loaded"] == False
    assert "error" in result.context_usage
    assert result.document_context is None


@pytest.mark.asyncio
async def test_document_metadata_extraction():
    """Should extract and use document metadata."""
    
    loader = MarkdownDocumentLoader("/Users/michaelhaase/Desktop/coding/diary-coach/docs/memory")
    
    state = ContextState(
        messages=[{"type": "user", "content": "Tell me about my product leadership framework", "timestamp": datetime.now().isoformat()}],
        context_relevance={"documents": 0.9},
        conversation_id="test_conv"
    )
    
    result = await loader.load_documents(state)
    
    # Should extract metadata about documents
    assert "document_metadata" in result.context_usage
    metadata = result.context_usage["document_metadata"]
    
    # Should include file information
    assert isinstance(metadata, list)
    if metadata:
        assert "filename" in metadata[0]
        assert "size_chars" in metadata[0]
        assert "last_modified" in metadata[0]
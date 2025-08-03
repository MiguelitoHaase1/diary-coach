"""Tests for Claude Web Search Agent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.agents.claude_web_search_agent import ClaudeWebSearchAgent
from src.agents.base import AgentRequest, AgentCapability


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = Mock()
    service.generate_response = AsyncMock()
    return service


@pytest.fixture
def web_search_agent(mock_llm_service):
    """Create a web search agent with mocked LLM service."""
    with patch('src.agents.claude_web_search_agent.LLMFactory') as mock_factory:
        mock_factory.create_service.return_value = mock_llm_service
        agent = ClaudeWebSearchAgent()
        return agent


@pytest.mark.asyncio
async def test_agent_initialization(web_search_agent):
    """Test agent initializes with correct capabilities."""
    assert web_search_agent.name == "claude_web_search"
    assert AgentCapability.WEB_SEARCH in web_search_agent.capabilities
    assert AgentCapability.RESEARCH in web_search_agent.capabilities
    assert AgentCapability.CONTENT_CURATION in web_search_agent.capabilities
    
    await web_search_agent.initialize()
    assert web_search_agent.is_initialized


@pytest.mark.asyncio
async def test_handle_request_with_themes(web_search_agent, mock_llm_service):
    """Test handling request with themes."""
    # Setup mock response
    mock_llm_service.generate_response.return_value = """
- **"Building Autonomous Teams"** - Harvard Business Review
  URL: https://hbr.org/example
  Summary: How to build self-organizing teams.
"""
    
    request = AgentRequest(
        from_agent="test",
        to_agent="claude_web_search",
        query="search",
        context={
            "themes": ["autonomous teams", "design systems"]
        }
    )
    
    response = await web_search_agent.handle_request(request)
    
    assert response.agent_name == "claude_web_search"
    assert "autonomous teams" in response.content
    assert response.metadata["search_type"] == "claude_native_websearch"
    assert response.metadata["searches_performed"] == 2
    assert mock_llm_service.generate_response.call_count == 2


@pytest.mark.asyncio
async def test_handle_request_with_queries(web_search_agent, mock_llm_service):
    """Test handling request with direct queries."""
    mock_llm_service.generate_response.return_value = "Found articles."
    
    request = AgentRequest(
        from_agent="test",
        to_agent="claude_web_search",
        query="search",
        context={
            "queries": ["team management best practices"]
        }
    )
    
    response = await web_search_agent.handle_request(request)
    
    assert response.metadata["searches_performed"] == 1
    assert response.metadata["searches_successful"] == 1
    # Should use the query directly, not convert from themes
    assert mock_llm_service.generate_response.call_count == 1


@pytest.mark.asyncio
async def test_handle_request_no_queries(web_search_agent):
    """Test handling request with no queries or themes."""
    request = AgentRequest(
        from_agent="test",
        to_agent="claude_web_search",
        query="search",
        context={}
    )
    
    response = await web_search_agent.handle_request(request)
    
    assert response.content == "No search queries provided."
    assert response.metadata.get("error") == "No queries to search"


@pytest.mark.asyncio
async def test_search_error_handling(web_search_agent, mock_llm_service):
    """Test error handling during search."""
    mock_llm_service.generate_response.side_effect = Exception("API Error")
    
    request = AgentRequest(
        from_agent="test",
        to_agent="claude_web_search",
        query="search",
        context={
            "queries": ["test query"]
        }
    )
    
    response = await web_search_agent.handle_request(request)
    
    assert response.metadata["searches_successful"] == 0
    search_details = response.metadata["search_details"][0]
    assert not search_details["found"]
    assert "API Error" in search_details["error"]


@pytest.mark.asyncio
async def test_query_limit(web_search_agent, mock_llm_service):
    """Test that only 3 queries are processed even if more provided."""
    mock_llm_service.generate_response.return_value = "Results"
    
    request = AgentRequest(
        from_agent="test",
        to_agent="claude_web_search",
        query="search",
        context={
            "queries": ["query1", "query2", "query3", "query4", "query5"]
        }
    )
    
    response = await web_search_agent.handle_request(request)
    
    # Should only process first 3
    assert response.metadata["searches_performed"] == 3
    assert mock_llm_service.generate_response.call_count == 3


@pytest.mark.asyncio
async def test_theme_to_query_conversion(web_search_agent, mock_llm_service):
    """Test themes are converted to search queries."""
    mock_llm_service.generate_response.return_value = "Articles found"
    
    request = AgentRequest(
        from_agent="test",
        to_agent="claude_web_search",
        query="search",
        context={
            "themes": ["leadership", "team dynamics"]
        }
    )
    
    await web_search_agent.handle_request(request)
    
    # Check that the themes were converted to queries
    calls = mock_llm_service.generate_response.call_args_list
    assert len(calls) == 2
    
    # First call should have leadership query
    first_call_content = calls[0][1]["messages"][0]["content"]
    assert "leadership best practices articles research" in first_call_content
    
    # Second call should have team dynamics query
    second_call_content = calls[1][1]["messages"][0]["content"]
    assert "team dynamics best practices articles research" in second_call_content


@pytest.mark.asyncio
async def test_mixed_success_and_failure(web_search_agent, mock_llm_service):
    """Test handling mixed success and failure in searches."""
    # First call succeeds, second fails
    mock_llm_service.generate_response.side_effect = [
        "Success results",
        Exception("Network error")
    ]
    
    request = AgentRequest(
        from_agent="test",
        to_agent="claude_web_search",
        query="search",
        context={
            "queries": ["query1", "query2"]
        }
    )
    
    response = await web_search_agent.handle_request(request)
    
    assert response.metadata["searches_performed"] == 2
    assert response.metadata["searches_successful"] == 1
    
    # Check search details
    details = response.metadata["search_details"]
    assert details[0]["found"] is True
    assert details[1]["found"] is False
    assert "Network error" in details[1]["error"]
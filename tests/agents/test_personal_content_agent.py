"""Tests for Personal Content Agent."""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
from unittest.mock import AsyncMock, patch

from src.agents.personal_content_agent import PersonalContentAgent
from src.agents.base import AgentRequest, AgentCapability


@pytest.fixture
def personal_docs_dir():
    """Create a temporary directory with test personal documents."""
    temp_dir = tempfile.mkdtemp()
    docs_path = Path(temp_dir) / "personal"
    docs_path.mkdir()

    # Create subdirectories
    beliefs_dir = docs_path / "Beliefs"
    beliefs_dir.mkdir()
    about_dir = docs_path / "AboutMe"
    about_dir.mkdir()

    # Create test documents in new structure
    (beliefs_dir / "core_beliefs.md").write_text("""# Core Beliefs

## On Growth
I believe that continuous learning is essential. Every challenge is an opportunity
to grow stronger and wiser.

## On Authenticity
Being true to myself is more important than fitting in. Authenticity creates
deeper connections and genuine happiness.

## On Purpose
My purpose is to help others while maintaining my own well-being. Balance is key.
""")

    (about_dir / "life_experiences.md").write_text("""# Life Experiences

## Career Journey
Started as a software engineer, transitioned to product management.
The shift taught me the importance of understanding user needs.

## Personal Challenges
Overcame anxiety through mindfulness practices and therapy.
This experience taught me resilience and self-compassion.
""")

    (docs_path / "goals_2025.md").write_text("""# Goals for 2025

## Professional
- Launch the coaching platform successfully
- Build a team of 5 dedicated people
- Achieve product-market fit

## Personal
- Maintain daily meditation practice
- Read 24 books this year
- Spend quality time with family weekly
""")

    yield str(docs_path)

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def empty_docs_dir():
    """Create an empty temporary directory."""
    temp_dir = tempfile.mkdtemp()
    docs_path = Path(temp_dir) / "personal"
    docs_path.mkdir()

    yield str(docs_path)

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for tests."""
    with patch('src.agents.personal_content_agent.LLMFactory') as mock_factory:
        mock_service = AsyncMock()
        mock_factory.create_service.return_value = mock_service

        # Default mock response
        mock_service.generate_response.return_value = (
            "RELEVANT CONTEXT:\n"
            "- I believe that continuous learning is essential\n"
            "- Being true to myself is more important than fitting in\n"
            "- Authenticity creates deeper connections\n\n"
            "SUGGESTED INTEGRATION:\n"
            "Reference these core beliefs when discussing current challenges"
        )

        yield mock_service


@pytest.mark.asyncio
async def test_personal_content_agent_initialization(personal_docs_dir):
    """Test agent initializes and finds documents."""
    agent = PersonalContentAgent(documents_path=personal_docs_dir)

    assert agent.name == "personal_content"
    assert AgentCapability.PERSONAL_CONTEXT in agent.capabilities
    assert not agent.is_initialized

    await agent.initialize()

    assert agent.is_initialized
    assert len(agent.available_documents) == 3
    # Check for documents with their relative paths
    doc_names = [doc for doc in agent.available_documents]
    assert any("core_beliefs.md" in doc for doc in doc_names)
    assert any("life_experiences.md" in doc for doc in doc_names)
    assert any("goals_2025.md" in doc for doc in doc_names)


@pytest.mark.asyncio
async def test_personal_content_agent_empty_directory(empty_docs_dir):
    """Test agent handles empty directory gracefully."""
    agent = PersonalContentAgent(documents_path=empty_docs_dir)
    await agent.initialize()

    assert agent.is_initialized
    assert len(agent.available_documents) == 0


@pytest.mark.asyncio
async def test_find_core_beliefs(personal_docs_dir, mock_llm_service):
    """Test finding content about core beliefs."""
    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What are the user's core beliefs about growth and authenticity?",
        context={}
    )

    response = await agent.handle_request(request)

    assert response.agent_name == "personal_content"
    assert not response.error
    assert "continuous learning" in response.content
    assert "authenticity" in response.content.lower()
    assert "RELEVANT CONTEXT:" in response.content
    assert "SUGGESTED INTEGRATION:" in response.content

    # Verify LLM was called
    mock_llm_service.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_find_past_experiences(personal_docs_dir, mock_llm_service):
    """Test finding past experiences."""
    # Configure mock for this specific test
    mock_llm_service.generate_response.return_value = (
        "RELEVANT CONTEXT:\n"
        "- Overcame anxiety through mindfulness practices and therapy\n"
        "- This experience taught me resilience and self-compassion\n\n"
        "SUGGESTED INTEGRATION:\n"
        "Draw parallels between past experiences and current situation"
    )

    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="Has the user dealt with anxiety before? What helped them?",
        context={}
    )

    response = await agent.handle_request(request)

    assert "anxiety" in response.content.lower()
    assert "mindfulness" in response.content
    assert response.metadata["documents_found"] > 0


@pytest.mark.asyncio
async def test_find_goals(personal_docs_dir, mock_llm_service):
    """Test finding user goals."""
    # Configure mock for this specific test
    mock_llm_service.generate_response.return_value = (
        "RELEVANT CONTEXT:\n"
        "- Launch the coaching platform successfully\n"
        "- Build a team of 5 dedicated people\n"
        "- Achieve product-market fit\n\n"
        "SUGGESTED INTEGRATION:\n"
        "Connect current discussion to long-term aspirations"
    )

    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="orchestrator",
        to_agent="personal_content",
        query="What are the user's professional goals for this year?",
        context={}
    )

    response = await agent.handle_request(request)

    assert "coaching platform" in response.content
    assert "team" in response.content
    assert "product-market fit" in response.content


@pytest.mark.asyncio
async def test_no_relevant_content(personal_docs_dir, mock_llm_service):
    """Test when no relevant content is found."""
    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What is the user's favorite color?",
        context={}
    )

    response = await agent.handle_request(request)

    # Even with no specific match, document loader might find some content
    # based on general relevance scoring
    assert response.agent_name == "personal_content"
    assert not response.error


@pytest.mark.asyncio
async def test_structured_response_format(personal_docs_dir, mock_llm_service):
    """Test that responses follow the structured format."""
    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="Tell me about the user's values and purpose",
        context={}
    )

    response = await agent.handle_request(request)

    # Check structured format
    assert "RELEVANT CONTEXT:" in response.content
    assert "SUGGESTED INTEGRATION:" in response.content

    # Check metadata
    assert "documents_found" in response.metadata
    assert "documents_used" in response.metadata
    assert "sources" in response.metadata
    assert "llm_tier" in response.metadata
    assert "llm_model" in response.metadata


@pytest.mark.asyncio
async def test_error_handling_missing_directory():
    """Test agent handles missing directory gracefully."""
    agent = PersonalContentAgent(documents_path="/nonexistent/path")
    await agent.initialize()

    assert agent.is_initialized
    assert len(agent.available_documents) == 0

    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="Any content?",
        context={}
    )

    response = await agent.handle_request(request)
    assert response.agent_name == "personal_content"
    # Should handle gracefully without error


@pytest.mark.asyncio
async def test_metadata_tracking(personal_docs_dir, mock_llm_service):
    """Test that agent tracks metadata properly."""
    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What drives the user's purpose?",
        context={}
    )

    response = await agent.handle_request(request)

    assert response.request_id == request.request_id
    assert isinstance(response.timestamp, datetime)
    assert response.metadata["documents_found"] >= 1
    assert len(response.metadata["sources"]) >= 1
    assert all(
        isinstance(source, str)
        for source in response.metadata["sources"]
    )


@pytest.mark.asyncio
async def test_integration_suggestions(personal_docs_dir, mock_llm_service):
    """Test that integration suggestions vary by query type."""
    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()

    # Test belief query
    belief_request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What are their core values?",
        context={}
    )
    belief_response = await agent.handle_request(belief_request)
    assert "core beliefs" in belief_response.content.lower()

    # Test experience query
    exp_request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What past experiences shape them?",
        context={}
    )

    # Configure mock response for experience query
    mock_llm_service.generate_response.return_value = (
        "RELEVANT CONTEXT:\n"
        "- Past experience in software engineering\n"
        "- Learned resilience through challenges\n\n"
        "SUGGESTED INTEGRATION:\n"
        "Draw parallels between past experiences and current situation"
    )

    exp_response = await agent.handle_request(exp_request)
    assert (
        "parallels" in exp_response.content.lower() or
        "experience" in exp_response.content.lower()
    )

    # Test goal query with more specific wording
    goal_request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What are their goals and aspirations for the future?",
        context={}
    )

    # Configure mock response for goal query
    mock_llm_service.generate_response.return_value = (
        "RELEVANT CONTEXT:\n"
        "- Launch the coaching platform successfully\n"
        "- Build a team of dedicated people\n"
        "- Personal goal: maintain daily meditation practice\n\n"
        "SUGGESTED INTEGRATION:\n"
        "Connect current discussion to long-term aspirations"
    )

    goal_response = await agent.handle_request(goal_request)
    # Should find goals document or return no content message
    assert (
        "goal" in goal_response.content.lower() or
        "aspiration" in goal_response.content.lower() or
        "no relevant" in goal_response.content.lower()
    )

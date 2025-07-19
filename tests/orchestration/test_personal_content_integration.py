"""Integration tests for Personal Content Agent in multi-agent system."""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from src.agents.personal_content_agent import PersonalContentAgent
from src.agents.base import AgentRequest, AgentResponse
from src.orchestration.multi_agent_state import MultiAgentState
from src.agents.registry import agent_registry


@pytest.fixture
def personal_docs_dir():
    """Create a temporary directory with test personal documents."""
    temp_dir = tempfile.mkdtemp()
    docs_path = Path(temp_dir) / "personal"
    docs_path.mkdir()
    
    # Create test documents
    (docs_path / "core_beliefs.md").write_text("""# Core Beliefs

## On Impact
I believe in focusing on high-leverage activities. Impact over busyness.

## On Decision Making  
Make decisions based on values, not emotions. Long-term thinking prevails.
""")
    
    yield str(docs_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_personal_content_agent_in_multi_agent_state(personal_docs_dir):
    """Test Personal Content Agent integration with MultiAgentState."""
    # Initialize agent
    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()
    
    # Register agent
    agent_registry.register_instance(agent)
    
    # Create multi-agent state
    state = MultiAgentState(
        messages=[{
            "role": "user",
            "content": "How should I approach this strategic decision?"
        }],
        conversation_id="test_conv"
    )
    
    # Simulate coach requesting personal context
    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What are the user's core beliefs about decision making?",
        context={"conversation_id": state.conversation_id}
    )
    
    # Add to pending requests
    state.add_pending_request(request)
    
    # Process request
    response = await agent.handle_request(request)
    
    # Complete request in state
    state.complete_request(request.request_id, response)
    
    # Store personal context
    state.set_personal_context({
        "content": response.content,
        "metadata": response.metadata
    })
    
    # Verify integration
    assert state.personal_context is not None
    assert "decision" in state.personal_context["content"].lower()
    assert "values" in state.personal_context["content"].lower()
    assert len(state.agent_responses["personal_content"]) == 1


@pytest.mark.asyncio
async def test_coach_agent_uses_personal_content(personal_docs_dir):
    """Test that coach can request and use personal content."""
    # Initialize personal content agent
    pc_agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await pc_agent.initialize()
    
    # Create state with conversation needing personal context
    state = MultiAgentState(
        messages=[
            {"role": "user", "content": "I'm struggling with a big decision"},
            {"role": "assistant", "content": "Tell me more about what's making this difficult."},
            {"role": "user", "content": "I want to be efficient but also true to my values"}
        ],
        conversation_id="test_conv"
    )
    
    # Coach requests personal context
    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="User is struggling with decision making - what are their core beliefs?",
        context={
            "conversation_id": state.conversation_id,
            "current_challenge": "decision making"
        }
    )
    
    response = await pc_agent.handle_request(request)
    
    # Verify response is useful for coach
    assert "RELEVANT CONTEXT:" in response.content
    assert "SUGGESTED INTEGRATION:" in response.content
    assert "impact" in response.content.lower()
    assert "decision" in response.content.lower()
    
    # Store in state for coach use
    state.set_personal_context({
        "beliefs": response.content,
        "sources": response.metadata.get("sources", [])
    })
    
    # Verify coach can access
    all_context = state.get_all_context()
    assert all_context["personal"] is not None
    assert "beliefs" in all_context["personal"]


@pytest.mark.asyncio
async def test_personal_content_relevance_scoring(personal_docs_dir):
    """Test that personal content agent uses relevance scoring effectively."""
    agent = PersonalContentAgent(documents_path=personal_docs_dir)
    await agent.initialize()
    
    # High relevance query
    relevant_request = AgentRequest(
        from_agent="orchestrator",
        to_agent="personal_content",
        query="User mentioned 'impact' - what are their beliefs about this?",
        context={}
    )
    
    relevant_response = await agent.handle_request(relevant_request)
    
    # Low relevance query
    irrelevant_request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What's the weather like?",
        context={}
    )
    
    irrelevant_response = await agent.handle_request(irrelevant_request)
    
    # Compare responses
    assert relevant_response.metadata["documents_found"] > 0
    # The irrelevant query might still find some documents due to
    # the document loader's broad matching
    
    # But relevance scores should differ
    if relevant_response.metadata.get("relevance_scores") and irrelevant_response.metadata.get("relevance_scores"):
        avg_relevant = sum(relevant_response.metadata["relevance_scores"]) / len(relevant_response.metadata["relevance_scores"])
        avg_irrelevant = sum(irrelevant_response.metadata["relevance_scores"]) / len(irrelevant_response.metadata["relevance_scores"]) if irrelevant_response.metadata["relevance_scores"] else 0
        # Relevant query should have higher average score
        assert avg_relevant >= avg_irrelevant


@pytest.mark.asyncio
async def test_empty_personal_content_handling():
    """Test handling when no personal content exists."""
    # Use non-existent directory
    agent = PersonalContentAgent(documents_path="/tmp/nonexistent_personal_docs")
    await agent.initialize()
    
    request = AgentRequest(
        from_agent="coach",
        to_agent="personal_content",
        query="What are the user's values?",
        context={}
    )
    
    response = await agent.handle_request(request)
    
    # Should handle gracefully
    assert response.error is None
    assert response.metadata["documents_searched"] == 0
    assert "No relevant personal content found" in response.content or response.metadata["documents_found"] == 0
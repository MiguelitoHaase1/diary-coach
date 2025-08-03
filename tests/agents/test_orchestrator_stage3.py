"""Tests for Orchestrator Stage 3 coordination."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.base import AgentRequest, AgentResponse, AgentCapability


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = Mock()
    service.generate_response = AsyncMock(return_value='{"status": "success"}')
    return service


@pytest.fixture
def orchestrator(mock_llm_service):
    """Create an orchestrator with mocked dependencies."""
    return OrchestratorAgent(mock_llm_service)


@pytest.fixture
def mock_agents():
    """Create mock agents for testing."""
    # Mock memory agent
    memory = Mock()
    memory.name = "memory"
    memory.capabilities = [AgentCapability.MEMORY_ACCESS]
    memory.handle_request = AsyncMock(return_value=Mock(
        content="Memory insights: past conversations show...",
        error=None
    ))
    
    # Mock personal content agent
    personal = Mock()
    personal.name = "personal_content"
    personal.capabilities = [AgentCapability.PERSONAL_CONTEXT]
    personal.handle_request = AsyncMock(return_value=Mock(
        content="Personal beliefs: empowerment and autonomy",
        error=None
    ))
    
    # Mock MCP agent
    mcp = Mock()
    mcp.name = "mcp"
    mcp.capabilities = [AgentCapability.TASK_MANAGEMENT]
    mcp.handle_request = AsyncMock(return_value=Mock(
        content="Tasks: 3 relevant tasks found",
        error=None
    ))
    
    # Mock reporter agent
    reporter = Mock()
    reporter.name = "reporter"
    reporter.capabilities = [AgentCapability.REPORT_GENERATION]
    reporter.handle_request = AsyncMock(return_value=Mock(
        content="Deep Thoughts Report\n[NEEDS_WEBSEARCH: team autonomy]",
        error=None
    ))
    
    # Mock web search agent
    search = Mock()
    search.name = "claude_web_search"
    search.capabilities = [AgentCapability.WEB_SEARCH]
    search.handle_request = AsyncMock(return_value=Mock(
        content="Found 3 articles on team autonomy",
        error=None,
        metadata={"searches_successful": 1}
    ))
    
    return {
        "memory": memory,
        "personal_content": personal,
        "mcp": mcp,
        "reporter": reporter,
        "claude_web_search": search
    }


@pytest.mark.asyncio
async def test_coordinate_stage3_synthesis_success(orchestrator, mock_agents):
    """Test successful Stage 3 coordination."""
    with patch('src.agents.orchestrator_agent.agent_registry') as mock_registry:
        # Setup registry to return our mocks
        mock_registry.get_agent.side_effect = lambda name: mock_agents.get(name)
        
        context = {
            "conversation": [
                {"role": "user", "content": "Help with team building"},
                {"role": "assistant", "content": "Let's explore that"}
            ]
        }
        
        result = await orchestrator.coordinate_stage3_synthesis(context)
        
        assert result["status"] == "success"
        assert "memory" in result["agent_contributions"]
        assert "personal_content" in result["agent_contributions"]
        assert "mcp" in result["agent_contributions"]
        assert result["initial_report"] == "Deep Thoughts Report\n[NEEDS_WEBSEARCH: team autonomy]"
        assert result["web_search_results"]["status"] == "success"
        
        # Verify all agents were called
        assert mock_agents["memory"].handle_request.called
        assert mock_agents["personal_content"].handle_request.called
        assert mock_agents["mcp"].handle_request.called
        assert mock_agents["reporter"].handle_request.called


@pytest.mark.asyncio
async def test_coordinate_stage3_with_mcp_no_tasks(orchestrator, mock_agents):
    """Test Stage 3 when MCP returns no relevant tasks."""
    mock_agents["mcp"].handle_request.return_value = Mock(
        content="No relevant tasks found.",
        error=None
    )
    
    with patch('src.agents.orchestrator_agent.agent_registry') as mock_registry:
        mock_registry.get_agent.side_effect = lambda name: mock_agents.get(name)
        
        context = {"conversation": []}
        result = await orchestrator.coordinate_stage3_synthesis(context)
        
        # MCP should not be in contributions when no tasks
        assert "mcp" not in result["agent_contributions"]
        assert "memory" in result["agent_contributions"]
        assert "personal_content" in result["agent_contributions"]


@pytest.mark.asyncio
async def test_coordinate_stage3_agent_timeout(orchestrator, mock_agents):
    """Test Stage 3 handling of agent timeout."""
    # Make memory agent timeout
    async def timeout_response(*args, **kwargs):
        import asyncio
        await asyncio.sleep(10)  # Longer than timeout
        
    mock_agents["memory"].handle_request = timeout_response
    
    with patch('src.agents.orchestrator_agent.agent_registry') as mock_registry:
        mock_registry.get_agent.side_effect = lambda name: mock_agents.get(name)
        
        context = {"conversation": []}
        result = await orchestrator.coordinate_stage3_synthesis(context)
        
        # Should still succeed but without memory contribution
        assert result["status"] == "success"
        assert "memory" not in result["agent_contributions"]
        assert "personal_content" in result["agent_contributions"]


@pytest.mark.asyncio
async def test_coordinate_stage3_no_reporter(orchestrator, mock_agents):
    """Test Stage 3 when reporter is not available."""
    with patch('src.agents.orchestrator_agent.agent_registry') as mock_registry:
        def get_agent(name):
            if name == "reporter":
                return None
            return mock_agents.get(name)
        
        mock_registry.get_agent.side_effect = get_agent
        
        context = {"conversation": []}
        result = await orchestrator.coordinate_stage3_synthesis(context)
        
        # Should still succeed but with empty report
        assert result["status"] == "success"
        assert result["initial_report"] == ""
        # No web search should be triggered without report
        assert result["web_search_results"] == {}


@pytest.mark.asyncio
async def test_coordinate_stage3_exception_handling(orchestrator):
    """Test Stage 3 handling of unexpected exceptions."""
    with patch('src.agents.orchestrator_agent.agent_registry') as mock_registry:
        # Make registry throw exception
        mock_registry.get_agent.side_effect = Exception("Registry error")
        
        context = {"conversation": []}
        result = await orchestrator.coordinate_stage3_synthesis(context)
        
        assert result["status"] == "error"
        assert "Registry error" in result["error"]
        assert result["fallback"] == "Direct agent calls recommended"


@pytest.mark.asyncio
async def test_web_search_coordination(orchestrator, mock_agents, mock_llm_service):
    """Test web search coordination in Stage 3."""
    # Setup LLM to identify search needs
    mock_llm_service.generate_response.return_value = "team autonomy\ndesign systems"
    
    with patch('src.agents.orchestrator_agent.agent_registry') as mock_registry:
        mock_registry.get_agent.side_effect = lambda name: mock_agents.get(name)
        
        report = "Deep Thoughts\n[NEEDS_WEBSEARCH: team autonomy]"
        context = {"conversation": []}
        
        result = await orchestrator.coordinate_phase3_search(report, context)
        
        assert result["status"] == "success"
        assert result["queries_executed"] > 0
        assert "structured_brief" in result


@pytest.mark.asyncio
async def test_search_needs_extraction(orchestrator, mock_llm_service):
    """Test extraction of search needs from report."""
    # Test with markers
    report_with_markers = """
    Report content
    [NEEDS_WEBSEARCH: autonomous teams]
    [NEEDS_WEBSEARCH: design patterns]
    """
    
    needs = await orchestrator._analyze_search_needs(report_with_markers)
    assert len(needs) == 2
    assert "autonomous teams" in needs
    assert "design patterns" in needs
    
    # Test without markers (uses LLM)
    mock_llm_service.generate_response.return_value = "leadership\nteam building"
    report_without_markers = "Report about teams and leadership"
    
    needs = await orchestrator._analyze_search_needs(report_without_markers)
    assert len(needs) == 2
    assert "leadership" in needs
    assert "team building" in needs


@pytest.mark.asyncio
async def test_retry_logic_in_search(orchestrator, mock_agents):
    """Test retry logic in web search execution."""
    # Setup search agent to fail first, then succeed
    call_count = 0
    
    async def search_with_retry(request):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Temporary failure")
        return Mock(
            content="Success on retry",
            error=None,
            metadata={"retry_attempt": call_count}
        )
    
    search_agent = Mock()
    search_agent.name = "claude_web_search"
    search_agent.handle_request = search_with_retry
    
    # Need to patch both import locations
    with patch('src.agents.orchestrator_agent.agent_registry') as mock_registry1, \
         patch('src.agents.registry.agent_registry') as mock_registry2:
        mock_registry1.get_agent.return_value = search_agent
        mock_registry2.get_agent.return_value = search_agent
        
        queries = [{"search_query": "test query", "original_need": "test", "retry_count": 0}]
        results = await orchestrator._execute_searches_with_retry(queries, max_retries=2)
        
        assert len(results) == 1
        assert results[0]["success"] is True
        assert call_count == 2  # Failed once, succeeded on retry


@pytest.mark.asyncio
async def test_coordination_metadata(orchestrator, mock_agents):
    """Test that coordination metadata is properly collected."""
    with patch('src.agents.orchestrator_agent.agent_registry') as mock_registry:
        mock_registry.get_agent.side_effect = lambda name: mock_agents.get(name)
        
        context = {"conversation": []}
        result = await orchestrator.coordinate_stage3_synthesis(context)
        
        metadata = result["coordination_metadata"]
        assert metadata["stage"] == "stage3_synthesis"
        assert "timestamp" in metadata
        assert set(metadata["agents_queried"]) == {"memory", "personal_content", "mcp"}
        assert metadata["web_search_performed"] is True
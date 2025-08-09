"""
Tests for parallel agent execution optimization
"""
import asyncio
import time
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.performance.parallel_executor import (
    ParallelExecutor,
    AgentDependencyGraph,
    ExecutionPlan,
    ParallelConfig
)


class TestParallelExecution:
    """Test parallel execution of agents"""
    
    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing"""
        agents = {}
        
        # Memory agent - independent
        memory_agent = Mock()
        memory_agent.name = "memory"
        memory_agent.handle_request = AsyncMock()
        memory_agent.handle_request.return_value = Mock(
            content="Past conversations show...",
            error=None,
            metadata={"execution_time": 0.5}
        )
        agents["memory"] = memory_agent
        
        # MCP agent - independent
        mcp_agent = Mock()
        mcp_agent.name = "mcp"
        mcp_agent.handle_request = AsyncMock()
        mcp_agent.handle_request.return_value = Mock(
            content="Today's tasks: Task 1, Task 2",
            error=None,
            metadata={"execution_time": 0.3}
        )
        agents["mcp"] = mcp_agent
        
        # Personal content agent - independent
        personal_agent = Mock()
        personal_agent.name = "personal_content"
        personal_agent.handle_request = AsyncMock()
        personal_agent.handle_request.return_value = Mock(
            content="Your core beliefs include...",
            error=None,
            metadata={"execution_time": 0.4}
        )
        agents["personal_content"] = personal_agent
        
        # Reporter agent - depends on other agents
        reporter_agent = Mock()
        reporter_agent.name = "reporter"
        reporter_agent.handle_request = AsyncMock()
        reporter_agent.handle_request.return_value = Mock(
            content="Deep thoughts synthesis...",
            error=None,
            metadata={"execution_time": 1.0}
        )
        agents["reporter"] = reporter_agent
        
        return agents
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, mock_agents):
        """Test that independent agents run in parallel"""
        executor = ParallelExecutor()
        
        # Create execution plan for independent agents
        plan = ExecutionPlan()
        plan.add_independent_agents(["memory", "mcp", "personal_content"])
        
        start_time = time.perf_counter()
        
        # Execute agents in parallel
        results = await executor.execute_agents(
            agents=mock_agents,
            plan=plan,
            context={"query": "Good morning"}
        )
        
        execution_time = time.perf_counter() - start_time
        
        # Should complete in roughly the time of the slowest agent (0.5s)
        # not the sum of all agents (1.2s)
        assert execution_time < 0.7  # Allow some overhead
        
        # All agents should have been called
        assert len(results) == 3
        assert "memory" in results
        assert "mcp" in results
        assert "personal_content" in results
    
    @pytest.mark.asyncio
    async def test_dependency_ordering(self, mock_agents):
        """Test that dependent agents wait for prerequisites"""
        executor = ParallelExecutor()
        
        # Create dependency graph
        graph = AgentDependencyGraph()
        graph.add_agent("memory")
        graph.add_agent("mcp")
        graph.add_agent("personal_content")
        graph.add_agent("reporter")
        
        # Reporter depends on the other three
        graph.add_dependency("reporter", "memory")
        graph.add_dependency("reporter", "mcp")
        graph.add_dependency("reporter", "personal_content")
        
        # Generate execution plan
        plan = graph.generate_execution_plan()
        
        # Verify plan has correct phases
        assert len(plan.phases) == 2
        assert set(plan.phases[0]) == {"memory", "mcp", "personal_content"}
        assert set(plan.phases[1]) == {"reporter"}
        
        # Execute with dependencies
        results = await executor.execute_with_dependencies(
            agents=mock_agents,
            graph=graph,
            context={"query": "Generate deep thoughts"}
        )
        
        # All agents should have been called
        assert len(results) == 4
        assert "reporter" in results
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_agents):
        """Test graceful timeout handling"""
        # Make one agent slow
        slow_agent = mock_agents["memory"]
        async def slow_response(request):
            await asyncio.sleep(5)  # Longer than timeout
            return Mock(content="Slow response", error=None)
        slow_agent.handle_request = slow_response
        
        config = ParallelConfig(
            max_parallel=3,
            timeout_seconds=1.0,  # 1 second timeout
            enable_fallback=True
        )
        
        executor = ParallelExecutor(config)
        
        plan = ExecutionPlan()
        plan.add_independent_agents(["memory", "mcp"])
        
        start_time = time.perf_counter()
        results = await executor.execute_agents(
            agents=mock_agents,
            plan=plan,
            context={}
        )
        execution_time = time.perf_counter() - start_time
        
        # Should timeout after 1 second, not wait for 5
        assert execution_time < 1.5
        
        # Memory agent should have timed out
        assert "memory" in results
        assert results["memory"].error == "Timeout after 1.0 seconds"
        
        # MCP agent should have succeeded
        assert "mcp" in results
        assert results["mcp"].error is None
    
    @pytest.mark.asyncio
    async def test_error_isolation(self, mock_agents):
        """Test that errors in one agent don't affect others"""
        # Make one agent fail
        mock_agents["mcp"].handle_request.side_effect = Exception("MCP error")
        
        executor = ParallelExecutor()
        
        plan = ExecutionPlan()
        plan.add_independent_agents(["memory", "mcp", "personal_content"])
        
        results = await executor.execute_agents(
            agents=mock_agents,
            plan=plan,
            context={}
        )
        
        # MCP should have error
        assert "mcp" in results
        assert "MCP error" in str(results["mcp"].error)
        
        # Others should succeed
        assert "memory" in results
        assert results["memory"].error is None
        assert "personal_content" in results
        assert results["personal_content"].error is None
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, mock_agents):
        """Test rate limiting prevents thundering herd"""
        config = ParallelConfig(
            max_parallel=2,  # Only 2 agents at a time
            timeout_seconds=5.0
        )
        
        executor = ParallelExecutor(config)
        
        # Track concurrent calls
        concurrent_calls = []
        max_concurrent = [0]
        
        async def tracked_request(agent_name):
            concurrent_calls.append(agent_name)
            max_concurrent[0] = max(max_concurrent[0], len(concurrent_calls))
            await asyncio.sleep(0.1)  # Simulate work
            concurrent_calls.remove(agent_name)
            return Mock(content=f"{agent_name} response", error=None)
        
        # Replace all agent handlers with tracked version
        for name, agent in mock_agents.items():
            agent.handle_request = lambda n=name: tracked_request(n)
        
        plan = ExecutionPlan()
        plan.add_independent_agents(["memory", "mcp", "personal_content"])
        
        await executor.execute_agents(
            agents=mock_agents,
            plan=plan,
            context={}
        )
        
        # Should never exceed max_parallel
        assert max_concurrent[0] <= 2
    
    @pytest.mark.asyncio
    async def test_result_aggregation(self, mock_agents):
        """Test aggregation of parallel results"""
        executor = ParallelExecutor()
        
        plan = ExecutionPlan()
        plan.add_independent_agents(["memory", "mcp", "personal_content"])
        
        results = await executor.execute_agents(
            agents=mock_agents,
            plan=plan,
            context={"query": "Morning check-in"}
        )
        
        # Aggregate results
        aggregated = executor.aggregate_results(results)
        
        assert "memory" in aggregated["successful"]
        assert "mcp" in aggregated["successful"]
        assert "personal_content" in aggregated["successful"]
        assert len(aggregated["failed"]) == 0
        assert aggregated["total_time"] < 1.0  # Parallel execution
    
    def test_cyclic_dependency_detection(self):
        """Test detection of cyclic dependencies"""
        graph = AgentDependencyGraph()
        
        graph.add_agent("A")
        graph.add_agent("B")
        graph.add_agent("C")
        
        graph.add_dependency("A", "B")
        graph.add_dependency("B", "C")
        
        # This creates a cycle
        with pytest.raises(ValueError, match="Cyclic dependency detected"):
            graph.add_dependency("C", "A")
    
    def test_execution_plan_optimization(self):
        """Test that execution plan is optimized"""
        graph = AgentDependencyGraph()
        
        # Add agents with various dependencies
        graph.add_agent("A")
        graph.add_agent("B")
        graph.add_agent("C")
        graph.add_agent("D")
        graph.add_agent("E")
        
        # A and B are independent
        # C depends on A
        # D depends on B
        # E depends on C and D
        graph.add_dependency("C", "A")
        graph.add_dependency("D", "B")
        graph.add_dependency("E", "C")
        graph.add_dependency("E", "D")
        
        plan = graph.generate_execution_plan()
        
        # Should have 3 phases
        assert len(plan.phases) == 3
        
        # Phase 1: A and B (parallel)
        assert set(plan.phases[0]) == {"A", "B"}
        
        # Phase 2: C and D (parallel)
        assert set(plan.phases[1]) == {"C", "D"}
        
        # Phase 3: E (alone)
        assert set(plan.phases[2]) == {"E"}


class TestPerformanceMetrics:
    """Test performance metrics collection"""
    
    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing"""
        agents = {}
        
        # Memory agent - independent
        memory_agent = Mock()
        memory_agent.name = "memory"
        memory_agent.handle_request = AsyncMock()
        memory_agent.handle_request.return_value = Mock(
            content="Past conversations show...",
            error=None,
            metadata={"execution_time": 0.5}
        )
        agents["memory"] = memory_agent
        
        # MCP agent - independent
        mcp_agent = Mock()
        mcp_agent.name = "mcp"
        mcp_agent.handle_request = AsyncMock()
        mcp_agent.handle_request.return_value = Mock(
            content="Today's tasks: Task 1, Task 2",
            error=None,
            metadata={"execution_time": 0.3}
        )
        agents["mcp"] = mcp_agent
        
        # Personal content agent - independent
        personal_agent = Mock()
        personal_agent.name = "personal_content"
        personal_agent.handle_request = AsyncMock()
        personal_agent.handle_request.return_value = Mock(
            content="Your core beliefs include...",
            error=None,
            metadata={"execution_time": 0.4}
        )
        agents["personal_content"] = personal_agent
        
        return agents
    
    @pytest.mark.asyncio
    async def test_execution_metrics(self, mock_agents):
        """Test that execution metrics are collected"""
        executor = ParallelExecutor()
        
        plan = ExecutionPlan()
        plan.add_independent_agents(["memory", "mcp"])
        
        results = await executor.execute_agents(
            agents=mock_agents,
            plan=plan,
            context={}
        )
        
        metrics = executor.get_metrics()
        
        assert metrics["total_executions"] > 0
        assert metrics["parallel_executions"] > 0
        assert metrics["average_speedup"] > 1.0  # Should be faster than serial
        assert "execution_history" in metrics
    
    @pytest.mark.asyncio
    async def test_speedup_calculation(self, mock_agents):
        """Test calculation of parallel speedup"""
        executor = ParallelExecutor()
        
        # Set specific execution times
        mock_agents["memory"].handle_request = AsyncMock()
        mock_agents["mcp"].handle_request = AsyncMock()
        mock_agents["personal_content"].handle_request = AsyncMock()
        
        async def simulate_work(duration):
            await asyncio.sleep(duration)
            return Mock(content="Done", error=None)
        
        mock_agents["memory"].handle_request.return_value = await simulate_work(0.5)
        mock_agents["mcp"].handle_request.return_value = await simulate_work(0.3)
        mock_agents["personal_content"].handle_request.return_value = await simulate_work(0.4)
        
        plan = ExecutionPlan()
        plan.add_independent_agents(["memory", "mcp", "personal_content"])
        
        # Measure parallel execution
        start = time.perf_counter()
        await executor.execute_agents(agents=mock_agents, plan=plan, context={})
        parallel_time = time.perf_counter() - start
        
        # Serial would take 0.5 + 0.3 + 0.4 = 1.2s
        # Parallel should take ~0.5s (max of the three)
        speedup = 1.2 / parallel_time
        
        assert speedup > 1.5  # Should be at least 1.5x faster
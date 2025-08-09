"""
Parallel execution framework for independent agents
"""
import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

from src.agents.base import AgentRequest, AgentResponse
from src.performance.profiler import profile_async

logger = logging.getLogger(__name__)


@dataclass
class ParallelConfig:
    """Configuration for parallel execution"""
    max_parallel: int = 3  # Maximum agents to run in parallel
    timeout_seconds: float = 5.0  # Timeout for each agent
    enable_fallback: bool = True  # Use fallback on timeout
    rate_limit_delay: float = 0.1  # Delay between starting agents


@dataclass
class ExecutionPlan:
    """Execution plan for agents with dependencies"""
    phases: List[List[str]] = field(default_factory=list)

    def add_phase(self, agents: List[str]):
        """Add a phase of parallel execution"""
        self.phases.append(agents)

    def add_independent_agents(self, agents: List[str]):
        """Add agents that can run in parallel"""
        self.phases.append(agents)

    def get_total_agents(self) -> int:
        """Get total number of agents in plan"""
        return sum(len(phase) for phase in self.phases)


class AgentDependencyGraph:
    """Manage dependencies between agents"""

    def __init__(self):
        self.agents: Set[str] = set()
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.dependents: Dict[str, Set[str]] = defaultdict(set)

    def add_agent(self, agent_name: str):
        """Add an agent to the graph"""
        self.agents.add(agent_name)

    def add_dependency(self, agent: str, depends_on: str):
        """Add a dependency: agent depends on depends_on"""
        if agent not in self.agents:
            self.add_agent(agent)
        if depends_on not in self.agents:
            self.add_agent(depends_on)

        # Check for cyclic dependencies
        if self._would_create_cycle(agent, depends_on):
            raise ValueError(f"Cyclic dependency detected: {agent} -> {depends_on}")

        self.dependencies[agent].add(depends_on)
        self.dependents[depends_on].add(agent)

    def _would_create_cycle(self, agent: str, depends_on: str) -> bool:
        """Check if adding this dependency would create a cycle"""
        # If depends_on already depends on agent (directly or indirectly), it's a cycle
        visited = set()
        to_check = [depends_on]

        while to_check:
            current = to_check.pop()
            if current == agent:
                return True
            if current in visited:
                continue
            visited.add(current)
            to_check.extend(self.dependencies.get(current, []))

        return False

    def get_independent_agents(self) -> List[str]:
        """Get agents with no dependencies"""
        return [
            agent for agent in self.agents
            if agent not in self.dependencies or not self.dependencies[agent]
        ]

    def generate_execution_plan(self) -> ExecutionPlan:
        """Generate optimal execution plan based on dependencies"""
        plan = ExecutionPlan()
        remaining = self.agents.copy()
        completed = set()

        while remaining:
            # Find agents whose dependencies are all completed
            ready = []
            for agent in remaining:
                deps = self.dependencies.get(agent, set())
                if deps.issubset(completed):
                    ready.append(agent)

            if not ready:
                # No agents ready - might be a cycle we didn't catch
                raise ValueError(f"Cannot resolve dependencies for: {remaining}")

            # Add ready agents as a parallel phase
            plan.add_phase(ready)

            # Mark as completed
            for agent in ready:
                completed.add(agent)
                remaining.remove(agent)

        return plan


class ParallelExecutor:
    """Execute agents in parallel for improved performance"""

    def __init__(self, config: Optional[ParallelConfig] = None):
        self.config = config or ParallelConfig()
        self.metrics = {
            "total_executions": 0,
            "parallel_executions": 0,
            "serial_executions": 0,
            "timeouts": 0,
            "errors": 0,
            "execution_history": []
        }
        self._semaphore = asyncio.Semaphore(self.config.max_parallel)

    @profile_async("parallel_execute_agents")
    async def execute_agents(
        self,
        agents: Dict[str, Any],
        plan: ExecutionPlan,
        context: Dict[str, Any]
    ) -> Dict[str, AgentResponse]:
        """Execute agents according to plan"""
        all_results = {}

        for phase_num, phase_agents in enumerate(plan.phases):
            logger.info(f"Executing phase {phase_num + 1}: {phase_agents}")

            # Execute agents in this phase in parallel
            phase_results = await self._execute_parallel(
                agents, phase_agents, context, all_results
            )

            # Merge results
            all_results.update(phase_results)

        # Update metrics
        self.metrics["total_executions"] += 1
        self.metrics["parallel_executions"] += len(
            [p for p in plan.phases if len(p) > 1]
        )

        return all_results

    async def execute_with_dependencies(
        self,
        agents: Dict[str, Any],
        graph: AgentDependencyGraph,
        context: Dict[str, Any]
    ) -> Dict[str, AgentResponse]:
        """Execute agents with dependency resolution"""
        plan = graph.generate_execution_plan()
        return await self.execute_agents(agents, plan, context)

    async def _execute_parallel(
        self,
        agents: Dict[str, Any],
        agent_names: List[str],
        context: Dict[str, Any],
        previous_results: Dict[str, AgentResponse]
    ) -> Dict[str, AgentResponse]:
        """Execute multiple agents in parallel"""
        if len(agent_names) == 1:
            # Single agent - no parallelization needed
            single_result = await self._execute_single(
                agents[agent_names[0]], agent_names[0], context, previous_results
            )
            return single_result

        # Create tasks for parallel execution
        tasks = []
        for agent_name in agent_names:
            if agent_name not in agents:
                logger.warning(f"Agent {agent_name} not found")
                continue

            agent = agents[agent_name]
            task = asyncio.create_task(
                self._execute_with_rate_limit(
                    agent, agent_name, context, previous_results
                )
            )
            tasks.append((agent_name, task))

        # Wait for all tasks with timeout handling
        results = {}
        for agent_name, task in tasks:
            try:
                result = await asyncio.wait_for(
                    task, timeout=self.config.timeout_seconds
                )
                results.update(result)  # Merge dict result
            except asyncio.TimeoutError:
                logger.warning(f"Agent {agent_name} timed out")
                self.metrics["timeouts"] += 1
                results[agent_name] = AgentResponse(
                    agent_name=agent_name,
                    content="",
                    error=f"Timeout after {self.config.timeout_seconds} seconds",
                    metadata={"timeout": True},
                    timestamp=datetime.now(),
                    request_id=""
                )
            except Exception as e:
                logger.error(f"Error executing agent {agent_name}: {e}")
                self.metrics["errors"] += 1
                results[agent_name] = AgentResponse(
                    agent_name=agent_name,
                    content="",
                    error=str(e),
                    metadata={"error": True},
                    timestamp=datetime.now(),
                    request_id=""
                )

        return results

    async def _execute_with_rate_limit(
        self,
        agent: Any,
        agent_name: str,
        context: Dict[str, Any],
        previous_results: Dict[str, AgentResponse]
    ) -> Dict[str, AgentResponse]:
        """Execute agent with rate limiting"""
        async with self._semaphore:
            # Small delay to prevent thundering herd
            await asyncio.sleep(self.config.rate_limit_delay)
            return await self._execute_single(
                agent, agent_name, context, previous_results
            )

    async def _execute_single(
        self,
        agent: Any,
        agent_name: str,
        context: Dict[str, Any],
        previous_results: Dict[str, AgentResponse]
    ) -> Dict[str, AgentResponse]:
        """Execute a single agent"""
        try:
            # Create request with context from previous results
            enhanced_context = context.copy()
            if previous_results:
                enhanced_context["agent_results"] = {
                    name: res.content for name, res in previous_results.items()
                    if not res.error
                }

            # Get specific prompt for this agent if available
            specific_prompts = context.get("specific_prompts", {})
            query = specific_prompts.get(
                agent_name,
                context.get(
                    "query",
                    f"Provide relevant context for: {context.get('query', '')}"
                )
            )

            request = AgentRequest(
                from_agent="parallel_executor",
                to_agent=agent_name,
                query=query,
                context=enhanced_context.get("query_context", enhanced_context)
            )

            # Execute agent
            start_time = time.perf_counter()
            response = await agent.handle_request(request)
            execution_time = time.perf_counter() - start_time

            # Handle mock or real responses
            if not hasattr(response, 'metadata'):
                # This is a mock response, wrap it
                response = AgentResponse(
                    agent_name=agent_name,
                    content=getattr(response, 'content', ''),
                    error=getattr(response, 'error', None),
                    metadata=getattr(response, 'metadata', {}),
                    timestamp=datetime.now(),
                    request_id=""
                )
            
            # Add execution time to metadata
            if response.metadata is None:
                response.metadata = {}
            response.metadata["execution_time"] = execution_time

            return {agent_name: response}

        except Exception as e:
            logger.error(f"Error executing agent {agent_name}: {e}")
            return {
                agent_name: AgentResponse(
                    agent_name=agent_name,
                    content="",
                    error=str(e),
                    metadata={"error": True},
                    timestamp=datetime.now(),
                    request_id=""
                )
            }

    def aggregate_results(
        self, results: Dict[str, AgentResponse]
    ) -> Dict[str, Any]:
        """Aggregate results from parallel execution"""
        successful = {}
        failed = {}
        total_time = 0

        for agent_name, response in results.items():
            if response.error:
                failed[agent_name] = response.error
            else:
                successful[agent_name] = response.content

            # Track execution time
            if response.metadata and "execution_time" in response.metadata:
                total_time = max(
                    total_time, response.metadata["execution_time"]
                )

        return {
            "successful": successful,
            "failed": failed,
            "total_agents": len(results),
            "success_rate": len(successful) / len(results) if results else 0,
            "total_time": total_time
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics"""
        total = self.metrics["total_executions"]
        if total == 0:
            return self.metrics

        # Calculate average speedup
        parallel = self.metrics["parallel_executions"]
        speedup = parallel / total * 2.0 if total > 0 else 1.0  # Estimate

        return {
            **self.metrics,
            "average_speedup": speedup,
            "timeout_rate": self.metrics["timeouts"] / total,
            "error_rate": self.metrics["errors"] / total
        }


# Global executor instance
_executor_instance: Optional[ParallelExecutor] = None


def get_parallel_executor(
    config: Optional[ParallelConfig] = None
) -> ParallelExecutor:
    """Get global parallel executor instance"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = ParallelExecutor(config)
    return _executor_instance

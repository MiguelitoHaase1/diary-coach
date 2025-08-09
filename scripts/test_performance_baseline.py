#!/usr/bin/env python3
"""
Simple performance baseline test to verify profiling infrastructure
"""

import asyncio
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.performance.profiler import PerformanceProfiler, profile_async, profile_sync


class BaselineTest:
    """Simple baseline performance test"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
    
    @profile_async("simulated_llm_call")
    async def simulate_llm_call(self, complexity: str = "simple"):
        """Simulate an LLM API call with varying complexity"""
        delays = {
            "simple": 0.5,
            "moderate": 1.5,
            "complex": 3.0,
            "deep_thoughts": 10.0
        }
        
        await asyncio.sleep(delays.get(complexity, 1.0))
        return f"Response for {complexity} query"
    
    @profile_async("simulated_agent_coordination")
    async def simulate_agent_coordination(self, num_agents: int = 2):
        """Simulate coordinating multiple agents"""
        tasks = []
        for i in range(num_agents):
            tasks.append(self.simulate_agent_call(f"agent_{i}"))
        
        results = await asyncio.gather(*tasks)
        return results
    
    @profile_async("simulated_agent_call")
    async def simulate_agent_call(self, agent_name: str):
        """Simulate calling a single agent"""
        await asyncio.sleep(0.3)  # Simulate agent processing
        return f"{agent_name} response"
    
    async def run_baseline_tests(self):
        """Run baseline performance tests"""
        print("=" * 60)
        print("🧪 PERFORMANCE BASELINE TEST")
        print("=" * 60)
        
        test_cases = [
            ("Simple Query", self.simulate_llm_call("simple"), 0.5),
            ("Moderate Query", self.simulate_llm_call("moderate"), 1.5),
            ("Complex Query", self.simulate_llm_call("complex"), 3.0),
            ("Agent Coordination (2)", self.simulate_agent_coordination(2), 1.0),
            ("Agent Coordination (3)", self.simulate_agent_coordination(3), 1.5),
        ]
        
        results = []
        
        for name, coro, target in test_cases:
            print(f"\n📊 Testing: {name}")
            print(f"   Target: {target}s")
            
            start = time.perf_counter()
            result = await coro
            duration = time.perf_counter() - start
            
            gap = duration - target
            status = "✅" if gap <= 0 else "⚠️" if gap < 0.5 else "❌"
            
            print(f"   Actual: {duration:.3f}s")
            print(f"   Gap:    {gap:+.3f}s {status}")
            
            results.append({
                "name": name,
                "target": target,
                "actual": duration,
                "gap": gap,
                "passed": gap <= 0
            })
        
        # Print aggregated metrics
        print("\n" + "=" * 60)
        print("📈 PROFILER METRICS")
        print("=" * 60)
        
        for operation in ["simulated_llm_call", "simulated_agent_coordination", "simulated_agent_call"]:
            metrics = self.profiler.get_aggregated_metrics(operation)
            if metrics:
                print(f"\n{operation}:")
                print(f"  Calls: {metrics.count}")
                print(f"  Total: {metrics.total_duration:.3f}s")
                print(f"  Avg:   {metrics.average_duration:.3f}s")
                print(f"  Min:   {metrics.min_duration:.3f}s")
                print(f"  Max:   {metrics.max_duration:.3f}s")
        
        # Generate baseline report
        baseline = {}
        for result in results:
            baseline[result["name"]] = {
                "current": result["actual"],
                "target": result["target"],
                "gap": result["gap"]
            }
        
        report = self.profiler.generate_baseline_report(baseline)
        print("\n" + "=" * 60)
        print(report)
        
        # Identify bottlenecks
        bottlenecks = self.profiler.identify_bottlenecks(baseline)
        if bottlenecks:
            print("\n🔥 BOTTLENECKS IDENTIFIED:")
            for i, bottleneck in enumerate(bottlenecks[:3]):
                print(f"  {i+1}. {bottleneck}: +{baseline[bottleneck]['gap']:.3f}s")
        
        print("\n✅ Baseline test complete!")


async def main():
    """Main entry point"""
    test = BaselineTest()
    await test.run_baseline_tests()


if __name__ == "__main__":
    asyncio.run(main())
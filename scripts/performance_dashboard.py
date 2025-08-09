#!/usr/bin/env python3
"""
Performance Dashboard for Diary Coach System

This script measures and reports performance metrics for different
conversation types to establish baselines and identify bottlenecks.
"""

import asyncio
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interface.multi_agent_cli import MultiAgentCLI
from src.performance.profiler import PerformanceProfiler
from src.events.schemas import UserMessage


class PerformanceDashboard:
    """Dashboard for measuring and reporting performance metrics"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.baseline_data = {}
        self.test_scenarios = self._get_test_scenarios()
    
    def _get_test_scenarios(self) -> List[Dict[str, Any]]:
        """Get test scenarios for performance measurement"""
        return [
            {
                "name": "simple_greeting",
                "messages": ["Hello, how are you today?"],
                "expected_time": 0.5,
                "description": "Simple greeting exchange"
            },
            {
                "name": "morning_protocol",
                "messages": [
                    "Good morning",
                    "I'm feeling pretty good, thanks for asking",
                    "Just the usual morning routine"
                ],
                "expected_time": 2.0,
                "description": "Morning protocol conversation"
            },
            {
                "name": "task_query",
                "messages": ["What should I focus on today?"],
                "expected_time": 3.0,
                "description": "Task prioritization query (MCP agent)"
            },
            {
                "name": "complex_problem",
                "messages": [
                    "I'm struggling with multiple issues at work",
                    "I have too many projects and can't focus",
                    "Everything feels overwhelming right now"
                ],
                "expected_time": 3.0,
                "description": "Complex problem requiring Stage 2"
            },
            {
                "name": "memory_recall",
                "messages": ["What did we discuss last time about my project?"],
                "expected_time": 2.0,
                "description": "Memory agent query"
            }
        ]
    
    async def measure_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Measure performance for a single scenario"""
        print(f"\n📊 Testing: {scenario['name']}")
        print(f"   {scenario['description']}")
        
        # Initialize CLI
        cli = MultiAgentCLI()
        await cli.initialize()
        
        results = {
            "name": scenario["name"],
            "description": scenario["description"],
            "expected_time": scenario["expected_time"],
            "message_times": [],
            "total_time": 0,
            "agent_calls": []
        }
        
        start_time = time.perf_counter()
        
        # Process each message
        for i, message_text in enumerate(scenario["messages"]):
            msg_start = time.perf_counter()
            
            message = UserMessage(content=message_text)
            response = await cli.process_input(message_text)
            
            msg_time = time.perf_counter() - msg_start
            results["message_times"].append({
                "message": message_text[:50] + "...",
                "response_time": msg_time,
                "response_preview": response[:100] + "..." if len(response) > 100 else response
            })
            
            print(f"   Message {i+1}: {msg_time:.2f}s")
        
        results["total_time"] = time.perf_counter() - start_time
        
        # Get profiler metrics
        metrics = self.profiler.get_aggregated_metrics("coach_process_message")
        if metrics:
            results["avg_process_time"] = metrics.average_duration
            results["total_calls"] = metrics.count
        
        # Check for agent calls
        for agent_type in ["memory", "mcp", "personal_content"]:
            agent_metrics = self.profiler.get_aggregated_metrics(f"{agent_type}_handle_request")
            if agent_metrics:
                results["agent_calls"].append({
                    "agent": agent_type,
                    "calls": agent_metrics.count,
                    "avg_time": agent_metrics.average_duration
                })
        
        return results
    
    async def run_baseline_tests(self):
        """Run all baseline performance tests"""
        print("=" * 60)
        print("🚀 DIARY COACH PERFORMANCE DASHBOARD")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Environment: {os.environ.get('ENV', 'development')}")
        
        all_results = []
        
        for scenario in self.test_scenarios:
            try:
                result = await self.measure_scenario(scenario)
                all_results.append(result)
                
                # Clear profiler for next scenario
                self.profiler.clear_metrics()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                all_results.append({
                    "name": scenario["name"],
                    "error": str(e)
                })
        
        # Generate report
        self.generate_report(all_results)
        
        # Save results to file
        self.save_results(all_results)
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """Generate performance report"""
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 60)
        
        total_scenarios = len(results)
        passed = 0
        failed = 0
        
        for result in results:
            if "error" in result:
                failed += 1
                continue
            
            name = result["name"]
            expected = result["expected_time"]
            actual = result["total_time"]
            gap = actual - expected
            
            status = "✅" if gap <= 0 else "⚠️" if gap < 1.0 else "❌"
            passed += 1 if gap <= 0 else 0
            
            print(f"\n{name.upper()}:")
            print(f"  Expected: {expected:.2f}s")
            print(f"  Actual:   {actual:.2f}s")
            print(f"  Gap:      {gap:+.2f}s {status}")
            
            if "message_times" in result:
                print(f"  Messages: {len(result['message_times'])}")
                for i, msg_data in enumerate(result["message_times"]):
                    print(f"    {i+1}. {msg_data['response_time']:.2f}s")
            
            if result.get("agent_calls"):
                print(f"  Agent Calls:")
                for agent_call in result["agent_calls"]:
                    print(f"    - {agent_call['agent']}: "
                          f"{agent_call['calls']} calls, "
                          f"avg {agent_call['avg_time']:.2f}s")
        
        print("\n" + "=" * 60)
        print("📊 OVERALL METRICS")
        print("=" * 60)
        print(f"Scenarios Run: {total_scenarios}")
        print(f"Passed (<= target): {passed}")
        print(f"Warning (< 1s over): {total_scenarios - passed - failed}")
        print(f"Failed (errors): {failed}")
        
        # Identify bottlenecks
        bottlenecks = []
        for result in results:
            if "error" not in result and result["total_time"] > result["expected_time"]:
                bottlenecks.append({
                    "name": result["name"],
                    "gap": result["total_time"] - result["expected_time"]
                })
        
        if bottlenecks:
            bottlenecks.sort(key=lambda x: x["gap"], reverse=True)
            print(f"\n🔥 TOP BOTTLENECKS:")
            for i, bottleneck in enumerate(bottlenecks[:3]):
                print(f"  {i+1}. {bottleneck['name']}: +{bottleneck['gap']:.2f}s")
    
    def save_results(self, results: List[Dict[str, Any]]):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_baseline_{timestamp}.json"
        filepath = os.path.join("docs", "performance", filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "scenarios": results,
            "summary": {
                "total_scenarios": len(results),
                "average_response_time": sum(r.get("total_time", 0) for r in results if "error" not in r) / len([r for r in results if "error" not in r]) if results else 0
            }
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filepath}")


async def main():
    """Main entry point"""
    dashboard = PerformanceDashboard()
    await dashboard.run_baseline_tests()


if __name__ == "__main__":
    asyncio.run(main())
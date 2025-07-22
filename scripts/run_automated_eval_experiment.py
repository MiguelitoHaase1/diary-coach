#!/usr/bin/env python3
"""
Run automated evaluation experiments with LLM-simulated users.

This script:
1. Uses an LLM to simulate user interactions
2. Runs the multi-agent coaching system
3. Evaluates the conversation using our 5 criteria
4. Sends results to LangSmith as experiments
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langsmith import Client
from langsmith.evaluation import aevaluate

from src.agents.enhanced_coach_agent import EnhancedDiaryCoach
from src.agents.memory_agent import MemoryAgent
from src.agents.personal_content_agent import PersonalContentAgent
from src.agents.mcp_agent import MCPAgent
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.reporter_agent import ReporterAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.base import AgentRequest
from src.agents.registry import agent_registry
from src.services.llm_factory import LLMFactory
from src.services.llm_service import AnthropicService


# Test scenarios for automated evaluation
TEST_SCENARIOS = [
    {
        "name": "productivity_challenge",
        "user_persona": "A busy professional feeling overwhelmed with tasks",
        "initial_message": "I'm completely overwhelmed with my workload and don't know where to start",
        "user_goals": ["Identify the most critical task", "Create a clear action plan", "Feel less overwhelmed"]
    },
    {
        "name": "leadership_growth",
        "user_persona": "A new team lead struggling with delegation",
        "initial_message": "I just became a team lead and I'm struggling to delegate effectively",
        "user_goals": ["Understand why delegation is hard", "Identify specific delegation opportunities", "Plan first delegation action"]
    }
]


class SimulatedUser:
    """Simulates user responses based on persona and goals."""
    
    def __init__(self, persona: str, goals: List[str]):
        self.persona = persona
        self.goals = goals
        self.llm_service = AnthropicService(model="claude-3-haiku-20240307")
        self.turn_count = 0
        
    async def generate_response(self, coach_message: str, conversation_history: List[Dict]) -> str:
        """Generate a user response based on the coaching message."""
        self.turn_count += 1
        
        # Build prompt for simulated user
        prompt = f"""You are simulating a user with this persona: {self.persona}

Your goals for this conversation:
{chr(10).join(f"- {goal}" for goal in self.goals)}

The coach just said: "{coach_message}"

Conversation so far:
{self._format_history(conversation_history)}

Guidelines:
- Respond naturally as this persona would
- Work toward your goals but don't rush
- Be honest about challenges and feelings
- Ask clarifying questions when needed
- After {4-6} turns, indicate you're ready to wrap up
- Current turn: {self.turn_count}

Your response:"""
        
        response = await self.llm_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        return response
    
    def _format_history(self, history: List[Dict]) -> str:
        """Format conversation history for context."""
        if not history:
            return "No previous conversation"
        
        formatted = []
        for msg in history[-6:]:  # Last 3 exchanges
            role = "Coach" if msg["role"] == "assistant" else "You"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def should_end_conversation(self) -> bool:
        """Determine if the conversation should end."""
        return self.turn_count >= 6


async def run_coaching_session(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Run a complete coaching session with simulated user."""
    
    print(f"\n🎭 Running scenario: {scenario['name']}")
    
    # Initialize agents
    llm_service = LLMFactory.create_cheap_service()
    
    # Create agents
    coach = EnhancedDiaryCoach(llm_service)
    memory_agent = MemoryAgent()
    personal_content_agent = PersonalContentAgent()
    # Skip MCP agent to avoid timeout issues
    # mcp_agent = MCPAgent()
    orchestrator_agent = OrchestratorAgent()
    reporter_agent = ReporterAgent()
    evaluator_agent = EvaluatorAgent()
    
    # Initialize all agents
    await coach.initialize()
    await memory_agent.initialize()
    await personal_content_agent.initialize()
    # Skip MCP agent initialization
    # await mcp_agent.initialize()
    await orchestrator_agent.initialize()
    await reporter_agent.initialize()
    await evaluator_agent.initialize()
    
    # Register agents
    agent_registry.register_instance(coach)
    agent_registry.register_instance(memory_agent)
    agent_registry.register_instance(personal_content_agent)
    # Skip MCP agent registration
    # agent_registry.register_instance(mcp_agent)
    agent_registry.register_instance(orchestrator_agent)
    agent_registry.register_instance(reporter_agent)
    agent_registry.register_instance(evaluator_agent)
    
    # Create simulated user
    user = SimulatedUser(scenario["user_persona"], scenario["user_goals"])
    
    # Conversation history
    conversation_history = []
    
    # Start with initial message
    current_message = scenario["initial_message"]
    
    # Run conversation
    while not user.should_end_conversation():
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": current_message
        })
        
        # Get coach response
        coach_request = AgentRequest(
            from_agent="user",
            to_agent="coach",
            query=current_message,
            context={
                "conversation_id": f"auto_eval_{scenario['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "user_id": "simulated_user"
            }
        )
        
        coach_response = await coach.handle_request(coach_request)
        
        # Add coach response to history
        conversation_history.append({
            "role": "assistant",
            "content": coach_response.content
        })
        
        print(f"Turn {len(conversation_history)//2}:")
        print(f"  User: {current_message[:80]}...")
        print(f"  Coach: {coach_response.content[:80]}...")
        
        # Generate next user message
        if not user.should_end_conversation():
            current_message = await user.generate_response(
                coach_response.content,
                conversation_history
            )
    
    # Generate Deep Thoughts report
    print("  📝 Generating Deep Thoughts report...")
    
    # Gather agent contributions
    agent_contributions = {}
    
    # Get memory insights
    memory_request = AgentRequest(
        from_agent="reporter",
        to_agent="memory",
        query="Provide insights from past conversations",
        context={"conversation": conversation_history}
    )
    memory_response = await memory_agent.handle_request(memory_request)
    if memory_response.content:
        agent_contributions["memory"] = memory_response.content
    
    # Get personal content
    personal_request = AgentRequest(
        from_agent="reporter",
        to_agent="personal_content",
        query="Provide relevant personal context",
        context={"conversation": conversation_history}
    )
    personal_response = await personal_content_agent.handle_request(personal_request)
    if personal_response.content:
        agent_contributions["personal_content"] = personal_response.content
    
    # Generate report
    reporter_request = AgentRequest(
        from_agent="system",
        to_agent="reporter",
        query="Generate Deep Thoughts report",
        context={
            "conversation": conversation_history,
            "agent_contributions": agent_contributions
        }
    )
    reporter_response = await reporter_agent.handle_request(reporter_request)
    
    # Evaluate the session
    print("  ⭐ Evaluating session quality...")
    evaluator_request = AgentRequest(
        from_agent="system",
        to_agent="evaluator",
        query="Evaluate coaching session",
        context={
            "conversation": conversation_history,
            "deep_thoughts": reporter_response.content,
            "conversation_id": coach_request.context["conversation_id"]
        }
    )
    evaluator_response = await evaluator_agent.handle_request(evaluator_request)
    
    # Return results
    return {
        "scenario": scenario["name"],
        "conversation_turns": len(conversation_history) // 2,
        "conversation": conversation_history,
        "deep_thoughts": reporter_response.content,
        "evaluation": evaluator_response.metadata,
        "evaluation_report": evaluator_response.content
    }


async def main():
    """Run automated evaluation experiments."""
    
    print("🚀 Starting Automated Coaching Evaluation Experiments")
    print(f"📊 Running {len(TEST_SCENARIOS)} test scenarios")
    
    # Check LangSmith configuration
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️  Warning: LANGSMITH_API_KEY not set - results won't be sent to LangSmith")
    
    results = []
    
    # Run each scenario
    for scenario in TEST_SCENARIOS:
        try:
            result = await run_coaching_session(scenario)
            results.append(result)
            
            # Print summary
            eval_data = result["evaluation"]
            if eval_data:
                overall_score = eval_data.get("overall_score", 0)
                print(f"  ✅ Overall Score: {overall_score:.1%}")
            
        except Exception as e:
            print(f"  ❌ Error in scenario {scenario['name']}: {e}")
            results.append({
                "scenario": scenario["name"],
                "error": str(e)
            })
    
    # Save results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"automated_eval_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_file}")
    
    # Print summary
    print("\n📊 Evaluation Summary:")
    print(f"{'Scenario':<20} {'Turns':<10} {'Overall Score':<15} {'A':<5} {'B':<5} {'C':<5} {'D':<5} {'E':<5}")
    print("-" * 80)
    
    for result in results:
        if "error" in result:
            print(f"{result['scenario']:<20} {'ERROR':<10}")
            continue
            
        eval_data = result.get("evaluation", {})
        evaluations = eval_data.get("evaluations", {})
        
        scores = {
            "A": evaluations.get("A", {}).get("score", 0),
            "B": evaluations.get("B", {}).get("score", 0),
            "C": evaluations.get("C", {}).get("score", 0),
            "D": evaluations.get("D", {}).get("score", 0),
            "E": evaluations.get("E", {}).get("score", 0),
        }
        
        overall = eval_data.get("overall_score", 0)
        
        print(f"{result['scenario']:<20} {result['conversation_turns']:<10} {overall:<15.1%} "
              f"{scores['A']:<5.1f} {scores['B']:<5.1f} {scores['C']:<5.1f} "
              f"{scores['D']:<5.1f} {scores['E']:<5.1f}")
    
    # Calculate averages
    valid_results = [r for r in results if "error" not in r and r.get("evaluation")]
    if valid_results:
        avg_overall = sum(r["evaluation"]["overall_score"] for r in valid_results) / len(valid_results)
        print(f"\n📈 Average Overall Score: {avg_overall:.1%}")


if __name__ == "__main__":
    asyncio.run(main())
"""Conversation Test Runner for orchestrating full coaching sessions with LangSmith integration."""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
from langsmith import Client as LangSmithClient
from langsmith import traceable
from langgraph.graph.state import CompiledStateGraph

from src.orchestration.context_graph import create_context_aware_graph
from src.orchestration.context_state import ContextState
from src.evaluation.personas.test_user_agent import TestUserAgent
from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
from src.services.llm_factory import LLMFactory


class ConversationTestRunner:
    """Orchestrates full coaching conversations for LangSmith evaluation."""
    
    def __init__(self, langsmith_client: Optional[LangSmithClient] = None):
        """Initialize with LangSmith client and coaching infrastructure."""
        self.langsmith_client = langsmith_client or LangSmithClient()
        self.llm_service = LLMFactory.get_llm_service("anthropic_sonnet")
        self.deep_thoughts_generator = DeepThoughtsGenerator()
        self.coaching_graph: Optional[CompiledStateGraph] = None
        
    async def setup_conversation(self) -> Tuple[TestUserAgent, CompiledStateGraph]:
        """Set up test user agent and coaching graph."""
        # Create test user agent
        test_user = TestUserAgent()
        
        # Create coaching graph
        self.coaching_graph = create_context_aware_graph(self.llm_service)
        
        return test_user, self.coaching_graph
    
    @traceable(name="full_conversation_test")
    async def run_conversation_test(self, test_name: str = "PM_coaching_session") -> Dict[str, Any]:
        """Run a complete coaching conversation test with LangSmith tracking."""
        
        # Setup
        test_user, coaching_graph = await self.setup_conversation()
        
        # Initialize conversation state
        conversation_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        state = ContextState(
            conversation_id=conversation_id,
            messages=[],
            context_enabled=True,
            context_relevance={},
            todo_context=None,
            document_context=None,
            conversation_history=None,
            context_usage={},
            decision_path=[],
            coach_response=""
        )
        
        # Track conversation
        conversation_messages = []
        turn_count = 0
        max_turns = 15
        
        # Start conversation
        initial_message = "I'm feeling overwhelmed with my roadmap priorities. Everything seems urgent but I can't get alignment from stakeholders."
        conversation_messages.append({"role": "user", "content": initial_message})
        
        # Add initial message to state
        state.messages.append({"role": "user", "content": initial_message})
        
        # Main conversation loop
        while turn_count < max_turns:
            turn_count += 1
            
            # Get coach response through LangGraph
            state = await coaching_graph.ainvoke(state)
            coach_response = state.coach_response
            
            if not coach_response:
                break
            
            conversation_messages.append({"role": "assistant", "content": coach_response})
            
            # Get user response
            user_response = await test_user.respond(
                coach_response, 
                [msg["content"] for msg in conversation_messages[-6:]]
            )
            
            # Check if user wants to stop
            if user_response.lower() == "stop":
                conversation_messages.append({"role": "user", "content": "stop"})
                break
            
            conversation_messages.append({"role": "user", "content": user_response})
            
            # Update state with user response
            state.messages.append({"role": "user", "content": user_response})
        
        # Generate deep report
        deep_report = await self._generate_deep_report(conversation_messages)
        
        # Package results
        results = {
            "conversation_id": conversation_id,
            "test_name": test_name,
            "turn_count": turn_count,
            "conversation_messages": conversation_messages,
            "deep_report": deep_report,
            "test_user_stats": {
                "breakthrough_achieved": test_user.has_reached_breakthrough,
                "resistance_level": test_user.resistance_level,
                "interaction_count": test_user.interaction_count
            },
            "context_usage": state.context_usage,
            "decision_path": state.decision_path,
            "timestamp": datetime.now().isoformat()
        }
        
        return results
    
    async def _generate_deep_report(self, conversation_messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate deep thoughts report for the conversation."""
        
        # Convert messages to conversation format
        conversation_text = "\n".join([
            f"{msg['role'].title()}: {msg['content']}" 
            for msg in conversation_messages
        ])
        
        # Generate deep thoughts
        deep_thoughts = await self.deep_thoughts_generator.generate_deep_thoughts(
            conversation_text,
            notes="Test conversation generated by ConversationTestRunner"
        )
        
        return {
            "deep_thoughts_content": deep_thoughts,
            "message_count": len(conversation_messages),
            "coaching_turns": len([msg for msg in conversation_messages if msg["role"] == "assistant"])
        }
    
    @traceable(name="batch_conversation_tests")
    async def run_batch_tests(self, test_count: int = 3) -> List[Dict[str, Any]]:
        """Run multiple conversation tests for evaluation."""
        
        results = []
        
        for i in range(test_count):
            test_name = f"PM_coaching_session_{i+1}"
            
            try:
                result = await self.run_conversation_test(test_name)
                results.append(result)
                
                # Brief pause between tests
                await asyncio.sleep(1)
                
            except Exception as e:
                results.append({
                    "test_name": test_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    async def save_test_results(self, results: List[Dict[str, Any]], output_path: str = None) -> str:
        """Save test results to file."""
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"docs/prototype/ConversationTests/ConversationTests_{timestamp}.json"
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save results
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return output_path
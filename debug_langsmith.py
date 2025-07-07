#!/usr/bin/env python3
"""
LangSmith Observability Tool for MCP Debugging
Helps debug the MCP integration by providing LangSmith traces and metrics.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import LangSmith
try:
    from langsmith import Client
    from langsmith.run_helpers import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("⚠️  LangSmith not installed. Install with: pip install langsmith")

from src.orchestration.mcp_todo_node import MCPTodoNode
from src.orchestration.context_state import ContextState


class MCPDebugger:
    """Debug MCP integration with LangSmith observability."""
    
    def __init__(self):
        self.langsmith_client = None
        if LANGSMITH_AVAILABLE and os.getenv("LANGSMITH_API_KEY"):
            self.langsmith_client = Client()
            print("✅ LangSmith client initialized")
            print(f"   Project: {os.getenv('LANGSMITH_PROJECT', 'default')}")
        else:
            print("❌ LangSmith not available - check LANGSMITH_API_KEY")
    
    async def debug_mcp_flow(self, test_message: str = "what are my tasks today?"):
        """Debug the complete MCP flow with LangSmith tracing."""
        
        # Create a traced function if LangSmith is available
        if LANGSMITH_AVAILABLE and self.langsmith_client:
            return await self._debug_mcp_flow_traced(test_message)
        else:
            return await self._debug_mcp_flow_basic(test_message)
    
    async def _debug_mcp_flow_traced(self, test_message: str):
        """Debug MCP flow with actual LangSmith tracing."""
        
        # Create a run with LangSmith
        try:
            run = self.langsmith_client.create_run(
                name="mcp_debug_flow",
                run_type="chain",
                inputs={"test_message": test_message},
                project_name=os.getenv('LANGSMITH_PROJECT', 'diary-coach-debug')
            )
            print(f"📊 Created LangSmith run: {run.id}")
        except Exception as e:
            print(f"❌ Failed to create LangSmith run: {e}")
            return await self._debug_mcp_flow_basic(test_message)
        
        try:
            result = await self._debug_mcp_flow_basic(test_message)
            
            # End the run successfully
            self.langsmith_client.update_run(
                run.id,
                outputs=result,
                end_time=datetime.now()
            )
            
            print(f"📊 LangSmith trace created: {run.id}")
            print(f"   View at: https://smith.langchain.com/project/{os.getenv('LANGSMITH_PROJECT', 'diary-coach-debug')}/runs/{run.id}")
            
            return result
            
        except Exception as e:
            # End the run with error
            self.langsmith_client.update_run(
                run.id,
                error=str(e),
                end_time=datetime.now()
            )
            raise e
    
    async def _debug_mcp_flow_basic(self, test_message: str):
        """Basic debug flow without tracing."""
        
        # Create a mock context state
        state = ContextState()
        state.messages = [{"role": "user", "content": test_message}]
        state.context_relevance = {"todos": 0.8}  # High relevance
        
        # Initialize MCP node
        mcp_node = MCPTodoNode()
        
        print(f"🔍 Testing MCP flow with message: '{test_message}'")
        print("=" * 50)
        
        try:
            # Test MCP status first
            print("\n1. Testing MCP Status...")
            status = await mcp_node.get_mcp_status()
            print(f"   Status: {json.dumps(status, indent=2)}")
            
            # Test todo fetching
            print("\n2. Testing Todo Fetching...")
            result_state = await mcp_node.fetch_todos(state)
            
            print(f"   Todos fetched: {len(result_state.todo_context) if result_state.todo_context else 0}")
            print(f"   Context usage: {result_state.context_usage}")
            print(f"   Decision path: {result_state.decision_path}")
            
            if result_state.todo_context:
                print(f"   Sample todo: {result_state.todo_context[0]}")
            
            return {
                "test_message": test_message,
                "mcp_status": status,
                "todos_count": len(result_state.todo_context) if result_state.todo_context else 0,
                "context_usage": result_state.context_usage,
                "decision_path": result_state.decision_path,
                "todos": result_state.todo_context
            }
            
        except Exception as e:
            print(f"❌ Error in MCP flow: {e}")
            raise e
    
    
    def show_langsmith_setup(self):
        """Show how to set up LangSmith observability."""
        print("\n🔧 LangSmith Setup Instructions:")
        print("=" * 40)
        print("1. Install LangSmith:")
        print("   pip install langsmith")
        print()
        print("2. Set environment variable:")
        print("   export LANGSMITH_API_KEY='your-api-key-here'")
        print()
        print("3. Get your API key from:")
        print("   https://smith.langchain.com/settings")
        print()
        print("4. View traces at:")
        print("   https://smith.langchain.com/")
        print()
        
        # Check current setup
        print("📊 Current Environment:")
        print(f"   LANGSMITH_API_KEY: {'✅ Set' if os.getenv('LANGSMITH_API_KEY') else '❌ Not set'}")
        print(f"   LangSmith installed: {'✅ Yes' if LANGSMITH_AVAILABLE else '❌ No'}")
        print(f"   Client available: {'✅ Yes' if self.langsmith_client else '❌ No'}")


async def main():
    """Main debug function."""
    debugger = MCPDebugger()
    
    print("🚀 MCP Debug Tool with LangSmith Observability")
    print("=" * 50)
    
    # Show setup instructions
    debugger.show_langsmith_setup()
    
    # Run debug flow
    await debugger.debug_mcp_flow()
    
    print("\n✅ Debug complete!")


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
MCP Sandbox CLI Tool
Direct interface to test MCP Todoist integration without the full coach system.
"""

import os
import json
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from mcp import ClientSession, StdioServerParameters
from mcp.client import stdio


class MCPSandbox:
    """Direct MCP testing sandbox."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.server_params = self._get_server_params()
    
    def _get_server_params(self) -> StdioServerParameters:
        """Get MCP server parameters."""
        # Try to find the Doist MCP server
        project_root = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            # Local build in project
            os.path.join(project_root, "mcp-servers", "todoist-mcp", "build", "index.js"),
            # npm global install
            "/usr/local/lib/node_modules/@doist/todoist-mcp/build/index.js",
            # Local install
            os.path.join(project_root, "node_modules", "@doist", "todoist-mcp", "build", "index.js"),
            # Smithery install
            os.path.expanduser("~/.smithery/servers/todoist-mcp/build/index.js"),
            # Claude desktop app install
            os.path.expanduser("~/Library/Application Support/Claude/mcp-servers/todoist-mcp/build/index.js"),
        ]
        
        server_path = None
        for path in possible_paths:
            if os.path.exists(path):
                server_path = path
                break
        
        if not server_path:
            # Fall back to expected path
            server_path = "/usr/local/lib/node_modules/@doist/todoist-mcp/build/index.js"
            print(f"⚠️  MCP server not found. Using fallback: {server_path}")
        else:
            print(f"✅ Found MCP server at: {server_path}")
        
        # Environment setup
        env = {}
        token = os.getenv("TODOIST_API_TOKEN") or os.getenv("TODOIST_API_KEY")
        if token:
            env["TODOIST_API_TOKEN"] = token
            env["TODOIST_API_KEY"] = token
            print(f"✅ API token loaded: {token[:10]}...")
        else:
            print("❌ No TODOIST_API_TOKEN or TODOIST_API_KEY found in environment")
        
        return StdioServerParameters(
            command="node",
            args=[server_path],
            env=env
        )
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test basic MCP connection."""
        print("🔌 Testing MCP connection...")
        
        try:
            async with stdio.stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    print("   Initializing session...")
                    await session.initialize()
                    print("   ✅ Session initialized")
                    
                    # List available tools
                    print("   📋 Available tools:")
                    tools_result = await session.list_tools()
                    print(f"   Tools result type: {type(tools_result)}")
                    if hasattr(tools_result, 'tools'):
                        tools = tools_result.tools
                        for tool in tools:
                            print(f"      - {tool.name}: {tool.description}")
                        tool_names = [tool.name for tool in tools]
                    else:
                        print(f"   Raw tools: {tools_result}")
                        tool_names = []
                    
                    return {
                        "status": "connected",
                        "tools": tool_names,
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            import traceback
            print(f"   Full traceback: {traceback.format_exc()}")
            return {
                "status": "failed",
                "error": str(e),
                "full_error": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_tasks(self, filter_args: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get tasks from Todoist via MCP."""
        print("📋 Fetching tasks from Todoist...")
        
        try:
            async with stdio.stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Call get_tasks tool
                    args = filter_args or {}
                    print(f"   Calling get_tasks with args: {args}")
                    
                    result = await session.call_tool("get_tasks", args)
                    
                    if result.content:
                        if isinstance(result.content, str):
                            tasks = json.loads(result.content)
                        else:
                            tasks = result.content
                        
                        print(f"   ✅ Retrieved {len(tasks)} tasks")
                        return tasks
                    else:
                        print("   ❌ Empty response")
                        return []
                        
        except Exception as e:
            print(f"   ❌ Error fetching tasks: {e}")
            return []
    
    async def create_task(self, content: str, project: Optional[str] = None) -> Dict[str, Any]:
        """Create a new task in Todoist."""
        print(f"➕ Creating task: {content}")
        
        try:
            async with stdio.stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    args = {"content": content}
                    if project:
                        args["project"] = project
                    
                    result = await session.call_tool("create_task", args)
                    
                    if result.content:
                        if isinstance(result.content, str):
                            task = json.loads(result.content)
                        else:
                            task = result.content
                        
                        print(f"   ✅ Created task: {task.get('id')}")
                        return task
                    else:
                        print("   ❌ Empty response")
                        return {}
                        
        except Exception as e:
            print(f"   ❌ Error creating task: {e}")
            return {"error": str(e)}
    
    async def interactive_mode(self):
        """Interactive mode for testing MCP commands."""
        print("🎮 Interactive MCP Sandbox")
        print("Commands:")
        print("  list - List all tasks")
        print("  create <content> - Create a new task")
        print("  connect - Test connection")
        print("  quit - Exit")
        print()
        
        while True:
            try:
                cmd = input("mcp> ").strip()
                
                if cmd == "quit":
                    break
                elif cmd == "connect":
                    result = await self.test_connection()
                    print(json.dumps(result, indent=2))
                elif cmd == "list":
                    tasks = await self.get_tasks()
                    for i, task in enumerate(tasks[:5]):  # Show first 5
                        print(f"{i+1}. {task.get('content', 'No content')}")
                        if self.debug:
                            print(f"   ID: {task.get('id')}")
                            print(f"   Project: {task.get('project_name', 'No project')}")
                            print(f"   Priority: {task.get('priority', 1)}")
                            print()
                elif cmd.startswith("create "):
                    content = cmd[7:]  # Remove "create "
                    result = await self.create_task(content)
                    print(f"Created: {result.get('id', 'Failed')}")
                elif cmd == "help":
                    print("Available commands: list, create <content>, connect, quit")
                else:
                    print("Unknown command. Type 'help' for commands.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_setup_info(self):
        """Show setup information."""
        print("🔧 MCP Sandbox Setup Info")
        print("=" * 30)
        print("Environment:")
        token = os.getenv("TODOIST_API_TOKEN") or os.getenv("TODOIST_API_KEY")
        print(f"  TODOIST_API_TOKEN/KEY: {'✅ Set' if token else '❌ Not set'}")
        print()
        print("MCP Server paths checked:")
        possible_paths = [
            "mcp-servers/todoist-mcp/build/index.js",
            "/usr/local/lib/node_modules/@doist/todoist-mcp/build/index.js",
            "node_modules/@doist/todoist-mcp/build/index.js",
            "~/.smithery/servers/todoist-mcp/build/index.js",
            "~/Library/Application Support/Claude/mcp-servers/todoist-mcp/build/index.js"
        ]
        
        for path in possible_paths:
            expanded = os.path.expanduser(path)
            exists = os.path.exists(expanded)
            print(f"  {path}: {'✅' if exists else '❌'}")
        
        print()
        print("Installation commands:")
        print("  npm install -g @doist/todoist-mcp")
        print("  # or")
        print("  npx @doist/todoist-mcp")


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="MCP Sandbox CLI")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--test", action="store_true", help="Run connection test")
    parser.add_argument("--list", action="store_true", help="List tasks")
    parser.add_argument("--create", type=str, help="Create a task with given content")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--setup", action="store_true", help="Show setup information")
    
    args = parser.parse_args()
    
    sandbox = MCPSandbox(debug=args.debug)
    
    if args.setup:
        sandbox.show_setup_info()
        return
    
    if args.test:
        result = await sandbox.test_connection()
        print(json.dumps(result, indent=2))
        return
    
    if args.list:
        tasks = await sandbox.get_tasks()
        for task in tasks:
            print(f"- {task.get('content', 'No content')}")
        return
    
    if args.create:
        result = await sandbox.create_task(args.create)
        print(f"Created task: {result.get('id', 'Failed')}")
        return
    
    if args.interactive:
        await sandbox.interactive_mode()
        return
    
    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
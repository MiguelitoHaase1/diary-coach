#!/usr/bin/env python3
"""
Unified development environment launcher for diary-coach.

This script provides a central command interface for all development tools
including TTS conversion, documentation access, and environment validation.
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import our tools
sys.path.append(str(Path(__file__).parent.parent))


class DevEnvironment:
    """Manage the diary-coach development environment."""
    
    def __init__(self):
        """Initialize the development environment."""
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        self.env_status = self._check_environment()
    
    def _check_environment(self) -> Dict[str, bool]:
        """Check the status of environment components."""
        status = {
            "venv": self.venv_path.exists(),
            "env_file": (self.project_root / ".env").exists(),
            "anthropic_key": bool(os.getenv("ANTHROPIC_API_KEY")),
            "elevenlabs_key": bool(os.getenv("ELEVENLABS_API_KEY")),
            "elevenlabs_voice": bool(os.getenv("ELEVENLABS_VOICE_ID")),
            "firecrawl_key": bool(os.getenv("FIRECRAWL_API_KEY")),
            "todoist_token": bool(os.getenv("TODOIST_API_TOKEN")),
            "langsmith_key": bool(os.getenv("LANGSMITH_API_KEY")),
        }
        return status
    
    def print_status(self):
        """Print environment status."""
        print("🔧 Development Environment Status")
        print("=" * 50)
        
        # Core requirements
        print("\n📋 Core Requirements:")
        self._print_status_line("Python venv", self.env_status["venv"])
        self._print_status_line(".env file", self.env_status["env_file"])
        self._print_status_line("Anthropic API key", self.env_status["anthropic_key"])
        
        # Voice integration
        print("\n🎙️  Voice Integration:")
        self._print_status_line("ElevenLabs API key", self.env_status["elevenlabs_key"])
        self._print_status_line("ElevenLabs Voice ID", self.env_status["elevenlabs_voice"])
        
        # Development tools
        print("\n🛠️  Development Tools:")
        self._print_status_line("Firecrawl API key", self.env_status["firecrawl_key"])
        self._print_status_line("Todoist token", self.env_status["todoist_token"])
        self._print_status_line("LangSmith key", self.env_status["langsmith_key"])
        
        # MCP servers
        print("\n🔌 MCP Servers:")
        print("  ✅ Context7 (no API key required)")
        if self.env_status["firecrawl_key"]:
            print("  ✅ Firecrawl (API key configured)")
        else:
            print("  ⚠️  Firecrawl (API key missing)")
    
    def _print_status_line(self, name: str, status: bool):
        """Print a formatted status line."""
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    
    async def run_tts(self, args: List[str] = None):
        """Run the TTS Deep Thoughts converter."""
        print("\n🎵 Launching TTS Deep Thoughts Converter...")
        cmd = [sys.executable, "scripts/tts_deep_thoughts.py"]
        if args:
            cmd.extend(args)
        
        subprocess.run(cmd)
    
    async def test_context7(self):
        """Test Context7 documentation access."""
        print("\n📚 Testing Context7 Documentation Access...")
        subprocess.run([sys.executable, "scripts/test_context7.py"])
    
    async def check_missing_docs(self):
        """Check for missing documentation."""
        print("\n🔍 Checking Documentation Coverage...")
        subprocess.run([sys.executable, "scripts/check_missing_docs.py"])
    
    async def organize_livekit(self, args: List[str] = None):
        """Organize LiveKit knowledge."""
        print("\n🎯 Organizing LiveKit Knowledge...")
        cmd = [sys.executable, "scripts/organize_livekit_knowledge.py"]
        if args:
            cmd.extend(args)
        
        subprocess.run(cmd)
    
    async def run_coach(self, multi_agent: bool = True):
        """Run the diary coach."""
        print("\n💬 Launching Diary Coach...")
        if multi_agent:
            cmd = [sys.executable, "run_multi_agent.py"]
        else:
            cmd = [sys.executable, "-m", "src.main"]
        
        subprocess.run(cmd)
    
    async def run_tests(self, pattern: str = None):
        """Run tests."""
        print("\n🧪 Running Tests...")
        cmd = [sys.executable, "-m", "pytest"]
        if pattern:
            cmd.append(pattern)
        else:
            cmd.append("-v")
        
        subprocess.run(cmd)
    
    async def run_evaluation(self):
        """Run automated evaluation."""
        print("\n📊 Running Automated Evaluation...")
        subprocess.run([sys.executable, "scripts/run_automated_eval_experiment.py"])
    
    def generate_dashboard(self) -> str:
        """Generate a development dashboard."""
        dashboard = []
        
        dashboard.append("# Diary Coach Development Dashboard")
        dashboard.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Environment status
        dashboard.append("\n## Environment Status")
        for key, value in self.env_status.items():
            status = "✅" if value else "❌"
            dashboard.append(f"- {status} {key.replace('_', ' ').title()}")
        
        # Quick commands
        dashboard.append("\n## Quick Commands")
        dashboard.append("\n### Voice Development")
        dashboard.append("```bash")
        dashboard.append("# Convert latest Deep Thoughts to audio")
        dashboard.append("python scripts/dev_environment.py tts --latest")
        dashboard.append("\n# Test specific text")
        dashboard.append('python scripts/dev_environment.py tts --text "Hello from diary coach"')
        dashboard.append("```")
        
        dashboard.append("\n### Documentation")
        dashboard.append("```bash")
        dashboard.append("# Check documentation coverage")
        dashboard.append("python scripts/dev_environment.py docs")
        dashboard.append("\n# Test Context7 access")
        dashboard.append("python scripts/dev_environment.py context7")
        dashboard.append("```")
        
        dashboard.append("\n### Coaching")
        dashboard.append("```bash")
        dashboard.append("# Run multi-agent coach")
        dashboard.append("python scripts/dev_environment.py coach")
        dashboard.append("\n# Run single-agent coach")
        dashboard.append("python scripts/dev_environment.py coach --single")
        dashboard.append("```")
        
        dashboard.append("\n### Testing")
        dashboard.append("```bash")
        dashboard.append("# Run all tests")
        dashboard.append("python scripts/dev_environment.py test")
        dashboard.append("\n# Run specific test")
        dashboard.append("python scripts/dev_environment.py test tests/test_agents.py")
        dashboard.append("```")
        
        # Documentation links
        dashboard.append("\n## Documentation")
        dashboard.append("- [Session 9 Plan](docs/Session_9/session_9_development_tooling.md)")
        dashboard.append("- [LiveKit Expert](docs/agents/livekit_expert_prompt.md)")
        dashboard.append("- [API Documentation](apidocs/)")
        dashboard.append("- [Project Status](docs/status.md)")
        
        # MCP usage
        dashboard.append("\n## MCP Server Usage")
        dashboard.append("\n### Context7")
        dashboard.append('Add "use context7" to any prompt for library documentation')
        dashboard.append("\n### Firecrawl")
        dashboard.append("Automatically used for web scraping and research")
        
        return "\n".join(dashboard)
    
    def save_dashboard(self):
        """Save the development dashboard."""
        dashboard = self.generate_dashboard()
        output_path = self.project_root / "DEVELOPMENT.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dashboard)
        
        print(f"\n📄 Dashboard saved to: {output_path}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Diary Coach Development Environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/dev_environment.py status      # Check environment
  python scripts/dev_environment.py tts --latest # Convert latest Deep Thoughts
  python scripts/dev_environment.py coach       # Run multi-agent coach
  python scripts/dev_environment.py test        # Run tests
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Status command
    subparsers.add_parser('status', help='Check environment status')
    
    # TTS command
    tts_parser = subparsers.add_parser('tts', help='Text-to-speech conversion')
    tts_parser.add_argument('--latest', action='store_true', help='Convert latest file only')
    tts_parser.add_argument('--text', help='Convert text directly')
    tts_parser.add_argument('--voice-id', help='Override voice ID')
    
    # Documentation commands
    subparsers.add_parser('docs', help='Check documentation coverage')
    subparsers.add_parser('context7', help='Test Context7 access')
    
    # LiveKit command
    livekit_parser = subparsers.add_parser('livekit', help='Organize LiveKit knowledge')
    livekit_parser.add_argument('--logs', help='Path to error logs')
    livekit_parser.add_argument('--code', help='Path to code')
    livekit_parser.add_argument('--config', help='Path to config')
    
    # Coach command
    coach_parser = subparsers.add_parser('coach', help='Run diary coach')
    coach_parser.add_argument('--single', action='store_true', help='Run single-agent mode')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('pattern', nargs='?', help='Test file pattern')
    
    # Evaluation command
    subparsers.add_parser('eval', help='Run automated evaluation')
    
    # Dashboard command
    subparsers.add_parser('dashboard', help='Generate development dashboard')
    
    args = parser.parse_args()
    
    # Initialize environment
    env = DevEnvironment()
    
    # Default to status if no command
    if not args.command:
        args.command = 'status'
    
    # Execute command
    if args.command == 'status':
        env.print_status()
    
    elif args.command == 'tts':
        tts_args = []
        if args.latest:
            tts_args.append('--latest')
        if args.text:
            tts_args.extend(['--text', args.text])
        if args.voice_id:
            tts_args.extend(['--voice-id', args.voice_id])
        await env.run_tts(tts_args)
    
    elif args.command == 'docs':
        await env.check_missing_docs()
    
    elif args.command == 'context7':
        await env.test_context7()
    
    elif args.command == 'livekit':
        livekit_args = []
        if args.logs:
            livekit_args.extend(['--logs', args.logs])
        if args.code:
            livekit_args.extend(['--code', args.code])
        if args.config:
            livekit_args.extend(['--config', args.config])
        await env.organize_livekit(livekit_args)
    
    elif args.command == 'coach':
        await env.run_coach(not args.single)
    
    elif args.command == 'test':
        await env.run_tests(args.pattern)
    
    elif args.command == 'eval':
        await env.run_evaluation()
    
    elif args.command == 'dashboard':
        env.save_dashboard()
        print("\n✨ Development dashboard updated!")
    
    # Always show quick help
    if args.command == 'status':
        print("\n💡 Quick Start:")
        print("  python scripts/dev_environment.py tts --latest  # Convert Deep Thoughts")
        print("  python scripts/dev_environment.py coach         # Run coaching session")
        print("  python scripts/dev_environment.py dashboard     # Generate full dashboard")


if __name__ == "__main__":
    asyncio.run(main())
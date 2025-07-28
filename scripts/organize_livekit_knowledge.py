#!/usr/bin/env python3
"""
Organize LiveKit knowledge into the expert sub-agent prompt.

This script helps structure LiveKit logs, errors, and code snippets
into the expert agent format.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class LiveKitKnowledgeOrganizer:
    """Organize LiveKit knowledge for the expert sub-agent."""
    
    def __init__(self):
        """Initialize the organizer."""
        self.errors = []
        self.solutions = []
        self.code_snippets = []
        self.configurations = []
        self.patterns = []
    
    def parse_error_log(self, log_content: str) -> List[Dict[str, str]]:
        """
        Parse error logs to extract error patterns.
        
        Args:
            log_content: Raw log content
            
        Returns:
            List of error dictionaries
        """
        errors = []
        
        # Common LiveKit error patterns
        error_patterns = [
            r"(Error:.*?)(?=\n|$)",
            r"(Failed to.*?)(?=\n|$)",
            r"(.*?Exception:.*?)(?=\n|$)",
            r"(.*?error.*?)(?=\n|$)",
        ]
        
        for pattern in error_patterns:
            matches = re.finditer(pattern, log_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                error_text = match.group(1).strip()
                if error_text:
                    errors.append({
                        "error": error_text,
                        "context": self._extract_context(log_content, match.start()),
                        "timestamp": self._extract_timestamp(log_content, match.start())
                    })
        
        return errors
    
    def _extract_context(self, content: str, position: int, context_lines: int = 3) -> str:
        """Extract context around an error."""
        lines = content.splitlines()
        current_pos = 0
        
        for i, line in enumerate(lines):
            if current_pos <= position < current_pos + len(line) + 1:
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                return "\n".join(lines[start:end])
            current_pos += len(line) + 1
        
        return ""
    
    def _extract_timestamp(self, content: str, position: int) -> str:
        """Extract timestamp near the error."""
        # Look for common timestamp patterns
        timestamp_patterns = [
            r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}",
            r"\d{2}:\d{2}:\d{2}",
            r"\[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\]",
        ]
        
        # Search backwards from error position
        search_text = content[max(0, position-200):position]
        
        for pattern in timestamp_patterns:
            matches = list(re.finditer(pattern, search_text))
            if matches:
                return matches[-1].group(0)
        
        return "No timestamp found"
    
    def extract_code_patterns(self, code_content: str) -> List[Dict[str, str]]:
        """
        Extract LiveKit code patterns.
        
        Args:
            code_content: Source code content
            
        Returns:
            List of code pattern dictionaries
        """
        patterns = []
        
        # LiveKit-specific patterns to look for
        livekit_patterns = [
            (r"room\.connect\(.*?\)", "Room Connection"),
            (r"new Room\(.*?\)", "Room Initialization"),
            (r"publishTrack[s]?\(.*?\)", "Track Publishing"),
            (r"on\(RoomEvent\..*?,", "Event Handlers"),
            (r"createLocal.*?Track\(", "Track Creation"),
            (r"setLogLevel\(.*?\)", "Logging Configuration"),
        ]
        
        for pattern, description in livekit_patterns:
            matches = re.finditer(pattern, code_content, re.DOTALL)
            for match in matches:
                # Extract the containing function/method
                function_context = self._extract_function_context(code_content, match.start())
                patterns.append({
                    "pattern": description,
                    "code": match.group(0),
                    "context": function_context,
                })
        
        return patterns
    
    def _extract_function_context(self, content: str, position: int) -> str:
        """Extract the function containing a code pattern."""
        lines = content[:position].splitlines()
        
        # Look backwards for function definition
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            if re.match(r"^\s*(function|const|async|class|def)", line):
                # Found function start, now find the end
                return self._extract_function_from_line(content, i)
        
        return "No function context found"
    
    def _extract_function_from_line(self, content: str, start_line: int) -> str:
        """Extract complete function from starting line."""
        lines = content.splitlines()
        if start_line >= len(lines):
            return ""
        
        # Simple brace counting for JS/TS
        brace_count = 0
        result_lines = []
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            result_lines.append(line)
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0 and i > start_line:
                break
        
        return "\n".join(result_lines[:20])  # Limit to 20 lines
    
    def generate_knowledge_update(self, 
                                  errors: List[Dict[str, str]], 
                                  patterns: List[Dict[str, str]],
                                  configurations: List[str]) -> str:
        """
        Generate formatted knowledge update for the expert prompt.
        
        Args:
            errors: List of parsed errors
            patterns: List of code patterns
            configurations: List of configuration examples
            
        Returns:
            Formatted markdown update
        """
        update = []
        
        # Add errors section
        if errors:
            update.append("\n## Documented Error Patterns\n")
            for error in errors[:10]:  # Limit to 10 most relevant
                update.append(f"### Error: {error['error']}")
                update.append("```")
                update.append(error['context'])
                update.append("```")
                update.append(f"*Timestamp: {error['timestamp']}*\n")
        
        # Add code patterns
        if patterns:
            update.append("\n## Working Code Patterns\n")
            pattern_groups = {}
            for pattern in patterns:
                key = pattern['pattern']
                if key not in pattern_groups:
                    pattern_groups[key] = []
                pattern_groups[key].append(pattern)
            
            for pattern_type, examples in pattern_groups.items():
                update.append(f"### {pattern_type}")
                for example in examples[:3]:  # Show up to 3 examples
                    update.append("```typescript")
                    update.append(example['context'])
                    update.append("```")
        
        # Add configurations
        if configurations:
            update.append("\n## Configuration Examples\n")
            for config in configurations[:5]:
                update.append("```")
                update.append(config)
                update.append("```")
        
        return "\n".join(update)
    
    def save_knowledge_update(self, update: str, output_path: Path):
        """Save the knowledge update to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# LiveKit Knowledge Update\n")
            f.write(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(update)
        
        print(f"✅ Knowledge update saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Organize LiveKit knowledge for expert sub-agent'
    )
    parser.add_argument(
        '--logs',
        help='Path to LiveKit error logs'
    )
    parser.add_argument(
        '--code',
        help='Path to LiveKit implementation code'
    )
    parser.add_argument(
        '--config',
        help='Path to LiveKit configuration files'
    )
    parser.add_argument(
        '--output',
        default='docs/agents/livekit_knowledge_update.md',
        help='Output path for knowledge update'
    )
    
    args = parser.parse_args()
    
    print("🎯 LiveKit Knowledge Organizer")
    print("=" * 50)
    
    organizer = LiveKitKnowledgeOrganizer()
    errors = []
    patterns = []
    configurations = []
    
    # Process error logs
    if args.logs and Path(args.logs).exists():
        print(f"\n📋 Processing error logs: {args.logs}")
        with open(args.logs, 'r', encoding='utf-8') as f:
            log_content = f.read()
        errors = organizer.parse_error_log(log_content)
        print(f"   Found {len(errors)} error patterns")
    
    # Process code files
    if args.code and Path(args.code).exists():
        print(f"\n💻 Processing code: {args.code}")
        if Path(args.code).is_file():
            with open(args.code, 'r', encoding='utf-8') as f:
                code_content = f.read()
            patterns = organizer.extract_code_patterns(code_content)
        else:
            # Process directory
            for file_path in Path(args.code).rglob("*.{js,ts,jsx,tsx,py}"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    patterns.extend(organizer.extract_code_patterns(f.read()))
        print(f"   Found {len(patterns)} code patterns")
    
    # Process configuration files
    if args.config and Path(args.config).exists():
        print(f"\n⚙️  Processing configurations: {args.config}")
        if Path(args.config).is_file():
            with open(args.config, 'r', encoding='utf-8') as f:
                configurations.append(f.read())
        else:
            for config_path in Path(args.config).rglob("*.{json,yml,yaml,env}"):
                with open(config_path, 'r', encoding='utf-8') as f:
                    configurations.append(f"# {config_path.name}\n{f.read()}")
        print(f"   Found {len(configurations)} configuration examples")
    
    # Generate knowledge update
    if errors or patterns or configurations:
        print("\n📝 Generating knowledge update...")
        update = organizer.generate_knowledge_update(errors, patterns, configurations)
        output_path = Path(args.output)
        organizer.save_knowledge_update(update, output_path)
        
        print("\n✨ Knowledge organization complete!")
        print(f"\nNext steps:")
        print(f"1. Review the generated update: {output_path}")
        print(f"2. Add specific solutions for the errors")
        print(f"3. Append to docs/agents/livekit_expert_prompt.md")
    else:
        print("\n⚠️  No knowledge sources provided")
        print("\nUsage examples:")
        print("  python scripts/organize_livekit_knowledge.py --logs path/to/error.log")
        print("  python scripts/organize_livekit_knowledge.py --code path/to/livekit/code")
        print("  python scripts/organize_livekit_knowledge.py --config path/to/config.json")


if __name__ == "__main__":
    main()
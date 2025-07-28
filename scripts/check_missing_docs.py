#!/usr/bin/env python3
"""
Check for missing documentation and prepare Firecrawl queries.

This script identifies which libraries need documentation
and prepares queries for Firecrawl MCP server.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple

# Core project dependencies
CORE_DEPENDENCIES = {
    "anthropic": "https://docs.anthropic.com/claude/reference/python-sdk-overview",
    "langchain": "https://python.langchain.com/docs/get_started/introduction",
    "langgraph": "https://langchain-ai.github.io/langgraph/",
    "elevenlabs": "https://elevenlabs.io/docs/introduction",
    "livekit": "https://docs.livekit.io/",
    "pytest": "https://docs.pytest.org/",
    "pydantic": "https://docs.pydantic.dev/",
    "redis": "https://redis-py.readthedocs.io/",
    "mcp": "https://modelcontextprotocol.io/docs/",
    "playwright": "https://playwright.dev/python/docs/intro",
}

# Voice-specific dependencies
VOICE_DEPENDENCIES = {
    "webrtc": "https://webrtc.org/getting-started/overview",
    "pyaudio": "https://people.csail.mit.edu/hubert/pyaudio/docs/",
    "sounddevice": "https://python-sounddevice.readthedocs.io/",
}


def check_existing_docs() -> Tuple[List[str], List[str]]:
    """
    Check which documentation files already exist.
    
    Returns:
        Tuple of (existing_libs, missing_libs)
    """
    apidocs_dir = Path("apidocs")
    existing = []
    missing = []
    
    all_deps = {**CORE_DEPENDENCIES, **VOICE_DEPENDENCIES}
    
    for lib in all_deps:
        doc_path = apidocs_dir / f"{lib}_documentation.md"
        if doc_path.exists():
            existing.append(lib)
        else:
            missing.append(lib)
    
    return existing, missing


def generate_firecrawl_queries(missing_libs: List[str]) -> List[Dict[str, str]]:
    """
    Generate Firecrawl queries for missing documentation.
    
    Args:
        missing_libs: List of libraries missing documentation
        
    Returns:
        List of query dictionaries
    """
    all_deps = {**CORE_DEPENDENCIES, **VOICE_DEPENDENCIES}
    queries = []
    
    for lib in missing_libs:
        if lib in all_deps:
            queries.append({
                "library": lib,
                "url": all_deps[lib],
                "query": f"Fetch {lib} documentation including API reference, examples, and best practices"
            })
    
    return queries


def main():
    """Main entry point."""
    print("📚 Documentation Coverage Check")
    print("=" * 50)
    
    # Check existing documentation
    existing, missing = check_existing_docs()
    
    print(f"\n✅ Existing Documentation ({len(existing)}):")
    for lib in sorted(existing):
        print(f"  - {lib}")
    
    print(f"\n❌ Missing Documentation ({len(missing)}):")
    for lib in sorted(missing):
        print(f"  - {lib}")
    
    # Generate Firecrawl queries
    if missing:
        queries = generate_firecrawl_queries(missing)
        
        print("\n🔥 Firecrawl Queries to Execute:")
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. {query['library']}:")
            print(f"   URL: {query['url']}")
            print(f"   Query: {query['query']}")
    
    # Check environment
    print("\n🔑 Environment Check:")
    if os.getenv("FIRECRAWL_API_KEY"):
        print("  ✅ FIRECRAWL_API_KEY is set")
    else:
        print("  ❌ FIRECRAWL_API_KEY is not set")
        print("     Get your API key from: https://firecrawl.dev")
    
    # Generate quick reference
    print("\n📋 Quick Reference:")
    print("\nContext7 is best for:")
    print("  - Popular, well-documented libraries")
    print("  - Getting latest API references")
    print("  - Code examples and patterns")
    
    print("\nFirecrawl is best for:")
    print("  - Missing documentation")
    print("  - Niche libraries")
    print("  - Custom project documentation")
    print("  - Web-based API docs")
    
    # Save missing docs list
    if missing:
        output_path = Path("docs/Session_9/missing_docs.txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("Missing Documentation Libraries:\n")
            for lib in sorted(missing):
                f.write(f"- {lib}\n")
        print(f"\n📄 Missing docs list saved to: {output_path}")


if __name__ == "__main__":
    main()
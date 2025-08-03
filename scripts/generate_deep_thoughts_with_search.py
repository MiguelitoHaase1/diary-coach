#!/usr/bin/env python3
"""Generate a Deep Thoughts report and enhance it with real web searches.

This script demonstrates the two-phase approach:
1. Generate Deep Thoughts with search suggestions
2. Perform actual web searches and update the report
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
from src.services.llm_factory import LLMTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_search_instructions(report_content: str):
    """Print instructions for performing web searches."""
    print("\n" + "="*60)
    print("DEEP THOUGHTS REPORT GENERATED")
    print("="*60)
    
    # Check if search suggestions are present
    if "Search terms:" in report_content:
        print("\nThe report includes search suggestions in the Recommended readings section.")
        print("\nTo add real articles:")
        print("1. Note the search terms suggested for each theme")
        print("2. Perform web searches using those terms")
        print("3. Focus on quality sources (HBR, Atlantic, MIT Sloan, etc.)")
        print("4. Replace the suggestions with actual article titles and URLs")
        
        # Extract and show the search terms
        import re
        pattern = r'Search terms: "([^"]+)"'
        matches = re.findall(pattern, report_content)
        
        if matches:
            print("\nSuggested searches:")
            for i, query in enumerate(matches, 1):
                print(f"  {i}. \"{query}\"")
    else:
        print("\nNo search suggestions found in the report.")
    
    print("\n" + "="*60 + "\n")


async def main():
    """Generate Deep Thoughts and provide search guidance."""
    
    # For demonstration, use a simple conversation
    conversation_history = [
        {
            'role': 'user',
            'content': 'I struggle with work-life balance and productivity'
        },
        {
            'role': 'assistant',
            'content': 'Tell me more about what work-life balance means to you and where you feel the tension.'
        },
        {
            'role': 'user',
            'content': 'I work long hours but feel unproductive, and miss time with family'
        },
        {
            'role': 'assistant',
            'content': 'It sounds like you\'re caught between quantity and quality - both in work output and family time. What would "productive" look like to you?'
        }
    ]
    
    print("Generating Deep Thoughts report...")
    
    # Phase 1: Generate report with search suggestions
    generator = DeepThoughtsGenerator(tier=LLMTier.PREMIUM)
    
    try:
        report_content = await generator.generate_deep_thoughts(
            conversation_history=conversation_history,
            conversation_id="demo_with_search",
            enable_web_search=True  # This enables search suggestions
        )
        
        output_path = generator.get_output_filepath()
        print(f"\n✅ Report generated: {output_path}")
        
        # Phase 2: Guide user on web searches
        print_search_instructions(report_content)
        
        # In a production system, this is where we would:
        # 1. Extract the search queries
        # 2. Call a web search API (Google, Bing, etc.)
        # 3. Filter for quality sources
        # 4. Update the report with real articles
        
        print("Note: To automatically perform web searches, you would need to:")
        print("- Integrate a web search API (Google Custom Search, Bing, etc.)")
        print("- Or use an MCP server with web search capabilities")
        print("- Or have an agent with native web search access perform the searches")
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
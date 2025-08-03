#!/usr/bin/env python3
"""Script to enhance Deep Thoughts reports with real web search results.

This script reads a Deep Thoughts report and performs web searches
for the recommended themes, then updates the report with real articles.

Usage:
    python scripts/enhance_deep_thoughts_with_search.py [report_file]
    
If no file is specified, it will use the most recent Deep Thoughts report.
"""

import asyncio
import sys
from pathlib import Path
import re
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.web_search_post_processor import WebSearchPostProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractiveWebSearchProcessor(WebSearchPostProcessor):
    """Interactive version that prompts for web search results."""
    
    async def _perform_searches(self, themes):
        """Override to prompt user to perform searches."""
        print("\n" + "="*60)
        print("WEB SEARCH NEEDED")
        print("="*60)
        print("\nThe Deep Thoughts report suggests searching for these themes:\n")
        
        results = {}
        
        for i, (theme_name, query) in enumerate(themes, 1):
            print(f"{i}. {theme_name}")
            print(f"   Suggested search: \"{query}\"")
            print(f"   Recommended sources: Harvard Business Review, The Atlantic, ")
            print(f"                       MIT Sloan Review, Psychology Today, Aeon\n")
            
            # In a real implementation, this is where we'd call a web search API
            # For now, we'll note that searches should be performed
            results[theme_name] = [{
                'query': query,
                'note': 'Please perform this search manually or use an API'
            }]
        
        print("\nTo complete the enhancement:")
        print("1. Perform web searches for each theme")
        print("2. Find 2-3 high-quality articles per theme")
        print("3. Update the report with actual article titles and URLs")
        print("\n" + "="*60 + "\n")
        
        return results


async def find_latest_report():
    """Find the most recent Deep Thoughts report."""
    reports_dir = Path("docs/prototype/DeepThoughts")
    if not reports_dir.exists():
        return None
    
    # Find all Deep Thoughts files
    deep_thoughts_files = list(reports_dir.glob("DeepThoughts_*.md"))
    deep_thoughts_files.extend(list(reports_dir.glob("deep_thoughts_*.md")))
    
    if not deep_thoughts_files:
        return None
    
    # Sort by modification time and return the most recent
    return max(deep_thoughts_files, key=lambda f: f.stat().st_mtime)


async def main():
    """Main entry point."""
    # Get report file
    if len(sys.argv) > 1:
        report_path = Path(sys.argv[1])
    else:
        report_path = await find_latest_report()
        if not report_path:
            print("No Deep Thoughts report found.")
            print("Usage: python enhance_deep_thoughts_with_search.py [report_file]")
            return
    
    if not report_path.exists():
        print(f"Report file not found: {report_path}")
        return
    
    print(f"Processing report: {report_path}")
    
    # Read the report
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # Check if it already has real articles
    if "harvard business review" in report_content.lower() and "http" in report_content:
        print("\nThis report appears to already have real articles.")
        response = input("Process anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Process the report
    processor = InteractiveWebSearchProcessor()
    enhanced_report = await processor.enhance_with_web_search(report_content)
    
    if processor.search_performed:
        # Save the enhanced report
        output_path = report_path.parent / f"enhanced_{report_path.name}"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_report)
        
        print(f"\nEnhanced report saved to: {output_path}")
        print("\nNext steps:")
        print("1. The report now shows where web searches should be performed")
        print("2. Use a web search API or service to find real articles")
        print("3. Update the enhanced report with actual article information")
    else:
        print("\nNo search themes found in the report.")


if __name__ == "__main__":
    asyncio.run(main())
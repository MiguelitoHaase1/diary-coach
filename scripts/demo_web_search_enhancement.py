#!/usr/bin/env python3
"""Demonstrate web search enhancement for Deep Thoughts reports.

This script shows how the web search enhancement works:
1. Read a Deep Thoughts report with search suggestions
2. Extract the themes
3. Show where real web searches would be performed
4. Format the results

In production, this would be called by an agent with web search access.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.web_search_enhancer import WebSearchEnhancer


def main():
    """Demonstrate the web search enhancement process."""
    
    # Example Deep Thoughts report with search suggestions
    sample_report = """**The Paradox of Productivity**

In 1911, Frederick Taylor published "The Principles of Scientific Management," promising to solve productivity through time and motion studies. Yet here we are, over a century later, with more productivity tools than ever, feeling less productive than before. Your struggle with work-life balance while feeling unproductive despite long hours echoes a fundamental paradox of modern work: the harder we chase productivity, the more it eludes us.

**Today's Crux**

The crux isn't simply managing time better or working fewer hours. It's recognizing that your current definition of productivity might be the very thing preventing both productivity and life satisfaction. When you say you work long hours but feel unproductive, you're revealing a disconnect between effort and meaningful output. This matters because you're likely measuring productivity by hours logged rather than value created, leading to a vicious cycle where more time invested yields diminishing returns while eroding the family connections that provide meaning to the work itself.

**Recommended readings**

Based on our exploration of productivity paradoxes and work-life integration, I recommend searching for articles on these themes:

**Theme 1: Redefining productivity beyond time spent**
Search terms: "deep work productivity not busy work"
Look for articles in: Harvard Business Review, MIT Sloan Review, Cal Newport's blog
Why this matters: Understanding the difference between being busy and being productive is crucial for breaking the cycle of long hours with little satisfaction. Articles on deep work and focused productivity can provide frameworks for measuring output by value rather than time.

**Theme 2: Work-life integration strategies for knowledge workers**
Search terms: "work life integration not balance Harvard Business Review"
Look for articles in: Harvard Business Review, MIT Sloan Review, Stanford Business
Why this matters: The traditional concept of work-life balance implies a zero-sum game. Modern research on work-life integration offers more nuanced approaches that align with how knowledge work actually functions.

Note: Since I cannot perform real web searches in this context, these are suggested search queries that should yield relevant, high-quality articles on these topics."""
    
    print("=== Web Search Enhancement Demo ===\n")
    
    # Extract themes
    themes = WebSearchEnhancer.extract_search_themes(sample_report)
    
    print("Extracted themes from report:")
    for i, (theme, query) in enumerate(themes, 1):
        print(f"\n{i}. Theme: {theme}")
        print(f"   Search query: \"{query}\"")
    
    # Simulate search results (in production, these would come from real web searches)
    mock_search_results = {
        "Redefining productivity beyond time spent": [
            {
                "title": "The Case for Deep Work in a Distracted World",
                "url": "https://hbr.org/2024/01/deep-work-distracted-world",
                "source": "Harvard Business Review",
                "summary": "Research shows that 4 hours of deep, focused work produces more valuable output than 10 hours of fragmented attention. This article provides practical strategies for creating deep work blocks and measuring productivity by outcomes rather than hours."
            },
            {
                "title": "Why Busy Isn't Productive",
                "url": "https://sloanreview.mit.edu/article/busy-not-productive/",
                "source": "MIT Sloan Management Review", 
                "summary": "A study of 5,000 knowledge workers found an inverse relationship between hours worked and value created after the 6-hour mark. The article explores how to identify high-value activities and eliminate productivity theater."
            }
        ],
        "Work-life integration strategies for knowledge workers": [
            {
                "title": "From Balance to Integration: A New Model for Work and Life",
                "url": "https://hbr.org/2023/11/work-life-integration-model",
                "source": "Harvard Business Review",
                "summary": "Work-life integration recognizes that strict boundaries often create more stress than flexibility. This piece presents a framework for creating permeable but intentional boundaries that honor both professional excellence and personal priorities."
            },
            {
                "title": "The Myth of Work-Life Balance",
                "url": "https://www.gsb.stanford.edu/insights/myth-work-life-balance",
                "source": "Stanford Graduate School of Business",
                "summary": "Stanford researchers argue that work-life balance is an outdated industrial-age concept. They propose 'work-life navigation' - a dynamic approach that adjusts to life phases and daily rhythms rather than seeking perfect equilibrium."
            }
        ]
    }
    
    print("\n\n=== Enhanced Report Preview ===\n")
    
    # Create enhanced report
    enhanced_report = WebSearchEnhancer.create_enhanced_report(
        sample_report, 
        mock_search_results
    )
    
    # Show just the enhanced recommendations section
    if "Recommended readings" in enhanced_report:
        recs_start = enhanced_report.find("Recommended readings")
        recs_section = enhanced_report[recs_start:recs_start + 1500]
        print(recs_section)
        if len(enhanced_report[recs_start:]) > 1500:
            print("...")
    
    print("\n\n=== How This Works in Production ===\n")
    print("1. Deep Thoughts generates a report with search suggestions")
    print("2. An agent with web search access reads the report")
    print("3. The agent performs real web searches for each theme")
    print("4. The agent uses WebSearchEnhancer to format results")
    print("5. The enhanced report is saved with real articles")
    print("\nThis two-phase approach ensures:")
    print("- No hallucinated articles")
    print("- Real, current web content")
    print("- Quality sources from reputable publications")


if __name__ == "__main__":
    main()
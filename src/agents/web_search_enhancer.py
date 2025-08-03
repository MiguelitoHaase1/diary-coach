"""Web Search Enhancer for Deep Thoughts reports.

This agent is designed to be called by Claude (who has web search access)
to enhance Deep Thoughts reports with real articles.
"""

import re
import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)


class WebSearchEnhancer:
    """Enhances Deep Thoughts reports with real web search results.
    
    This class is designed to be used by an LLM with web search capabilities.
    It extracts themes from reports and formats search results.
    """
    
    @staticmethod
    def extract_search_themes(report_content: str) -> List[Tuple[str, str]]:
        """Extract search themes and queries from a Deep Thoughts report.
        
        Args:
            report_content: The Deep Thoughts report content
            
        Returns:
            List of (theme_name, search_query) tuples
        """
        themes = []
        
        # Pattern 1: Look for "Theme N: [theme]" followed by "Search terms:"
        pattern1 = r'\*\*Theme \d+: ([^*]+)\*\*\s*\nSearch terms: "([^"]+)"'
        matches = re.findall(pattern1, report_content)
        
        for theme, query in matches:
            themes.append((theme.strip(), query.strip()))
        
        # Pattern 2: Look for themes in recommended readings section
        if not themes and "recommend searching for articles on these themes:" in report_content:
            # Extract the themes paragraph
            sections = report_content.split("recommend searching for articles on these themes:")
            if len(sections) > 1:
                theme_section = sections[1].split("\n\n")[0]
                # Look for bullet points or numbered items
                theme_lines = [line.strip() for line in theme_section.split('\n') if line.strip()]
                
                for line in theme_lines:
                    # Remove bullet points, numbers, etc.
                    clean_line = re.sub(r'^[-•*\d.]\s*', '', line)
                    if clean_line and len(clean_line) > 5:
                        # Use the theme as both name and query
                        themes.append((clean_line, clean_line))
        
        return themes[:3]  # Limit to 3 themes
    
    @staticmethod
    def format_search_results(articles: List[Dict[str, Any]], theme: str) -> str:
        """Format a list of articles for a specific theme.
        
        Args:
            articles: List of article dictionaries with title, url, source, summary
            theme: The theme these articles relate to
            
        Returns:
            Formatted markdown string
        """
        if not articles:
            return f"**{theme}**\n*No articles found for this theme.*\n"
        
        formatted = [f"**{theme}**\n"]
        
        for article in articles[:3]:  # Limit to 3 articles per theme
            title = article.get('title', 'Unknown Title')
            url = article.get('url', '')
            source = article.get('source', '')
            summary = article.get('summary', '')
            
            # Format the article
            if url:
                formatted.append(f'**"{title}"** - {source}')
                formatted.append(f"[Read article]({url})")
            else:
                formatted.append(f'**"{title}"** - {source}')
            
            if summary:
                formatted.append(f"{summary}")
            
            formatted.append("")  # Blank line between articles
        
        return '\n'.join(formatted)
    
    @staticmethod
    def create_enhanced_report(
        original_report: str, 
        search_results: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Create an enhanced report with real search results.
        
        Args:
            original_report: The original Deep Thoughts report
            search_results: Dict mapping themes to lists of articles
            
        Returns:
            Enhanced report with real articles
        """
        # Find the Recommended readings section
        sections = original_report.split('Recommended readings')
        if len(sections) < 2:
            # No recommendations section, append one
            return original_report + "\n\n**Recommended readings**\n\n" + \
                   WebSearchEnhancer._format_all_results(search_results)
        
        # Replace the recommendations with real results
        before_recs = sections[0]
        after_recs_parts = sections[1].split('\n\n', 1)
        
        # Build the enhanced report
        enhanced = before_recs + 'Recommended readings\n\n'
        enhanced += "Based on our exploration, here are carefully selected articles " \
                   "that can deepen your understanding:\n\n"
        enhanced += WebSearchEnhancer._format_all_results(search_results)
        
        # Add any content that came after recommendations
        if len(after_recs_parts) > 1 and not after_recs_parts[1].startswith("Note:"):
            # Check if there's meaningful content after recommendations
            remaining = after_recs_parts[1].strip()
            if remaining and not remaining.startswith("Search terms:"):
                enhanced += "\n\n" + remaining
        
        return enhanced
    
    @staticmethod
    def _format_all_results(search_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format all search results into a recommendations section."""
        formatted_sections = []
        
        for theme, articles in search_results.items():
            section = WebSearchEnhancer.format_search_results(articles, theme)
            formatted_sections.append(section)
        
        return '\n'.join(formatted_sections)
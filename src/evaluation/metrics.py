# src/evaluation/metrics.py
import re
from typing import Set

class ResponseRelevanceMetric:
    """Evaluates response relevance using keyword matching."""
    
    def __init__(self):
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'you', 'your', 'i', 'me',
            'my', 'we', 'us', 'our'
        }
    
    def _normalize_word(self, word: str) -> str:
        """Normalize word to handle variations."""
        # Simple stemming for common patterns
        if word.endswith('s') and len(word) > 3:
            return word[:-1]  # goals -> goal, wants -> want
        return word
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out stop words and short words, then normalize
        keywords = {self._normalize_word(word) for word in words 
                   if word not in self.stop_words and len(word) > 2}
        return keywords
    
    async def evaluate(self, context: str, response: str) -> float:
        """
        Evaluate response relevance to context.
        
        Args:
            context: The conversation context
            response: The agent's response
            
        Returns:
            Relevance score between 0 and 1
        """
        context_keywords = self._extract_keywords(context)
        response_keywords = self._extract_keywords(response)
        
        if not context_keywords:
            return 0.0
        
        # Calculate overlap
        common_keywords = context_keywords.intersection(response_keywords)
        relevance_score = len(common_keywords) / len(context_keywords)
        
        # Boost score for coaching-relevant terms (normalized)
        coaching_terms = {'goal', 'accomplish', 'important', 'explore', 'want', 'today'}
        coaching_overlap = response_keywords.intersection(coaching_terms)
        
        # Add significant bonus for coaching terms
        if coaching_overlap:
            relevance_score += 0.65 * len(coaching_overlap) / len(coaching_terms)
        
        # Cap at 1.0
        return min(relevance_score, 1.0)
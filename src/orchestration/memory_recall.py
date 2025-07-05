"""Memory Recall Node for Session 6.7 - Explicit 'remember when' queries."""

import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.orchestration.context_state import ContextState


logger = logging.getLogger(__name__)


class MemoryRecallNode:
    """Handles explicit memory recall queries like 'remember when...'"""
    
    def __init__(self):
        # Patterns that indicate explicit memory queries
        self.recall_patterns = [
            r"remember\s+(?:when|what|our|the|that)",
            r"what\s+did\s+we\s+discuss",
            r"recall\s+(?:our|the|that)\s*(?:conversation|discussion|talk)?",
            r"last\s+time\s+we\s+talked",
            r"you\s+mentioned\s+(?:before|earlier)",
            r"what\s+was\s+that\s+(?:thing\s+)?about",
            r"didn't\s+we\s+cover",
            r"as\s+we\s+discussed",
            r"do\s+you\s+remember",
            r"can\s+you\s+recall"
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.recall_patterns]
    
    async def process_memory_query(self, state: ContextState) -> ContextState:
        """Process explicit memory recall queries."""
        
        # Initialize context usage tracking
        if not state.context_usage:
            state.context_usage = {}
        
        # Check if this is a memory recall query
        is_memory_query = self._detect_memory_query(state.messages)
        
        if not is_memory_query:
            state.context_usage["memory_recall_triggered"] = False
            return state
        
        # Extract memory search terms
        search_terms = self._extract_search_terms(state.messages)
        
        # Search conversation history for relevant memories
        relevant_memories = self._search_conversation_history(
            state.conversation_history or [], 
            search_terms
        )
        
        # Format memories for coach response
        formatted_recall = self._format_memory_recall(relevant_memories, search_terms)
        
        # Update state
        state.memory_recall = formatted_recall
        state.recall_mode = True
        state.context_usage.update({
            "memory_recall_triggered": True,
            "search_terms": search_terms,
            "memories_found": len(relevant_memories),
            "recall_confidence": self._calculate_recall_confidence(relevant_memories, search_terms)
        })
        
        state.decision_path.append("memory_recall")
        return state
    
    def _detect_memory_query(self, messages: List[Dict[str, Any]]) -> bool:
        """Detect if the conversation contains memory recall queries."""
        
        if not messages:
            return False
        
        # Check the last user message for memory patterns
        last_message = messages[-1]
        if last_message.get("type") != "user":
            return False
        
        content = last_message.get("content", "").lower()
        
        # Check against all recall patterns
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                return True
        
        return False
    
    def _extract_search_terms(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract search terms from memory query."""
        
        if not messages:
            return []
        
        content = messages[-1].get("content", "").lower()
        
        # Extract meaningful terms after common memory phrases
        search_terms = []
        
        # Look for terms after "about", "regarding", "on", etc.
        about_pattern = r"(?:about|regarding|on|concerning|discuss(?:ed)?|talk(?:ed)?.*about)\s+([a-zA-Z\s]+)"
        matches = re.findall(about_pattern, content, re.IGNORECASE)
        
        for match in matches:
            # Clean up and extract keywords
            terms = self._extract_keywords(match)
            search_terms.extend(terms)
        
        # Also extract general keywords from the query
        general_keywords = self._extract_keywords(content)
        search_terms.extend(general_keywords)
        
        # Remove duplicates and common words
        search_terms = list(set(search_terms))
        
        # Filter out very common words that appeared in recall patterns
        stop_words = {"remember", "when", "what", "did", "we", "discuss", "talked", "mentioned", "the", "a", "an", "and", "or", "but"}
        search_terms = [term for term in search_terms if term not in stop_words and len(term) > 2]
        
        return search_terms[:10]  # Limit to top 10 terms
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove very common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        keywords = [word for word in words if word not in stop_words]
        return keywords
    
    def _search_conversation_history(self, conversation_history: List[Dict[str, Any]], search_terms: List[str]) -> List[Dict[str, Any]]:
        """Search conversation history for relevant memories."""
        
        if not conversation_history or not search_terms:
            return []
        
        relevant_memories = []
        
        for memory in conversation_history:
            relevance_score = self._calculate_memory_relevance(memory, search_terms)
            if relevance_score > 0.3:  # Threshold for relevance
                memory_with_score = memory.copy()
                memory_with_score["relevance_score"] = relevance_score
                relevant_memories.append(memory_with_score)
        
        # Sort by relevance score
        relevant_memories.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Return top 5 most relevant memories
        return relevant_memories[:5]
    
    def _calculate_memory_relevance(self, memory: Dict[str, Any], search_terms: List[str]) -> float:
        """Calculate relevance score between memory and search terms."""
        
        # Combine all memory text fields
        memory_text = " ".join([
            memory.get("topic", ""),
            memory.get("insights", ""),
            memory.get("summary", ""),
            str(memory.get("content", ""))
        ]).lower()
        
        if not memory_text:
            return 0.0
        
        # Score based on term matches
        matches = 0
        for term in search_terms:
            if term.lower() in memory_text:
                matches += 1
        
        # Calculate relevance score
        relevance = matches / len(search_terms) if search_terms else 0
        
        # Boost score for exact topic matches
        topic_boost = 0.0
        memory_topic = memory.get("topic", "").lower()
        if memory_topic and any(term.lower() in memory_topic for term in search_terms):
            topic_boost = 0.3
        
        # Recent memories get slight boost
        recency_boost = 0.0
        if "date" in memory:
            try:
                memory_date = datetime.fromisoformat(memory["date"])
                days_ago = (datetime.now() - memory_date).days
                if days_ago <= 7:  # Within last week
                    recency_boost = 0.1
            except:
                pass
        
        total_score = min(relevance + topic_boost + recency_boost, 1.0)
        return total_score
    
    def _format_memory_recall(self, memories: List[Dict[str, Any]], search_terms: List[str]) -> str:
        """Format memories for coach response."""
        
        if not memories:
            return f"I don't have specific memories about {', '.join(search_terms[:3])}. Could you refresh my memory with more details?"
        
        # Format memories into coherent recall
        recall_parts = []
        recall_parts.append(f"Yes, I remember our discussions about {', '.join(search_terms[:3])}.")
        
        for i, memory in enumerate(memories[:3]):  # Top 3 memories
            date_str = ""
            if "date" in memory:
                try:
                    date_obj = datetime.fromisoformat(memory["date"])
                    date_str = f" on {date_obj.strftime('%B %d')}"
                except:
                    pass
            
            topic = memory.get("topic", "")
            insights = memory.get("insights", "")
            
            if topic and insights:
                recall_parts.append(f"We discussed {topic}{date_str}: {insights}")
            elif topic:
                recall_parts.append(f"We covered {topic}{date_str}.")
            elif insights:
                recall_parts.append(f"Key insight{date_str}: {insights}")
        
        recall_parts.append("How would you like to build on these previous insights?")
        
        return " ".join(recall_parts)
    
    def _calculate_recall_confidence(self, memories: List[Dict[str, Any]], search_terms: List[str]) -> float:
        """Calculate confidence in memory recall quality."""
        
        if not memories:
            return 0.0
        
        # Base confidence on number of memories found
        memory_confidence = min(len(memories) / 3, 1.0)  # Optimal is 3 memories
        
        # Boost confidence for high relevance scores
        if memories:
            avg_relevance = sum(mem.get("relevance_score", 0) for mem in memories) / len(memories)
            relevance_confidence = avg_relevance
        else:
            relevance_confidence = 0.0
        
        # Combine confidences
        total_confidence = (memory_confidence + relevance_confidence) / 2
        
        return total_confidence
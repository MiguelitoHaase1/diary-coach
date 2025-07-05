"""Enhanced relevance scoring system for Session 6.3."""

import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Pattern

from src.orchestration.context_state import ContextState


logger = logging.getLogger(__name__)


class EnhancedRelevanceScorer:
    """Advanced relevance scorer with pattern matching and optional LLM analysis."""
    
    def __init__(
        self,
        use_llm: bool = False,
        todo_threshold: float = 0.6,
        document_threshold: float = 0.6,
        memory_threshold: float = 0.6
    ):
        """Initialize enhanced relevance scorer.
        
        Args:
            use_llm: Whether to use LLM for sophisticated analysis
            todo_threshold: Threshold for todo context relevance
            document_threshold: Threshold for document context relevance
            memory_threshold: Threshold for memory context relevance
        """
        self.use_llm = use_llm
        self.todo_threshold = todo_threshold
        self.document_threshold = document_threshold
        self.memory_threshold = memory_threshold
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for fast pattern matching."""
        self.todo_patterns = [
            re.compile(r'\b(?:task|tasks|todo|priority|prioritize|should|need|must)\b', re.IGNORECASE),
            re.compile(r'\b(?:today|tomorrow|work|project|deadline)\b', re.IGNORECASE),
            re.compile(r'\b(?:focus|execution|deliver|complete|finish)\b', re.IGNORECASE),
            re.compile(r'\b(?:schedule|agenda|plan|organize)\b', re.IGNORECASE)
        ]
        
        self.document_patterns = [
            re.compile(r'\b(?:belief|core|values|principle|philosophy)\b', re.IGNORECASE),
            re.compile(r'\b(?:strategic|strategy|vision|mission|planning)\b', re.IGNORECASE),
            re.compile(r'\b(?:framework|approach|method|system)\b', re.IGNORECASE),
            re.compile(r'\b(?:reference|guide|documentation)\b', re.IGNORECASE)
        ]
        
        self.memory_patterns = [
            re.compile(r'\b(?:remember|recall|previous|before|earlier)\b', re.IGNORECASE),
            re.compile(r'\b(?:discussed|talked|mentioned|said)\b', re.IGNORECASE),
            re.compile(r'\b(?:last time|yesterday|past|history)\b', re.IGNORECASE),
            re.compile(r'\b(?:conversation|session|meeting)\b', re.IGNORECASE)
        ]
        
        self.calendar_patterns = [
            re.compile(r'\b(?:schedule|calendar|appointment|meeting)\b', re.IGNORECASE),
            re.compile(r'\b(?:time|when|available|busy|free)\b', re.IGNORECASE),
            re.compile(r'\b(?:today|tomorrow|week|month|prioritize)\b', re.IGNORECASE)
        ]
    
    async def score(self, state: ContextState) -> ContextState:
        """Score context relevance using enhanced pattern matching and optional LLM."""
        if not state.messages:
            state.context_relevance = {
                "todos": 0.0, 
                "documents": 0.0, 
                "memory": 0.0,
                "calendar": 0.0
            }
            state.decision_path.append("context_relevance_scorer")
            return state
        
        # Initialize context usage tracking
        if not state.context_usage:
            state.context_usage = {}
        
        start_time = datetime.now()
        
        # Get content from messages (prioritize recent messages)
        content_blocks = self._extract_content(state.messages)
        state.context_usage["analyzed_messages"] = len(state.messages)
        
        # Pattern-based scoring (fast)
        pattern_scores = self._score_with_patterns(content_blocks)
        
        # Optional LLM-based scoring (sophisticated but slower)
        if self.use_llm:
            llm_scores = await self._score_with_llm(content_blocks)
            # Combine pattern and LLM scores (weighted average)
            combined_scores = self._combine_scores(pattern_scores, llm_scores)
            state.context_usage["llm_analysis"] = True
            state.context_usage["reasoning"] = "Combined pattern matching with LLM analysis"
        else:
            combined_scores = pattern_scores
            state.context_usage["llm_analysis"] = False
        
        # Apply thresholds
        state.context_relevance = combined_scores
        
        # Track performance
        duration = (datetime.now() - start_time).total_seconds()
        state.context_usage["scoring_duration_ms"] = int(duration * 1000)
        
        state.decision_path.append("context_relevance_scorer")
        return state
    
    def _extract_content(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract content from messages, prioritizing recent ones."""
        content_blocks = []
        
        # Take last 5 messages for relevance (performance optimization)
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        
        for message in recent_messages:
            content = message.get("content", "")
            if content and isinstance(content, str):
                content_blocks.append(content)
        
        return content_blocks
    
    def _score_with_patterns(self, content_blocks: List[str]) -> Dict[str, float]:
        """Score relevance using compiled regex patterns."""
        combined_content = " ".join(content_blocks).lower()
        
        scores = {
            "todos": self._calculate_pattern_score(combined_content, self.todo_patterns),
            "documents": self._calculate_pattern_score(combined_content, self.document_patterns),
            "memory": self._calculate_pattern_score(combined_content, self.memory_patterns),
            "calendar": self._calculate_pattern_score(combined_content, self.calendar_patterns)
        }
        
        return scores
    
    def _calculate_pattern_score(self, content: str, patterns: List[Pattern]) -> float:
        """Calculate relevance score for a set of patterns."""
        total_matches = 0
        unique_patterns_matched = 0
        
        for pattern in patterns:
            matches = len(pattern.findall(content))
            if matches > 0:
                total_matches += matches
                unique_patterns_matched += 1
        
        # Score based on both total matches and pattern diversity
        base_score = min(total_matches * 0.25, 0.8)  # Increased sensitivity
        diversity_bonus = unique_patterns_matched * 0.15  # Increased bonus for pattern variety
        
        return min(base_score + diversity_bonus, 1.0)
    
    async def _score_with_llm(self, content_blocks: List[str]) -> Dict[str, float]:
        """Score relevance using LLM analysis (mock implementation)."""
        # Mock LLM scoring for now - would integrate with actual LLM in production
        combined_content = " ".join(content_blocks).lower()
        
        # Simple heuristics that simulate LLM understanding
        scores = {}
        
        # Todo relevance - detect action orientation and planning language
        if any(word in combined_content for word in ["execute", "deliver", "accomplish", "balance", "execution"]):
            scores["todos"] = 0.8
        elif any(word in combined_content for word in ["task", "work", "project", "focus", "daily"]):
            scores["todos"] = 0.6
        else:
            scores["todos"] = 0.2
        
        # Document relevance - detect strategic/philosophical language
        if any(word in combined_content for word in ["strategic", "philosophy", "approach", "thinking"]):
            scores["documents"] = 0.7
        elif any(word in combined_content for word in ["belief", "value", "principle"]):
            scores["documents"] = 0.9
        else:
            scores["documents"] = 0.1
        
        # Memory relevance - detect explicit recall requests
        if any(word in combined_content for word in ["remember", "discussed", "previous"]):
            scores["memory"] = 0.9
        else:
            scores["memory"] = 0.1
        
        # Calendar relevance
        if any(word in combined_content for word in ["schedule", "time", "available"]):
            scores["calendar"] = 0.8
        else:
            scores["calendar"] = 0.2
        
        return scores
    
    def _combine_scores(self, pattern_scores: Dict[str, float], llm_scores: Dict[str, float]) -> Dict[str, float]:
        """Combine pattern and LLM scores with weighted average."""
        combined = {}
        pattern_weight = 0.4
        llm_weight = 0.6
        
        for key in pattern_scores:
            pattern_score = pattern_scores.get(key, 0.0)
            llm_score = llm_scores.get(key, 0.0)
            combined[key] = (pattern_score * pattern_weight) + (llm_score * llm_weight)
        
        return combined
    
    def get_threshold(self, context_type: str) -> float:
        """Get the relevance threshold for a context type."""
        thresholds = {
            "todos": self.todo_threshold,
            "documents": self.document_threshold,
            "memory": self.memory_threshold,
            "calendar": self.todo_threshold  # Use todo threshold for calendar
        }
        return thresholds.get(context_type, 0.6)
    
    def should_fetch_context(self, context_type: str, relevance_score: float) -> bool:
        """Determine if context should be fetched based on score and threshold."""
        threshold = self.get_threshold(context_type)
        return relevance_score >= threshold
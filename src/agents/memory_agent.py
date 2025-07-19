"""Memory Agent for accessing and analyzing past conversations."""

import os
import json
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter
import re

from src.agents.base import BaseAgent, AgentCapability, AgentRequest, AgentResponse


class MemoryAgent(BaseAgent):
    """Agent responsible for accessing and analyzing past conversations."""

    def __init__(self, conversations_dir: str = "data/conversations"):
        """Initialize Memory Agent.

        Args:
            conversations_dir: Directory containing conversation history files
        """
        super().__init__(
            name="memory",
            capabilities=[AgentCapability.MEMORY_ACCESS]
        )
        self.conversations_dir = conversations_dir
        self.conversations_cache: List[Dict[str, Any]] = []
        self.patterns_cache: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """Load and pre-process conversation history."""
        self.conversations_cache = await self._load_conversations()
        self.patterns_cache = await self._extract_patterns()
        self.is_initialized = True

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle memory-related requests from other agents.

        Args:
            request: The agent request to handle

        Returns:
            AgentResponse with conversation history or patterns
        """
        try:
            query_lower = request.query.lower()

            # Determine request type
            if "remember when" in query_lower or "last time" in query_lower:
                result = await self._find_specific_memory(request.query)
            elif "patterns" in query_lower or "topics" in query_lower:
                result = self._get_conversation_patterns()
            elif "summary" in query_lower:
                result = self._get_conversation_summary()
            else:
                # General search
                result = await self._search_conversations(request.query)

            return AgentResponse(
                agent_name=self.name,
                content=json.dumps(result),
                metadata={
                    "conversation_count": len(self.conversations_cache),
                    "patterns": list(self.patterns_cache.keys())
                },
                request_id=request.request_id,
                timestamp=datetime.now()
            )

        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="Unable to retrieve memory",
                metadata={},
                request_id=request.request_id,
                timestamp=datetime.now(),
                error=str(e)
            )

    async def _load_conversations(self) -> List[Dict[str, Any]]:
        """Load all conversations from the conversations directory."""
        conversations = []

        if not os.path.exists(self.conversations_dir):
            return conversations

        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.conversations_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        conv_data = json.load(f)
                        conversations.append(conv_data)
                except Exception:
                    # Skip malformed files
                    continue

        # Sort by timestamp (newest first)
        conversations.sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )

        return conversations

    async def _extract_patterns(self) -> Dict[str, Any]:
        """Extract common patterns and topics from conversations."""
        patterns = {
            "challenges": Counter(),
            "values": Counter(),
            "topics": Counter(),
            "emotions": Counter(),
            "time_patterns": {}
        }

        # Common patterns to look for
        challenge_keywords = [
            "problem", "challenge", "issue", "struggle", "difficult",
            "organize", "focus", "productivity", "clarity"
        ]

        value_keywords = [
            "value", "believe", "important", "matter", "care",
            "purpose", "meaning", "growth", "authenticity"
        ]

        emotion_keywords = [
            "feel", "feeling", "anxious", "worried", "excited",
            "happy", "frustrated", "overwhelmed", "confident"
        ]

        for conv in self.conversations_cache:
            messages = conv.get('messages', [])

            for msg in messages:
                if msg.get('type') == 'user':
                    content = msg.get('content', '').lower()

                    # Extract challenges
                    for keyword in challenge_keywords:
                        if keyword in content:
                            patterns["challenges"][keyword] += 1

                    # Extract values
                    for keyword in value_keywords:
                        if keyword in content:
                            patterns["values"][keyword] += 1

                    # Extract emotions
                    for keyword in emotion_keywords:
                        if keyword in content:
                            patterns["emotions"][keyword] += 1

                    # Extract general topics (2-3 word phrases)
                    words = re.findall(r'\b\w+\b', content)
                    for i in range(len(words) - 1):
                        bigram = f"{words[i]} {words[i+1]}"
                        if len(words[i]) > 3 and len(words[i+1]) > 3:
                            patterns["topics"][bigram] += 1

        # Keep only top patterns
        for category in ["challenges", "values", "topics", "emotions"]:
            patterns[category] = dict(patterns[category].most_common(10))

        return patterns

    async def _find_specific_memory(self, query: str) -> Dict[str, Any]:
        """Find specific memories based on query."""
        results = []
        query_lower = query.lower()

        # Extract key terms from query
        key_terms = re.findall(r'\b\w{4,}\b', query_lower)

        for conv in self.conversations_cache:
            relevance_score = 0
            matching_messages = []

            for msg in conv.get('messages', []):
                content_lower = msg.get('content', '').lower()

                # Check for key term matches
                matches = sum(1 for term in key_terms if term in content_lower)
                if matches > 0:
                    relevance_score += matches
                    matching_messages.append({
                        "content": msg.get('content'),
                        "timestamp": msg.get('timestamp'),
                        "type": msg.get('type')
                    })

            if relevance_score > 0:
                results.append({
                    "conversation_id": conv.get('conversation_id'),
                    "timestamp": conv.get('timestamp'),
                    "relevance_score": relevance_score,
                    "matching_messages": matching_messages[:3]  # Top 3
                })

        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)

        return {
            "query": query,
            "results": results[:5],  # Top 5 conversations
            "total_found": len(results)
        }

    async def _search_conversations(self, query: str) -> Dict[str, Any]:
        """General search through conversations."""
        return await self._find_specific_memory(query)

    def _get_conversation_patterns(self) -> Dict[str, Any]:
        """Return extracted conversation patterns."""
        return {
            "patterns": self.patterns_cache,
            "summary": {
                "total_conversations": len(self.conversations_cache),
                "top_challenges": list(self.patterns_cache.get(
                    "challenges", {}
                ).keys())[:3],
                "top_values": list(self.patterns_cache.get(
                    "values", {}
                ).keys())[:3],
                "top_emotions": list(self.patterns_cache.get(
                    "emotions", {}
                ).keys())[:3]
            }
        }

    def _get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of all conversations."""
        if not self.conversations_cache:
            return {"summary": "No conversation history found"}

        total_messages = sum(
            len(conv.get('messages', []))
            for conv in self.conversations_cache
        )

        # Get date range
        timestamps = [
            conv.get('timestamp', '')
            for conv in self.conversations_cache
            if conv.get('timestamp')
        ]

        date_range = {
            "earliest": min(timestamps) if timestamps else None,
            "latest": max(timestamps) if timestamps else None
        }

        return {
            "total_conversations": len(self.conversations_cache),
            "total_messages": total_messages,
            "date_range": date_range,
            "patterns": self._get_conversation_patterns()
        }

"""Tests for coaching behavior analyzers."""

import pytest
from unittest.mock import AsyncMock, patch
import json

from src.evaluation.analyzers.specificity import SpecificityPushAnalyzer
from src.evaluation.analyzers.action import ActionOrientationAnalyzer
from src.evaluation.analyzers.emotional import EmotionalPresenceAnalyzer
from src.evaluation.analyzers.framework import FrameworkDisruptionAnalyzer


class TestSpecificityPushAnalyzer:
    """Test specificity push analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create specificity push analyzer for testing."""
        from unittest.mock import Mock
        mock_llm = Mock()
        return SpecificityPushAnalyzer(llm_service=mock_llm)
    
    @pytest.mark.asyncio
    async def test_specificity_push_analyzer_weak_coaching(self, analyzer):
        """Test analyzer detects weak coaching that accepts vague goals."""
        context = ["User: I want to be more productive"]
        response = "That's a great goal! How can I help you achieve that?"
        
        analyzer.llm_service.complete = AsyncMock(return_value=json.dumps({
            "score": 0.2,
            "reasoning": "accepts vague goal without pushing for clarity"
        }))
        
        score = await analyzer.analyze(response, context)
        
        assert score.value < 0.3
        assert "accepts vague goal" in score.reasoning
        assert score.analyzer_name == "SpecificityPush"
    
    @pytest.mark.asyncio
    async def test_specificity_push_analyzer_strong_coaching(self, analyzer):
        """Test analyzer detects strong coaching that challenges vagueness."""
        context = ["User: I want to be more productive"]
        response = "Productive is a big word. What's one specific thing you'd do differently if you were 'productive' today?"
        
        analyzer.llm_service.complete = AsyncMock(return_value=json.dumps({
            "score": 0.8,
            "reasoning": "challenges vagueness with specific follow-up question"
        }))
        
        score = await analyzer.analyze(response, context)
        
        assert score.value > 0.7
        assert "challenges vagueness" in score.reasoning
        assert score.analyzer_name == "SpecificityPush"


class TestActionOrientationAnalyzer:
    """Test action orientation analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create action orientation analyzer for testing."""
        from unittest.mock import Mock
        mock_llm = Mock()
        return ActionOrientationAnalyzer(llm_service=mock_llm)
    
    @pytest.mark.asyncio
    async def test_action_orientation_weak(self, analyzer):
        """Test detection of weak action orientation."""
        context = ["User: I'm struggling with my team meetings"]
        response = "Team meetings can be challenging. Tell me more about what's bothering you."
        
        analyzer.llm_service.complete = AsyncMock(return_value=json.dumps({
            "score": 0.3,
            "reasoning": "focuses on exploration without driving toward concrete action"
        }))
        
        score = await analyzer.analyze(response, context)
        
        assert score.value < 0.5
        assert "without driving toward" in score.reasoning
    
    @pytest.mark.asyncio
    async def test_action_orientation_strong(self, analyzer):
        """Test detection of strong action orientation."""
        context = ["User: I'm struggling with my team meetings"]
        response = "What's one specific thing you could do differently in tomorrow's team meeting?"
        
        analyzer.llm_service.complete = AsyncMock(return_value=json.dumps({
            "score": 0.9,
            "reasoning": "immediately pushes toward specific actionable commitment"
        }))
        
        score = await analyzer.analyze(response, context)
        
        assert score.value > 0.8
        assert "actionable commitment" in score.reasoning


class TestEmotionalPresenceAnalyzer:
    """Test emotional presence analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create emotional presence analyzer for testing."""
        from unittest.mock import Mock
        mock_llm = Mock()
        return EmotionalPresenceAnalyzer(llm_service=mock_llm)
    
    @pytest.mark.asyncio
    async def test_emotional_presence_missing(self, analyzer):
        """Test detection of missing emotional acknowledgment."""
        context = ["User: I'm really frustrated with my boss's micromanaging"]
        response = "Let's create a framework for managing up to your boss more effectively."
        
        analyzer.llm_service.complete = AsyncMock(return_value=json.dumps({
            "score": 0.1,
            "reasoning": "jumps to solution without acknowledging frustration"
        }))
        
        score = await analyzer.analyze(response, context)
        
        assert score.value < 0.3
        assert "without acknowledging" in score.reasoning
    
    @pytest.mark.asyncio
    async def test_emotional_presence_strong(self, analyzer):
        """Test detection of strong emotional acknowledgment."""
        context = ["User: I'm really frustrated with my boss's micromanaging"]
        response = "That frustration sounds exhausting. What's it like to work under that kind of scrutiny?"
        
        analyzer.llm_service.complete = AsyncMock(return_value=json.dumps({
            "score": 0.9,
            "reasoning": "directly acknowledges emotion and invites deeper exploration"
        }))
        
        score = await analyzer.analyze(response, context)
        
        assert score.value > 0.8
        assert "acknowledges emotion" in score.reasoning


class TestFrameworkDisruptionAnalyzer:
    """Test framework disruption analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create framework disruption analyzer for testing."""
        from unittest.mock import Mock
        mock_llm = Mock()
        return FrameworkDisruptionAnalyzer(llm_service=mock_llm)
    
    @pytest.mark.asyncio
    async def test_framework_disruption_weak(self, analyzer):
        """Test detection of weak framework disruption."""
        context = ["User: I think I need a better system for prioritizing tasks"]
        response = "Let's create a comprehensive prioritization framework with multiple criteria."
        
        analyzer.llm_service.complete = AsyncMock(return_value=json.dumps({
            "score": 0.2,
            "reasoning": "reinforces framework thinking instead of disrupting it"
        }))
        
        score = await analyzer.analyze(response, context)
        
        assert score.value < 0.4
        assert "reinforces framework" in score.reasoning
    
    @pytest.mark.asyncio
    async def test_framework_disruption_strong(self, analyzer):
        """Test detection of strong framework disruption."""
        context = ["User: I think I need a better system for prioritizing tasks"]
        response = "What if you threw away all your systems for one day? What would you naturally gravitate toward?"
        
        analyzer.llm_service.complete = AsyncMock(return_value=json.dumps({
            "score": 0.9,
            "reasoning": "disrupts system-thinking by inviting experimentation"
        }))
        
        score = await analyzer.analyze(response, context)
        
        assert score.value > 0.8
        assert "disrupts system-thinking" in score.reasoning
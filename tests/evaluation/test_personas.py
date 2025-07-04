"""Tests for PM personas and conversation generator."""

import pytest
from unittest.mock import AsyncMock, Mock

from src.evaluation.personas.framework_rigid import FrameworkRigidPersona
from src.evaluation.personas.control_freak import ControlFreakPersona
from src.evaluation.personas.legacy_builder import LegacyBuilderPersona
from src.evaluation.generator import ConversationGenerator


class TestFrameworkRigidPersona:
    """Test framework rigid persona behavior."""
    
    @pytest.fixture
    def persona(self):
        """Create framework rigid persona for testing."""
        return FrameworkRigidPersona()
    
    @pytest.mark.asyncio
    async def test_framework_rigid_resistance_patterns(self, persona):
        """Test framework rigid persona shows resistance patterns."""
        # Coach tries to disrupt with experimentation
        coach_message = "What if you threw away all your planning frameworks for one day?"
        context = ["User: I need a better way to prioritize my product roadmap"]
        
        response = await persona.respond(coach_message, context)
        
        # Should show intellectual avoidance while mentioning task
        assert any(word in response.lower() for word in ["thinking", "analysis", "user research", "file organization", "team communication", "roadmap", "performance"])
        assert any(word in response.lower() for word in ["think", "approach", "model", "framework"])
        assert persona.resistance_level > 0.7
    
    @pytest.mark.asyncio
    async def test_framework_rigid_breakthrough_detection(self, persona):
        """Test framework rigid persona can detect effective challenges."""
        # Effective challenge that pushes for action over thinking
        coach_message = "What if you tested this with customers instead of thinking about it more?"
        context = ["User: I think I should work on the user research analysis"]
        
        # Simulate multiple effective challenges - check if challenge is detected
        effective_count = 0
        for _ in range(6):  # Try more iterations
            if persona.detects_effective_challenge(coach_message):
                effective_count += 1
            await persona.respond(coach_message, context)
        
        # Should detect effective challenges and reduce resistance
        assert effective_count > 0  # At least some challenges detected
        assert persona.interaction_count >= 4


class TestControlFreakPersona:
    """Test control freak persona behavior."""
    
    @pytest.fixture
    def persona(self):
        """Create control freak persona for testing."""
        return ControlFreakPersona()
    
    @pytest.mark.asyncio
    async def test_control_freak_resistance_patterns(self, persona):
        """Test control freak persona shows procrastination and fear patterns."""
        coach_message = "What if you started working on this today instead of waiting?"
        context = ["User: I think I should focus on organizing my files"]
        
        response = await persona.respond(coach_message, context)
        
        # Should show procrastination or fear patterns with task reference
        assert any(word in response.lower() for word in ["wait", "tomorrow", "proper", "right", "afraid", "wrong", "waste", "file", "user research", "team", "roadmap", "performance", "analytics", "collaboration", "documentation"])
        assert persona.resistance_level > 0.7
    
    @pytest.mark.asyncio 
    async def test_control_freak_perfectionist_language(self, persona):
        """Test control freak uses procrastination and fear language patterns."""
        coach_message = "Ship it today, even if it's not perfect."
        context = ["User: This feature could be 10% better if I spend another week on it"]
        
        response = await persona.respond(coach_message, context)
        
        # Should show procrastination/fear patterns with task references
        assert any(word in response.lower() for word in ["wait", "tomorrow", "proper", "afraid", "wrong", "waste", "half-baked", "file", "research", "team", "roadmap", "performance", "analytics"])


class TestLegacyBuilderPersona:
    """Test legacy builder persona behavior."""
    
    @pytest.fixture
    def persona(self):
        """Create legacy builder persona for testing."""
        return LegacyBuilderPersona()
    
    @pytest.mark.asyncio
    async def test_legacy_builder_future_focus(self, persona):
        """Test legacy builder deflects to vision thinking."""
        coach_message = "What's the most important thing you could work on today?"
        context = ["User: I want to focus on the team communication issue"]
        
        response = await persona.respond(coach_message, context)
        
        # Should deflect to vision language while mentioning task
        assert any(word in response.lower() for word in ["vision", "transformative", "game-changing", "revolutionary", "strategic", "case study", "team", "communication", "file", "research", "big picture", "industry-defining", "legacy"])
        assert persona.resistance_level > 0.7
    
    @pytest.mark.asyncio
    async def test_legacy_builder_avoids_present_feelings(self, persona):
        """Test legacy builder avoids immediate execution focus."""
        coach_message = "What's the immediate problem you need to solve today?"
        context = ["User: I'm considering the API performance fixes"]
        
        response = await persona.respond(coach_message, context)
        
        # Should deflect to vision while mentioning task
        assert any(word in response.lower() for word in ["vision", "transformational", "strategic", "game-changing", "api", "performance", "file", "research", "big picture", "industry-defining", "legacy", "revolutionary"])


class TestConversationGenerator:
    """Test conversation generator with PM personas."""
    
    @pytest.fixture
    def mock_coach(self):
        """Mock coach for testing."""
        coach = Mock()
        coach.process_message = AsyncMock()
        return coach
    
    @pytest.fixture
    def generator(self, mock_coach):
        """Create conversation generator for testing."""
        return ConversationGenerator(coach=mock_coach)
    
    @pytest.mark.asyncio
    async def test_pm_persona_conversations(self, generator, mock_coach):
        """Test generating conversations with PM personas."""
        # Mock coach responses with AsyncMock
        mock_coach.process_message = AsyncMock(return_value=Mock(content="That sounds important. What specifically would success look like?"))
        
        # Test with Framework Rigid persona
        framework_rigid = FrameworkRigidPersona()
        convo1 = await generator.generate_conversation(
            persona=framework_rigid,
            scenario="morning_goal_setting",
            min_exchanges=5
        )
        
        # Should see resistance patterns
        conversation_text = " ".join([msg.get("content", "") for msg in convo1.messages])
        assert any(word in conversation_text.lower() for word in ["structured", "approach", "framework", "systematic"])
        assert framework_rigid.resistance_level > 0.7
        
        # Test with Control Freak persona
        control_freak = ControlFreakPersona()
        convo2 = await generator.generate_conversation(
            persona=control_freak,
            scenario="evening_reflection",
            min_exchanges=5
        )
        
        conversation_text = " ".join([msg.get("content", "") for msg in convo2.messages])
        assert "perfect" in conversation_text.lower() or "quality" in conversation_text.lower()
        
    @pytest.mark.asyncio
    async def test_conversation_structure(self, generator, mock_coach):
        """Test generated conversation has proper structure."""
        # Mock coach response
        mock_coach.process_message.return_value = Mock(content="Test response")
        
        persona = FrameworkRigidPersona()
        conversation = await generator.generate_conversation(
            persona=persona,
            scenario="morning_goal_setting",
            min_exchanges=3
        )
        
        # Should have proper conversation structure
        assert hasattr(conversation, 'messages')
        assert len(conversation.messages) >= 6  # 3 exchanges = 6 messages minimum
        assert conversation.scenario == "morning_goal_setting"
        assert conversation.persona_type == "FrameworkRigid"
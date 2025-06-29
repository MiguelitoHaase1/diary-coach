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
        
        # Should absorb challenge into framework thinking
        assert any(word in response.lower() for word in ["structured", "approach", "framework", "systematic", "methodology", "process", "organize"])
        assert persona.resistance_level > 0.7
    
    @pytest.mark.asyncio
    async def test_framework_rigid_breakthrough_detection(self, persona):
        """Test framework rigid persona can detect effective challenges."""
        # Effective challenge that questions framework assumptions
        coach_message = "When you create frameworks, what are you trying to control?"
        context = ["User: I keep creating new systems but they don't seem to help"]
        
        # Simulate multiple effective challenges
        for _ in range(4):  # Breakthrough threshold is 4
            await persona.respond(coach_message, context)
        
        # Should eventually show breakthrough after repeated effective challenges
        assert persona.resistance_level < 0.7
        assert persona.interaction_count >= 4


class TestControlFreakPersona:
    """Test control freak persona behavior."""
    
    @pytest.fixture
    def persona(self):
        """Create control freak persona for testing."""
        return ControlFreakPersona()
    
    @pytest.mark.asyncio
    async def test_control_freak_resistance_patterns(self, persona):
        """Test control freak persona shows perfectionist resistance."""
        coach_message = "What if good enough is actually good enough?"
        context = ["User: I keep refining this presentation but it's never perfect"]
        
        response = await persona.respond(coach_message, context)
        
        # Should resist with perfectionist language (broader check)
        assert "quality" in response.lower() or "time" in response.lower() or any(word in response.lower() for word in ["perfect", "exactly", "refine", "better", "right", "flawlessly", "meticulously", "impeccably", "optimized", "refined"])
        assert persona.resistance_level > 0.7
    
    @pytest.mark.asyncio 
    async def test_control_freak_perfectionist_language(self, persona):
        """Test control freak uses perfectionist language patterns."""
        coach_message = "Ship it today, even if it's not perfect."
        context = ["User: This feature could be 10% better if I spend another week on it"]
        
        response = await persona.respond(coach_message, context)
        
        # Should show need for control and perfection
        assert "quality" in response.lower() or "time" in response.lower() or any(word in response.lower() for word in ["perfect", "right", "flawlessly", "exactly", "meticulously", "impeccably", "optimized", "refined"])


class TestLegacyBuilderPersona:
    """Test legacy builder persona behavior."""
    
    @pytest.fixture
    def persona(self):
        """Create legacy builder persona for testing."""
        return LegacyBuilderPersona()
    
    @pytest.mark.asyncio
    async def test_legacy_builder_future_focus(self, persona):
        """Test legacy builder deflects to future impact."""
        coach_message = "How are you feeling right now about this decision?"
        context = ["User: I'm torn between two product directions"]
        
        response = await persona.respond(coach_message, context)
        
        # Should deflect to future thinking
        assert any(word in response.lower() for word in ["future", "impact", "legacy", "long-term", "stronger"])
        assert persona.resistance_level > 0.7
    
    @pytest.mark.asyncio
    async def test_legacy_builder_avoids_present_feelings(self, persona):
        """Test legacy builder avoids present-moment emotional content."""
        coach_message = "What's the anxiety telling you right now?"
        context = ["User: I'm anxious about this product launch"]
        
        response = await persona.respond(coach_message, context)
        
        # Should avoid present feelings, redirect to future meaning
        assert "future" in response.lower() or "experience" in response.lower() or "stronger" in response.lower()


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
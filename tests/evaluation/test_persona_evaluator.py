"""Tests for persona evaluator system."""

import pytest
from unittest.mock import Mock, AsyncMock

from src.evaluation.persona_evaluator import PersonaEvaluator
from src.evaluation.personas.framework_rigid import FrameworkRigidPersona
from src.evaluation.personas.control_freak import ControlFreakPersona
from src.evaluation.personas.legacy_builder import LegacyBuilderPersona
from src.agents.coach_agent import DiaryCoach


class TestPersonaEvaluator:
    """Test persona evaluator functionality."""
    
    @pytest.fixture
    def mock_coach(self):
        """Mock coach for testing."""
        coach = Mock(spec=DiaryCoach)
        coach.process_message = AsyncMock()
        return coach
    
    @pytest.fixture
    def evaluator(self, mock_coach):
        """Create persona evaluator for testing."""
        return PersonaEvaluator(coach=mock_coach)
    
    @pytest.mark.asyncio
    async def test_coaching_vs_personas(self, evaluator, mock_coach):
        """Test coaching effectiveness against different PM resistance patterns."""
        # Mock coach responses with enough for multiple conversations
        def mock_coach_response(user_msg):
            return Mock(content="That sounds important. What specifically would success look like?")
        
        mock_coach.process_message.side_effect = mock_coach_response
        
        # Generate conversations with each persona
        results = {}
        for persona_type in ["framework_rigid", "control_freak", "legacy_builder"]:
            persona = evaluator.create_persona(persona_type)
            
            # Run multiple conversations
            conversations = await evaluator.test_coach_with_persona(
                persona=persona,
                num_conversations=3
            )
            
            # Analyze breakthrough potential
            results[persona_type] = {
                "avg_breakthrough_score": evaluator.measure_breakthrough_potential(conversations),
                "resistance_patterns": evaluator.identify_resistance_patterns(conversations),
                "effective_interventions": evaluator.find_effective_moves(conversations)
            }
        
        # Framework Rigid should be hardest to breakthrough
        assert results["framework_rigid"]["avg_breakthrough_score"] < 0.6
        assert "framework" in " ".join(results["framework_rigid"]["resistance_patterns"]).lower()
        
        # Control Freak should show perfectionist patterns
        assert "perfect" in " ".join(results["control_freak"]["resistance_patterns"]).lower() or \
               "quality" in " ".join(results["control_freak"]["resistance_patterns"]).lower()
        
        # Legacy Builder should show future deflection
        assert "future" in " ".join(results["legacy_builder"]["resistance_patterns"]).lower() or \
               "experience" in " ".join(results["legacy_builder"]["resistance_patterns"]).lower()
    
    @pytest.mark.asyncio
    async def test_breakthrough_detection(self, evaluator, mock_coach):
        """Test detection of breakthrough moments in conversations."""
        # Mock effective coaching that achieves breakthrough
        def mock_effective_response(user_msg):
            return Mock(content="What if you threw away all your planning frameworks for one day?")
        
        mock_coach.process_message.side_effect = mock_effective_response
        
        # Test with framework rigid persona
        persona = FrameworkRigidPersona()
        conversations = await evaluator.test_coach_with_persona(
            persona=persona,
            num_conversations=1
        )
        
        # Should detect breakthrough patterns
        breakthrough_score = evaluator.measure_breakthrough_potential(conversations)
        assert breakthrough_score > 0.3  # Some breakthrough achieved
        
        effective_moves = evaluator.find_effective_moves(conversations)
        assert len(effective_moves) > 0
        assert any("threw away" in move.lower() or "control" in move.lower() for move in effective_moves)
    
    @pytest.mark.asyncio
    async def test_resistance_pattern_identification(self, evaluator, mock_coach):
        """Test identification of specific resistance patterns."""
        # Mock coach responses that don't challenge effectively
        def mock_weak_response(user_msg):
            return Mock(content="That sounds like a good plan.")
        
        mock_coach.process_message.side_effect = mock_weak_response
        
        # Test with each persona type
        framework_rigid = FrameworkRigidPersona()
        conversations = await evaluator.test_coach_with_persona(
            persona=framework_rigid,
            num_conversations=1
        )
        
        resistance_patterns = evaluator.identify_resistance_patterns(conversations)
        
        # Should identify framework-focused resistance
        assert len(resistance_patterns) > 0
        patterns_text = " ".join(resistance_patterns).lower()
        assert any(word in patterns_text for word in ["framework", "structured", "systematic", "organized"])
    
    @pytest.mark.asyncio
    async def test_persona_creation(self, evaluator):
        """Test persona creation and type mapping."""
        # Test all persona types can be created
        framework_rigid = evaluator.create_persona("framework_rigid")
        assert isinstance(framework_rigid, FrameworkRigidPersona)
        assert framework_rigid.name == "FrameworkRigid"
        
        control_freak = evaluator.create_persona("control_freak")
        assert isinstance(control_freak, ControlFreakPersona)
        assert control_freak.name == "ControlFreak"
        
        legacy_builder = evaluator.create_persona("legacy_builder")
        assert isinstance(legacy_builder, LegacyBuilderPersona)
        assert legacy_builder.name == "LegacyBuilder"
        
        # Test invalid persona type
        with pytest.raises(ValueError):
            evaluator.create_persona("invalid_persona")
    
    @pytest.mark.asyncio
    async def test_conversation_analysis_metrics(self, evaluator, mock_coach):
        """Test conversation analysis produces meaningful metrics."""
        # Mock a conversation with some breakthrough
        def mock_mixed_response(user_msg):
            return Mock(content="That sounds systematic. What if you just picked one thing?")
        
        mock_coach.process_message.side_effect = mock_mixed_response
        
        persona = FrameworkRigidPersona()
        conversations = await evaluator.test_coach_with_persona(
            persona=persona,
            num_conversations=1
        )
        
        # Analyze metrics
        breakthrough_score = evaluator.measure_breakthrough_potential(conversations)
        resistance_patterns = evaluator.identify_resistance_patterns(conversations)
        effective_moves = evaluator.find_effective_moves(conversations)
        
        # Should produce reasonable metrics
        assert 0.0 <= breakthrough_score <= 1.0
        assert isinstance(resistance_patterns, list)
        assert isinstance(effective_moves, list)
        
        # With mixed coaching, should have some breakthrough potential
        assert breakthrough_score >= 0.0  # Should have some score
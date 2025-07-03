"""Test configuration for cheap evaluation using GPT-4o-mini."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.llm_factory import LLMFactory, LLMTier
from src.evaluation.reporting.deep_thoughts import DeepThoughtsGenerator
from src.evaluation.personas.control_freak import ControlFreakPersona
from src.evaluation.personas.framework_rigid import FrameworkRigidPersona
from src.evaluation.personas.legacy_builder import LegacyBuilderPersona


class TestCheapEvaluation:
    """Test suite for cheap evaluation setup using GPT-4o-mini."""
    
    @pytest.fixture
    def cheap_llm_service(self):
        """Create a cheap LLM service for testing."""
        return LLMFactory.create_cheap_service()
    
    @pytest.fixture
    def cheap_deep_thoughts_generator(self, cheap_llm_service):
        """Create Deep Thoughts generator with cheap LLM service."""
        return DeepThoughtsGenerator(llm_service=cheap_llm_service, tier=LLMTier.CHEAP)
    
    @pytest.fixture
    def sample_conversation_history(self):
        """Sample conversation history for testing."""
        return [
            {"role": "user", "content": "I need to organize my files today."},
            {"role": "assistant", "content": "What makes organizing files feel important right now?"},
            {"role": "user", "content": "I just feel like everything is messy and I can't focus."},
            {"role": "assistant", "content": "What would happen if you left the files as they are and tackled something else first?"}
        ]
    
    @pytest.mark.asyncio
    async def test_cheap_deep_thoughts_generation(self, cheap_deep_thoughts_generator, sample_conversation_history):
        """Test that cheap Deep Thoughts generation works."""
        # Mock the LLM service to avoid actual API calls in tests
        cheap_deep_thoughts_generator.llm_service.generate_response = AsyncMock(
            return_value="# Deep Thoughts: Test Analysis\n\n## Core Problem\nTest problem analysis."
        )
        
        result = await cheap_deep_thoughts_generator.generate_deep_thoughts(
            conversation_history=sample_conversation_history,
            conversation_id="test_cheap_001"
        )
        
        assert result is not None
        assert "Deep Thoughts" in result
        assert cheap_deep_thoughts_generator.tier == LLMTier.CHEAP
    
    @pytest.mark.asyncio
    async def test_persona_with_cheap_llm(self, cheap_llm_service):
        """Test that personas work with cheap LLM service."""
        persona = ControlFreakPersona()
        
        # Mock LLM service for persona if it uses one
        if hasattr(persona, 'llm_service'):
            persona.llm_service = cheap_llm_service
        
        response = await persona.respond("What's your biggest priority today?", [])
        
        assert response is not None
        assert len(response) > 0
        
        # Check that response contains expected procrastination or fear patterns
        fear_keywords = ["wait", "proper time", "wrong", "waste", "afraid", "tomorrow"]
        assert any(keyword in response.lower() for keyword in fear_keywords)
    
    @pytest.mark.asyncio
    async def test_all_personas_cheap_mode(self, cheap_llm_service):
        """Test all personas in cheap mode."""
        personas = [
            ControlFreakPersona(),
            FrameworkRigidPersona(), 
            LegacyBuilderPersona()
        ]
        
        for persona in personas:
            if hasattr(persona, 'llm_service'):
                persona.llm_service = cheap_llm_service
            
            response = await persona.respond("What should we focus on?", [])
            assert response is not None
            assert len(response) > 10  # Ensure non-trivial response
    
    def test_llm_factory_cheap_creation(self):
        """Test that LLM factory creates cheap services correctly."""
        cheap_service = LLMFactory.create_cheap_service()
        
        assert cheap_service is not None
        assert cheap_service.get_model_tier() == "cheap"
    
    def test_model_tier_configurations(self):
        """Test that different tiers are configured correctly."""
        cheap = LLMFactory.create_cheap_service()
        standard = LLMFactory.create_standard_service()
        premium = LLMFactory.create_premium_service()
        
        assert cheap.get_model_tier() == "cheap"
        assert standard.get_model_tier() == "standard" 
        assert premium.get_model_tier() == "premium"
    
    @pytest.mark.asyncio
    async def test_cheap_vs_premium_deep_thoughts(self, sample_conversation_history):
        """Test that cheap and premium Deep Thoughts generators work differently."""
        cheap_generator = DeepThoughtsGenerator(tier=LLMTier.CHEAP)
        premium_generator = DeepThoughtsGenerator(tier=LLMTier.PREMIUM)
        
        # Mock both services
        cheap_generator.llm_service.generate_response = AsyncMock(
            return_value="# Cheap Analysis\nBasic insight."
        )
        premium_generator.llm_service.generate_response = AsyncMock(
            return_value="# Premium Analysis\nDeep breakthrough insight."
        )
        
        cheap_result = await cheap_generator.generate_deep_thoughts(
            conversation_history=sample_conversation_history,
            conversation_id="test_cheap"
        )
        
        premium_result = await premium_generator.generate_deep_thoughts(
            conversation_history=sample_conversation_history,
            conversation_id="test_premium"
        )
        
        assert "Cheap Analysis" in cheap_result
        assert "Premium Analysis" in premium_result
        assert cheap_generator.tier == LLMTier.CHEAP
        assert premium_generator.tier == LLMTier.PREMIUM


if __name__ == "__main__":
    pytest.main([__file__])
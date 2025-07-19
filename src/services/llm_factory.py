"""Factory for creating LLM services with different tiers."""

from typing import Optional, Union
from enum import Enum

from src.services.llm_service import AnthropicService
from src.services.openai_service import OpenAIService, OPENAI_AVAILABLE
from src.config import get_model_for_tier, ModelProvider


class LLMTier(Enum):
    """Available LLM tiers for different use cases."""
    CHEAP = "cheap"        # GPT-4o-mini for frequent testing
    STANDARD = "standard"  # Claude Sonnet for regular use
    PREMIUM = "premium"    # Claude Opus for high-quality analysis
    O3 = "o3"             # GPT o3-mini for Deep Thoughts (cheaper than Opus)


class LLMFactory:
    """Factory for creating LLM services based on tier and use case."""
    
    @staticmethod
    def create_service(
        tier: LLMTier,
        api_key: Optional[str] = None,
        openai_key: Optional[str] = None
    ) -> Union[AnthropicService, OpenAIService]:
        """Create an LLM service based on tier.
        
        Args:
            tier: The LLM tier to use
            api_key: Anthropic API key (optional)
            openai_key: OpenAI API key (optional)
            
        Returns:
            Appropriate LLM service instance
            
        Raises:
            ValueError: If tier is not supported or required dependencies missing
        """
        tier_str = tier.value
        
        if tier == LLMTier.CHEAP:
            if not OPENAI_AVAILABLE:
                # Fallback to cheap Anthropic model
                model = get_model_for_tier(tier_str, ModelProvider.ANTHROPIC)
                return AnthropicService(api_key, model=model)
            model = get_model_for_tier(tier_str, ModelProvider.OPENAI)
            return OpenAIService(api_key=openai_key, model=model)
        
        elif tier == LLMTier.STANDARD:
            model = get_model_for_tier(tier_str, ModelProvider.ANTHROPIC)
            return AnthropicService(api_key, model=model)
        
        elif tier == LLMTier.PREMIUM:
            model = get_model_for_tier(tier_str, ModelProvider.ANTHROPIC)
            return AnthropicService(api_key, model=model)
        
        elif tier == LLMTier.O3:
            if not OPENAI_AVAILABLE:
                # Fallback to premium Anthropic model
                model = get_model_for_tier("premium", ModelProvider.ANTHROPIC)
                return AnthropicService(api_key, model=model)
            # TODO: Switch to "o3-mini" once access is granted
            # For now, use gpt-4o-2024-11-20 (latest available version)
            model = get_model_for_tier("premium", ModelProvider.OPENAI)
            return OpenAIService(api_key=openai_key, model=model)
        
        else:
            raise ValueError(f"Unsupported LLM tier: {tier}")
    
    @staticmethod
    def create_cheap_service(
        api_key: Optional[str] = None,
        openai_key: Optional[str] = None
    ) -> Union[AnthropicService, OpenAIService]:
        """Create a cheap LLM service for frequent testing."""
        return LLMFactory.create_service(LLMTier.CHEAP, api_key, openai_key)
    
    @staticmethod
    def create_standard_service(api_key: Optional[str] = None) -> AnthropicService:
        """Create a standard LLM service for regular use."""
        return LLMFactory.create_service(LLMTier.STANDARD, api_key)
    
    @staticmethod
    def create_premium_service(api_key: Optional[str] = None) -> AnthropicService:
        """Create a premium LLM service for high-quality analysis."""
        return LLMFactory.create_service(LLMTier.PREMIUM, api_key)
    
    @staticmethod
    def create_o3_service(
        api_key: Optional[str] = None,
        openai_key: Optional[str] = None
    ) -> Union[AnthropicService, OpenAIService]:
        """Create an O3 LLM service for Deep Thoughts analysis."""
        return LLMFactory.create_service(LLMTier.O3, api_key, openai_key)
"""Factory for creating LLM services with different tiers."""

from typing import Optional, Union
from enum import Enum

from src.services.llm_service import AnthropicService
from src.services.openai_service import OpenAIService, OPENAI_AVAILABLE


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
        if tier == LLMTier.CHEAP:
            if not OPENAI_AVAILABLE:
                # Fallback to cheap Anthropic model
                return AnthropicService.create_cheap_service(api_key)
            return OpenAIService(api_key=openai_key, model="gpt-4o-mini")
        
        elif tier == LLMTier.STANDARD:
            return AnthropicService.create_standard_service(api_key)
        
        elif tier == LLMTier.PREMIUM:
            return AnthropicService.create_premium_service(api_key)
        
        elif tier == LLMTier.O3:
            if not OPENAI_AVAILABLE:
                # Fallback to premium Anthropic model
                return AnthropicService.create_premium_service(api_key)
            return OpenAIService(api_key=openai_key, model="o3")
        
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
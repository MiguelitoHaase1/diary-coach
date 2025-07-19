"""Centralized model configuration and constants."""

from dataclasses import dataclass
from typing import Dict
from enum import Enum


class ModelProvider(Enum):
    """Supported model providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    provider: ModelProvider
    input_cost_per_million: float
    output_cost_per_million: float
    tier: str
    max_context_tokens: int = 200000  # Default for most models
    default_max_output: int = 1500
    default_temperature: float = 0.7


# Centralized model configurations
MODEL_CONFIGS: Dict[str, ModelConfig] = {
    # Anthropic models
    "claude-3-opus-20240229": ModelConfig(
        name="claude-3-opus-20240229",
        provider=ModelProvider.ANTHROPIC,
        input_cost_per_million=15.0,
        output_cost_per_million=75.0,
        tier="premium",
        max_context_tokens=200000,
        default_max_output=4096
    ),
    "claude-opus-4-20250514": ModelConfig(
        name="claude-opus-4-20250514",
        provider=ModelProvider.ANTHROPIC,
        input_cost_per_million=15.0,
        output_cost_per_million=75.0,
        tier="premium",
        max_context_tokens=200000,
        default_max_output=4096
    ),
    "claude-3-5-sonnet-20241022": ModelConfig(
        name="claude-3-5-sonnet-20241022",
        provider=ModelProvider.ANTHROPIC,
        input_cost_per_million=3.0,
        output_cost_per_million=15.0,
        tier="standard",
        max_context_tokens=200000,
        default_max_output=2048
    ),
    "claude-sonnet-4-20250514": ModelConfig(
        name="claude-sonnet-4-20250514",
        provider=ModelProvider.ANTHROPIC,
        input_cost_per_million=3.0,
        output_cost_per_million=15.0,
        tier="standard",
        max_context_tokens=200000,
        default_max_output=2048
    ),
    "claude-3-haiku-20240307": ModelConfig(
        name="claude-3-haiku-20240307",
        provider=ModelProvider.ANTHROPIC,
        input_cost_per_million=0.25,
        output_cost_per_million=1.25,
        tier="cheap",
        max_context_tokens=200000,
        default_max_output=1024
    ),
    
    # OpenAI models
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider=ModelProvider.OPENAI,
        input_cost_per_million=0.15,
        output_cost_per_million=0.6,
        tier="cheap",
        max_context_tokens=128000,
        default_max_output=1024
    ),
    "gpt-4o-2024-11-20": ModelConfig(
        name="gpt-4o-2024-11-20",
        provider=ModelProvider.OPENAI,
        input_cost_per_million=2.5,
        output_cost_per_million=10.0,
        tier="premium",
        max_context_tokens=128000,
        default_max_output=4096
    ),
    "o3-mini": ModelConfig(
        name="o3-mini",
        provider=ModelProvider.OPENAI,
        input_cost_per_million=1.0,  # Estimated
        output_cost_per_million=4.0,  # Estimated
        tier="premium",
        max_context_tokens=128000,
        default_max_output=4096
    )
}


# Model tier mappings
TIER_MODELS = {
    "cheap": {
        ModelProvider.ANTHROPIC: "claude-3-haiku-20240307",
        ModelProvider.OPENAI: "gpt-4o-mini"
    },
    "standard": {
        ModelProvider.ANTHROPIC: "claude-sonnet-4-20250514",
        ModelProvider.OPENAI: None  # No standard tier for OpenAI
    },
    "premium": {
        ModelProvider.ANTHROPIC: "claude-opus-4-20250514",
        ModelProvider.OPENAI: "gpt-4o-2024-11-20"
    },
    "o3": {
        ModelProvider.ANTHROPIC: "claude-3-opus-20240229",  # Fallback
        ModelProvider.OPENAI: "o3-mini"  # When available
    }
}


# Agent-specific model recommendations
AGENT_MODEL_RECOMMENDATIONS = {
    "coach": "standard",
    "memory": "cheap",
    "mcp": "cheap",
    "personal_content": "cheap",
    "orchestrator": "standard",
    "reporter": "premium",
    "evaluator": "standard"
}


def get_model_for_tier(tier: str, provider: ModelProvider) -> str:
    """Get the model name for a given tier and provider.
    
    Args:
        tier: The tier (cheap, standard, premium, o3)
        provider: The model provider
        
    Returns:
        Model name string
        
    Raises:
        ValueError: If tier/provider combination not supported
    """
    if tier not in TIER_MODELS:
        raise ValueError(f"Unknown tier: {tier}")
    
    model = TIER_MODELS[tier].get(provider)
    if model is None:
        raise ValueError(
            f"No {provider.value} model available for tier: {tier}"
        )
    
    return model


def get_model_config(model_name: str) -> ModelConfig:
    """Get configuration for a specific model.
    
    Args:
        model_name: The model name
        
    Returns:
        ModelConfig object
        
    Raises:
        ValueError: If model not found
    """
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model: {model_name}")
    
    return MODEL_CONFIGS[model_name]


def calculate_cost(
    model_name: str, 
    input_tokens: int, 
    output_tokens: int
) -> float:
    """Calculate cost for a model usage.
    
    Args:
        model_name: The model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Cost in dollars
    """
    config = get_model_config(model_name)
    
    input_cost = (input_tokens / 1_000_000) * config.input_cost_per_million
    output_cost = (output_tokens / 1_000_000) * config.output_cost_per_million
    
    return input_cost + output_cost

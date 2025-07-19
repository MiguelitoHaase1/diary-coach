"""Configuration package for diary coach system."""

from .models import (
    ModelProvider,
    ModelConfig,
    MODEL_CONFIGS,
    TIER_MODELS,
    AGENT_MODEL_RECOMMENDATIONS,
    get_model_for_tier,
    get_model_config,
    calculate_cost
)

__all__ = [
    "ModelProvider",
    "ModelConfig",
    "MODEL_CONFIGS",
    "TIER_MODELS",
    "AGENT_MODEL_RECOMMENDATIONS",
    "get_model_for_tier",
    "get_model_config",
    "calculate_cost"
]
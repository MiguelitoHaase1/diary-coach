"""Prompt management utilities for consistent prompt loading across the system."""

from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum


class PromptContext(Enum):
    """Available prompt contexts for dynamic selection."""
    MORNING = "morning"
    EVENING = "evening"
    DEFAULT = "default"


@dataclass
class PromptMetadata:
    """Metadata for a prompt file."""
    name: str
    path: Path
    context: Optional[PromptContext] = None
    priority: int = 0


class PromptLoader:
    """Centralized prompt loader to ensure consistency across all agents."""

    _cache: Dict[str, str] = {}
    _registry: Dict[str, PromptMetadata] = {}

    @classmethod
    def load_prompt(cls, prompt_name: str) -> str:
        """Load a prompt from the prompts directory.

        Args:
            prompt_name: Name of the prompt file (without .md extension)

        Returns:
            The prompt content as a string

        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        # Use cache if available
        if prompt_name in cls._cache:
            return cls._cache[prompt_name]

        # Construct path to prompt file
        prompts_dir = Path(__file__).parent
        prompt_path = prompts_dir / f"{prompt_name}.md"

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        # Load and cache the prompt
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        cls._cache[prompt_name] = content
        return content

    @classmethod
    def get_coach_system_prompt(cls) -> str:
        """Get the main coaching system prompt."""
        return cls.load_prompt("coach_system_prompt")

    @classmethod
    def get_coach_morning_protocol(cls) -> str:
        """Get the morning protocol additions for the coach."""
        return cls.load_prompt("coach_morning_protocol")

    @classmethod
    def get_deep_thoughts_system_prompt(cls) -> str:
        """Get the Deep Thoughts generator system prompt."""
        return cls.load_prompt("deep_thoughts_system_prompt")

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the prompt cache (useful for testing)."""
        cls._cache.clear()

    @classmethod
    def register_prompt(cls, name: str, path: Path,
                        context: Optional[PromptContext] = None,
                        priority: int = 0) -> None:
        """Register a prompt in the system.

        Args:
            name: Unique identifier for the prompt
            path: Path to the prompt file
            context: Optional context for the prompt
            priority: Priority for context-based selection
        """
        cls._registry[name] = PromptMetadata(
            name=name, path=path, context=context, priority=priority
        )

    @classmethod
    def get_available_prompts(cls) -> List[str]:
        """Get list of all available prompt names."""
        prompts_dir = Path(__file__).parent
        return [p.stem for p in prompts_dir.glob("*.md")]

    @classmethod
    def get_prompts_by_context(cls, context: PromptContext) -> List[PromptMetadata]:
        """Get all prompts for a specific context, sorted by priority."""
        prompts = [
            meta for meta in cls._registry.values()
            if meta.context == context
        ]
        return sorted(prompts, key=lambda x: x.priority, reverse=True)


# Convenience functions for easy imports
def get_coach_system_prompt() -> str:
    """Get the main coaching system prompt."""
    return PromptLoader.get_coach_system_prompt()


def get_coach_morning_protocol() -> str:
    """Get the morning protocol additions for the coach."""
    return PromptLoader.get_coach_morning_protocol()


def get_deep_thoughts_system_prompt() -> str:
    """Get the Deep Thoughts generator system prompt."""
    return PromptLoader.get_deep_thoughts_system_prompt()


def get_orchestrator_agent_prompt() -> str:
    """Get the Orchestrator agent system prompt."""
    return PromptLoader.load_prompt("orchestrator_agent_prompt")

"""Prompt management utilities for consistent prompt loading across the system."""

import os
from pathlib import Path
from typing import Dict, Optional


class PromptLoader:
    """Centralized prompt loader to ensure consistency across all agents."""
    
    _cache: Dict[str, str] = {}
    
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
    def get_deep_thoughts_system_prompt(cls) -> str:
        """Get the Deep Thoughts generator system prompt."""
        return cls.load_prompt("deep_thoughts_system_prompt")
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the prompt cache (useful for testing)."""
        cls._cache.clear()


# Convenience functions for easy imports
def get_coach_system_prompt() -> str:
    """Get the main coaching system prompt."""
    return PromptLoader.get_coach_system_prompt()

def get_deep_thoughts_system_prompt() -> str:
    """Get the Deep Thoughts generator system prompt."""
    return PromptLoader.get_deep_thoughts_system_prompt()
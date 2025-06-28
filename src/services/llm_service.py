"""LLM service integration with Anthropic API."""

import asyncio
import os
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic


class AnthropicError(Exception):
    """Custom exception for Anthropic API errors."""
    pass


class AnthropicService:
    """Async wrapper for Anthropic Claude API with token tracking."""
    
    # Pricing per token (approximate, adjust based on actual pricing)
    INPUT_COST_PER_TOKEN = 0.000003  # $3 per million input tokens
    OUTPUT_COST_PER_TOKEN = 0.000015  # $15 per million output tokens
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize Anthropic service.
        
        Args:
            api_key: Anthropic API key. If None, uses ANTHROPIC_API_KEY env var.
            model: Claude model to use for generation.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = AsyncAnthropic(api_key=self.api_key)
        
        # Usage tracking
        self.total_tokens = 0
        self.total_cost = 0.0
        self.session_cost = 0.0
        
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 200,
        temperature: float = 0.7
    ) -> str:
        """Generate response from Claude API with retry logic.
        
        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Response randomness (0-1)
            
        Returns:
            Generated response text
            
        Raises:
            AnthropicError: If API call fails after retries
        """
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Prepare API call parameters
                call_params = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": messages
                }
                
                if system_prompt:
                    call_params["system"] = system_prompt
                
                # Make API call
                response = await self.client.messages.create(**call_params)
                
                # Extract response text
                response_text = response.content[0].text
                
                # Track usage
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                total_tokens = input_tokens + output_tokens
                
                call_cost = (
                    input_tokens * self.INPUT_COST_PER_TOKEN +
                    output_tokens * self.OUTPUT_COST_PER_TOKEN
                )
                
                self.total_tokens += total_tokens
                self.total_cost += call_cost
                self.session_cost += call_cost
                
                return response_text
                
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Wait before retry with exponential backoff
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    break
        
        # All retries failed
        raise AnthropicError(f"API call failed after {max_retries} attempts: {last_error}")
    
    def reset_session_cost(self) -> float:
        """Reset session cost tracking and return previous value."""
        previous_cost = self.session_cost
        self.session_cost = 0.0
        return previous_cost
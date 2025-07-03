"""OpenAI service integration for cheap testing with GPT-4o-mini."""

import asyncio
import os
from typing import List, Dict, Any, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass


class OpenAIService:
    """Async wrapper for OpenAI API with token tracking for cheap testing."""
    
    # Pricing per token for GPT-4o-mini (approximate)
    INPUT_COST_PER_TOKEN = 0.00000015   # $0.15 per million input tokens
    OUTPUT_COST_PER_TOKEN = 0.0000006   # $0.60 per million output tokens
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
            model: OpenAI model to use for generation.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        
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
        """Generate response from OpenAI API with retry logic.
        
        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Response randomness (0-1)
            
        Returns:
            Generated response text
            
        Raises:
            OpenAIError: If API call fails after retries
        """
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Prepare messages for OpenAI format
                openai_messages = []
                
                if system_prompt:
                    openai_messages.append({"role": "system", "content": system_prompt})
                
                openai_messages.extend(messages)
                
                # Make API call
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                # Extract response text
                response_text = response.choices[0].message.content
                
                # Track usage
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
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
        raise OpenAIError(f"API call failed after {max_retries} attempts: {last_error}")
    
    def reset_session_cost(self) -> float:
        """Reset session cost tracking and return previous value."""
        previous_cost = self.session_cost
        self.session_cost = 0.0
        return previous_cost
    
    def get_model_tier(self) -> str:
        """Get the tier of the current model."""
        return "cheap"
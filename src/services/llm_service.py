"""LLM service integration with Anthropic API."""

import asyncio
import os
from typing import List, Dict, Optional
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from src.config import get_model_config, calculate_cost

# Load environment variables
load_dotenv()

# Try to import LangSmith for tracing
try:
    from langsmith import Client as LangSmithClient
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False

# Try to import OpenAI for GPT-4o-mini support


class AnthropicError(Exception):
    """Custom exception for Anthropic API errors."""
    pass


class AnthropicService:
    """Async wrapper for Anthropic Claude API with token tracking."""

    def __init__(self, api_key: Optional[str] = None,
                 model: str = "claude-sonnet-4-20250514",
                 use_subscription: bool = False):
        """Initialize Anthropic service.

        Args:
            api_key: Anthropic API key. If None, uses ANTHROPIC_API_KEY env var.
            model: Claude model to use for generation.
            use_subscription: If True, uses Claude subscription instead of API.
        """
        self.use_subscription = use_subscription

        if use_subscription:
            # For subscription usage, we don't need an API key
            self.api_key = None
            self.client = AsyncAnthropic()  # Uses default auth
        else:
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            self.client = AsyncAnthropic(api_key=self.api_key)

        self.model = model

        # Get model config from centralized configuration
        try:
            self.model_config = get_model_config(model)
        except ValueError:
            # Default to Sonnet 4 if model not found
            self.model_config = get_model_config("claude-sonnet-4-20250514")

        # Usage tracking
        self.total_tokens = 0
        self.total_cost = 0.0
        self.session_cost = 0.0

        # Initialize LangSmith client if available
        self.langsmith_client = None
        if LANGSMITH_AVAILABLE and os.getenv("LANGSMITH_API_KEY"):
            try:
                self.langsmith_client = LangSmithClient()
            except Exception as e:
                print(f"Warning: LangSmith initialization failed: {e}")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 200,
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
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

                if tools:
                    call_params["tools"] = tools

                # Make API call with optional LangSmith tracing
                if self.langsmith_client:
                    try:
                        from uuid import uuid4
                        # Create LangSmith run for this API call
                        run_id = str(uuid4())
                        self.langsmith_client.create_run(
                            id=run_id,
                            name="anthropic_api_call",
                            run_type="llm",
                            inputs={
                                "messages": messages,
                                "system_prompt": system_prompt,
                                "model": self.model,
                                "max_tokens": max_tokens,
                                "temperature": temperature
                            },
                            project_name=os.getenv(
                                "LANGSMITH_PROJECT", "diary-coach-debug")
                        )
                    except Exception as e:
                        print(f"LangSmith run creation failed: {e}")
                        run_id = None
                else:
                    run_id = None

                response = await self.client.messages.create(**call_params)

                # Extract response text - handle tool use responses
                response_text = ""
                for block in response.content:
                    if hasattr(block, 'type'):
                        if block.type == 'text':
                            response_text += block.text + "\n"
                        elif block.type in [
                            'server_tool_use', 'web_search_tool_result'
                        ]:
                            # Tool responses are in text blocks
                            continue
                # Fallback to old method if no text found
                if not response_text and response.content:
                    if hasattr(response.content[0], 'text'):
                        response_text = response.content[0].text

                # Track usage
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                total_tokens = input_tokens + output_tokens

                call_cost = calculate_cost(self.model, input_tokens, output_tokens)

                self.total_tokens += total_tokens
                self.total_cost += call_cost
                self.session_cost += call_cost

                # Update LangSmith run with results
                if self.langsmith_client and run_id:
                    try:
                        self.langsmith_client.update_run(
                            run_id=run_id,
                            outputs={"response": response_text},
                            extra={
                                "input_tokens": input_tokens,
                                "output_tokens": output_tokens,
                                "total_tokens": total_tokens,
                                "cost": call_cost,
                                "model": self.model
                            }
                        )
                    except Exception as e:
                        print(f"LangSmith run update failed: {e}")

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
        raise AnthropicError(
            f"API call failed after {max_retries} attempts: {last_error}"
        )

    def reset_session_cost(self) -> float:
        """Reset session cost tracking and return previous value."""
        previous_cost = self.session_cost
        self.session_cost = 0.0
        return previous_cost

    def get_model_tier(self) -> str:
        """Get the tier of the current model."""
        return self.model_config.tier

    @classmethod
    def create_cheap_service(
        cls, api_key: Optional[str] = None
    ) -> 'AnthropicService':
        """Create a cheap AnthropicService using Haiku model."""
        return cls(api_key=api_key, model="claude-3-haiku-20240307")

    @classmethod
    def create_premium_service(
        cls, api_key: Optional[str] = None
    ) -> 'AnthropicService':
        """Create a premium AnthropicService using Opus model."""
        return cls(api_key=api_key, model="claude-3-opus-20240229")

    @classmethod
    def create_standard_service(
        cls, api_key: Optional[str] = None
    ) -> 'AnthropicService':
        """Create a standard AnthropicService using Sonnet 4 model."""
        return cls(api_key=api_key, model="claude-sonnet-4-20250514")

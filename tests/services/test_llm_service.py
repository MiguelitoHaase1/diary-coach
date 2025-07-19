"""Tests for LLM service integration with Anthropic API."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.llm_service import AnthropicService, AnthropicError


class TestAnthropicService:
    """Test suite for AnthropicService async wrapper."""

    @pytest.mark.asyncio
    async def test_anthropic_service_basic_call(self):
        """Test basic LLM call with mocked response."""
        service = AnthropicService(api_key="test", model="claude-sonnet-4-20250514")
        
        # Mock the anthropic client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello! How can I help you today?")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 8
        
        service.client.messages.create = AsyncMock(return_value=mock_response)
        
        response = await service.generate_response(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="You are a helpful assistant"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert response == "Hello! How can I help you today?"

    @pytest.mark.asyncio
    async def test_anthropic_service_tracks_usage(self):
        """Test that service tracks token usage and costs."""
        service = AnthropicService(api_key="test")
        
        # Mock the anthropic client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 12
        
        service.client.messages.create = AsyncMock(return_value=mock_response)
        
        response = await service.generate_response(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        assert service.total_tokens == 27  # 15 + 12
        assert service.total_cost > 0
        assert service.session_cost > 0

    @pytest.mark.asyncio
    async def test_anthropic_service_handles_errors(self):
        """Test error handling for invalid API calls."""
        service = AnthropicService(api_key="invalid")
        
        # Mock the anthropic client to raise an exception
        service.client.messages.create = AsyncMock(
            side_effect=Exception("API Error: Invalid API key")
        )
        
        with pytest.raises(AnthropicError):
            await service.generate_response(messages=[])

    @pytest.mark.asyncio
    async def test_anthropic_service_retry_logic(self):
        """Test retry logic with temporary failures."""
        service = AnthropicService(api_key="test")
        
        # Mock first two calls to fail, third to succeed
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Success after retry")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5
        
        service.client.messages.create = AsyncMock(
            side_effect=[
                Exception("Temporary failure"),
                Exception("Another failure"),
                mock_response
            ]
        )
        
        response = await service.generate_response(
            messages=[{"role": "user", "content": "Test"}]
        )
        
        assert response == "Success after retry"
        assert service.client.messages.create.call_count == 3

    @pytest.mark.asyncio
    async def test_anthropic_service_multiple_calls(self):
        """Test cumulative token tracking across multiple calls."""
        service = AnthropicService(api_key="test")
        
        # Mock two different responses
        mock_response1 = MagicMock()
        mock_response1.content = [MagicMock(text="First response")]
        mock_response1.usage.input_tokens = 10
        mock_response1.usage.output_tokens = 5
        
        mock_response2 = MagicMock()
        mock_response2.content = [MagicMock(text="Second response")]
        mock_response2.usage.input_tokens = 8
        mock_response2.usage.output_tokens = 7
        
        service.client.messages.create = AsyncMock(
            side_effect=[mock_response1, mock_response2]
        )
        
        # Make two calls
        response1 = await service.generate_response(
            messages=[{"role": "user", "content": "First"}]
        )
        response2 = await service.generate_response(
            messages=[{"role": "user", "content": "Second"}]
        )
        
        assert response1 == "First response"
        assert response2 == "Second response"
        assert service.total_tokens == 30  # (10+5) + (8+7)
        assert service.session_cost > 0
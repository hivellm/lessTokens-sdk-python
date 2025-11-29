"""Tests for Anthropic provider"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.providers.anthropic import AnthropicProvider
from lesstokens_sdk.types import LLMConfig


@pytest.mark.unit
class TestAnthropicProvider:
    """Test suite for AnthropicProvider"""

    def test_init_success(self) -> None:
        """Test provider initialization."""
        with patch("lesstokens_sdk.providers.anthropic.AsyncAnthropic") as mock_client_class:
            provider = AnthropicProvider("test-key")
            assert provider.client is not None
            mock_client_class.assert_called_once_with(api_key="test-key")

    def test_init_missing_sdk(self) -> None:
        """Test provider initialization when Anthropic SDK is not installed."""
        with patch("lesstokens_sdk.providers.anthropic.AsyncAnthropic", None):
            with pytest.raises(ImportError) as exc_info:
                AnthropicProvider("test-key")
            assert "Anthropic SDK not installed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_chat_success(self) -> None:
        """Test successful chat completion."""
        mock_content = MagicMock()
        mock_content.text = "Test response"
        mock_content.type = "text"

        mock_message = MagicMock()
        mock_message.content = [mock_content]

        mock_usage = MagicMock()
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 5

        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_response.usage = mock_usage
        mock_response.model = "claude-3-opus-20240229"

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
                "max_tokens": 1024,
            }
            messages = [{"role": "user", "content": "Hello"}]

            result = await provider.chat(messages, config)

            assert result.content == "Test response"
            assert result.usage.prompt_tokens == 10
            assert result.usage.completion_tokens == 5
            assert result.metadata is not None
            assert result.metadata.provider == "anthropic"

    @pytest.mark.asyncio
    async def test_chat_with_system_role(self) -> None:
        """Test chat with system role (converted to user)."""
        mock_content = MagicMock()
        mock_content.text = "Test response"
        mock_content.type = "text"

        mock_usage = MagicMock()
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 5

        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_response.usage = mock_usage
        mock_response.model = "claude-3-opus-20240229"

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
            }
            messages = [{"role": "system", "content": "You are a helpful assistant"}]

            await provider.chat(messages, config)

            # Verify system role was converted to user
            call_args = mock_client.messages.create.call_args
            assert call_args is not None
            anthropic_messages = call_args[1]["messages"]
            assert anthropic_messages[0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_chat_without_usage(self) -> None:
        """Test chat completion without usage metadata."""
        mock_content = MagicMock()
        mock_content.text = "Test response"
        mock_content.type = "text"

        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_response.usage = None  # No usage
        mock_response.model = "claude-3-opus-20240229"

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
            }
            messages = [{"role": "user", "content": "Hello"}]

            result = await provider.chat(messages, config)

            assert result.content == "Test response"
            assert result.usage.prompt_tokens == 0
            assert result.usage.completion_tokens == 0

    @pytest.mark.asyncio
    async def test_chat_with_less_tokens_error(self) -> None:
        """Test chat re-throws LessTokensError."""
        error = LessTokensError("Test error", ErrorCodes.LLM_API_ERROR, 500)
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=error)

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
            }
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await provider.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    @pytest.mark.asyncio
    async def test_chat_api_error(self) -> None:
        """Test chat with Anthropic API error."""
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
            }
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await provider.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    @pytest.mark.asyncio
    async def test_chat_stream_success(self) -> None:
        """Test successful streaming chat completion."""
        # Mock stream events
        mock_delta_event = MagicMock()
        mock_delta_event.type = "content_block_delta"
        mock_delta_event.delta = MagicMock()
        mock_delta_event.delta.type = "text_delta"
        mock_delta_event.delta.text = "Hello"

        mock_stop_event = MagicMock()
        mock_stop_event.type = "message_stop"

        async def mock_stream():
            yield mock_delta_event
            yield mock_stop_event

        mock_final_message = MagicMock()
        mock_final_message.usage = MagicMock()
        mock_final_message.usage.input_tokens = 10
        mock_final_message.usage.output_tokens = 5

        mock_stream_obj = AsyncMock()
        mock_stream_obj.get_final_message = AsyncMock(return_value=mock_final_message)
        # Make it an async iterable
        mock_stream_obj.__aiter__ = lambda self: mock_stream()

        mock_client = AsyncMock()
        mock_client.messages.stream = AsyncMock(return_value=mock_stream_obj)

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
            }
            messages = [{"role": "user", "content": "Hello"}]

            chunks = []
            async for chunk in provider.chat_stream(messages, config):
                chunks.append(chunk)

            assert len(chunks) >= 2
            assert chunks[0].content == "Hello"
            assert chunks[0].done is False
            assert chunks[-1].done is True
            assert chunks[-1].usage is not None

    @pytest.mark.asyncio
    async def test_chat_stream_with_system_role(self) -> None:
        """Test streaming with system role (converted to user)."""
        mock_delta_event = MagicMock()
        mock_delta_event.type = "content_block_delta"
        mock_delta_event.delta = MagicMock()
        mock_delta_event.delta.type = "text_delta"
        mock_delta_event.delta.text = "Response"

        mock_stop_event = MagicMock()
        mock_stop_event.type = "message_stop"

        async def mock_stream():
            yield mock_delta_event
            yield mock_stop_event

        mock_final_message = MagicMock()
        mock_final_message.usage = None

        mock_stream_obj = AsyncMock()
        mock_stream_obj.get_final_message = AsyncMock(return_value=mock_final_message)
        mock_stream_obj.__aiter__ = lambda self: mock_stream()

        mock_client = AsyncMock()
        mock_client.messages.stream = AsyncMock(return_value=mock_stream_obj)

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
            }
            messages = [{"role": "system", "content": "You are a helpful assistant"}]

            chunks = []
            async for chunk in provider.chat_stream(messages, config):
                chunks.append(chunk)

            # Verify system role was converted to user
            call_args = mock_client.messages.stream.call_args
            assert call_args is not None
            anthropic_messages = call_args[1]["messages"]
            assert anthropic_messages[0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_chat_stream_without_final_message(self) -> None:
        """Test streaming without final message."""
        mock_delta_event = MagicMock()
        mock_delta_event.type = "content_block_delta"
        mock_delta_event.delta = MagicMock()
        mock_delta_event.delta.type = "text_delta"
        mock_delta_event.delta.text = "Hello"

        async def mock_stream():
            yield mock_delta_event

        mock_stream_obj = AsyncMock()
        # No get_final_message method
        del mock_stream_obj.get_final_message
        # Make it an async iterable
        mock_stream_obj.__aiter__ = lambda self: mock_stream()

        mock_client = AsyncMock()
        mock_client.messages.stream = AsyncMock(return_value=mock_stream_obj)

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
            }
            messages = [{"role": "user", "content": "Hello"}]

            chunks = []
            async for chunk in provider.chat_stream(messages, config):
                chunks.append(chunk)

            assert len(chunks) >= 1
            assert chunks[-1].done is True

    @pytest.mark.asyncio
    async def test_chat_stream_api_error(self) -> None:
        """Test streaming with API error."""
        mock_client = AsyncMock()
        mock_client.messages.stream = AsyncMock(side_effect=Exception("Stream error"))

        with patch(
            "lesstokens_sdk.providers.anthropic.AsyncAnthropic",
            MagicMock(return_value=mock_client),
        ):
            provider = AnthropicProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "claude-3-opus-20240229",
            }
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                async for _ in provider.chat_stream(messages, config):
                    pass

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

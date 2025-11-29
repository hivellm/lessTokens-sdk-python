"""Tests for DeepSeek provider"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.providers.deepseek import DeepSeekProvider
from lesstokens_sdk.types import LLMConfig


@pytest.mark.unit
class TestDeepSeekProvider:
    """Test suite for DeepSeekProvider"""

    def test_init_success(self) -> None:
        """Test provider initialization."""
        with patch(
            "lesstokens_sdk.providers.deepseek.AsyncOpenAI"
        ) as mock_client_class:
            provider = DeepSeekProvider("test-key")
            assert provider.client is not None
            mock_client_class.assert_called_once_with(
                api_key="test-key", base_url="https://api.deepseek.com"
            )

    def test_init_missing_sdk(self) -> None:
        """Test provider initialization when OpenAI SDK is not installed."""
        with patch("lesstokens_sdk.providers.deepseek.AsyncOpenAI", None):
            with pytest.raises(ImportError) as exc_info:
                DeepSeekProvider("test-key")
            assert "OpenAI SDK not installed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_chat_success(self) -> None:
        """Test successful chat completion."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Test response"

        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 5
        mock_usage.total_tokens = 15

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        mock_response.model = "deepseek-chat"

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch(
            "lesstokens_sdk.providers.deepseek.AsyncOpenAI", return_value=mock_client
        ):
            provider = DeepSeekProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "deepseek-chat"}
            messages = [{"role": "user", "content": "Hello"}]

            result = await provider.chat(messages, config)

            assert result.content == "Test response"
            assert result.usage.total_tokens == 15
            assert result.metadata is not None
            assert result.metadata.provider == "deepseek"

    @pytest.mark.asyncio
    async def test_chat_no_response(self) -> None:
        """Test chat with no response from DeepSeek."""
        mock_response = MagicMock()
        mock_response.choices = []  # No choices

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch(
            "lesstokens_sdk.providers.deepseek.AsyncOpenAI", return_value=mock_client
        ):
            provider = DeepSeekProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "deepseek-chat"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await provider.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    @pytest.mark.asyncio
    async def test_chat_with_less_tokens_error(self) -> None:
        """Test chat re-throws LessTokensError."""
        error = LessTokensError("Test error", ErrorCodes.LLM_API_ERROR, 500)
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=error)

        with patch(
            "lesstokens_sdk.providers.deepseek.AsyncOpenAI", return_value=mock_client
        ):
            provider = DeepSeekProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "deepseek-chat"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await provider.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    @pytest.mark.asyncio
    async def test_chat_api_error(self) -> None:
        """Test chat with DeepSeek API error."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        with patch(
            "lesstokens_sdk.providers.deepseek.AsyncOpenAI", return_value=mock_client
        ):
            provider = DeepSeekProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "deepseek-chat"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await provider.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    @pytest.mark.asyncio
    async def test_chat_stream_success(self) -> None:
        """Test successful streaming chat completion."""
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = "Hello"
        mock_chunk1.choices[0].finish_reason = None
        mock_chunk1.usage = None

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = " World"
        mock_chunk2.choices[0].finish_reason = "stop"
        mock_chunk2.usage = MagicMock()
        mock_chunk2.usage.prompt_tokens = 10
        mock_chunk2.usage.completion_tokens = 2
        mock_chunk2.usage.total_tokens = 12

        async def mock_stream():
            yield mock_chunk1
            yield mock_chunk2

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())

        with patch(
            "lesstokens_sdk.providers.deepseek.AsyncOpenAI", return_value=mock_client
        ):
            provider = DeepSeekProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "deepseek-chat"}
            messages = [{"role": "user", "content": "Hello"}]

            chunks = []
            async for chunk in provider.chat_stream(messages, config):
                chunks.append(chunk)

            assert len(chunks) >= 2
            assert chunks[0].content == "Hello"
            assert chunks[-1].done is True

    @pytest.mark.asyncio
    async def test_chat_stream_api_error(self) -> None:
        """Test streaming with API error."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("Stream error")
        )

        with patch(
            "lesstokens_sdk.providers.deepseek.AsyncOpenAI", return_value=mock_client
        ):
            provider = DeepSeekProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "deepseek-chat"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                async for _ in provider.chat_stream(messages, config):
                    pass

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

"""Tests for OpenAI provider"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.providers.openai import OpenAIProvider
from lesstokens_sdk.types import LLMConfig


@pytest.mark.unit
class TestOpenAIProvider:
    """Test suite for OpenAIProvider"""

    def test_init_success(self) -> None:
        """Test provider initialization."""
        with patch("lesstokens_sdk.providers.openai.OpenAI", MagicMock()), patch(
            "lesstokens_sdk.providers.openai.AsyncOpenAI"
        ) as mock_client_class:
            provider = OpenAIProvider("test-key")
            assert provider.client is not None
            mock_client_class.assert_called_once_with(api_key="test-key", base_url=None)

    def test_init_with_base_url(self) -> None:
        """Test provider initialization with base URL."""
        with patch("lesstokens_sdk.providers.openai.OpenAI", MagicMock()), patch(
            "lesstokens_sdk.providers.openai.AsyncOpenAI"
        ) as mock_client_class:
            provider = OpenAIProvider("test-key", "https://custom.url")
            assert provider.client is not None
            mock_client_class.assert_called_once_with(
                api_key="test-key", base_url="https://custom.url"
            )

    def test_init_missing_sdk(self) -> None:
        """Test provider initialization when OpenAI SDK is not installed."""
        with patch("lesstokens_sdk.providers.openai.AsyncOpenAI", None):
            with pytest.raises(ImportError) as exc_info:
                OpenAIProvider("test-key")
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
        mock_response.model = "gpt-4"

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("lesstokens_sdk.providers.openai.OpenAI", MagicMock()), patch(
            "lesstokens_sdk.providers.openai.AsyncOpenAI", return_value=mock_client
        ):
            provider = OpenAIProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gpt-4"}
            messages = [{"role": "user", "content": "Hello"}]

            result = await provider.chat(messages, config)

            assert result.content == "Test response"
            assert result.usage.prompt_tokens == 10
            assert result.usage.completion_tokens == 5
            assert result.usage.total_tokens == 15
            assert result.metadata is not None
            assert result.metadata.model == "gpt-4"
            assert result.metadata.provider == "openai"

    @pytest.mark.asyncio
    async def test_chat_with_all_options(self) -> None:
        """Test chat with all OpenAI options."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Response"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.model = "gpt-4"

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("lesstokens_sdk.providers.openai.OpenAI", MagicMock()), patch(
            "lesstokens_sdk.providers.openai.AsyncOpenAI", return_value=mock_client
        ):
            provider = OpenAIProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 0.9,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.5,
                "stop": ["\n", "Human:"],
            }
            messages = [{"role": "user", "content": "Hello"}]

            await provider.chat(messages, config)

            # Verify all options were passed
            call_args = mock_client.chat.completions.create.call_args
            assert call_args is not None
            kwargs = call_args[1]
            assert kwargs["temperature"] == 0.7
            assert kwargs["max_tokens"] == 1000
            assert kwargs["top_p"] == 0.9
            assert kwargs["frequency_penalty"] == 0.5
            assert kwargs["presence_penalty"] == 0.5
            assert kwargs["stop"] == ["\n", "Human:"]

    @pytest.mark.asyncio
    async def test_chat_no_response(self) -> None:
        """Test chat with no response from OpenAI."""
        mock_response = MagicMock()
        mock_response.choices = []

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("lesstokens_sdk.providers.openai.OpenAI", MagicMock()), patch(
            "lesstokens_sdk.providers.openai.AsyncOpenAI", return_value=mock_client
        ):
            provider = OpenAIProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gpt-4"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await provider.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    @pytest.mark.asyncio
    async def test_chat_api_error(self) -> None:
        """Test chat with OpenAI API error."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        with patch("lesstokens_sdk.providers.openai.OpenAI", MagicMock()), patch(
            "lesstokens_sdk.providers.openai.AsyncOpenAI", return_value=mock_client
        ):
            provider = OpenAIProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gpt-4"}
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
        mock_chunk2.usage = None

        mock_chunk3 = MagicMock()
        mock_chunk3.choices = [MagicMock()]
        mock_chunk3.choices[0].delta.content = None
        mock_chunk3.choices[0].finish_reason = "stop"
        mock_chunk3.usage = MagicMock()
        mock_chunk3.usage.prompt_tokens = 10
        mock_chunk3.usage.completion_tokens = 2
        mock_chunk3.usage.total_tokens = 12

        async def mock_stream():
            yield mock_chunk1
            yield mock_chunk2
            yield mock_chunk3

        mock_client = AsyncMock()
        # Return the generator function, not the result of calling it
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())

        with patch("lesstokens_sdk.providers.openai.OpenAI", MagicMock()), patch(
            "lesstokens_sdk.providers.openai.AsyncOpenAI", return_value=mock_client
        ):
            provider = OpenAIProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gpt-4"}
            messages = [{"role": "user", "content": "Hello"}]

            chunks = []
            async for chunk in provider.chat_stream(messages, config):
                chunks.append(chunk)

            # Provider generates chunks for content AND for usage separately
            # The exact number may vary, but we should have:
            # - At least 2 content chunks ("Hello" and " World")
            # - At least 1 usage chunk (done=True)
            assert len(chunks) >= 3

            # Verify content chunks
            content_chunks = [c for c in chunks if not c.done]
            assert len(content_chunks) >= 2
            contents = [c.content for c in content_chunks]
            assert "Hello" in contents
            assert " World" in contents or any(" World" in c for c in contents)

            # Verify usage chunk
            usage_chunks = [c for c in chunks if c.done and c.usage]
            assert len(usage_chunks) >= 1
            assert usage_chunks[0].usage.total_tokens == 12

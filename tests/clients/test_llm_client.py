"""Tests for LLMClient"""

from typing import Dict, List

import pytest
from unittest.mock import AsyncMock, patch

from lesstokens_sdk.clients.llm_client import LLMClient
from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.types import LLMConfig, LLMResponse, StreamChunk, TokenUsage


@pytest.mark.unit
class TestLLMClient:
    """Test suite for LLMClient"""

    @pytest.mark.asyncio
    async def test_chat_success(self) -> None:
        """Test successful chat completion."""
        mock_provider = AsyncMock()
        mock_provider.chat.return_value = LLMResponse(
            content="Test response",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )

        with patch(
            "lesstokens_sdk.clients.llm_client.create_provider",
            return_value=mock_provider,
        ):
            client = LLMClient("openai", "test-api-key")
            config: LLMConfig = {"api_key": "test-api-key", "model": "gpt-4"}
            messages = [{"role": "user", "content": "Hello"}]

            result = await client.chat(messages, config)

            assert result.content == "Test response"
            assert result.usage.total_tokens == 15
            mock_provider.chat.assert_called_once_with(messages, config)

    @pytest.mark.asyncio
    async def test_chat_stream_success(self) -> None:
        """Test successful streaming chat completion."""
        mock_chunks = [
            StreamChunk(content="Hello", done=False),
            StreamChunk(content=" World", done=False),
            StreamChunk(
                content="",
                done=True,
                usage=TokenUsage(
                    prompt_tokens=10, completion_tokens=2, total_tokens=12
                ),
            ),
        ]

        async def mock_stream(
            messages: List[Dict[str, str]], config: LLMConfig
        ) -> StreamChunk:
            for chunk in mock_chunks:
                yield chunk

        mock_provider = AsyncMock()
        mock_provider.chat_stream = mock_stream

        with patch(
            "lesstokens_sdk.clients.llm_client.create_provider",
            return_value=mock_provider,
        ):
            client = LLMClient("openai", "test-api-key")
            config: LLMConfig = {"api_key": "test-api-key", "model": "gpt-4"}
            messages = [{"role": "user", "content": "Hello"}]

            chunks = []
            async for chunk in client.chat_stream(messages, config):
                chunks.append(chunk)

            assert len(chunks) == 3
            assert chunks[0].content == "Hello"
            assert chunks[1].content == " World"
            assert chunks[2].done is True
            assert chunks[2].usage is not None

    @pytest.mark.asyncio
    async def test_chat_provider_error(self) -> None:
        """Test chat with provider error."""
        mock_provider = AsyncMock()
        mock_provider.chat.side_effect = LessTokensError(
            "Provider error", ErrorCodes.LLM_API_ERROR, 500
        )

        with patch(
            "lesstokens_sdk.clients.llm_client.create_provider",
            return_value=mock_provider,
        ):
            client = LLMClient("openai", "test-api-key")
            config: LLMConfig = {"api_key": "test-api-key", "model": "gpt-4"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await client.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    def test_init_invalid_provider(self) -> None:
        """Test initialization with invalid provider."""
        with patch(
            "lesstokens_sdk.clients.llm_client.create_provider",
            side_effect=LessTokensError(
                "Invalid provider", ErrorCodes.INVALID_PROVIDER
            ),
        ):
            with pytest.raises(LessTokensError) as exc_info:
                LLMClient("invalid", "test-api-key")

            assert exc_info.value.code == ErrorCodes.INVALID_PROVIDER

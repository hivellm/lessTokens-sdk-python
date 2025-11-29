"""Tests for Google provider"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.providers.google import GoogleProvider
from lesstokens_sdk.types import LLMConfig


@pytest.mark.unit
class TestGoogleProvider:
    """Test suite for GoogleProvider"""

    def test_init_success(self) -> None:
        """Test provider initialization."""
        with patch("lesstokens_sdk.providers.google.genai") as mock_genai:
            mock_genai.configure = MagicMock()
            provider = GoogleProvider("test-key")
            assert provider.api_key == "test-key"
            mock_genai.configure.assert_called_once_with(api_key="test-key")

    def test_init_missing_sdk(self) -> None:
        """Test provider initialization when Google SDK is not installed."""
        with patch("lesstokens_sdk.providers.google.genai", None):
            with pytest.raises(ImportError) as exc_info:
                GoogleProvider("test-key")
            assert "Google Generative AI SDK not installed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_chat_success(self) -> None:
        """Test successful chat completion."""
        mock_part = MagicMock()
        mock_part.text = "Test response"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_usage = MagicMock()
        mock_usage.prompt_token_count = 10
        mock_usage.candidates_token_count = 5

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]
        mock_response.usage_metadata = mock_usage

        mock_model = AsyncMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch("lesstokens_sdk.providers.google.genai") as mock_genai:
            mock_genai.configure = MagicMock()
            mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

            provider = GoogleProvider("test-key")
            config: LLMConfig = {
                "api_key": "test-key",
                "model": "gemini-pro",
            }
            messages = [{"role": "user", "content": "Hello"}]

            result = await provider.chat(messages, config)

            assert result.content == "Test response"
            assert result.usage.prompt_tokens == 10
            assert result.usage.completion_tokens == 5
            assert result.metadata is not None
            assert result.metadata.provider == "google"

    @pytest.mark.asyncio
    async def test_chat_with_less_tokens_error(self) -> None:
        """Test chat re-throws LessTokensError."""
        error = LessTokensError("Test error", ErrorCodes.LLM_API_ERROR, 500)
        mock_model = AsyncMock()
        mock_model.generate_content_async = AsyncMock(side_effect=error)

        with patch("lesstokens_sdk.providers.google.genai") as mock_genai:
            mock_genai.configure = MagicMock()
            mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

            provider = GoogleProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gemini-pro"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await provider.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    @pytest.mark.asyncio
    async def test_chat_api_error(self) -> None:
        """Test chat with Google API error."""
        mock_model = AsyncMock()
        mock_model.generate_content_async = AsyncMock(
            side_effect=Exception("API Error")
        )

        with patch("lesstokens_sdk.providers.google.genai") as mock_genai:
            mock_genai.configure = MagicMock()
            mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

            provider = GoogleProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gemini-pro"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                await provider.chat(messages, config)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

    @pytest.mark.asyncio
    async def test_chat_stream_success(self) -> None:
        """Test successful streaming chat completion."""
        # Mock chunk with text attribute
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Hello"

        # Mock chunk with candidates
        mock_chunk2 = MagicMock()
        mock_chunk2.text = None
        mock_part = MagicMock()
        mock_part.text = " World"
        mock_candidate = MagicMock()
        mock_candidate.content = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_chunk2.candidates = [mock_candidate]

        async def mock_stream():
            yield mock_chunk1
            yield mock_chunk2

        mock_model = AsyncMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_stream())

        with patch("lesstokens_sdk.providers.google.genai") as mock_genai:
            mock_genai.configure = MagicMock()
            mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

            provider = GoogleProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gemini-pro"}
            messages = [{"role": "user", "content": "Hello"}]

            chunks = []
            async for chunk in provider.chat_stream(messages, config):
                chunks.append(chunk)

            assert len(chunks) >= 2
            assert "Hello" in [c.content for c in chunks]
            assert chunks[-1].done is True

    @pytest.mark.asyncio
    async def test_chat_stream_with_assistant_role(self) -> None:
        """Test streaming with assistant role (converted to model)."""
        mock_chunk = MagicMock()
        mock_chunk.text = "Response"

        async def mock_stream():
            yield mock_chunk

        mock_model = AsyncMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_stream())

        with patch("lesstokens_sdk.providers.google.genai") as mock_genai:
            mock_genai.configure = MagicMock()
            mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

            provider = GoogleProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gemini-pro"}
            messages = [{"role": "assistant", "content": "Previous response"}]

            chunks = []
            async for chunk in provider.chat_stream(messages, config):
                chunks.append(chunk)

            # Verify role conversion
            call_args = mock_model.generate_content_async.call_args
            assert call_args is not None
            contents = call_args[1]["contents"]
            assert contents[0]["role"] == "model"

    @pytest.mark.asyncio
    async def test_chat_stream_api_error(self) -> None:
        """Test streaming with API error."""
        mock_model = AsyncMock()
        mock_model.generate_content_async = AsyncMock(
            side_effect=Exception("Stream error")
        )

        with patch("lesstokens_sdk.providers.google.genai") as mock_genai:
            mock_genai.configure = MagicMock()
            mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

            provider = GoogleProvider("test-key")
            config: LLMConfig = {"api_key": "test-key", "model": "gemini-pro"}
            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(LessTokensError) as exc_info:
                async for _ in provider.chat_stream(messages, config):
                    pass

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

"""Tests for LessTokensSDK"""

from typing import Dict, List

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lesstokens_sdk import LessTokensSDK
from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.types import (
    CompressionOptions,
    LLMConfig,
    ProcessPromptOptions,
    StreamChunk,
    TokenUsage,
)


@pytest.mark.unit
class TestLessTokensSDK:
    """Test suite for LessTokensSDK"""

    def test_init_success(self, sample_sdk_config: dict) -> None:
        """Test SDK initialization with valid config."""
        sdk = LessTokensSDK(sample_sdk_config)
        assert sdk.provider == "openai"
        assert sdk.less_tokens_client is not None

    def test_init_invalid_api_key(self) -> None:
        """Test SDK initialization with invalid API key."""
        with pytest.raises(LessTokensError) as exc_info:
            LessTokensSDK({"api_key": "", "provider": "openai"})

        assert exc_info.value.code == ErrorCodes.INVALID_API_KEY

    def test_init_invalid_provider(self) -> None:
        """Test SDK initialization with invalid provider."""
        with pytest.raises(LessTokensError) as exc_info:
            LessTokensSDK({"api_key": "test-key", "provider": "invalid"})

        assert exc_info.value.code == ErrorCodes.INVALID_PROVIDER

    @pytest.mark.asyncio
    async def test_process_prompt_success(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test successful prompt processing."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        mock_llm_response = MagicMock()
        mock_llm_response.content = "LLM response"
        mock_llm_response.usage = TokenUsage(
            prompt_tokens=50, completion_tokens=25, total_tokens=75
        )
        mock_llm_response.metadata = None

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()
            mock_llm_client.chat = AsyncMock(return_value=mock_llm_response)
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
            }

            result = await sdk.process_prompt(options)

            assert result.content == "LLM response"
            assert result.usage.compressed_tokens == 50
            assert result.usage.savings == 50.0
            assert result.metadata is not None
            assert result.metadata.compression_ratio == 0.5

    @pytest.mark.asyncio
    async def test_process_prompt_with_messages(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test prompt processing with conversation history."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        mock_llm_response = MagicMock()
        mock_llm_response.content = "LLM response"
        mock_llm_response.usage = TokenUsage(
            prompt_tokens=50, completion_tokens=25, total_tokens=75
        )
        mock_llm_response.metadata = None

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()
            mock_llm_client.chat = AsyncMock(return_value=mock_llm_response)
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
                "messages": [{"role": "user", "content": "Previous message"}],
            }

            await sdk.process_prompt(options)

            # Verify messages were passed correctly
            call_args = mock_llm_client.chat.call_args
            assert call_args is not None
            messages = call_args[0][0]
            assert len(messages) == 2
            assert messages[0]["role"] == "user"
            assert messages[0]["content"] == "Previous message"
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "Compressed prompt"

    @pytest.mark.asyncio
    async def test_process_prompt_with_custom_role(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test prompt processing with custom message role."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        mock_llm_response = MagicMock()
        mock_llm_response.content = "LLM response"
        mock_llm_response.usage = TokenUsage(
            prompt_tokens=50, completion_tokens=25, total_tokens=75
        )
        mock_llm_response.metadata = None

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()
            mock_llm_client.chat = AsyncMock(return_value=mock_llm_response)
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
                "message_role": "system",
            }

            await sdk.process_prompt(options)

            # Verify custom role was used
            call_args = mock_llm_client.chat.call_args
            assert call_args is not None
            messages = call_args[0][0]
            assert messages[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_process_prompt_with_custom_content(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test prompt processing with custom message content."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        mock_llm_response = MagicMock()
        mock_llm_response.content = "LLM response"
        mock_llm_response.usage = TokenUsage(
            prompt_tokens=50, completion_tokens=25, total_tokens=75
        )
        mock_llm_response.metadata = None

        def custom_content(compressed: MagicMock) -> str:
            return f"Custom: {compressed.compressed}"

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()
            mock_llm_client.chat = AsyncMock(return_value=mock_llm_response)
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
                "message_content": custom_content,
            }

            await sdk.process_prompt(options)

            # Verify custom content was used
            call_args = mock_llm_client.chat.call_args
            assert call_args is not None
            messages = call_args[0][0]
            assert messages[0]["content"] == "Custom: Compressed prompt"

    @pytest.mark.asyncio
    async def test_process_prompt_stream_success(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test successful streaming prompt processing."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()

            async def mock_stream_gen(
                messages: List[Dict[str, str]], config: LLMConfig
            ):
                yield StreamChunk(content="Hello", done=False)
                yield StreamChunk(content=" World", done=False)
                yield StreamChunk(
                    content="",
                    done=True,
                    usage=TokenUsage(
                        prompt_tokens=50, completion_tokens=2, total_tokens=52
                    ),
                )

            # chat_stream is an async generator, returns AsyncIterator directly
            # We need to assign the function directly, not wrap it
            mock_llm_client.chat_stream = mock_stream_gen
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
            }

            chunks = []
            async for chunk in sdk.process_prompt_stream(options):
                chunks.append(chunk)

            assert len(chunks) == 3
            assert chunks[0].content == "Hello"
            assert chunks[1].content == " World"
            assert chunks[2].done is True
            assert chunks[2].usage is not None
            assert chunks[2].usage.compressed_tokens == 50
            assert chunks[2].usage.savings == 50.0

    @pytest.mark.asyncio
    async def test_process_prompt_stream_without_usage(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test streaming prompt processing without usage in final chunk."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()

            async def mock_stream_gen(
                messages: List[Dict[str, str]], config: LLMConfig
            ):
                yield StreamChunk(content="Hello", done=False)
                yield StreamChunk(content=" World", done=False)
                # Final chunk without usage
                yield StreamChunk(content="", done=True, usage=None)

            mock_llm_client.chat_stream = mock_stream_gen
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
            }

            chunks = []
            async for chunk in sdk.process_prompt_stream(options):
                chunks.append(chunk)

            # Should have content chunks + final chunk with usage created
            assert len(chunks) >= 3
            assert chunks[-1].done is True
            assert chunks[-1].usage is not None
            assert chunks[-1].usage.compressed_tokens == 50

    @pytest.mark.asyncio
    async def test_process_prompt_stream_with_callable_content(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test streaming with callable message_content."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        def custom_content(compressed: MagicMock) -> str:
            return f"Custom: {compressed.compressed}"

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()

            async def mock_stream_gen(
                messages: List[Dict[str, str]], config: LLMConfig
            ):
                yield StreamChunk(content="Hello", done=False)
                yield StreamChunk(
                    content="",
                    done=True,
                    usage=TokenUsage(
                        prompt_tokens=50, completion_tokens=2, total_tokens=52
                    ),
                )

            # chat_stream is an async generator, returns AsyncIterator directly
            mock_llm_client.chat_stream = mock_stream_gen
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
                "message_content": custom_content,
            }

            chunks = []
            async for chunk in sdk.process_prompt_stream(options):
                chunks.append(chunk)

            # Verify streaming worked
            assert len(chunks) >= 2
            assert chunks[-1].done is True

    @pytest.mark.asyncio
    async def test_process_prompt_stream_with_messages(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test streaming with additional messages."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()

            async def mock_stream_gen(
                messages: List[Dict[str, str]], config: LLMConfig
            ):
                yield StreamChunk(content="Hello", done=False)
                yield StreamChunk(
                    content="",
                    done=True,
                    usage=TokenUsage(
                        prompt_tokens=50, completion_tokens=2, total_tokens=52
                    ),
                )

            # chat_stream is an async generator, returns AsyncIterator directly
            mock_llm_client.chat_stream = mock_stream_gen
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
                "messages": [{"role": "user", "content": "Previous message"}],
            }

            chunks = []
            async for chunk in sdk.process_prompt_stream(options):
                chunks.append(chunk)

            # Verify streaming worked
            assert len(chunks) >= 2
            assert chunks[-1].done is True

    @pytest.mark.asyncio
    async def test_compress_prompt_success(self, sample_sdk_config: dict) -> None:
        """Test successful prompt compression."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.savings = 50.0
        mock_compressed.ratio = 0.5

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: CompressionOptions = {
                "target_ratio": 0.5,
                "preserve_context": True,
            }

            result = await sdk.compress_prompt("Test prompt", options)

            assert result.compressed == "Compressed prompt"
            assert result.original_tokens == 100
            assert result.compressed_tokens == 50
            mock_client.compress.assert_called_once_with("Test prompt", options)

    @pytest.mark.asyncio
    async def test_compress_prompt_without_options(
        self, sample_sdk_config: dict
    ) -> None:
        """Test prompt compression without options."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.savings = 50.0
        mock_compressed.ratio = 0.5

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            sdk = LessTokensSDK(sample_sdk_config)
            result = await sdk.compress_prompt("Test prompt")

            assert result.compressed == "Compressed prompt"
            mock_client.compress.assert_called_once_with("Test prompt", None)

    @pytest.mark.asyncio
    async def test_process_prompt_compression_error(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test prompt processing with compression error."""
        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(
                side_effect=LessTokensError(
                    "Compression failed", ErrorCodes.COMPRESSION_FAILED, 500
                )
            )
            mock_client_class.return_value = mock_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
            }

            with pytest.raises(LessTokensError) as exc_info:
                await sdk.process_prompt(options)

            assert exc_info.value.code == ErrorCodes.COMPRESSION_FAILED

    @pytest.mark.asyncio
    async def test_process_prompt_llm_error(
        self, sample_sdk_config: dict, sample_llm_config: dict
    ) -> None:
        """Test prompt processing with LLM error."""
        mock_compressed = MagicMock()
        mock_compressed.compressed = "Compressed prompt"
        mock_compressed.original_tokens = 100
        mock_compressed.compressed_tokens = 50
        mock_compressed.ratio = 0.5

        with patch("lesstokens_sdk.sdk.LessTokensClient") as mock_client_class, patch(
            "lesstokens_sdk.sdk.LLMClient"
        ) as mock_llm_client_class:
            mock_client = AsyncMock()
            mock_client.compress = AsyncMock(return_value=mock_compressed)
            mock_client_class.return_value = mock_client

            mock_llm_client = AsyncMock()
            mock_llm_client.chat = AsyncMock(
                side_effect=LessTokensError("LLM error", ErrorCodes.LLM_API_ERROR, 500)
            )
            mock_llm_client_class.return_value = mock_llm_client

            sdk = LessTokensSDK(sample_sdk_config)
            options: ProcessPromptOptions = {
                "prompt": "Test prompt",
                "llm_config": sample_llm_config,
            }

            with pytest.raises(LessTokensError) as exc_info:
                await sdk.process_prompt(options)

            assert exc_info.value.code == ErrorCodes.LLM_API_ERROR

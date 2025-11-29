"""Tests for LessTokensClient"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lesstokens_sdk.clients.less_tokens_client import LessTokensClient
from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.types import CompressionOptions


@pytest.mark.unit
class TestLessTokensClient:
    """Test suite for LessTokensClient"""

    def test_init_with_defaults(self) -> None:
        """Test client initialization with default values."""
        client = LessTokensClient("test-api-key")
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://lesstokens.hive-hub.ai"
        assert client.timeout == 30.0  # 30000ms / 1000

    def test_init_with_custom_values(self) -> None:
        """Test client initialization with custom values."""
        client = LessTokensClient(
            "test-api-key",
            base_url="https://custom.url",
            timeout=60000,
        )
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://custom.url"
        assert client.timeout == 60.0

    def test_init_strips_trailing_slash(self) -> None:
        """Test that base_url trailing slash is stripped."""
        client = LessTokensClient("test-api-key", base_url="https://example.com/")
        assert client.base_url == "https://example.com"

    @pytest.mark.asyncio
    async def test_compress_success(self, mock_httpx_response: MagicMock) -> None:
        """Test successful compression."""
        mock_httpx_response.is_success = True
        mock_httpx_response.json.return_value = {
            "data": {
                "compressed": "Compressed text",
                "originalTokens": 100,
                "compressedTokens": 50,
                "tokensSaved": 50.0,
                "compressionRatio": 0.5,
            }
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_httpx_response
            mock_client_class.return_value = mock_client

            client = LessTokensClient("test-api-key")
            result = await client.compress("Test prompt")

            assert result.compressed == "Compressed text"
            assert result.original_tokens == 100
            assert result.compressed_tokens == 50
            assert result.savings == 50.0
            assert result.ratio == 0.5

    @pytest.mark.asyncio
    async def test_compress_with_options(self, mock_httpx_response: MagicMock) -> None:
        """Test compression with custom options."""
        mock_httpx_response.is_success = True
        mock_httpx_response.json.return_value = {
            "data": {
                "compressed": "Compressed text",
                "originalTokens": 100,
                "compressedTokens": 30,
                "tokensSaved": 70.0,
                "compressionRatio": 0.3,
            }
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_httpx_response
            mock_client_class.return_value = mock_client

            client = LessTokensClient("test-api-key")
            options: CompressionOptions = {
                "target_ratio": 0.3,
                "preserve_context": True,
                "aggressive": False,
            }
            await client.compress("Test prompt", options)

            # Verify request body includes options
            call_args = mock_client.post.call_args
            assert call_args is not None
            request_body = call_args[1]["json"]
            assert request_body["targetRatio"] == 0.3
            assert request_body["preserveContext"] is True
            assert request_body["aggressive"] is False

    @pytest.mark.asyncio
    async def test_compress_invalid_api_key(self) -> None:
        """Test compression with invalid API key."""
        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.status_text = "Unauthorized"
        mock_response.json.return_value = {"message": "Invalid API key"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = LessTokensClient("invalid-key")
            with pytest.raises(LessTokensError) as exc_info:
                await client.compress("Test prompt")

            assert exc_info.value.code == ErrorCodes.INVALID_API_KEY
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_compress_failure_invalid_json(self) -> None:
        """Test compression failure with invalid JSON response."""
        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception("Invalid JSON")  # Exception on json()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = LessTokensClient("test-key")
            with pytest.raises(LessTokensError) as exc_info:
                await client.compress("Test prompt")

            assert exc_info.value.code == ErrorCodes.COMPRESSION_FAILED
            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_compress_failure(self) -> None:
        """Test compression failure."""
        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.status_text = "Internal Server Error"
        mock_response.json.return_value = {"message": "Compression failed"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = LessTokensClient("test-api-key")
            with pytest.raises(LessTokensError) as exc_info:
                await client.compress("Test prompt")

            assert exc_info.value.code == ErrorCodes.COMPRESSION_FAILED
            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_compress_timeout(self) -> None:
        """Test compression timeout."""
        import httpx

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.side_effect = httpx.TimeoutException("Request timeout")
            mock_client_class.return_value = mock_client

            client = LessTokensClient("test-api-key", timeout=1000)
            with pytest.raises(LessTokensError) as exc_info:
                await client.compress("Test prompt")

            assert exc_info.value.code == ErrorCodes.TIMEOUT

    @pytest.mark.asyncio
    async def test_compress_network_error(self) -> None:
        """Test network error during compression."""
        import httpx

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.side_effect = httpx.RequestError("Network error")
            mock_client_class.return_value = mock_client

            client = LessTokensClient("test-api-key")
            with pytest.raises(LessTokensError) as exc_info:
                await client.compress("Test prompt")

            assert exc_info.value.code == ErrorCodes.NETWORK_ERROR

    @pytest.mark.asyncio
    async def test_compress_network_error_with_code(self) -> None:
        """Test compression with network error that has code attribute."""
        error = LessTokensError("Network error", ErrorCodes.TIMEOUT, 408)
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.side_effect = error
            mock_client_class.return_value = mock_client

            client = LessTokensClient("test-key")
            with pytest.raises(LessTokensError) as exc_info:
                await client.compress("Test prompt")

            # Should re-throw the LessTokensError
            assert exc_info.value.code == ErrorCodes.TIMEOUT

    @pytest.mark.asyncio
    async def test_compress_retry_on_timeout(self) -> None:
        """Test that compression retries on timeout."""
        import httpx

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "data": {
                "compressed": "Compressed text",
                "originalTokens": 100,
                "compressedTokens": 50,
                "tokensSaved": 50.0,
                "compressionRatio": 0.5,
            }
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            # First call fails with timeout, second succeeds
            mock_client.post.side_effect = [
                httpx.TimeoutException("Request timeout"),
                mock_response,
            ]
            mock_client_class.return_value = mock_client

            client = LessTokensClient("test-api-key")
            result = await client.compress("Test prompt")

            # Should succeed after retry
            assert result.compressed == "Compressed text"
            # Should have retried (2 calls)
            assert mock_client.post.call_count == 2

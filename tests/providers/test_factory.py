"""Tests for provider factory"""

import pytest
from unittest.mock import patch

from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.providers.factory import create_provider


@pytest.mark.unit
class TestProviderFactory:
    """Test suite for provider factory"""

    def test_create_openai_provider(self) -> None:
        """Test creating OpenAI provider."""
        with patch("lesstokens_sdk.providers.factory.OpenAIProvider") as mock_provider:
            mock_instance = mock_provider.return_value
            result = create_provider("openai", "test-key")
            assert result == mock_instance
            mock_provider.assert_called_once_with("test-key", None)

    def test_create_openai_provider_with_base_url(self) -> None:
        """Test creating OpenAI provider with base URL."""
        with patch("lesstokens_sdk.providers.factory.OpenAIProvider") as mock_provider:
            mock_instance = mock_provider.return_value
            result = create_provider("openai", "test-key", "https://custom.url")
            assert result == mock_instance
            mock_provider.assert_called_once_with("test-key", "https://custom.url")

    def test_create_anthropic_provider(self) -> None:
        """Test creating Anthropic provider."""
        with patch("lesstokens_sdk.providers.factory.AnthropicProvider") as mock_provider:
            mock_instance = mock_provider.return_value
            result = create_provider("anthropic", "test-key")
            assert result == mock_instance
            mock_provider.assert_called_once_with("test-key")

    def test_create_google_provider(self) -> None:
        """Test creating Google provider."""
        with patch("lesstokens_sdk.providers.factory.GoogleProvider") as mock_provider:
            mock_instance = mock_provider.return_value
            result = create_provider("google", "test-key")
            assert result == mock_instance
            mock_provider.assert_called_once_with("test-key")

    def test_create_deepseek_provider(self) -> None:
        """Test creating DeepSeek provider."""
        with patch("lesstokens_sdk.providers.factory.DeepSeekProvider") as mock_provider:
            mock_instance = mock_provider.return_value
            result = create_provider("deepseek", "test-key")
            assert result == mock_instance
            mock_provider.assert_called_once_with("test-key")

    def test_create_provider_case_insensitive(self) -> None:
        """Test that provider names are case-insensitive."""
        with patch("lesstokens_sdk.providers.factory.OpenAIProvider") as mock_provider:
            mock_instance = mock_provider.return_value
            result = create_provider("OPENAI", "test-key")
            assert result == mock_instance
            mock_provider.assert_called_once_with("test-key", None)

    def test_create_provider_invalid(self) -> None:
        """Test creating provider with invalid name."""
        with pytest.raises(LessTokensError) as exc_info:
            create_provider("invalid", "test-key")

        assert exc_info.value.code == ErrorCodes.INVALID_PROVIDER
        assert "invalid" in exc_info.value.message.lower()

"""Pytest configuration and shared fixtures"""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from lesstokens_sdk.types import (
    CompressedPrompt,
    LLMResponse,
    ResponseMetadata,
    TokenUsage,
)

# pytest-asyncio will handle event loop automatically
# No need for custom event_loop fixture if pytest-asyncio is installed


@pytest.fixture
def sample_compressed_prompt() -> CompressedPrompt:
    """Provide a sample compressed prompt for testing."""
    return CompressedPrompt(
        compressed="Compressed text",
        original_tokens=100,
        compressed_tokens=50,
        savings=50.0,
        ratio=0.5,
    )


@pytest.fixture
def sample_llm_response() -> LLMResponse:
    """Provide a sample LLM response for testing."""
    return LLMResponse(
        content="Test response",
        usage=TokenUsage(
            prompt_tokens=50,
            completion_tokens=25,
            total_tokens=75,
            compressed_tokens=50,
            savings=50.0,
        ),
        metadata=ResponseMetadata(
            model="gpt-4",
            provider="openai",
            timestamp="2025-01-01T00:00:00Z",
            compression_ratio=0.5,
        ),
    )


@pytest.fixture
def sample_llm_config() -> Dict[str, Any]:
    """Provide a sample LLM configuration for testing."""
    return {
        "api_key": "test-api-key",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
    }


@pytest.fixture
def sample_sdk_config() -> Dict[str, Any]:
    """Provide a sample SDK configuration for testing."""
    return {
        "api_key": "test-lesstokens-api-key",
        "provider": "openai",
        "base_url": "https://lesstokens.hive-hub.ai",
        "timeout": 30000,
    }


@pytest.fixture
def mock_httpx_response() -> MagicMock:
    """Provide a mock httpx response."""
    response = MagicMock()
    response.is_success = True
    response.status_code = 200
    response.json.return_value = {
        "data": {
            "compressed": "Compressed text",
            "originalTokens": 100,
            "compressedTokens": 50,
            "tokensSaved": 50.0,
            "compressionRatio": 0.5,
        }
    }
    return response


@pytest.fixture
def mock_async_httpx_client(mock_httpx_response: MagicMock) -> AsyncMock:
    """Provide a mock async httpx client."""
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.__aexit__.return_value = None
    client.post.return_value = mock_httpx_response
    return client

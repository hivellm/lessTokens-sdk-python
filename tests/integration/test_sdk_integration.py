"""Integration tests for LessTokens SDK

These tests require real API keys and should be run separately.
Marked with @pytest.mark.integration to exclude from regular test runs.
"""

import os
import pytest

from lesstokens_sdk import LessTokensSDK


@pytest.mark.integration
@pytest.mark.asyncio
class TestSDKIntegration:
    """Integration tests for LessTokens SDK with real APIs"""

    @pytest.fixture
    def sdk_config(self) -> dict:
        """Get SDK configuration from environment."""
        api_key = os.getenv("LESSTOKENS_API_KEY")
        if not api_key:
            pytest.skip("LESSTOKENS_API_KEY not set")
        return {
            "api_key": api_key,
            "provider": "openai",
        }

    @pytest.fixture
    def llm_config(self) -> dict:
        """Get LLM configuration from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        return {
            "api_key": api_key,
            "model": "gpt-3.5-turbo",
        }

    @pytest.mark.asyncio
    async def test_compress_prompt_integration(self, sdk_config: dict) -> None:
        """Test prompt compression with real LessTokens API."""
        sdk = LessTokensSDK(sdk_config)
        result = await sdk.compress_prompt("This is a test prompt for compression.")

        assert result.compressed is not None
        assert len(result.compressed) > 0
        assert result.original_tokens > 0
        assert result.compressed_tokens > 0
        assert result.savings >= 0
        assert result.ratio > 0

    @pytest.mark.asyncio
    async def test_process_prompt_integration(self, sdk_config: dict, llm_config: dict) -> None:
        """Test full prompt processing with real APIs."""
        sdk = LessTokensSDK(sdk_config)
        response = await sdk.process_prompt(
            {
                "prompt": "Say hello in one word.",
                "llm_config": llm_config,
            }
        )

        assert response.content is not None
        assert len(response.content) > 0
        assert response.usage is not None
        assert response.usage.total_tokens > 0
        assert response.usage.compressed_tokens is not None
        assert response.usage.savings is not None

    @pytest.mark.asyncio
    async def test_process_prompt_stream_integration(
        self, sdk_config: dict, llm_config: dict
    ) -> None:
        """Test streaming prompt processing with real APIs."""
        sdk = LessTokensSDK(sdk_config)
        chunks = []
        async for chunk in sdk.process_prompt_stream(
            {
                "prompt": "Count from 1 to 5.",
                "llm_config": llm_config,
            }
        ):
            chunks.append(chunk)

        assert len(chunks) > 0
        # Last chunk should be done
        assert chunks[-1].done is True
        assert chunks[-1].usage is not None
        assert chunks[-1].usage.compressed_tokens is not None

    @pytest.mark.asyncio
    async def test_multi_turn_conversation_integration(
        self, sdk_config: dict, llm_config: dict
    ) -> None:
        """Test multi-turn conversation with real APIs."""
        sdk = LessTokensSDK(sdk_config)

        # First message
        response1 = await sdk.process_prompt(
            {
                "prompt": "My name is Alice.",
                "llm_config": llm_config,
            }
        )

        # Second message with conversation history
        response2 = await sdk.process_prompt(
            {
                "prompt": "What is my name?",
                "llm_config": llm_config,
                "messages": [
                    {"role": "user", "content": "My name is Alice."},
                    {"role": "assistant", "content": response1.content},
                ],
            }
        )

        assert response2.content is not None
        # Should remember the name from context
        assert "alice" in response2.content.lower()

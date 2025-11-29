"""
LLM client wrapper
"""

from typing import AsyncIterator, Dict, List, Optional

from lesstokens_sdk.providers import create_provider
from lesstokens_sdk.types import LLMConfig, LLMResponse, StreamChunk


class LLMClient:
    """LLM client that wraps provider implementations"""

    def __init__(self, provider: str, api_key: str, base_url: Optional[str] = None):
        self.provider = create_provider(provider, api_key, base_url)

    async def chat(
        self, messages: List[Dict[str, str]], config: LLMConfig
    ) -> LLMResponse:
        """Send a chat completion request"""
        return await self.provider.chat(messages, config)

    async def chat_stream(
        self, messages: List[Dict[str, str]], config: LLMConfig
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request"""
        # chat_stream is an async generator, returns AsyncIterator directly
        stream = self.provider.chat_stream(messages, config)  # type: ignore[attr-defined]
        async for chunk in stream:  # type: ignore[attr-defined]
            yield chunk

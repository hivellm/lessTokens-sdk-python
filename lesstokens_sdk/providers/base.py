"""
Base provider interface
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List

from lesstokens_sdk.types import LLMConfig, LLMResponse, StreamChunk


class LLMProvider(ABC):
    """Base provider interface that all providers must implement"""

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], config: LLMConfig) -> LLMResponse:
        """Send a chat completion request"""
        pass

    @abstractmethod
    async def chat_stream(
        self, messages: List[Dict[str, str]], config: LLMConfig
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request"""
        pass

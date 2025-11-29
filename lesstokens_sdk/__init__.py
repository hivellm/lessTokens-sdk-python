"""
LessTokens SDK - Python

Modern Python SDK for integrating with the LessTokens token compression API.
Compress prompts before sending to LLM providers to reduce token usage and costs.
"""

from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.sdk import LessTokensSDK
from lesstokens_sdk.types import (
    CompressedPrompt,
    CompressionOptions,
    LLMConfig,
    LLMResponse,
    LessTokensConfig,
    ProcessPromptOptions,
    ResponseMetadata,
    StreamChunk,
    TokenUsage,
)

__version__ = "0.1.0"
__all__ = [
    "LessTokensSDK",
    "LessTokensError",
    "ErrorCodes",
    "LessTokensConfig",
    "ProcessPromptOptions",
    "LLMConfig",
    "CompressionOptions",
    "LLMResponse",
    "TokenUsage",
    "ResponseMetadata",
    "CompressedPrompt",
    "StreamChunk",
]


"""
Core type definitions for the LessTokens SDK
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, TypedDict, Union


class LessTokensConfig(TypedDict, total=False):
    """Configuration for initializing the LessTokens SDK"""

    api_key: str  # Required
    provider: str  # Required
    base_url: Optional[str]  # Optional, default: 'https://lesstokens.hive-hub.ai'
    timeout: Optional[int]  # Optional, default: 30000 (milliseconds)


class CompressionOptions(TypedDict, total=False):
    """Compression options"""

    target_ratio: Optional[float]  # Target compression ratio (0.0 to 1.0, default: 0.5)
    preserve_context: Optional[
        bool
    ]  # Preserve context during compression (default: True)
    aggressive: Optional[bool]  # Use aggressive compression (default: False)


class LLMConfig(TypedDict, total=False):
    """LLM API configuration - supports all provider-specific options"""

    api_key: str  # Required
    model: str  # Required
    temperature: Optional[float]  # Temperature (0.0 to 2.0)
    max_tokens: Optional[int]  # Maximum tokens for completion
    maxTokens: Optional[int]  # Alternative naming (for compatibility)
    top_p: Optional[float]  # Top-p sampling
    topP: Optional[float]  # Alternative naming (for compatibility)
    frequency_penalty: Optional[float]  # Frequency penalty
    frequencyPenalty: Optional[float]  # Alternative naming (for compatibility)
    presence_penalty: Optional[float]  # Presence penalty
    presencePenalty: Optional[float]  # Alternative naming (for compatibility)
    stop: Optional[List[str]]  # Stop sequences
    # Allow any additional provider-specific options
    # Using Dict[str, Any] would be more accurate but TypedDict doesn't support that directly
    # So we use total=False and allow arbitrary keys via __getitem__


@dataclass
class TokenUsage:
    """Token usage metrics"""

    prompt_tokens: int  # Original prompt tokens
    completion_tokens: int  # Completion tokens
    total_tokens: int  # Total tokens
    compressed_tokens: Optional[int] = (
        None  # Compressed tokens (if compression was used)
    )
    savings: Optional[float] = None  # Savings percentage (0-100)


@dataclass
class ResponseMetadata:
    """Response metadata"""

    model: Optional[str] = None  # Model used
    provider: Optional[str] = None  # Provider name
    timestamp: Optional[str] = None  # ISO timestamp
    compression_ratio: Optional[float] = (
        None  # Compression ratio (if compression was used)
    )


@dataclass
class LLMResponse:
    """LLM response with usage metrics"""

    content: str  # Response content
    usage: TokenUsage  # Token usage information
    metadata: Optional[ResponseMetadata] = None  # Response metadata


@dataclass
class CompressedPrompt:
    """Compressed prompt result"""

    compressed: str  # Compressed prompt text
    original_tokens: int  # Original token count
    compressed_tokens: int  # Compressed token count
    savings: float  # Savings percentage (0-100)
    ratio: float  # Compression ratio (compressed_tokens / original_tokens)


@dataclass
class StreamChunk:
    """Streaming chunk"""

    content: str  # Chunk content
    done: bool  # Whether this is the final chunk
    usage: Optional[TokenUsage] = (
        None  # Usage information (available when done is True)
    )


class ProcessPromptOptions(TypedDict, total=False):
    """Options for processing a prompt"""

    prompt: str  # Required
    llm_config: LLMConfig  # Required
    compression_options: Optional[CompressionOptions]  # Optional
    message_role: Optional[str]  # Optional, default: 'user'
    message_content: Optional[Union[str, Callable[[CompressedPrompt], str]]]  # Optional
    messages: Optional[List[Dict[str, str]]]  # Optional, for multi-turn conversations


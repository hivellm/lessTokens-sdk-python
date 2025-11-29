# LessTokens SDK - API Reference

Complete API reference for the LessTokens Python SDK.

## Table of Contents

- [LessTokensSDK](#lesstokenssdk)
- [Types](#types)
- [Errors](#errors)
- [Utilities](#utilities)

## LessTokensSDK

### `LessTokensSDK`

Main SDK class for interacting with the LessTokens API and LLM providers.

#### Constructor

```python
LessTokensSDK(config: LessTokensConfig)
```

**Parameters:**
- `config` (LessTokensConfig): SDK configuration
  - `api_key` (str, required): LessTokens API key
  - `provider` (str, required): LLM provider name ('openai', 'anthropic', 'google', 'deepseek')
  - `base_url` (str, optional): Base URL for LessTokens API (default: 'https://lesstokens.hive-hub.ai')
  - `timeout` (int, optional): Request timeout in milliseconds (default: 30000)

**Raises:**
- `LessTokensError`: If configuration is invalid

**Example:**
```python
sdk = LessTokensSDK(
    api_key="your-api-key",
    provider="openai",
    base_url="https://lesstokens.hive-hub.ai",
    timeout=30000
)
```

#### Methods

##### `process_prompt(options: ProcessPromptOptions) -> LLMResponse`

Process a prompt through LessTokens compression and send to LLM.

**Parameters:**
- `options` (ProcessPromptOptions): Processing options
  - `prompt` (str, required): The prompt to compress and send
  - `llm_config` (LLMConfig, required): LLM provider configuration
  - `compression_options` (CompressionOptions, optional): Compression settings
  - `message_role` (str, optional): Custom message role (default: 'user')
  - `message_content` (str | Callable, optional): Custom message content
  - `messages` (List[Dict[str, str]], optional): Additional messages for multi-turn conversations

**Returns:**
- `LLMResponse`: LLM response with compression metrics

**Raises:**
- `LessTokensError`: If compression or LLM request fails

**Example:**
```python
response = await sdk.process_prompt({
    "prompt": "Explain quantum computing",
    "llm_config": {
        "api_key": "sk-...",
        "model": "gpt-4",
        "temperature": 0.7,
    }
})
```

##### `process_prompt_stream(options: ProcessPromptOptions) -> AsyncIterator[StreamChunk]`

Process a prompt with streaming response.

**Parameters:**
- Same as `process_prompt`

**Returns:**
- `AsyncIterator[StreamChunk]`: Async iterable of stream chunks

**Raises:**
- `LessTokensError`: If compression or LLM request fails

**Example:**
```python
async for chunk in sdk.process_prompt_stream({
    "prompt": "Tell a story",
    "llm_config": {
        "api_key": "sk-...",
        "model": "gpt-4",
    }
}):
    if chunk.done:
        print(f"Usage: {chunk.usage}")
    else:
        print(chunk.content, end="", flush=True)
```

##### `compress_prompt(prompt: str, options: Optional[CompressionOptions] = None) -> CompressedPrompt`

Compress a prompt without sending to LLM.

**Parameters:**
- `prompt` (str): The prompt to compress
- `options` (CompressionOptions, optional): Compression settings

**Returns:**
- `CompressedPrompt`: Compression results

**Raises:**
- `LessTokensError`: If compression fails

**Example:**
```python
compressed = await sdk.compress_prompt(
    "Very long prompt...",
    {
        "target_ratio": 0.3,
        "aggressive": True,
    }
)
```

## Types

### `LessTokensConfig`

Configuration for initializing the LessTokens SDK.

```python
{
    "api_key": str,  # Required
    "provider": str,  # Required: 'openai', 'anthropic', 'google', 'deepseek'
    "base_url": Optional[str],  # Optional
    "timeout": Optional[int],  # Optional, milliseconds
}
```

### `ProcessPromptOptions`

Options for processing a prompt.

```python
{
    "prompt": str,  # Required
    "llm_config": LLMConfig,  # Required
    "compression_options": Optional[CompressionOptions],
    "message_role": Optional[str],  # Default: 'user'
    "message_content": Optional[str | Callable[[CompressedPrompt], str]],
    "messages": Optional[List[Dict[str, str]]],  # For multi-turn conversations
}
```

### `LLMConfig`

LLM API configuration - supports all provider-specific options.

```python
{
    "api_key": str,  # Required
    "model": str,  # Required
    "temperature": Optional[float],  # 0.0 to 2.0
    "max_tokens": Optional[int],
    "top_p": Optional[float],
    "frequency_penalty": Optional[float],
    "presence_penalty": Optional[float],
    "stop": Optional[List[str]],
    # ... all provider-specific options
}
```

### `CompressionOptions`

Compression options.

```python
{
    "target_ratio": Optional[float],  # 0.0 to 1.0, default: 0.5
    "preserve_context": Optional[bool],  # Default: True
    "aggressive": Optional[bool],  # Default: False
}
```

### `LLMResponse`

LLM response with usage metrics.

```python
@dataclass
class LLMResponse:
    content: str  # Response content
    usage: TokenUsage  # Token usage information
    metadata: Optional[ResponseMetadata]  # Response metadata
```

### `TokenUsage`

Token usage metrics.

```python
@dataclass
class TokenUsage:
    prompt_tokens: int  # Original prompt tokens
    completion_tokens: int  # Completion tokens
    total_tokens: int  # Total tokens
    compressed_tokens: Optional[int]  # Compressed tokens (if compression was used)
    savings: Optional[float]  # Savings percentage (0-100)
```

### `ResponseMetadata`

Response metadata.

```python
@dataclass
class ResponseMetadata:
    model: Optional[str]  # Model used
    provider: Optional[str]  # Provider name
    timestamp: Optional[str]  # ISO timestamp
    compression_ratio: Optional[float]  # Compression ratio (if compression was used)
```

### `CompressedPrompt`

Compressed prompt result.

```python
@dataclass
class CompressedPrompt:
    compressed: str  # Compressed prompt text
    original_tokens: int  # Original token count
    compressed_tokens: int  # Compressed token count
    savings: float  # Savings percentage (0-100)
    ratio: float  # Compression ratio (compressed_tokens / original_tokens)
```

### `StreamChunk`

Streaming chunk.

```python
@dataclass
class StreamChunk:
    content: str  # Chunk content
    done: bool  # Whether this is the final chunk
    usage: Optional[TokenUsage]  # Usage information (available when done is True)
```

## Errors

### `LessTokensError`

Base error class for all LessTokens SDK errors.

**Attributes:**
- `message` (str): Error message
- `code` (str): Error code
- `status_code` (Optional[int]): HTTP status code (if applicable)
- `details` (Optional[Any]): Additional error details

**Example:**
```python
try:
    response = await sdk.process_prompt(...)
except LessTokensError as e:
    print(f"Error {e.code}: {e.message}")
```

### `ErrorCodes`

Error code constants.

- `INVALID_API_KEY`: Invalid API key
- `INVALID_PROVIDER`: Invalid provider
- `COMPRESSION_FAILED`: Compression failed
- `LLM_API_ERROR`: LLM API error
- `TIMEOUT`: Request timeout
- `NETWORK_ERROR`: Network error
- `VALIDATION_ERROR`: Validation error

## Utilities

### Retry

Retry utilities with exponential backoff.

#### `retry(fn: Callable, config: Optional[Dict] = None) -> T`

Retry a function with exponential backoff.

**Parameters:**
- `fn`: Async function to retry
- `config`: Optional retry configuration
  - `max_retries` (int, default: 3)
  - `initial_delay` (float, default: 1.0 seconds)
  - `max_delay` (float, default: 10.0 seconds)
  - `retryable_errors` (List[str], default: ["TIMEOUT", "NETWORK_ERROR", "RATE_LIMIT"])

**Returns:**
- Result of the function call

### Validation

Input validation utilities.

#### `validate_config(config: LessTokensConfig) -> None`

Validate LessTokens configuration.

#### `validate_prompt(prompt: str) -> None`

Validate prompt.

#### `validate_process_prompt_options(options: ProcessPromptOptions) -> None`

Validate process prompt options.

#### `validate_llm_config(config: LLMConfig) -> None`

Validate LLM configuration.

#### `validate_compression_options(options: CompressionOptions) -> None`

Validate compression options.



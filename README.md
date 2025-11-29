# LessTokens SDK - Python

[![PyPI version](https://img.shields.io/pypi/v/lesstokens-sdk.svg)](https://pypi.org/project/lesstokens-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Modern and simple Python SDK for integrating with the LessTokens token compression API. Compress prompts before sending to LLM providers (OpenAI, Anthropic, Google, DeepSeek) to reduce token usage and costs while maintaining response quality.

## ✨ Features

- 🚀 **Simple & Modern**: Intuitive and easy-to-use API
- 🔒 **Type-Safe**: Full type hints with Python 3.8+
- ⚡ **Performant**: Optimized for high performance
- 📦 **Lightweight**: Minimal dependencies
- 🔄 **Streaming**: Support for streaming responses
- 🎯 **Flexible**: Supports multiple LLM providers
- 🔌 **Full Provider Support**: Uses official SDKs for complete feature support

## 📦 Installation

```bash
pip install lesstokens-sdk
# or
pip install lesstokens-sdk[all]  # Install with all optional provider dependencies
```

### Provider-Specific Installation

```bash
# OpenAI only
pip install lesstokens-sdk[openai]

# Anthropic only
pip install lesstokens-sdk[anthropic]

# Google only
pip install lesstokens-sdk[google]

# DeepSeek only
pip install lesstokens-sdk[deepseek]

# Multiple providers
pip install lesstokens-sdk[openai,anthropic]
```

## 🚀 Quick Start

```python
from lesstokens_sdk import LessTokensSDK

# Initialize SDK
sdk = LessTokensSDK(
    api_key="your-less-tokens-api-key",
    provider="openai"
)

# Process prompt
response = sdk.process_prompt(
    prompt="Explain what artificial intelligence is",
    llm_config={
        "api_key": "your-openai-api-key",
        "model": "gpt-4",
        "temperature": 0.7,
        # All OpenAI API options are supported
    }
)

print(response.content)
print(f"Tokens saved: {response.usage.savings}%")
```

## 📖 Documentation

- [Full API Documentation](./docs/API.md) - Complete API reference
- [Examples](./examples/) - Usage examples
- [Architecture Guide](./docs/ARCHITECTURE.md) - Technical architecture
- [Integration Guide](./docs/INTEGRATION.md) - Integration patterns

## 🎯 How It Works

The LessTokens SDK facilitates token compression before sending prompts to LLM APIs:

```
1. You send the prompt to the SDK
2. SDK compresses the prompt via LessTokens API
3. SDK sends the compressed prompt to your LLM API (using official provider SDKs)
4. SDK returns the final response with savings metrics
```

**Note**: The SDK uses official provider SDKs (OpenAI, Anthropic, Google) internally, ensuring full feature support and optimal performance.

## 💡 Examples

### Basic Usage

```python
response = sdk.process_prompt(
    prompt="Your prompt here",
    llm_config={
        "api_key": "your-api-key",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
    }
)
```

### With Custom Compression

```python
response = sdk.process_prompt(
    prompt="Very long prompt...",
    llm_config={
        "api_key": "your-api-key",
        "model": "gpt-4",
    },
    compression_options={
        "target_ratio": 0.3,  # Compress to 30% of original size
        "preserve_context": True,
        "aggressive": False,
    }
)
```

### Streaming Responses

```python
async for chunk in sdk.process_prompt_stream(
    prompt="Your prompt here",
    llm_config={
        "api_key": "your-api-key",
        "model": "gpt-4",
    }
):
    if chunk.done:
        print(f"Usage: {chunk.usage}")
    else:
        print(chunk.content, end="", flush=True)
```

### Multi-turn Conversations

```python
response = sdk.process_prompt(
    prompt="What is the capital of France?",
    llm_config={
        "api_key": "your-api-key",
        "model": "gpt-4",
    },
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ]
)
```

### Custom Message Role and Content

```python
# Custom role
response = sdk.process_prompt(
    prompt="Explain quantum computing",
    llm_config={"api_key": "...", "model": "gpt-4"},
    message_role="system"
)

# Custom content with function
def custom_content(compressed):
    return f"Compressed: {compressed.compressed}\nOriginal tokens: {compressed.original_tokens}"

response = sdk.process_prompt(
    prompt="Explain quantum computing",
    llm_config={"api_key": "...", "model": "gpt-4"},
    message_content=custom_content
)
```

### Compression Only

```python
compressed = sdk.compress_prompt(
    prompt="Very long prompt...",
    compression_options={
        "target_ratio": 0.5,
        "preserve_context": True,
    }
)

print(f"Compressed: {compressed.compressed}")
print(f"Savings: {compressed.savings}%")
```

## 🔌 Supported Providers

### OpenAI

```python
sdk = LessTokensSDK(api_key="...", provider="openai")

response = sdk.process_prompt(
    prompt="...",
    llm_config={
        "api_key": "sk-...",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        # All OpenAI API options supported
    }
)
```

### Anthropic

```python
sdk = LessTokensSDK(api_key="...", provider="anthropic")

response = sdk.process_prompt(
    prompt="...",
    llm_config={
        "api_key": "sk-ant-...",
        "model": "claude-3-opus-20240229",
        "max_tokens": 1024,
        # All Anthropic API options supported
    }
)
```

### Google

```python
sdk = LessTokensSDK(api_key="...", provider="google")

response = sdk.process_prompt(
    prompt="...",
    llm_config={
        "api_key": "...",
        "model": "gemini-pro",
        "temperature": 0.7,
        # All Google API options supported
    }
)
```

### DeepSeek

```python
sdk = LessTokensSDK(api_key="...", provider="deepseek")

response = sdk.process_prompt(
    prompt="...",
    llm_config={
        "api_key": "...",
        "model": "deepseek-chat",
        "temperature": 0.7,
        # All DeepSeek API options supported
    }
)
```

## 📊 Response Format

```python
response = sdk.process_prompt(...)

# Response object structure:
response.content          # str: LLM response text
response.usage            # TokenUsage: Token usage information
response.usage.prompt_tokens      # int: Original prompt tokens
response.usage.completion_tokens  # int: Completion tokens
response.usage.total_tokens       # int: Total tokens
response.usage.compressed_tokens   # int: Compressed prompt tokens (if used)
response.usage.savings            # float: Savings percentage (0-100)
response.metadata         # ResponseMetadata: Additional metadata
response.metadata.model           # str: Model used
response.metadata.provider         # str: Provider name
response.metadata.timestamp        # str: ISO timestamp
response.metadata.compression_ratio # float: Compression ratio (if used)
```

## 🔧 Configuration

### SDK Configuration

```python
sdk = LessTokensSDK(
    api_key="your-less-tokens-api-key",
    provider="openai",  # 'openai', 'anthropic', 'google', 'deepseek'
    base_url="https://lesstokens.hive-hub.ai",  # Optional
    timeout=30000,  # Optional, milliseconds
)
```

### Compression Options

```python
compression_options = {
    "target_ratio": 0.5,      # Target compression ratio (0.0 to 1.0)
    "preserve_context": True,  # Preserve context during compression
    "aggressive": False,       # Use aggressive compression
}
```

## 🛠️ Error Handling

```python
from lesstokens_sdk import LessTokensSDK, LessTokensError, ErrorCodes

try:
    response = sdk.process_prompt(...)
except LessTokensError as e:
    if e.code == ErrorCodes.INVALID_API_KEY:
        print("Invalid API key")
    elif e.code == ErrorCodes.COMPRESSION_FAILED:
        print("Compression failed")
    elif e.code == ErrorCodes.LLM_API_ERROR:
        print("LLM API error")
    else:
        print(f"Error: {e.message}")
```

## 📚 Full Provider API Support

The SDK passes through all provider-specific options to the official SDKs, ensuring full compatibility:

### OpenAI Options

```python
llm_config = {
    "api_key": "...",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop": ["\n", "Human:"],
    "n": 1,
    "stream": False,
    # ... all OpenAI API options
}
```

### Anthropic Options

```python
llm_config = {
    "api_key": "...",
    "model": "claude-3-opus-20240229",
    "max_tokens": 1024,
    "temperature": 0.7,
    "top_p": 0.9,
    # ... all Anthropic API options
}
```

### Google Options

```python
llm_config = {
    "api_key": "...",
    "model": "gemini-pro",
    "temperature": 0.7,
    "max_output_tokens": 1000,
    "top_p": 0.9,
    "top_k": 40,
    # ... all Google API options
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lesstokens_sdk --cov-report=html

# Run specific test file
pytest tests/test_sdk.py
```

## 📝 License

MIT License - see [LICENSE](./LICENSE) file for details.

## 🔗 Links

- [LessTokens Website](https://lesstokens.hive-hub.ai)
- [Report Bug](https://github.com/lesstokens/sdk-typescript/issues)


## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.

## 📞 Support

- **Documentation**: [Full API Docs](./docs/API.md)
- **Issues**: [GitHub Issues](https://github.com/hivellm/lesstokens-sdk-python/issues)
- **Email**: support@hive-hub.ai

---

Made with ❤️ by the HiveHub Team



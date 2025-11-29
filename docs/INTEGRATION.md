# LessTokens SDK - Integration Guide

## Quick Start

### Installation

```bash
pip install lesstokens-sdk
```

### Basic Usage

```python
import asyncio
from lesstokens_sdk import LessTokensSDK

async def main():
    sdk = LessTokensSDK(
        api_key="your-less-tokens-api-key",
        provider="openai"
    )

    response = await sdk.process_prompt({
        "prompt": "Explain quantum computing",
        "llm_config": {
            "api_key": "your-openai-api-key",
            "model": "gpt-4",
            "temperature": 0.7,
        }
    })

    print(response.content)
    print(f"Tokens saved: {response.usage.savings}%")

asyncio.run(main())
```

## Integration Patterns

### 1. Simple Integration

For basic use cases, use `process_prompt`:

```python
async def ask_question(question: str) -> str:
    sdk = LessTokensSDK(
        api_key=os.getenv("LESSTOKENS_API_KEY"),
        provider="openai"
    )

    response = await sdk.process_prompt({
        "prompt": question,
        "llm_config": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4",
        }
    })

    return response.content
```

### 2. Streaming Integration

For real-time responses:

```python
async def stream_response(question: str):
    sdk = LessTokensSDK(
        api_key=os.getenv("LESSTOKENS_API_KEY"),
        provider="openai"
    )

    async for chunk in sdk.process_prompt_stream({
        "prompt": question,
        "llm_config": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4",
        }
    }):
        if chunk.done:
            print(f"\nTokens saved: {chunk.usage.savings}%")
        else:
            print(chunk.content, end="", flush=True)
```

### 3. Multi-turn Conversations

For conversation history:

```python
async def chat_with_history(messages: List[Dict[str, str]], new_message: str):
    sdk = LessTokensSDK(
        api_key=os.getenv("LESSTOKENS_API_KEY"),
        provider="openai"
    )

    response = await sdk.process_prompt({
        "prompt": new_message,
        "llm_config": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4",
        },
        "messages": messages,  # Previous conversation
    })

    return response.content
```

### 4. Compression Only

For compression without LLM call:

```python
async def compress_text(text: str) -> CompressedPrompt:
    sdk = LessTokensSDK(
        api_key=os.getenv("LESSTOKENS_API_KEY"),
        provider="openai"
    )

    compressed = await sdk.compress_prompt(
        text,
        {
            "target_ratio": 0.5,
            "preserve_context": True,
        }
    )

    return compressed
```

## Provider-Specific Integration

### OpenAI

```python
sdk = LessTokensSDK(
    api_key="...",
    provider="openai"
)

response = await sdk.process_prompt({
    "prompt": "...",
    "llm_config": {
        "api_key": "sk-...",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop": ["\n", "Human:"],
        # All OpenAI API options supported
    }
})
```

### Anthropic

```python
sdk = LessTokensSDK(
    api_key="...",
    provider="anthropic"
)

response = await sdk.process_prompt({
    "prompt": "...",
    "llm_config": {
        "api_key": "sk-ant-...",
        "model": "claude-3-opus-20240229",
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9,
        # All Anthropic API options supported
    }
})
```

### Google

```python
sdk = LessTokensSDK(
    api_key="...",
    provider="google"
)

response = await sdk.process_prompt({
    "prompt": "...",
    "llm_config": {
        "api_key": "...",
        "model": "gemini-pro",
        "temperature": 0.7,
        "max_output_tokens": 1000,
        "top_p": 0.9,
        "top_k": 40,
        # All Google API options supported
    }
})
```

### DeepSeek

```python
sdk = LessTokensSDK(
    api_key="...",
    provider="deepseek"
)

response = await sdk.process_prompt({
    "prompt": "...",
    "llm_config": {
        "api_key": "...",
        "model": "deepseek-chat",
        "temperature": 0.7,
        # All DeepSeek API options supported
    }
})
```

## Error Handling

### Basic Error Handling

```python
from lesstokens_sdk import LessTokensSDK, LessTokensError, ErrorCodes

try:
    response = await sdk.process_prompt(...)
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

### Retry Logic

The SDK includes built-in retry logic for transient errors. You can customize it:

```python
# Retry is handled internally, but you can catch and retry manually:
max_retries = 3
for attempt in range(max_retries):
    try:
        response = await sdk.process_prompt(...)
        break
    except LessTokensError as e:
        if e.code in [ErrorCodes.TIMEOUT, ErrorCodes.NETWORK_ERROR]:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
        raise
```

## Best Practices

### 1. Environment Variables

Store API keys in environment variables:

```python
import os

sdk = LessTokensSDK(
    api_key=os.getenv("LESSTOKENS_API_KEY"),
    provider="openai"
)
```

### 2. Reuse SDK Instance

Create SDK instance once and reuse:

```python
# Good
sdk = LessTokensSDK(...)
response1 = await sdk.process_prompt(...)
response2 = await sdk.process_prompt(...)

# Bad
response1 = await LessTokensSDK(...).process_prompt(...)
response2 = await LessTokensSDK(...).process_prompt(...)
```

### 3. Handle Errors Gracefully

Always handle errors:

```python
try:
    response = await sdk.process_prompt(...)
except LessTokensError as e:
    logger.error(f"Error: {e.code} - {e.message}")
    # Handle error appropriately
```

### 4. Use Streaming for Long Responses

For long responses, use streaming:

```python
async for chunk in sdk.process_prompt_stream(...):
    if not chunk.done:
        # Process chunk immediately
        process_chunk(chunk.content)
```

### 5. Monitor Usage

Track token usage and savings:

```python
response = await sdk.process_prompt(...)
logger.info(f"Tokens used: {response.usage.total_tokens}")
logger.info(f"Tokens saved: {response.usage.savings}%")
```

## Advanced Usage

### Custom Message Content

```python
def custom_content(compressed: CompressedPrompt) -> str:
    return f"""
    Original tokens: {compressed.original_tokens}
    Compressed tokens: {compressed.compressed_tokens}
    Savings: {compressed.savings}%
    
    Compressed prompt:
    {compressed.compressed}
    """

response = await sdk.process_prompt({
    "prompt": "...",
    "llm_config": {...},
    "message_content": custom_content,
})
```

### Custom Message Role

```python
response = await sdk.process_prompt({
    "prompt": "...",
    "llm_config": {...},
    "message_role": "system",
})
```

### Compression Options

```python
response = await sdk.process_prompt({
    "prompt": "...",
    "llm_config": {...},
    "compression_options": {
        "target_ratio": 0.3,  # Compress to 30% of original
        "preserve_context": True,
        "aggressive": False,
    }
})
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Install provider-specific dependencies: `pip install lesstokens-sdk[openai]`

2. **Timeout Errors**
   - Increase timeout: `timeout=60000` (60 seconds)

3. **API Key Errors**
   - Verify API keys are correct
   - Check environment variables

4. **Network Errors**
   - Check internet connection
   - Verify API endpoints are accessible

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## Migration Guide

### From Direct API Calls

If you're currently calling LLM APIs directly:

1. Install SDK: `pip install lesstokens-sdk`
2. Replace direct API calls with SDK calls
3. Add compression options as needed

### From Other SDKs

The LessTokens SDK is compatible with existing provider SDKs. You can:
- Use the same configuration options
- Get the same response format
- Add compression with minimal changes



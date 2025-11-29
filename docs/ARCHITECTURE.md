# LessTokens SDK - Architecture Guide

## Overview

The LessTokens SDK is designed as a thin wrapper that:
1. Compresses prompts via the LessTokens API
2. Delegates to official LLM provider SDKs for API calls
3. Provides a unified interface across multiple providers

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Code                         │
└──────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LessTokensSDK                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  - process_prompt()                                   │   │
│  │  - process_prompt_stream()                            │   │
│  │  - compress_prompt()                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   LessTokensClient       │    │      LLMClient               │
│  ┌────────────────────┐  │    │  ┌────────────────────────┐ │
│  │ - compress()       │  │    │  │ - chat()              │ │
│  │ - _perform_        │  │    │  │ - chat_stream()        │ │
│  │   compression_     │  │    │  └────────────────────────┘ │
│  │   request()        │  │    │            │                │
│  └────────────────────┘  │    │            ▼                │
└──────────┬───────────────┘    │  ┌────────────────────────┐ │
           │                     │  │   Provider Factory     │ │
           ▼                     │  │  - create_provider()  │ │
┌──────────────────────────┐     │  └────────────────────────┘ │
│   LessTokens API         │     │            │                │
│   (HTTP/REST)            │     │            ▼                │
└──────────────────────────┘     │  ┌────────────────────────┐ │
                                 │  │   Provider            │ │
                                 │  │   Implementations     │ │
                                 │  │  - OpenAIProvider     │ │
                                 │  │  - AnthropicProvider  │ │
                                 │  │  - GoogleProvider    │ │
                                 │  │  - DeepSeekProvider   │ │
                                 │  └────────────────────────┘ │
                                 └────────────┬───────────────┘
                                              │
                                              ▼
                                 ┌──────────────────────────────┐
                                 │   Official Provider SDKs     │
                                 │  - openai                    │
                                 │  - anthropic                 │
                                 │  - google-generativeai       │
                                 └──────────────────────────────┘
```

## Core Components

### 1. LessTokensSDK

Main entry point for the SDK. Coordinates compression and LLM API calls.

**Responsibilities:**
- Validate configuration and inputs
- Orchestrate compression and LLM requests
- Calculate and attach compression metrics
- Handle streaming responses

### 2. LessTokensClient

Client for communicating with the LessTokens API.

**Responsibilities:**
- Handle HTTP requests to LessTokens API
- Implement retry logic with exponential backoff
- Parse and normalize API responses
- Handle errors and timeouts

### 3. LLMClient

Wrapper around provider implementations.

**Responsibilities:**
- Provide unified interface for all providers
- Delegate to appropriate provider implementation
- Handle provider-specific differences

### 4. Provider Implementations

Provider-specific adapters that wrap official SDKs.

**Responsibilities:**
- Convert SDK types to internal types
- Handle provider-specific API differences
- Implement streaming support
- Extract usage metrics

### 5. Utilities

Supporting utilities for validation, retry, and error handling.

**Responsibilities:**
- Input validation
- Retry logic with exponential backoff
- Error creation and handling

## Data Flow

### Process Prompt Flow

1. **Input Validation**
   - Validate SDK configuration
   - Validate prompt and options
   - Validate LLM configuration

2. **Compression**
   - Send prompt to LessTokens API
   - Receive compressed prompt and metrics
   - Handle errors and retries

3. **LLM Request**
   - Create provider instance
   - Build messages array (with optional conversation history)
   - Send to LLM provider
   - Receive response and usage metrics

4. **Response Assembly**
   - Combine LLM response with compression metrics
   - Calculate total savings
   - Return unified response

### Streaming Flow

Similar to process prompt flow, but:
- LLM response is streamed chunk by chunk
- Compression metrics are added to final chunk
- Client receives chunks asynchronously

## Design Principles

### 1. Thin Wrapper

The SDK is a thin wrapper that:
- Uses official provider SDKs internally
- Doesn't reimplement provider logic
- Passes through all provider-specific options

### 2. Unified Interface

All providers share the same interface:
- Same method signatures
- Same response types
- Same error handling

### 3. Type Safety

Full type hints for:
- All public APIs
- Internal types
- Provider-specific options (via TypedDict)

### 4. Error Handling

Consistent error handling:
- Custom error class (`LessTokensError`)
- Error codes for programmatic handling
- Detailed error messages

### 5. Async/Await

Fully async implementation:
- Non-blocking I/O
- Efficient resource usage
- Native Python async support

## Extension Points

### Adding New Providers

1. Create provider class implementing `LLMProvider`
2. Add provider to factory function
3. Update validation and types

### Custom Retry Logic

Override retry configuration:
- Per-request retry settings
- Custom retryable errors
- Custom delay calculation

### Custom Message Formatting

Use `message_content` option:
- String: Direct content
- Callable: Dynamic content based on compression results

## Performance Considerations

### Connection Pooling

HTTP clients use connection pooling for efficiency.

### Streaming

Streaming responses reduce memory usage for large responses.

### Retry Logic

Exponential backoff prevents overwhelming APIs during retries.

### Type Conversions

Minimal type conversions to reduce overhead.

## Security Considerations

### API Keys

API keys are never logged or exposed in error messages.

### HTTPS

All API calls use HTTPS.

### Timeouts

Configurable timeouts prevent hanging requests.

## Testing Strategy

### Unit Tests

- Test each component in isolation
- Mock external dependencies
- Test error cases

### Integration Tests

- Test with real APIs (using test keys)
- Test provider-specific behavior
- Test streaming

### Coverage

- Aim for high test coverage
- Test edge cases
- Test error handling



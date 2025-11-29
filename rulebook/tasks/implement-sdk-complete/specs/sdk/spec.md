# LessTokens SDK Specification

## ADDED Requirements

### Requirement: LessTokensSDK Main Class
The SDK SHALL provide a main class `LessTokensSDK` that coordinates prompt compression and LLM API calls with a unified interface.

#### Scenario: Initialize SDK with valid configuration
Given a valid LessTokens API key and provider name
When initializing LessTokensSDK
Then the SDK MUST be initialized successfully with the provided configuration

#### Scenario: Process prompt with compression
Given a prompt and LLM configuration
When calling process_prompt()
Then the SDK MUST compress the prompt via LessTokens API, send to LLM provider, and return response with compression metrics

#### Scenario: Process prompt with streaming
Given a prompt and LLM configuration
When calling process_prompt_stream()
Then the SDK MUST return an async iterator that yields stream chunks with compression metrics in the final chunk

#### Scenario: Compress prompt without LLM call
Given a prompt and optional compression options
When calling compress_prompt()
Then the SDK MUST return compression results including compressed text, token counts, savings, and ratio

### Requirement: Provider Support
The SDK SHALL support multiple LLM providers (OpenAI, Anthropic, Google, DeepSeek) with full API compatibility.

#### Scenario: OpenAI provider support
Given OpenAI API key and configuration
When using provider "openai"
Then the SDK MUST support all OpenAI API options including temperature, max_tokens, top_p, frequency_penalty, presence_penalty, stop sequences

#### Scenario: Anthropic provider support
Given Anthropic API key and configuration
When using provider "anthropic"
Then the SDK MUST support all Anthropic API options including max_tokens, temperature, top_p

#### Scenario: Google provider support
Given Google API key and configuration
When using provider "google"
Then the SDK MUST support all Google API options including temperature, max_output_tokens, top_p, top_k

#### Scenario: DeepSeek provider support
Given DeepSeek API key and configuration
When using provider "deepseek"
Then the SDK MUST support all DeepSeek API options including temperature and other provider-specific options

### Requirement: Multi-turn Conversations
The SDK SHALL support multi-turn conversations with conversation history.

#### Scenario: Process prompt with conversation history
Given a prompt, LLM configuration, and previous messages
When calling process_prompt() with messages parameter
Then the SDK MUST include previous messages in the conversation context before sending the compressed prompt

### Requirement: Custom Message Formatting
The SDK SHALL support custom message roles and content formatting.

#### Scenario: Custom message role
Given a prompt and custom message role
When calling process_prompt() with message_role parameter
Then the SDK MUST use the custom role instead of default "user" role

#### Scenario: Custom message content
Given a prompt and custom message content function
When calling process_prompt() with message_content parameter
Then the SDK MUST use the custom content function to format the message with compression results

### Requirement: Compression Options
The SDK SHALL support customizable compression options.

#### Scenario: Target compression ratio
Given a prompt and target_ratio option
When calling process_prompt() or compress_prompt() with target_ratio
Then the SDK MUST compress the prompt to approximately the target ratio

#### Scenario: Preserve context during compression
Given a prompt and preserve_context option
When calling process_prompt() or compress_prompt() with preserve_context=True
Then the SDK MUST preserve important context during compression

#### Scenario: Aggressive compression
Given a prompt and aggressive option
When calling process_prompt() or compress_prompt() with aggressive=True
Then the SDK MUST apply more aggressive compression strategies

### Requirement: Usage Metrics
The SDK SHALL provide comprehensive usage metrics including token counts and savings.

#### Scenario: Calculate token usage
Given a processed prompt response
When receiving LLM response
Then the SDK MUST calculate and return prompt_tokens, completion_tokens, total_tokens, compressed_tokens, and savings percentage

#### Scenario: Calculate compression ratio
Given compression results
When compressing a prompt
Then the SDK MUST calculate and return compression ratio (compressed_tokens / original_tokens)

### Requirement: Error Handling
The SDK SHALL provide robust error handling with standardized error codes and messages.

#### Scenario: Invalid API key error
Given an invalid LessTokens API key
When making a compression request
Then the SDK MUST raise LessTokensError with code INVALID_API_KEY

#### Scenario: Invalid provider error
Given an unsupported provider name
When initializing LessTokensSDK
Then the SDK MUST raise LessTokensError with code INVALID_PROVIDER

#### Scenario: Compression failure error
Given a compression request that fails
When the LessTokens API returns an error
Then the SDK MUST raise LessTokensError with code COMPRESSION_FAILED

#### Scenario: LLM API error
Given an LLM API request that fails
When the provider API returns an error
Then the SDK MUST raise LessTokensError with code LLM_API_ERROR

#### Scenario: Timeout error
Given a request that exceeds timeout
When making an API request
Then the SDK MUST raise LessTokensError with code TIMEOUT

#### Scenario: Network error
Given a network connectivity issue
When making an API request
Then the SDK MUST raise LessTokensError with code NETWORK_ERROR

### Requirement: Retry Logic
The SDK SHALL implement retry logic with exponential backoff for transient errors.

#### Scenario: Retry on timeout
Given a request that times out
When the request fails with TIMEOUT error
Then the SDK MUST retry the request with exponential backoff up to max_retries

#### Scenario: Retry on network error
Given a request that fails due to network error
When the request fails with NETWORK_ERROR
Then the SDK MUST retry the request with exponential backoff up to max_retries

### Requirement: Type Safety
The SDK SHALL provide complete type hints for all public APIs.

#### Scenario: Type hints for configuration
Given SDK configuration types
When using LessTokensConfig, LLMConfig, CompressionOptions
Then all configuration types MUST be properly typed with TypedDict

#### Scenario: Type hints for responses
Given SDK response types
When using LLMResponse, CompressedPrompt, TokenUsage, StreamChunk
Then all response types MUST be properly typed with dataclasses

#### Scenario: Type hints for methods
Given SDK methods
When calling public methods
Then all method signatures MUST have complete type hints including parameters and return types



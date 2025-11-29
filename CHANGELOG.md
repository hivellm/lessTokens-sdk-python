# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-07

### Added

- Initial release of LessTokens Python SDK
- Support for OpenAI, Anthropic, Google, and DeepSeek providers
- Prompt compression via LessTokens API
- Streaming response support
- Multi-turn conversation support
- Custom message role and content
- Full provider API compatibility
- Comprehensive error handling
- Retry logic with exponential backoff
- Complete type hints
- Full documentation (API, Architecture, Integration guides)
- Example code for common use cases

### Features

- **LessTokensSDK**: Main SDK class for compressing prompts and sending to LLM providers
- **LessTokensClient**: Client for LessTokens API with retry logic
- **LLMClient**: Unified interface for all LLM providers
- **Provider Support**: OpenAI, Anthropic, Google, DeepSeek
- **Streaming**: Real-time streaming responses with compression metrics
- **Multi-turn Conversations**: Support for conversation history
- **Custom Messages**: Customize message roles and content
- **Full API Compatibility**: All provider-specific options supported

### Documentation

- README with quick start and examples
- Complete API reference
- Architecture guide explaining design decisions
- Integration guide with best practices
- Example code for common patterns

### Technical Details

- Python 3.8+ support
- Async/await throughout
- Full type hints
- Comprehensive error handling
- Retry logic with exponential backoff
- Minimal dependencies



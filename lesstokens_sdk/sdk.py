"""
Main LessTokens SDK class
"""

from typing import AsyncIterator, Dict, List, Optional

from lesstokens_sdk.clients.less_tokens_client import LessTokensClient
from lesstokens_sdk.clients.llm_client import LLMClient
from lesstokens_sdk.types import (
    CompressedPrompt,
    CompressionOptions,
    LLMResponse,
    LessTokensConfig,
    ProcessPromptOptions,
    ResponseMetadata,
    StreamChunk,
    TokenUsage,
)
from lesstokens_sdk.utils.validation import (
    validate_config,
    validate_process_prompt_options,
    validate_prompt,
)


class LessTokensSDK:
    """
    Main LessTokens SDK class

    Provides a simple interface to compress prompts using LessTokens API
    and send them to various LLM providers (OpenAI, Anthropic, Google, DeepSeek).
    """

    def __init__(self, config: LessTokensConfig):
        """
        Creates a new LessTokensSDK instance

        Args:
            config: SDK configuration
                - api_key: LessTokens API key (required)
                - provider: LLM provider name ('openai', 'anthropic', 'google', 'deepseek') (required)
                - base_url: Optional base URL for LessTokens API (default: 'https://lesstokens.hive-hub.ai')
                - timeout: Optional request timeout in milliseconds (default: 30000)

        Raises:
            LessTokensError: If configuration is invalid
        """
        validate_config(config)

        self.provider = config["provider"].lower()
        self.less_tokens_client = LessTokensClient(
            config["api_key"],
            config.get("base_url") or "https://lesstokens.hive-hub.ai",
            config.get("timeout") or 30000,
        )

    async def process_prompt(self, options: ProcessPromptOptions) -> LLMResponse:
        """
        Process a prompt through LessTokens compression and send to LLM

        This method:
        1. Compresses the prompt using LessTokens API
        2. Sends the compressed prompt to the configured LLM provider
        3. Returns the LLM response with compression metrics

        Args:
            options: Processing options
                - prompt: The prompt to compress and send (required)
                - llm_config: LLM provider configuration (API key, model, etc.) (required)
                - compression_options: Optional compression settings
                - message_role: Custom message role (default: 'user')
                - message_content: Custom message content. Can be a string or a function that receives the compressed prompt
                - messages: Additional messages for multi-turn conversations

        Returns:
            LLM response with compression metrics

        Raises:
            LessTokensError: If compression or LLM request fails
        """
        validate_process_prompt_options(options)

        # Step 1: Compress prompt via LessTokens
        compressed = await self.less_tokens_client.compress(
            options["prompt"], options.get("compression_options")
        )

        # Step 2: Send compressed prompt to LLM
        base_url: Optional[str] = options["llm_config"].get("base_url") or options[
            "llm_config"
        ].get("baseURL")  # type: ignore[assignment]
        llm_client = LLMClient(
            self.provider, options["llm_config"]["api_key"], base_url
        )

        # Determine message role and content
        role = options.get("message_role") or "user"
        message_content = options.get("message_content")
        if callable(message_content):
            content = message_content(compressed)
        else:
            content = (
                message_content
                if message_content is not None
                else compressed.compressed
            )

        # Build messages array - include additional messages if provided, then add the compressed prompt
        messages: List[Dict[str, str]] = []
        additional_messages = options.get("messages")
        if additional_messages and len(additional_messages) > 0:
            messages.extend(additional_messages)
        messages.append({"role": role, "content": content})

        response = await llm_client.chat(messages, options["llm_config"])

        # Step 3: Calculate savings and update usage
        savings = (
            (
                (compressed.original_tokens - compressed.compressed_tokens)
                / compressed.original_tokens
            )
            * 100
            if compressed.original_tokens > 0
            else 0
        )

        # Create updated usage with compression metrics
        updated_usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            compressed_tokens=compressed.compressed_tokens,
            savings=round(savings * 100) / 100,  # Round to 2 decimal places
        )

        # Create updated metadata with compression ratio
        updated_metadata = ResponseMetadata(
            model=response.metadata.model if response.metadata else None,
            provider=response.metadata.provider if response.metadata else None,
            timestamp=response.metadata.timestamp if response.metadata else None,
            compression_ratio=compressed.ratio,
        )

        return LLMResponse(
            content=response.content,
            usage=updated_usage,
            metadata=updated_metadata,
        )

    async def process_prompt_stream(
        self, options: ProcessPromptOptions
    ) -> AsyncIterator[StreamChunk]:
        """
        Process a prompt with streaming response

        Similar to process_prompt, but returns a stream of chunks instead of waiting
        for the complete response. The final chunk includes compression metrics.

        Args:
            options: Processing options (same as process_prompt)

        Returns:
            Async iterable of stream chunks

        Raises:
            LessTokensError: If compression or LLM request fails
        """
        validate_process_prompt_options(options)

        # Step 1: Compress prompt via LessTokens
        compressed = await self.less_tokens_client.compress(
            options["prompt"], options.get("compression_options")
        )

        # Step 2: Send compressed prompt to LLM with streaming
        base_url: Optional[str] = options["llm_config"].get("base_url") or options[
            "llm_config"
        ].get("baseURL")  # type: ignore[assignment]
        llm_client = LLMClient(
            self.provider, options["llm_config"]["api_key"], base_url
        )

        # Determine message role and content
        role = options.get("message_role") or "user"
        message_content = options.get("message_content")
        if callable(message_content):
            content = message_content(compressed)
        else:
            content = (
                message_content
                if message_content is not None
                else compressed.compressed
            )

        # Build messages array - include additional messages if provided, then add the compressed prompt
        messages: List[Dict[str, str]] = []
        additional_messages = options.get("messages")
        if additional_messages and len(additional_messages) > 0:
            messages.extend(additional_messages)
        messages.append({"role": role, "content": content})

        # chat_stream is an async generator, returns AsyncIterator directly
        stream = llm_client.chat_stream(messages, options["llm_config"])  # type: ignore[assignment]

        # Step 3: Wrap stream and add compression metrics to final chunk
        async for chunk in self._wrap_stream(stream, compressed):
            yield chunk

    async def compress_prompt(
        self, prompt: str, options: Optional[CompressionOptions] = None
    ) -> CompressedPrompt:
        """
        Compress a prompt without sending to LLM

        Useful when you only want to compress a prompt without sending it to an LLM.
        Returns compression results including token counts and savings.

        Args:
            prompt: The prompt to compress
            options: Optional compression settings
                - target_ratio: Target compression ratio (0.0-1.0)
                - preserve_context: Whether to preserve context during compression
                - aggressive: Whether to use aggressive compression

        Returns:
            Compression results

        Raises:
            LessTokensError: If compression fails
        """
        validate_prompt(prompt)
        return await self.less_tokens_client.compress(prompt, options)

    async def _wrap_stream(
        self, stream: AsyncIterator[StreamChunk], compressed: CompressedPrompt
    ) -> AsyncIterator[StreamChunk]:
        """Wrap stream and add compression metrics"""
        last_chunk: Optional[StreamChunk] = None

        async for chunk in stream:
            last_chunk = chunk
            if not chunk.done:
                yield chunk

        # Add compression metrics to final chunk
        if last_chunk and last_chunk.done and last_chunk.usage:
            savings = (
                (
                    (compressed.original_tokens - compressed.compressed_tokens)
                    / compressed.original_tokens
                )
                * 100
                if compressed.original_tokens > 0
                else 0
            )

            updated_usage = TokenUsage(
                prompt_tokens=last_chunk.usage.prompt_tokens,
                completion_tokens=last_chunk.usage.completion_tokens,
                total_tokens=last_chunk.usage.total_tokens,
                compressed_tokens=compressed.compressed_tokens,
                savings=round(savings * 100) / 100,
            )

            yield StreamChunk(content="", done=True, usage=updated_usage)
        elif last_chunk and last_chunk.done:
            # If no usage info, create it
            savings = (
                (
                    (compressed.original_tokens - compressed.compressed_tokens)
                    / compressed.original_tokens
                )
                * 100
                if compressed.original_tokens > 0
                else 0
            )

            yield StreamChunk(
                content="",
                done=True,
                usage=TokenUsage(
                    prompt_tokens=compressed.original_tokens,
                    completion_tokens=0,
                    total_tokens=compressed.original_tokens,
                    compressed_tokens=compressed.compressed_tokens,
                    savings=round(savings * 100) / 100,
                ),
            )


"""
Anthropic provider implementation
"""

from datetime import datetime
from typing import AsyncIterator, Dict, List

try:
    from anthropic import AsyncAnthropic
    from anthropic.types import Message, MessageParam, MessageStreamEvent
except ImportError:
    AsyncAnthropic = None  # type: ignore
    Message = None  # type: ignore
    MessageParam = None  # type: ignore
    MessageStreamEvent = None  # type: ignore

from lesstokens_sdk.errors import ErrorCodes, create_error
from lesstokens_sdk.providers.base import LLMProvider
from lesstokens_sdk.types import LLMConfig, LLMResponse, StreamChunk


class AnthropicProvider(LLMProvider):
    """Anthropic provider"""

    def __init__(self, api_key: str):
        if AsyncAnthropic is None:
            raise ImportError(
                "Anthropic SDK not installed. Install it with: pip install lesstokens-sdk[anthropic]"
            )
        self.client = AsyncAnthropic(api_key=api_key)

    async def chat(
        self, messages: List[Dict[str, str]], config: LLMConfig
    ) -> LLMResponse:
        """Send a chat completion request"""
        try:
            model = config["model"]
            temperature = config.get("temperature")
            max_tokens = config.get("max_tokens") or config.get("maxTokens") or 1024
            top_p = config.get("top_p") or config.get("topP")

            # Get all other options
            rest_options = {
                k: v
                for k, v in config.items()
                if k
                not in [
                    "api_key",
                    "model",
                    "temperature",
                    "max_tokens",
                    "maxTokens",
                    "top_p",
                    "topP",
                ]
            }

            # Convert messages to Anthropic format
            anthropic_messages: List[Dict[str, str]] = []
            for msg in messages:
                if msg["role"] == "system":
                    # Anthropic doesn't have system role, convert to user
                    anthropic_messages.append(
                        {"role": "user", "content": msg["content"]}
                    )
                else:
                    anthropic_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                messages=anthropic_messages,  # type: ignore
                **rest_options,
            )

            message = response
            text_content = None
            for item in message.content:
                if hasattr(item, "type") and item.type == "text":  # type: ignore
                    text_content = item.text if hasattr(item, "text") else None  # type: ignore
                    break

            content = text_content or ""

            return LLMResponse(
                content=content,
                usage=type(
                    "TokenUsage",
                    (),
                    {
                        "prompt_tokens": message.usage.input_tokens
                        if message.usage
                        else 0,
                        "completion_tokens": message.usage.output_tokens
                        if message.usage
                        else 0,
                        "total_tokens": (
                            message.usage.input_tokens if message.usage else 0
                        )
                        + (message.usage.output_tokens if message.usage else 0),
                    },
                )(),
                metadata=type(
                    "ResponseMetadata",
                    (),
                    {
                        "model": message.model,
                        "provider": "anthropic",
                        "timestamp": datetime.now().isoformat(),
                    },
                )(),
            )
        except Exception as error:
            if hasattr(error, "code"):
                raise  # Re-throw LessTokensError
            message = str(error) if error else "Unknown error"
            raise create_error(
                ErrorCodes.LLM_API_ERROR, f"Anthropic API error: {message}", None, error
            )

    async def chat_stream(  # type: ignore[override]
        self, messages: List[Dict[str, str]], config: LLMConfig
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request"""
        try:
            model = config["model"]
            temperature = config.get("temperature")
            max_tokens = config.get("max_tokens") or config.get("maxTokens") or 1024
            top_p = config.get("top_p") or config.get("topP")

            # Get all other options
            rest_options = {
                k: v
                for k, v in config.items()
                if k
                not in [
                    "api_key",
                    "model",
                    "temperature",
                    "max_tokens",
                    "maxTokens",
                    "top_p",
                    "topP",
                ]
            }

            # Convert messages to Anthropic format
            anthropic_messages: List[Dict[str, str]] = []
            for msg in messages:
                if msg["role"] == "system":
                    anthropic_messages.append(
                        {"role": "user", "content": msg["content"]}
                    )
                else:
                    anthropic_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            stream = await self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                messages=anthropic_messages,  # type: ignore
                **rest_options,
            )

            usage = None
            async for event in stream:
                if hasattr(event, "type"):
                    event_type = event.type  # type: ignore
                    if event_type == "content_block_delta":
                        if hasattr(event, "delta") and hasattr(event.delta, "type"):  # type: ignore
                            if event.delta.type == "text_delta":  # type: ignore
                                text = (
                                    event.delta.text
                                    if hasattr(event.delta, "text")
                                    else ""
                                )  # type: ignore
                                if text:
                                    yield StreamChunk(content=text, done=False)

                    if event_type == "message_stop":
                        # Usage is available in the final message
                        final_message = (
                            await stream.get_final_message()
                            if hasattr(stream, "get_final_message")
                            else None
                        )
                        if (
                            final_message
                            and hasattr(final_message, "usage")
                            and final_message.usage
                        ):
                            usage = type(
                                "TokenUsage",
                                (),
                                {
                                    "prompt_tokens": final_message.usage.input_tokens
                                    or 0,
                                    "completion_tokens": final_message.usage.output_tokens
                                    or 0,
                                    "total_tokens": (
                                        final_message.usage.input_tokens or 0
                                    )
                                    + (final_message.usage.output_tokens or 0),
                                },
                            )()

            # Final chunk with usage
            yield StreamChunk(content="", done=True, usage=usage)
        except Exception as error:
            message = str(error) if error else "Unknown error"
            raise create_error(
                ErrorCodes.LLM_API_ERROR, f"Anthropic API error: {message}", None, error
            )


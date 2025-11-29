"""
DeepSeek provider implementation
Uses OpenAI SDK with DeepSeek's base URL
"""

from datetime import datetime
from typing import AsyncIterator, Dict, List

try:
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletionChunk
except ImportError:
    AsyncOpenAI = None  # type: ignore
    ChatCompletionChunk = None  # type: ignore

from lesstokens_sdk.errors import ErrorCodes, create_error
from lesstokens_sdk.providers.base import LLMProvider
from lesstokens_sdk.types import LLMConfig, LLMResponse, StreamChunk


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider (OpenAI-compatible API)"""

    def __init__(self, api_key: str):
        if AsyncOpenAI is None:
            raise ImportError(
                "OpenAI SDK not installed. Install it with: pip install lesstokens-sdk[deepseek]"
            )
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    async def chat(
        self, messages: List[Dict[str, str]], config: LLMConfig
    ) -> LLMResponse:
        """Send a chat completion request"""
        try:
            model = config["model"]
            temperature = config.get("temperature")
            max_tokens = config.get("max_tokens") or config.get("maxTokens")
            top_p = config.get("top_p") or config.get("topP")
            frequency_penalty = config.get("frequency_penalty") or config.get(
                "frequencyPenalty"
            )
            presence_penalty = config.get("presence_penalty") or config.get(
                "presencePenalty"
            )
            stop = config.get("stop")

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
                    "frequency_penalty",
                    "frequencyPenalty",
                    "presence_penalty",
                    "presencePenalty",
                    "stop",
                ]
            }

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": msg["role"], "content": msg["content"]} for msg in messages
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                **rest_options,
            )

            completion = response
            choice = completion.choices[0] if completion.choices else None
            if not choice or not choice.message:
                raise create_error(
                    ErrorCodes.LLM_API_ERROR, "No response from DeepSeek"
                )

            return LLMResponse(
                content=choice.message.content or "",
                usage=type(
                    "TokenUsage",
                    (),
                    {
                        "prompt_tokens": completion.usage.prompt_tokens
                        if completion.usage
                        else 0,
                        "completion_tokens": completion.usage.completion_tokens
                        if completion.usage
                        else 0,
                        "total_tokens": completion.usage.total_tokens
                        if completion.usage
                        else 0,
                    },
                )(),
                metadata=type(
                    "ResponseMetadata",
                    (),
                    {
                        "model": completion.model,
                        "provider": "deepseek",
                        "timestamp": datetime.now().isoformat(),
                    },
                )(),
            )
        except Exception as error:
            if hasattr(error, "code"):
                raise  # Re-throw LessTokensError
            message = str(error) if error else "Unknown error"
            raise create_error(
                ErrorCodes.LLM_API_ERROR, f"DeepSeek API error: {message}", None, error
            )

    async def chat_stream(  # type: ignore[override]
        self, messages: List[Dict[str, str]], config: LLMConfig
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request"""
        try:
            model = config["model"]
            temperature = config.get("temperature")
            max_tokens = config.get("max_tokens") or config.get("maxTokens")
            top_p = config.get("top_p") or config.get("topP")
            frequency_penalty = config.get("frequency_penalty") or config.get(
                "frequencyPenalty"
            )
            presence_penalty = config.get("presence_penalty") or config.get(
                "presencePenalty"
            )
            stop = config.get("stop")

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
                    "frequency_penalty",
                    "frequencyPenalty",
                    "presence_penalty",
                    "presencePenalty",
                    "stop",
                ]
            }

            stream = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": msg["role"], "content": msg["content"]} for msg in messages
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                stream=True,
                **rest_options,
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield StreamChunk(content=delta.content, done=False)

                # Capture usage if available
                if chunk.usage:
                    yield StreamChunk(
                        content="",
                        done=True,
                        usage=type(
                            "TokenUsage",
                            (),
                            {
                                "prompt_tokens": chunk.usage.prompt_tokens or 0,
                                "completion_tokens": chunk.usage.completion_tokens or 0,
                                "total_tokens": chunk.usage.total_tokens or 0,
                            },
                        )(),
                    )
        except Exception as error:
            message = str(error) if error else "Unknown error"
            raise create_error(
                ErrorCodes.LLM_API_ERROR, f"DeepSeek API error: {message}", None, error
            )


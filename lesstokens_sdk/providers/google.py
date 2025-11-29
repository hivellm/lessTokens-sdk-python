"""
Google provider implementation
"""

from datetime import datetime
from typing import AsyncIterator, Dict, List

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # type: ignore

from lesstokens_sdk.errors import ErrorCodes, create_error
from lesstokens_sdk.providers.base import LLMProvider
from lesstokens_sdk.types import LLMConfig, LLMResponse, StreamChunk


class GoogleProvider(LLMProvider):
    """Google provider"""

    def __init__(self, api_key: str):
        if genai is None:
            raise ImportError(
                "Google Generative AI SDK not installed. Install it with: pip install lesstokens-sdk[google]"
            )
        genai.configure(api_key=api_key)
        self.api_key = api_key

    async def chat(self, messages: List[Dict[str, str]], config: LLMConfig) -> LLMResponse:
        """Send a chat completion request"""
        try:
            model_name = config["model"]
            temperature = config.get("temperature")
            max_tokens = config.get("max_tokens") or config.get("maxTokens")
            top_p = config.get("top_p") or config.get("topP")
            top_k = config.get("top_k") or config.get("topK")

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
                    "top_k",
                    "topK",
                ]
            }

            # Convert messages to Google format
            contents = []
            for msg in messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})

            model = genai.GenerativeModel(model_name)
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": top_p,
                "top_k": top_k,
                **rest_options,
            }

            response = await model.generate_content_async(
                contents=contents, generation_config=generation_config
            )

            # Extract text from response
            text = ""
            if response and hasattr(response, "candidates"):
                candidates = response.candidates  # type: ignore
                if candidates and len(candidates) > 0:
                    candidate = candidates[0]
                    if hasattr(candidate, "content") and candidate.content:  # type: ignore
                        parts = (
                            candidate.content.parts if hasattr(candidate.content, "parts") else []
                        )  # type: ignore
                        text = "".join(
                            part.text if hasattr(part, "text") else ""
                            for part in parts  # type: ignore
                        )

            # Try to get usage metadata
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:  # type: ignore
                usage_metadata = response.usage_metadata  # type: ignore
                prompt_tokens = getattr(usage_metadata, "prompt_token_count", 0) or 0
                completion_tokens = getattr(usage_metadata, "candidates_token_count", 0) or 0

            return LLMResponse(
                content=text,
                usage=type(
                    "TokenUsage",
                    (),
                    {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens,
                    },
                )(),
                metadata=type(
                    "ResponseMetadata",
                    (),
                    {
                        "model": model_name,
                        "provider": "google",
                        "timestamp": datetime.now().isoformat(),
                    },
                )(),
            )
        except Exception as error:
            if hasattr(error, "code"):
                raise  # Re-throw LessTokensError
            message = str(error) if error else "Unknown error"
            raise create_error(
                ErrorCodes.LLM_API_ERROR, f"Google API error: {message}", None, error
            )

    async def chat_stream(  # type: ignore[override]
        self, messages: List[Dict[str, str]], config: LLMConfig
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request"""
        try:
            model_name = config["model"]
            temperature = config.get("temperature")
            max_tokens = config.get("max_tokens") or config.get("maxTokens")
            top_p = config.get("top_p") or config.get("topP")
            top_k = config.get("top_k") or config.get("topK")

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
                    "top_k",
                    "topK",
                ]
            }

            # Convert messages to Google format
            contents = []
            for msg in messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})

            model = genai.GenerativeModel(model_name)
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": top_p,
                "top_k": top_k,
                **rest_options,
            }

            stream = await model.generate_content_async(
                contents=contents, generation_config=generation_config, stream=True
            )

            async for chunk in stream:
                if hasattr(chunk, "text") and chunk.text:  # type: ignore
                    yield StreamChunk(content=chunk.text, done=False)  # type: ignore
                elif hasattr(chunk, "candidates") and chunk.candidates:  # type: ignore
                    candidates = chunk.candidates  # type: ignore
                    if len(candidates) > 0:
                        candidate = candidates[0]
                        if hasattr(candidate, "content") and candidate.content:  # type: ignore
                            parts = (
                                candidate.content.parts
                                if hasattr(candidate.content, "parts")
                                else []
                            )  # type: ignore
                            text = "".join(
                                part.text if hasattr(part, "text") else ""
                                for part in parts  # type: ignore
                            )
                            if text:
                                yield StreamChunk(content=text, done=False)

            # Final chunk
            yield StreamChunk(content="", done=True)
        except Exception as error:
            message = str(error) if error else "Unknown error"
            raise create_error(
                ErrorCodes.LLM_API_ERROR, f"Google API error: {message}", None, error
            )

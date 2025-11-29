"""
Provider registry and factory
"""

from typing import Optional

from lesstokens_sdk.errors import ErrorCodes, create_error
from lesstokens_sdk.providers.anthropic import AnthropicProvider
from lesstokens_sdk.providers.deepseek import DeepSeekProvider
from lesstokens_sdk.providers.google import GoogleProvider
from lesstokens_sdk.providers.openai import OpenAIProvider
from lesstokens_sdk.providers.base import LLMProvider


def create_provider(provider: str, api_key: str, base_url: Optional[str] = None) -> LLMProvider:
    """Creates a provider instance based on the provider name"""
    normalized_provider = provider.lower()

    if normalized_provider == "openai":
        return OpenAIProvider(api_key, base_url)
    elif normalized_provider == "deepseek":
        return DeepSeekProvider(api_key)
    elif normalized_provider == "anthropic":
        return AnthropicProvider(api_key)
    elif normalized_provider == "google":
        return GoogleProvider(api_key)
    else:
        raise create_error(
            ErrorCodes.INVALID_PROVIDER,
            f"Unsupported provider: {provider}. Supported providers: openai, anthropic, google, deepseek",
        )

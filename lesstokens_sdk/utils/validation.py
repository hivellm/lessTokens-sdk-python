"""
Input validation utilities
"""

from lesstokens_sdk.errors import ErrorCodes, create_error
from lesstokens_sdk.types import (
    CompressionOptions,
    LessTokensConfig,
    LLMConfig,
    ProcessPromptOptions,
)

# Maximum prompt size in characters
MAX_PROMPT_SIZE = 1_000_000

# Minimum prompt size in characters
MIN_PROMPT_SIZE = 1


def validate_config(config: LessTokensConfig) -> None:
    """Validate LessTokens configuration"""
    if (
        not config.get("api_key")
        or not isinstance(config["api_key"], str)
        or not config["api_key"].strip()
    ):
        raise create_error(
            ErrorCodes.INVALID_API_KEY,
            "LessTokens API key is required and must be a non-empty string",
        )

    if (
        not config.get("provider")
        or not isinstance(config["provider"], str)
        or not config["provider"].strip()
    ):
        raise create_error(
            ErrorCodes.INVALID_PROVIDER,
            "Provider is required and must be a non-empty string",
        )

    supported_providers = ["openai", "anthropic", "google", "deepseek"]
    if config["provider"].lower() not in supported_providers:
        raise create_error(
            ErrorCodes.INVALID_PROVIDER,
            f"Provider '{config['provider']}' is not supported. Supported providers: {', '.join(supported_providers)}",
        )

    if "timeout" in config and config["timeout"] is not None:
        if not isinstance(config["timeout"], int) or config["timeout"] <= 0:
            raise create_error(
                ErrorCodes.VALIDATION_ERROR, "Timeout must be a positive number"
            )


def validate_prompt(prompt: str) -> None:
    """Validate prompt"""
    if not isinstance(prompt, str):
        raise create_error(ErrorCodes.VALIDATION_ERROR, "Prompt must be a string")

    if len(prompt) < MIN_PROMPT_SIZE:
        raise create_error(
            ErrorCodes.VALIDATION_ERROR,
            f"Prompt must be at least {MIN_PROMPT_SIZE} character long",
        )

    if len(prompt) > MAX_PROMPT_SIZE:
        raise create_error(
            ErrorCodes.VALIDATION_ERROR,
            f"Prompt must not exceed {MAX_PROMPT_SIZE} characters",
        )


def validate_process_prompt_options(options: ProcessPromptOptions) -> None:
    """Validate process prompt options"""
    if "prompt" not in options or not options.get("prompt"):
        raise create_error(ErrorCodes.VALIDATION_ERROR, "Prompt is required")
    validate_prompt(options["prompt"])

    if not options.get("llm_config") or not isinstance(options["llm_config"], dict):
        raise create_error(ErrorCodes.VALIDATION_ERROR, "LLM configuration is required")

    validate_llm_config(options["llm_config"])

    if "compression_options" in options and options["compression_options"]:
        validate_compression_options(options["compression_options"])


def validate_llm_config(config: LLMConfig) -> None:
    """Validate LLM configuration"""
    if (
        not config.get("api_key")
        or not isinstance(config["api_key"], str)
        or not config["api_key"].strip()
    ):
        raise create_error(
            ErrorCodes.VALIDATION_ERROR,
            "LLM API key is required and must be a non-empty string",
        )

    if (
        not config.get("model")
        or not isinstance(config["model"], str)
        or not config["model"].strip()
    ):
        raise create_error(
            ErrorCodes.VALIDATION_ERROR,
            "Model is required and must be a non-empty string",
        )


def validate_compression_options(options: CompressionOptions) -> None:
    """Validate compression options"""
    if "target_ratio" in options and options["target_ratio"] is not None:
        if (
            not isinstance(options["target_ratio"], (int, float))
            or options["target_ratio"] < 0
            or options["target_ratio"] > 1
        ):
            raise create_error(
                ErrorCodes.VALIDATION_ERROR,
                "target_ratio must be a number between 0.0 and 1.0",
            )

    if "preserve_context" in options and options["preserve_context"] is not None:
        if not isinstance(options["preserve_context"], bool):
            raise create_error(
                ErrorCodes.VALIDATION_ERROR, "preserve_context must be a boolean"
            )

    if "aggressive" in options and options["aggressive"] is not None:
        if not isinstance(options["aggressive"], bool):
            raise create_error(
                ErrorCodes.VALIDATION_ERROR, "aggressive must be a boolean"
            )


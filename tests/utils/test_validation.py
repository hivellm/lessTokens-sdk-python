"""Tests for validation utilities"""

import pytest

from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.types import CompressionOptions, LessTokensConfig, LLMConfig
from lesstokens_sdk.utils.validation import (
    validate_compression_options,
    validate_config,
    validate_llm_config,
    validate_prompt,
    validate_process_prompt_options,
)


@pytest.mark.unit
class TestValidation:
    """Test suite for validation utilities"""

    def test_validate_config_success(self) -> None:
        """Test successful config validation."""
        config: LessTokensConfig = {
            "api_key": "test-key",
            "provider": "openai",
        }
        # Should not raise
        validate_config(config)

    def test_validate_config_missing_api_key(self) -> None:
        """Test config validation with missing API key."""
        config: LessTokensConfig = {"provider": "openai"}
        with pytest.raises(LessTokensError) as exc_info:
            validate_config(config)
        assert exc_info.value.code == ErrorCodes.INVALID_API_KEY

    def test_validate_config_empty_api_key(self) -> None:
        """Test config validation with empty API key."""
        config: LessTokensConfig = {"api_key": "", "provider": "openai"}
        with pytest.raises(LessTokensError) as exc_info:
            validate_config(config)
        assert exc_info.value.code == ErrorCodes.INVALID_API_KEY

    def test_validate_config_missing_provider(self) -> None:
        """Test config validation with missing provider."""
        config: LessTokensConfig = {"api_key": "test-key"}
        with pytest.raises(LessTokensError) as exc_info:
            validate_config(config)
        assert exc_info.value.code == ErrorCodes.INVALID_PROVIDER

    def test_validate_config_invalid_provider(self) -> None:
        """Test config validation with invalid provider."""
        config: LessTokensConfig = {"api_key": "test-key", "provider": "invalid"}
        with pytest.raises(LessTokensError) as exc_info:
            validate_config(config)
        assert exc_info.value.code == ErrorCodes.INVALID_PROVIDER

    def test_validate_config_invalid_timeout(self) -> None:
        """Test config validation with invalid timeout."""
        config: LessTokensConfig = {
            "api_key": "test-key",
            "provider": "openai",
            "timeout": -1,
        }
        with pytest.raises(LessTokensError) as exc_info:
            validate_config(config)
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_prompt_success(self) -> None:
        """Test successful prompt validation."""
        # Should not raise
        validate_prompt("Valid prompt")

    def test_validate_prompt_empty(self) -> None:
        """Test prompt validation with empty prompt."""
        with pytest.raises(LessTokensError) as exc_info:
            validate_prompt("")
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_prompt_too_long(self) -> None:
        """Test prompt validation with prompt too long."""
        long_prompt = "a" * 1_000_001
        with pytest.raises(LessTokensError) as exc_info:
            validate_prompt(long_prompt)
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_prompt_not_string(self) -> None:
        """Test prompt validation with non-string prompt."""
        with pytest.raises(LessTokensError) as exc_info:
            validate_prompt(123)  # type: ignore
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_llm_config_success(self) -> None:
        """Test successful LLM config validation."""
        config: LLMConfig = {"api_key": "test-key", "model": "gpt-4"}
        # Should not raise
        validate_llm_config(config)

    def test_validate_llm_config_missing_api_key(self) -> None:
        """Test LLM config validation with missing API key."""
        config: LLMConfig = {"model": "gpt-4"}
        with pytest.raises(LessTokensError) as exc_info:
            validate_llm_config(config)
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_llm_config_missing_model(self) -> None:
        """Test LLM config validation with missing model."""
        config: LLMConfig = {"api_key": "test-key"}
        with pytest.raises(LessTokensError) as exc_info:
            validate_llm_config(config)
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_compression_options_success(self) -> None:
        """Test successful compression options validation."""
        options: CompressionOptions = {
            "target_ratio": 0.5,
            "preserve_context": True,
            "aggressive": False,
        }
        # Should not raise
        validate_compression_options(options)

    def test_validate_compression_options_invalid_target_ratio(self) -> None:
        """Test compression options validation with invalid target_ratio."""
        options: CompressionOptions = {"target_ratio": 1.5}
        with pytest.raises(LessTokensError) as exc_info:
            validate_compression_options(options)
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_compression_options_negative_target_ratio(self) -> None:
        """Test compression options validation with negative target_ratio."""
        options: CompressionOptions = {"target_ratio": -0.1}
        with pytest.raises(LessTokensError) as exc_info:
            validate_compression_options(options)
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_compression_options_invalid_preserve_context(self) -> None:
        """Test compression options validation with invalid preserve_context."""
        options: CompressionOptions = {"preserve_context": "invalid"}  # type: ignore
        with pytest.raises(LessTokensError) as exc_info:
            validate_compression_options(options)
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_compression_options_invalid_aggressive(self) -> None:
        """Test compression options validation with invalid aggressive."""
        options: CompressionOptions = {"aggressive": "invalid"}  # type: ignore
        with pytest.raises(LessTokensError) as exc_info:
            validate_compression_options(options)
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_process_prompt_options_success(self) -> None:
        """Test successful process prompt options validation."""
        options = {
            "prompt": "Test prompt",
            "llm_config": {"api_key": "test-key", "model": "gpt-4"},
        }
        # Should not raise
        validate_process_prompt_options(options)

    def test_validate_process_prompt_options_missing_prompt(self) -> None:
        """Test process prompt options validation with missing prompt."""
        options = {"llm_config": {"api_key": "test-key", "model": "gpt-4"}}
        with pytest.raises(LessTokensError) as exc_info:
            validate_process_prompt_options(options)  # type: ignore
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_process_prompt_options_missing_llm_config(self) -> None:
        """Test process prompt options validation with missing LLM config."""
        options = {"prompt": "Test prompt"}
        with pytest.raises(LessTokensError) as exc_info:
            validate_process_prompt_options(options)  # type: ignore
        assert exc_info.value.code == ErrorCodes.VALIDATION_ERROR

    def test_validate_process_prompt_options_with_compression_options(self) -> None:
        """Test process prompt options validation with compression options."""
        options = {
            "prompt": "Test prompt",
            "llm_config": {"api_key": "test-key", "model": "gpt-4"},
            "compression_options": {
                "target_ratio": 0.5,
                "preserve_context": True,
            },
        }
        # Should not raise
        validate_process_prompt_options(options)

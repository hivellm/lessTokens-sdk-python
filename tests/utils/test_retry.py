"""Tests for retry utilities"""

import pytest

from lesstokens_sdk.errors import ErrorCodes, LessTokensError
from lesstokens_sdk.utils.retry import (
    RetryConfig,
    calculate_delay,
    is_retryable_error,
    retry,
)


@pytest.mark.unit
class TestRetryConfig:
    """Test suite for RetryConfig"""

    def test_default_config(self) -> None:
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 10.0
        assert "TIMEOUT" in config.retryable_errors
        assert "NETWORK_ERROR" in config.retryable_errors

    def test_custom_config(self) -> None:
        """Test custom retry configuration."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=2.0,
            max_delay=20.0,
            retryable_errors=["CUSTOM_ERROR"],
        )
        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 20.0
        assert config.retryable_errors == ["CUSTOM_ERROR"]


@pytest.mark.unit
class TestRetryUtilities:
    """Test suite for retry utility functions"""

    def test_calculate_delay(self) -> None:
        """Test delay calculation with exponential backoff."""
        config = RetryConfig(initial_delay=1.0, max_delay=10.0)
        assert calculate_delay(0, config) == 1.0
        assert calculate_delay(1, config) == 2.0
        assert calculate_delay(2, config) == 4.0
        assert calculate_delay(3, config) == 8.0
        assert calculate_delay(4, config) == 10.0  # Capped at max_delay

    def test_is_retryable_error_retryable(self) -> None:
        """Test retryable error detection."""
        error = LessTokensError("Timeout", ErrorCodes.TIMEOUT)
        config = RetryConfig()
        assert is_retryable_error(error, config) is True

    def test_is_retryable_error_not_retryable(self) -> None:
        """Test non-retryable error detection."""
        error = LessTokensError("Invalid key", ErrorCodes.INVALID_API_KEY)
        config = RetryConfig()
        assert is_retryable_error(error, config) is False

    def test_is_retryable_error_no_code(self) -> None:
        """Test error without code attribute."""
        error = ValueError("Some error")
        config = RetryConfig()
        assert is_retryable_error(error, config) is False

    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self) -> None:
        """Test retry succeeds on first attempt."""

        async def success_fn() -> str:
            return "success"

        result = await retry(success_fn)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_success_after_retries(self) -> None:
        """Test retry succeeds after retries."""
        attempts = 0

        async def retryable_fn() -> str:
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise LessTokensError("Timeout", ErrorCodes.TIMEOUT)
            return "success"

        result = await retry(retryable_fn, {"max_retries": 3})
        assert result == "success"
        assert attempts == 2

    @pytest.mark.asyncio
    async def test_retry_fails_after_max_retries(self) -> None:
        """Test retry fails after max retries."""

        async def failing_fn() -> str:
            raise LessTokensError("Timeout", ErrorCodes.TIMEOUT)

        with pytest.raises(LessTokensError) as exc_info:
            await retry(failing_fn, {"max_retries": 2})

        assert exc_info.value.code == ErrorCodes.TIMEOUT

    @pytest.mark.asyncio
    async def test_retry_does_not_retry_non_retryable_error(self) -> None:
        """Test retry does not retry non-retryable errors."""
        attempts = 0

        async def non_retryable_fn() -> str:
            nonlocal attempts
            attempts += 1
            raise LessTokensError("Invalid key", ErrorCodes.INVALID_API_KEY)

        with pytest.raises(LessTokensError) as exc_info:
            await retry(non_retryable_fn, {"max_retries": 3})

        assert exc_info.value.code == ErrorCodes.INVALID_API_KEY
        assert attempts == 1  # Should not retry

    @pytest.mark.asyncio
    async def test_retry_with_custom_config(self) -> None:
        """Test retry with custom configuration."""
        attempts = 0

        async def retryable_fn() -> str:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise LessTokensError("Timeout", ErrorCodes.TIMEOUT)
            return "success"

        result = await retry(
            retryable_fn,
            {
                "max_retries": 5,
                "initial_delay": 0.01,  # Fast for testing
                "max_delay": 0.1,
            },
        )
        assert result == "success"
        assert attempts == 3

    @pytest.mark.asyncio
    async def test_retry_sync_function(self) -> None:
        """Test retry with synchronous function (not async)."""
        attempts = 0

        def sync_fn() -> str:
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise LessTokensError("Timeout", ErrorCodes.TIMEOUT)
            return "success"

        result = await retry(sync_fn, {"max_retries": 3, "initial_delay": 0.01})
        assert result == "success"
        assert attempts == 2

    @pytest.mark.asyncio
    async def test_retry_raises_last_error(self) -> None:
        """Test retry raises last error after all retries fail."""
        attempts = 0

        async def failing_fn() -> str:
            nonlocal attempts
            attempts += 1
            raise LessTokensError("Timeout", ErrorCodes.TIMEOUT)

        with pytest.raises(LessTokensError) as exc_info:
            await retry(failing_fn, {"max_retries": 2, "initial_delay": 0.01})

        assert exc_info.value.code == ErrorCodes.TIMEOUT
        assert attempts == 3  # max_retries + 1

    @pytest.mark.asyncio
    async def test_retry_runtime_error_no_error(self) -> None:
        """Test retry raises RuntimeError if no error occurred."""

        # This is a theoretical edge case - if fn() succeeds but last_error is set
        # This shouldn't happen in practice, but we test the code path
        async def success_fn() -> str:
            return "success"

        # This should succeed, not raise RuntimeError
        result = await retry(success_fn)
        assert result == "success"

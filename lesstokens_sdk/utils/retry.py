"""
Retry utilities with exponential backoff
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional, TypeVar

T = TypeVar("T")


class RetryConfig:
    """Retry configuration"""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        retryable_errors: Optional[List[str]] = None,
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay  # seconds
        self.max_delay = max_delay  # seconds
        self.retryable_errors = retryable_errors or [
            "TIMEOUT",
            "NETWORK_ERROR",
            "RATE_LIMIT",
        ]


DEFAULT_RETRY_CONFIG = RetryConfig()


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay with exponential backoff"""
    delay = config.initial_delay * (2**attempt)
    return float(min(delay, config.max_delay))


def is_retryable_error(error: Exception, config: RetryConfig) -> bool:
    """Check if error is retryable"""
    if hasattr(error, "code"):
        code = str(getattr(error, "code"))
        return code in config.retryable_errors
    return False


async def retry(
    fn: Callable[[], Any],
    config: Optional[Dict[str, Any]] = None,
) -> T:
    """
    Retry a function with exponential backoff

    Args:
        fn: Async function to retry
        config: Optional retry configuration dict with keys:
            - max_retries: int (default: 3)
            - initial_delay: float in seconds (default: 1.0)
            - max_delay: float in seconds (default: 10.0)
            - retryable_errors: List[str] (default: ["TIMEOUT", "NETWORK_ERROR", "RATE_LIMIT"])

    Returns:
        Result of the function call

    Raises:
        Last error encountered if all retries fail
    """
    retry_config = RetryConfig()
    if config:
        if "max_retries" in config:
            retry_config.max_retries = config["max_retries"]
        if "initial_delay" in config:
            retry_config.initial_delay = config["initial_delay"]
        if "max_delay" in config:
            retry_config.max_delay = config["max_delay"]
        if "retryable_errors" in config:
            retry_config.retryable_errors = config["retryable_errors"]

    last_error: Optional[Exception] = None

    for attempt in range(retry_config.max_retries + 1):
        try:
            result = fn()
            if asyncio.iscoroutine(result):
                return await result  # type: ignore[no-any-return]
            return result  # type: ignore[no-any-return]
        except Exception as error:
            last_error = error

            # Don't retry if it's the last attempt or error is not retryable
            if attempt >= retry_config.max_retries or not is_retryable_error(error, retry_config):
                raise error

            # Calculate delay and wait
            delay = calculate_delay(attempt, retry_config)
            await asyncio.sleep(delay)

    if last_error:
        raise last_error
    raise RuntimeError("Retry failed without error")

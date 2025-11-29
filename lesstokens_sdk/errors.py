"""
Custom error classes for the LessTokens SDK
"""

from typing import Any, Optional


class LessTokensError(Exception):
    """Base error class for all LessTokens SDK errors"""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.name = "LessTokensError"
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

    def __str__(self) -> str:
        return f"{self.name}(code={self.code}, message={self.message})"

    def __repr__(self) -> str:
        return (
            f"LessTokensError("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"status_code={self.status_code}, "
            f"details={self.details!r}"
            f")"
        )


class ErrorCodes:
    """Error codes"""

    INVALID_API_KEY = "INVALID_API_KEY"
    INVALID_PROVIDER = "INVALID_PROVIDER"
    COMPRESSION_FAILED = "COMPRESSION_FAILED"
    LLM_API_ERROR = "LLM_API_ERROR"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"


def create_error(
    code: str,
    message: str,
    status_code: Optional[int] = None,
    details: Optional[Any] = None,
) -> LessTokensError:
    """Create error from error code"""
    return LessTokensError(message, code, status_code, details)


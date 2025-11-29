"""Tests for error classes"""

import pytest

from lesstokens_sdk.errors import ErrorCodes, LessTokensError, create_error


@pytest.mark.unit
class TestErrors:
    """Test suite for error classes"""

    def test_less_tokens_error_str(self) -> None:
        """Test LessTokensError __str__ method."""
        error = LessTokensError("Test error", ErrorCodes.VALIDATION_ERROR, 400)
        error_str = str(error)
        assert "LessTokensError" in error_str
        assert ErrorCodes.VALIDATION_ERROR in error_str
        assert "Test error" in error_str

    def test_less_tokens_error_repr(self) -> None:
        """Test LessTokensError __repr__ method."""
        error = LessTokensError("Test error", ErrorCodes.VALIDATION_ERROR, 400)
        error_repr = repr(error)
        assert "LessTokensError" in error_repr
        assert "Test error" in error_repr

    def test_create_error(self) -> None:
        """Test create_error helper function."""
        error = create_error(
            ErrorCodes.VALIDATION_ERROR, "Test error", 400, {"key": "value"}
        )
        assert isinstance(error, LessTokensError)
        assert error.code == ErrorCodes.VALIDATION_ERROR
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.details == {"key": "value"}

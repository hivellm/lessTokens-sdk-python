"""
Client for LessTokens API
"""

from typing import Any, Dict, Optional

import httpx

from lesstokens_sdk.errors import ErrorCodes, create_error
from lesstokens_sdk.types import CompressedPrompt, CompressionOptions
from lesstokens_sdk.utils.retry import DEFAULT_RETRY_CONFIG, retry


class LessTokensClient:
    """Client for LessTokens API"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://lesstokens.hive-hub.ai",
        timeout: int = 30000,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout / 1000.0  # Convert to seconds for httpx

    async def _perform_compression_request(
        self, request_body: Dict[str, Any], prompt: str
    ) -> CompressedPrompt:
        """Internal method to perform the compression request"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/compress",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key,
                    },
                    json=request_body,
                )

                if not response.is_success:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except Exception:
                        pass

                    if response.status_code in (401, 403):
                        raise create_error(
                            ErrorCodes.INVALID_API_KEY,
                            "Invalid LessTokens API key",
                            response.status_code,
                            error_data,
                        )

                    raise create_error(
                        ErrorCodes.COMPRESSION_FAILED,
                        error_data.get("message")
                        or f"Compression failed: HTTP {response.status_code}",
                        response.status_code,
                        error_data,
                    )

                response_data = response.json()

                # Extract data from nested structure or use direct format
                data = response_data.get("data") or response_data

                # Handle both API response formats
                compression_ratio = (
                    data.get("compressionRatio") or data.get("ratio") or 1.0
                )
                original_tokens = data.get("originalTokens") or 0
                compressed_tokens = data.get("compressedTokens") or 0

                # Always calculate savings percentage from original and compressed tokens
                # This ensures accuracy regardless of API response format
                if original_tokens > 0 and compressed_tokens >= 0:
                    savings = (
                        (float(original_tokens) - float(compressed_tokens))
                        / float(original_tokens)
                    ) * 100
                else:
                    savings = 0.0

                return CompressedPrompt(
                    compressed=data.get("compressed") or prompt,
                    original_tokens=original_tokens,
                    compressed_tokens=compressed_tokens,
                    savings=round(savings * 100) / 100,  # Round to 2 decimal places
                    ratio=float(compression_ratio) if compression_ratio else 1.0,
                )
        except httpx.TimeoutException as error:
            raise create_error(
                ErrorCodes.TIMEOUT,
                f"Request timeout after {self.timeout}s",
                None,
                error,
            )
        except httpx.RequestError as error:
            raise create_error(
                ErrorCodes.NETWORK_ERROR,
                f"Network error: {str(error)}",
                None,
                error,
            )
        except Exception as error:
            if hasattr(error, "code"):
                raise  # Re-throw LessTokensError
            raise create_error(
                ErrorCodes.NETWORK_ERROR,
                f"Network error: {str(error)}",
                None,
                error,
            )

    async def compress(
        self, prompt: str, options: Optional[CompressionOptions] = None
    ) -> CompressedPrompt:
        """Compress a prompt using LessTokens API"""
        if options is None:
            options = {}

        # Build request body with only provided options
        request_body: Dict[str, Any] = {"prompt": prompt}

        # Only include optional fields if they are explicitly provided
        if "target_ratio" in options and options["target_ratio"] is not None:
            request_body["targetRatio"] = options["target_ratio"]
        if "preserve_context" in options and options["preserve_context"] is not None:
            request_body["preserveContext"] = options["preserve_context"]
        if "aggressive" in options and options["aggressive"] is not None:
            request_body["aggressive"] = options["aggressive"]

        # Create a named function to ensure full coverage
        async def perform_request() -> CompressedPrompt:
            return await self._perform_compression_request(request_body, prompt)

        retry_config = {
            "max_retries": DEFAULT_RETRY_CONFIG.max_retries,
            "initial_delay": DEFAULT_RETRY_CONFIG.initial_delay,
            "max_delay": DEFAULT_RETRY_CONFIG.max_delay,
            "retryable_errors": [
                ErrorCodes.TIMEOUT,
                ErrorCodes.NETWORK_ERROR,
                "RATE_LIMIT",
            ],
        }

        return await retry(perform_request, retry_config)


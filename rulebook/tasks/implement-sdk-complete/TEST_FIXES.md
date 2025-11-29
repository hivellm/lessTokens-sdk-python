# Test Fixes Required

## Issues Found (21 failing tests)

### 1. SDK Tests - Mocking Issue (9 tests)
**Problem:** Tests are using `patch.object` but `LessTokensClient` is created in `__init__`, so the patch doesn't work.

**Fix:** Use `patch("lesstokens_sdk.sdk.LessTokensClient")` before creating SDK instance.

**Affected tests:**
- test_process_prompt_success
- test_process_prompt_with_messages
- test_process_prompt_with_custom_role
- test_process_prompt_with_custom_content
- test_process_prompt_stream_success
- test_compress_prompt_success
- test_compress_prompt_without_options
- test_process_prompt_compression_error
- test_process_prompt_llm_error

### 2. Streaming Test - Async Generator Issue (1 test)
**Problem:** `mock_provider.chat_stream.return_value = mock_stream()` returns a coroutine, not an async generator.

**Fix:** Use `mock_provider.chat_stream = mock_stream` (assign the function, not call it).

**Affected test:**
- test_chat_stream_success

### 3. Provider Tests - Missing SDK Mocks (8 tests)
**Problem:** Tests try to instantiate providers but SDKs aren't installed. Need to mock the SDK imports.

**Fix:** Mock the SDK imports before instantiating providers.

**Affected tests:**
- All OpenAI provider tests (7 tests)
- Google provider test_chat_api_error (1 test)

### 4. Provider Tests - Mock Response Structure (2 tests)
**Problem:** Mock responses don't match expected structure.

**Affected tests:**
- test_anthropic_provider.test_chat_success
- test_google_provider.test_chat_success

### 5. Validation Test - KeyError (1 test)
**Problem:** `validate_process_prompt_options` tries to access `options["prompt"]` without checking if key exists.

**Fix:** Added check in validation.py (already fixed).

**Affected test:**
- test_validate_process_prompt_options_missing_prompt

### 6. Pytest Warnings - Async Markers (16 warnings)
**Problem:** Non-async tests are marked with `@pytest.mark.asyncio`.

**Fix:** Remove `@pytest.mark.asyncio` from non-async test methods.

**Affected tests:**
- All `test_init_*` methods
- All `test_validate_*` methods (non-async)

## Coverage Issues

Current coverage: 67% (target: 98%)

**Low coverage areas:**
- `sdk.py`: 33% (needs more tests)
- `providers/openai.py`: 31% (needs mocks fixed)
- `providers/anthropic.py`: 53%
- `providers/google.py`: 52%
- `providers/deepseek.py`: 61%

## Next Steps

1. Fix all mocking issues in SDK tests
2. Fix provider test mocks
3. Remove incorrect async markers
4. Add more tests to increase coverage
5. Re-run quality checks


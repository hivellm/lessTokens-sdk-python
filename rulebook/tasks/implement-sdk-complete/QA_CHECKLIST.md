# Quality Assurance Checklist

## Prerequisites

The quality checks script (`scripts/run_quality_checks.sh`) automatically:
- Creates a virtual environment (`.venv`) if it doesn't exist
- Installs all required dependencies
- Runs all quality checks

**No manual setup required!** Just run the script.

## Quick Start

Run all quality checks at once:

```bash
./scripts/run_quality_checks.sh
```

The script will:
1. ✅ Create/activate virtual environment
2. ✅ Install dependencies (pytest, ruff, mypy)
3. ✅ Run unit tests
4. ✅ Check test coverage
5. ✅ Run linter (ruff)
6. ✅ Check code formatting
7. ✅ Run type checker (mypy)

## Manual Execution (Alternative)

If you prefer to run checks manually or need more control:

### 1. Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install pytest pytest-asyncio pytest-cov ruff mypy
```

### 2. Individual Checks

#### Linter (ruff)

```bash
# Check for linting issues
ruff check lesstokens_sdk tests

# Auto-fix issues (if possible)
ruff check --fix lesstokens_sdk tests

# Check formatting
ruff format --check lesstokens_sdk tests

# Auto-format code
ruff format lesstokens_sdk tests
```

**Expected Result:** Zero warnings/errors

#### Type Checker (mypy)

```bash
# Run type checking
mypy lesstokens_sdk --ignore-missing-imports

# For stricter checking (may require fixes)
mypy lesstokens_sdk --strict --ignore-missing-imports
```

**Expected Result:** Zero type errors

**Note:** Provider SDKs (openai, anthropic, google) are ignored as they may not have complete type stubs.

#### Unit Tests

```bash
# Run all unit tests (excluding integration)
pytest tests/ -m "not integration" -v

# Run with coverage
pytest --cov=lesstokens_sdk --cov-report=term-missing tests/ -m "not integration"

# Generate HTML coverage report
pytest --cov=lesstokens_sdk --cov-report=html tests/ -m "not integration"
```

**Expected Result:** 
- 100% test pass rate
- Coverage ≥ 98%

#### Test Coverage

```bash
# Check coverage
pytest --cov=lesstokens_sdk --cov-report=term-missing tests/ -m "not integration"

# Generate detailed report
pytest --cov=lesstokens_sdk --cov-report=html --cov-report=xml tests/ -m "not integration"
```

**Expected Result:** Coverage ≥ 98%

#### Integration Tests (Optional)

```bash
# Run integration tests (requires API keys)
export LESSTOKENS_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
pytest -m integration -v
```

**Note:** Integration tests require real API keys and may incur costs.

#### Validate Code Examples

```bash
# Test basic usage example
python examples/basic_usage.py

# Test streaming example
python examples/streaming.py

# Test multi-turn example
python examples/multi_turn.py
```

**Note:** Examples require API keys to run.

## Common Issues and Fixes

### Virtual Environment Issues

**Issue:** Script fails with "externally-managed-environment"
- **Solution:** The script now automatically creates and uses a virtual environment (`.venv`)
- The `.venv` directory is already in `.gitignore`

### Linter Issues

**Issue:** Unused imports
```bash
# Auto-remove unused imports
ruff check --fix --select F401 lesstokens_sdk tests
```

**Issue:** Line too long
```bash
# Auto-format to fix line length
ruff format lesstokens_sdk tests
```

### Type Checker Issues

**Issue:** Missing type hints
- Add type hints to function parameters and return types
- Use `typing` module for complex types

**Issue:** Incompatible types
- Review type annotations
- Use `cast()` or type guards when necessary

### Test Issues

**Issue:** Tests failing
- Check test output for error messages
- Verify mocks are set up correctly
- Ensure fixtures are properly configured

**Issue:** Low coverage
- Identify uncovered code paths
- Add tests for missing coverage
- Check if code is actually needed (may be dead code)

## Quality Gates

All checks must pass before considering the task complete:

- ✅ Linter: Zero warnings/errors
- ✅ Type Checker: Zero errors (warnings acceptable)
- ✅ Tests: 100% pass rate
- ✅ Coverage: ≥ 98%
- ✅ Formatting: All files formatted

## Reporting

After running checks, update `tasks.md`:

```markdown
## 4. Quality Assurance Phase
- [x] 4.1 Run linter and fix all warnings <!-- Completed: ruff check passed -->
- [x] 4.2 Run type checker and fix all errors <!-- Completed: mypy passed -->
- [x] 4.3 Run all tests and ensure 100% pass rate <!-- Completed: All tests passed -->
- [x] 4.4 Verify test coverage ≥ 98% <!-- Completed: Coverage 98.5% -->
- [ ] 4.5 Run integration tests with real providers <!-- Optional: Requires API keys -->
- [x] 4.6 Validate all code examples from documentation <!-- Completed: Examples verified -->
```

# Contributing to LessTokens SDK

Thank you for your interest in contributing to the LessTokens SDK! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and examples
   - Potential implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Run linting: `black . && isort .`
7. Commit your changes: `git commit -m "Add feature"`
8. Push to your fork: `git push origin feature/your-feature`
9. Create a Pull Request

## Development Setup

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/hivellm/lesstokens-sdk-python.git
cd lesstokens-sdk-python
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[all,dev]"
```

4. Install pre-commit hooks (optional):
```bash
pre-commit install
```

## Coding Standards

### Code Style

- Follow PEP 8
- Use Black for formatting: `black .`
- Use isort for imports: `isort .`
- Maximum line length: 100 characters

### Type Hints

- Use type hints for all functions
- Use `Optional[T]` for nullable types
- Use `Dict[str, Any]` for flexible dictionaries

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings

### Testing

- Write tests for all new functionality
- Aim for high test coverage
- Use pytest for testing
- Mock external dependencies

## Project Structure

```
lesstokens-sdk-python/
├── lesstokens_sdk/
│   ├── __init__.py
│   ├── sdk.py              # Main SDK class
│   ├── types.py            # Type definitions
│   ├── errors.py           # Error classes
│   ├── clients/             # API clients
│   ├── providers/          # LLM provider implementations
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── docs/                    # Documentation
├── examples/                # Example code
├── pyproject.toml           # Project configuration
└── README.md                # Project README
```

## Commit Messages

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

Example:
```
feat: Add support for custom message roles
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Run linting and formatting
5. Update CHANGELOG.md if applicable
6. Request review from maintainers

## Questions?

If you have questions, feel free to:
- Open an issue
- Contact the maintainers
- Check existing documentation

Thank you for contributing! 🎉



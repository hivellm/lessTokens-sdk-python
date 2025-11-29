#!/bin/bash
# Quality checks script for LessTokens SDK
# Run this script to execute all quality checks required for Phase 4

set -e

echo "🔍 Running Quality Checks for LessTokens SDK"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run check with error handling
run_check() {
    local name=$1
    local command=$2
    
    echo -n "Running $name... "
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# 1. Setup virtual environment
echo "📦 Setting up environment..."
echo ""

if ! command_exists python3; then
    echo -e "${RED}✗ python3 not found${NC}"
    exit 1
fi

# Determine project root (script is in scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_CMD="python3"

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Update PYTHON_CMD to use venv python
PYTHON_CMD="$VENV_DIR/bin/python"

# Upgrade pip
echo "Upgrading pip..."
"$PYTHON_CMD" -m pip install --quiet --upgrade pip >/dev/null 2>&1

# Install project dependencies first
echo "Installing project dependencies..."
"$PYTHON_CMD" -m pip install --quiet -e . >/dev/null 2>&1

# Install test and quality check dependencies
echo "Installing test dependencies..."
"$PYTHON_CMD" -m pip install --quiet pytest pytest-asyncio pytest-cov ruff mypy >/dev/null 2>&1

echo ""
echo "🧪 Running Tests..."
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# 2. Run unit tests (excluding integration)
if "$PYTHON_CMD" -m pytest tests/ -m "not integration" -v --tb=short; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "📊 Checking Coverage..."
echo ""

# 3. Check test coverage
COVERAGE_OUTPUT=$("$PYTHON_CMD" -m pytest --cov=lesstokens_sdk --cov-report=term-missing --cov-report=json -q tests/ -m "not integration" 2>&1)
COVERAGE=$(echo "$COVERAGE_OUTPUT" | grep -oE 'TOTAL.*[0-9]+%' | grep -oE '[0-9]+%' | head -1 || echo "0%")
COVERAGE_NUM=$(echo "$COVERAGE" | sed 's/%//')

# Check if bc is available, otherwise use awk
if command_exists bc; then
    COVERAGE_CHECK=$(echo "$COVERAGE_NUM >= 98" | bc -l)
else
    COVERAGE_CHECK=$(awk "BEGIN {print ($COVERAGE_NUM >= 98) ? 1 : 0}")
fi

if [ "$COVERAGE_CHECK" -eq 1 ] 2>/dev/null || [ "$COVERAGE_NUM" -ge 98 ] 2>/dev/null; then
    echo -e "${GREEN}✓ Coverage: $COVERAGE (threshold: 98%)${NC}"
else
    echo -e "${RED}✗ Coverage: $COVERAGE (threshold: 98%)${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "🔍 Running Linter (ruff)..."
echo ""

# 4. Run linter
if "$VENV_DIR/bin/ruff" check lesstokens_sdk tests; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting failed${NC}"
    FAILURES=$((FAILURES + 1))
fi

# 5. Check formatting
echo ""
echo "🎨 Checking Code Formatting..."
echo ""

if "$VENV_DIR/bin/ruff" format --check lesstokens_sdk tests; then
    echo -e "${GREEN}✓ Formatting passed${NC}"
else
    echo -e "${YELLOW}⚠ Formatting issues found (run: ruff format .)${NC}"
fi

echo ""
echo "🔎 Running Type Checker (mypy)..."
echo ""

# 6. Run type checker
if "$VENV_DIR/bin/mypy" lesstokens_sdk --ignore-missing-imports; then
    echo -e "${GREEN}✓ Type checking passed${NC}"
else
    echo -e "${RED}✗ Type checking failed${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "=============================================="
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All quality checks passed!${NC}"
    deactivate 2>/dev/null || true
    exit 0
else
    echo -e "${RED}❌ $FAILURES check(s) failed${NC}"
    deactivate 2>/dev/null || true
    exit 1
fi


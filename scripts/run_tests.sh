#!/bin/bash
# Run all tests with coverage

set -e

echo "================================"
echo "Running AITradeGame Tests"
echo "================================"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run tests
echo ""
echo "Running tests..."
pytest -v --cov=backend --cov-report=term-missing --cov-report=html

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✓ All tests passed!"
    echo "================================"
    echo ""
    echo "Coverage report: htmlcov/index.html"
else
    echo ""
    echo "================================"
    echo "✗ Tests failed!"
    echo "================================"
    exit 1
fi

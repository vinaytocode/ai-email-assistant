#!/bin/bash

echo "🧪 Running tests..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the project root (parent directory of scripts/)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

echo "📂 Running from: $PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "ai-email-env" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run ./scripts/setup_env.sh first"
    exit 1
fi

# Activate virtual environment
source ai-email-env/bin/activate

# Run pytest with coverage
pytest \
    --cov=src \
    --cov-report=html \
    --cov-report=term-missing \
    --verbose \
    "$@"

echo ""
echo "📊 Coverage report generated in htmlcov/index.html"

# Deactivate virtual environment
deactivate

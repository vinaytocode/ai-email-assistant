#!/bin/bash

echo "🚀 Starting AI Email Assistant..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the project root (parent directory of scripts/)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

echo "📂 Running from: $PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "ai-email-env" ]; then
    echo "❌ Virtual environment not found in $PROJECT_ROOT"
    echo "Run ./scripts/setup_env.sh first"
    exit 1
fi

# Activate virtual environment
source ai-email-env/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Copy .env.example to .env and configure it"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file!"
    exit 1
fi

# Add project root to PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run Streamlit app
echo "📂 Running from: $PROJECT_ROOT"
echo "Starting Streamlit app on port ${APP_PORT:-8501}..."
streamlit run src/ui/streamlit_app.py \
    --server.port=${APP_PORT:-8501} \
    --server.address=0.0.0.0 \
    --browser.gatherUsageStats=false \
    --server.headless=true

# Deactivate virtual environment on exit
deactivate

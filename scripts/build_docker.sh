#!/bin/bash

echo "🐳 Building Docker image..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the project root (parent directory of scripts/)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

echo "📂 Building from: $PROJECT_ROOT"

# Build image
docker build -t ai-email-assistant:latest .

echo "✅ Docker image built successfully!"
echo ""
echo "Run with:"
echo "  docker-compose up"
echo ""
echo "Or run directly:"
echo "  docker run -p 8501:8501 --env-file .env ai-email-assistant:latest"

#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the project root (parent directory of scripts/)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${BLUE}🐳 Docker Build Script${NC}"
echo -e "${BLUE}📂 Building from: $PROJECT_ROOT${NC}"
echo ""

# Check if argument provided
BUILD_TYPE=${1:-local}

if [ "$BUILD_TYPE" == "prod" ] || [ "$BUILD_TYPE" == "production" ]; then
    echo -e "${YELLOW}🚀 Building PRODUCTION image (port 7860 - Hugging Face compatible)${NC}"
    docker build -f Dockerfile -t ai-email-assistant:prod .
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Production Docker image built successfully!${NC}"
        echo ""
        echo "Test production build locally:"
        echo -e "  ${BLUE}docker-compose -f docker-compose.prod.yml up${NC}"
        echo ""
        echo "Or run directly:"
        echo -e "  ${BLUE}docker run -p 7860:7860 --env-file .env ai-email-assistant:prod${NC}"
        echo ""
        echo "Access at: http://localhost:7860"
    else
        echo -e "${RED}❌ Build failed!${NC}"
        exit 1
    fi

elif [ "$BUILD_TYPE" == "local" ] || [ "$BUILD_TYPE" == "dev" ]; then
    echo -e "${YELLOW}🔧 Building LOCAL development image (port 8501)${NC}"
    docker build -f Dockerfile.local -t ai-email-assistant:latest .
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Local Docker image built successfully!${NC}"
        echo ""
        echo "Run with docker-compose:"
        echo -e "  ${BLUE}docker-compose up${NC}"
        echo ""
        echo "Or run directly:"
        echo -e "  ${BLUE}docker run -p 8501:8501 --env-file .env ai-email-assistant:latest${NC}"
        echo ""
        echo "Access at: http://localhost:8501"
    else
        echo -e "${RED}❌ Build failed!${NC}"
        exit 1
    fi

elif [ "$BUILD_TYPE" == "both" ]; then
    echo -e "${YELLOW}🔄 Building BOTH local and production images${NC}"
    echo ""
    
    # Build local
    echo -e "${BLUE}Building local image...${NC}"
    docker build -f Dockerfile.local -t ai-email-assistant:latest .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Local image built!${NC}"
    else
        echo -e "${RED}❌ Local build failed!${NC}"
        exit 1
    fi
    
    echo ""
    
    # Build production
    echo -e "${BLUE}Building production image...${NC}"
    docker build -f Dockerfile -t ai-email-assistant:prod .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Production image built!${NC}"
    else
        echo -e "${RED}❌ Production build failed!${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Both images built successfully!${NC}"
    echo ""
    echo "Local (port 8501):"
    echo -e "  ${BLUE}docker-compose up${NC}"
    echo ""
    echo "Production test (port 7860):"
    echo -e "  ${BLUE}docker-compose -f docker-compose.prod.yml up${NC}"

else
    echo -e "${YELLOW}❓ Usage:${NC}"
    echo "  ./scripts/build_docker.sh [local|prod|both]"
    echo ""
    echo "Options:"
    echo "  local (default) - Build for local development (port 8501)"
    echo "  prod            - Build for production/Hugging Face (port 7860)"
    echo "  both            - Build both versions"
    echo ""
    echo "Examples:"
    echo "  ./scripts/build_docker.sh           # Build local"
    echo "  ./scripts/build_docker.sh prod      # Build production"
    echo "  ./scripts/build_docker.sh both      # Build both"
    exit 1
fi
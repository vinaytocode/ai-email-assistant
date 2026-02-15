# Docker Setup Guide

This project supports both **local development** and **production deployment** (Hugging Face Spaces) configurations.

## Quick Start

### Local Development (Port 8501)
```bash
# Build and run
./scripts/build_docker.sh local
docker-compose up

# Access at http://localhost:8501
```

### Production Testing (Port 7860)
```bash
# Build and run production version locally
./scripts/build_docker.sh prod
docker-compose -f docker-compose.prod.yml up

# Access at http://localhost:7860
```

## File Overview

| File | Purpose | Port |
|------|---------|------|
| `Dockerfile` | Production (Hugging Face) | 7860 |
| `Dockerfile.local` | Local development | 8501 |
| `docker-compose.yml` | Local dev orchestration | 8501 |
| `docker-compose.prod.yml` | Production test locally | 7860 |
| `scripts/build_docker.sh` | Build script with options | Both |

## Build Script Usage

```bash
# Build for local development (default)
./scripts/build_docker.sh
./scripts/build_docker.sh local

# Build for production (Hugging Face compatible)
./scripts/build_docker.sh prod

# Build both versions
./scripts/build_docker.sh both
```

## Docker Compose Commands

### Local Development
```bash
# Start
docker-compose up

# Start in background
docker-compose up -d

# Stop
docker-compose down

# Rebuild and start
docker-compose up --build

# View logs
docker-compose logs -f
```

### Production Testing
```bash
# Start production version
docker-compose -f docker-compose.prod.yml up

# Start in background
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Manual Docker Commands

### Local Version
```bash
# Build
docker build -f Dockerfile.local -t ai-email-assistant:latest .

# Run
docker run -p 8501:8501 --env-file .env ai-email-assistant:latest

# Run with specific API key
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key ai-email-assistant:latest
```

### Production Version
```bash
# Build
docker build -f Dockerfile -t ai-email-assistant:prod .

# Run
docker run -p 7860:7860 --env-file .env ai-email-assistant:prod

# Run with specific API key
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key ai-email-assistant:prod
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (with defaults)
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_TEMPERATURE=0.3
MAX_TOKENS=1000
APP_TITLE=AI Email Assistant
APP_PORT=8501
DEBUG=false
MAX_CONTEXT_ENTRIES=3
ENABLE_CONTEXT_MEMORY=true
```

## Port Configuration

### Why Two Ports?

- **8501**: Standard Streamlit port, better for local development
- **7860**: Required by Hugging Face Spaces for production

### Accessing Your App

- **Local**: http://localhost:8501
- **Production test**: http://localhost:7860
- **Hugging Face**: https://huggingface.co/spaces/itzvinay/ai-email-assistant

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8501
lsof -i :7860

# Kill the process
kill -9 <PID>

# Or use different port
docker run -p 8080:8501 ai-email-assistant:latest
```

### Container Won't Start
```bash
# View logs
docker logs ai-email-assistant

# Or with docker-compose
docker-compose logs

# Check container status
docker ps -a
```

### Build Fails
```bash
# Clean build (no cache)
docker build --no-cache -f Dockerfile.local -t ai-email-assistant:latest .

# Remove old images
docker system prune -a
```

### API Key Not Found
```bash
# Make sure .env file exists
cat .env

# Or pass directly
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... ai-email-assistant:latest
```

## Volume Mounts

Both docker-compose files mount local directories:

```yaml
volumes:
  - ./data:/app/data    # Data persistence
  - ./logs:/app/logs    # Log files
```

This means:
- Data saved in the container persists on your machine
- Logs are accessible from your local `logs/` directory
- Changes to `data/` and `logs/` don't require rebuilding

## Development Workflow

### Typical Local Development Flow
```bash
# 1. Make code changes
vim src/ui/streamlit_app.py

# 2. Rebuild and restart
docker-compose down
docker-compose up --build

# Or just restart if only Python code changed
docker-compose restart
```

### Testing Production Build Before Deployment
```bash
# 1. Build production image
./scripts/build_docker.sh prod

# 2. Test locally on port 7860
docker-compose -f docker-compose.prod.yml up

# 3. Verify everything works
# Open http://localhost:7860

# 4. If good, deploy to Hugging Face
# (Copy Dockerfile, requirements.txt, src/, etc.)
```

## Deployment to Hugging Face

When ready to deploy:

```bash
# 1. Test production build locally first
./scripts/build_docker.sh prod
docker-compose -f docker-compose.prod.yml up

# 2. Clone your Hugging Face Space
git clone https://huggingface.co/spaces/itzvinay/ai-email-assistant
cd ai-email-assistant

# 3. Copy production files (NOT Dockerfile.local or docker-compose files)
cp /path/to/Dockerfile .
cp /path/to/requirements.txt .
cp /path/to/README.md .
cp -r /path/to/src .
cp -r /path/to/data .

# 4. Push to Hugging Face
git add .
git commit -m "Deploy to Hugging Face Spaces"
git push
```

## Best Practices

1. **Always test locally first** with production Dockerfile before pushing to HF
2. **Use .env for secrets** - never commit API keys
3. **Check logs** if something doesn't work
4. **Clean up** old images occasionally with `docker system prune`
5. **Volume mounts** for data persistence
6. **Separate configs** for dev vs prod environments

## Summary

- Use **docker-compose.yml** for daily local development
- Use **docker-compose.prod.yml** to test production build before deploying
- Use **Dockerfile** (production) for Hugging Face Spaces
- Use **Dockerfile.local** for local development
- Use **build_docker.sh** script to build either or both versions

Happy coding! 🚀

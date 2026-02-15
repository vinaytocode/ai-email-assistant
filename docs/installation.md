# Installation Guide - ai-email-assistant

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows 10/11
- **Python**: 3.9 or higher
- **RAM**: Minimum 2GB available
- **Disk Space**: 500MB for application and dependencies
- **Internet**: Required for OpenAI API access

### Required Accounts

- **OpenAI Account**: Sign up at [platform.openai.com](https://platform.openai.com)
- **API Key**: Generate from OpenAI dashboard
- **Credits**: Ensure you have available credits (very low cost with GPT-4o-mini)

## Installation Methods

### Method 1: Local Installation (Recommended for Development)

#### Step 1: Clone Repository
```bash
git clone https://github.com/vinaytocode/ai-email-assistant.git
cd ai-email-assistant
```

#### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv ai-email-env
source ai-email-env/bin/activate
```

**Windows:**
```bash
python -m venv ai-email-env
ai-email-env\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt

# (Optional) Install development dependencies
pip install -r requirements-dev.txt
```

#### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
nano .env
```

Add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-api-key-here
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_TEMPERATURE=0.3
MAX_TOKENS=1000
```

#### Step 5: Verify Installation
```bash
python -c "import streamlit, langgraph, openai; print('All dependencies installed!')"
```

#### Step 6: Run Application
```bash
# Using Streamlit directly
streamlit run src/ui/streamlit_app.py

# Or using the provided script
./scripts/run_local.sh

# Access at: http://localhost:8501
```

### Method 2: Docker Installation (Recommended for Production)

#### Prerequisites
- **Docker**: Install from [docker.com](https://www.docker.com/get-started)
- **Docker Compose**: Included with Docker Desktop

#### Step 1: Clone Repository
```bash
git clone https://github.com/vinaytocode/ai-email-assistant.git
cd ai-email-assistant
```

#### Step 2: Configure Environment
```bash
cp .env.example .env
# Add your API key
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
```

#### Step 3: Build and Run
```bash
docker-compose up --build
# Or in detached mode
docker-compose up -d --build
# Access at: http://localhost:8501
```

#### Step 4: Manage Container
```bash
docker-compose logs -f      # View logs
docker-compose down          # Stop container
docker-compose restart       # Restart container
docker-compose up --build    # Rebuild after code changes
```

### Method 3: Using Setup Script (Linux/macOS)
```bash
git clone https://github.com/vinaytocode/ai-email-assistant.git
cd ai-email-assistant
chmod +x scripts/*.sh
./scripts/setup_env.sh
nano .env                    # Add your API key
./scripts/run_local.sh
```

## Configuration Options

### Environment Variables

Create or edit `.env` file:
```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# OpenAI Settings
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_TEMPERATURE=0.3
MAX_TOKENS=1000

# Application Settings
APP_TITLE=AI Email Assistant
APP_PORT=8501
DEBUG=false

# Context Settings
MAX_CONTEXT_ENTRIES=3
ENABLE_CONTEXT_MEMORY=true
```

### User Profiles

Edit `src/memory/user_profiles.json` to customize profiles:
```json
{
  "your_profile_name": {
    "role": "Your Professional Role",
    "name": "Your Full Name",
    "company": "Your Company/Institution",
    "writing_style": "Describe your preferred writing style",
    "signature": "Your\nEmail\nSignature\nHere"
  }
}
```

### MCP Configuration

Edit `src/config/mcp.yaml` for advanced settings:
```yaml
agents:
  draft_writer:
    timeout_seconds: 60

workflow:
  stages:
    - stage: "content_creation"
      parallel: false
```

## Verification Checklist

After installation, verify the following:

- [ ] Virtual environment activated (local) or container running (Docker)
- [ ] All dependencies installed without errors
- [ ] `.env` file created with valid API key
- [ ] Application starts without errors
- [ ] Can access web interface at localhost:8501
- [ ] Can select user profiles from sidebar
- [ ] Can generate a test email successfully

### Test Email Generation

1. Open application in browser
2. Select any user profile (e.g., "Student")
3. Choose tone (e.g., "Professional")
4. Enter prompt: "Write a thank you email to my professor"
5. Click "Generate Email"
6. Verify email is generated successfully

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
source ai-email-env/bin/activate  # Linux/macOS
# or
ai-email-env\Scripts\activate      # Windows
pip install -r requirements.txt
```

#### 2. OpenAI API Errors

**Error**: `openai.error.AuthenticationError: Incorrect API key`

**Solution**:
```bash
cat .env | grep OPENAI_API_KEY
# Ensure no spaces or quotes around key
# OPENAI_API_KEY=sk-your-key-here
```

#### 3. Port Already in Use

**Solution**:
```bash
streamlit run src/ui/streamlit_app.py --server.port=8502
# Or kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

#### 4. Permission Denied (Scripts)

**Solution**:
```bash
chmod +x scripts/*.sh
```

#### 5. Docker Build Fails

**Solution**:
```bash
docker-compose down
docker system prune -a
docker-compose up --build
```

#### 6. Pydantic Validation Error

**Solution**:
```bash
cat .env.example  # Check required fields
nano .env         # Add missing fields
```

## Dependency Details

### Production Dependencies
```
streamlit>=1.28.0          # Web UI framework
langgraph>=0.0.40          # Multi-agent orchestration
langchain>=0.1.0           # LLM framework
langchain-openai>=0.0.5    # OpenAI integration
openai>=1.6.0              # OpenAI API client
pydantic>=2.0.0            # Data validation
python-dotenv>=1.0.0       # Environment management
pyyaml>=6.0.1              # YAML parsing
```

### Development Dependencies
```
pytest>=7.4.0              # Testing framework
pytest-cov>=4.1.0          # Coverage reporting
black>=23.7.0              # Code formatting
flake8>=6.1.0              # Linting
mypy>=1.5.0                # Type checking
```

## Updating

### Update Local Installation
```bash
git pull origin main
source ai-email-env/bin/activate
pip install -r requirements.txt --upgrade
```

### Update Docker Installation
```bash
git pull origin main
docker-compose down
docker-compose up --build
```

## Uninstallation

### Remove Local Installation
```bash
deactivate
cd ..
rm -rf ai-email-assistant
```

### Remove Docker Installation
```bash
docker-compose down
docker rmi ai-email-assistant:latest
cd ..
rm -rf ai-email-assistant
```

## Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [GitHub Issues](https://github.com/vinaytocode/ai-email-assistant/issues)
3. Create new issue with: OS version, Python version, error message, steps to reproduce

---

**Author**: Vinay K <itzvinay@gmail.com>
**Repository**: https://github.com/vinaytocode/ai-email-assistant
**Documentation**: See [docs/](../docs/)
**API Reference**: See [docs/api_reference.md](api_reference.md)

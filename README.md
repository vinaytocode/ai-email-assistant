---
title: AI Email Assistant
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# 📧 AI Email Assistant - Multi-Agent System

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Demo-yellow)

Multi-agent email generation system powered by **LangGraph** orchestration and **GPT-4o-mini**.

## 🎯 Key Features

- ✅ **Multi-Agent Architecture**: 7 specialized agents orchestrated via LangGraph
- ✅ **User Profiles**: Pre-configured professional personas in `src/memory/user_profiles.json`
- ✅ **LangGraph Workflow**: Complete orchestration in `src/workflow/langgraph_flow.py`
- ✅ **MCP Configuration**: Agent communication protocol in `src/config/mcp.yaml`
- ✅ **Context Memory**: Remembers last 3 email conversations
- ✅ **Export Options**: TXT and JSON export formats
- ✅ **Cost Optimized**: Uses GPT-4o-mini for efficient token usage
- ✅ **Streamlit UI**: Professional web interface

## 📋 Requirements Verification

| Requirement 			| Location | Status |
|-----------------------|-----------------------------------|----|
| User Profiles 		| `src/memory/user_profiles.json`	| ✅ |
| LangGraph Flow 		| `src/workflow/langgraph_flow.py` 	| ✅ |
| MCP Config 			| `src/config/mcp.yaml` 			| ✅ |
| Multi-Agent System 	| `src/agents/` 					| ✅ |
| Context Memory 		| `src/core/context_manager.py` 	| ✅ |
| Export Functionality 	| `src/core/export_manager.py` 		| ✅ |

## 🗂️ Project Structure

```
ai-email-assistant/
├── src/
│   ├── agents/           # Multi-agent system (7 agents)
│   ├── config/           # Settings & MCP configuration
│   ├── core/             # State models, context, export
│   ├── integrations/     # OpenAI client wrapper
│   ├── memory/           # User profiles
│   ├── ui/               # Streamlit interface
│   ├── utils/            # Logger, exceptions
│   └── workflow/         # LangGraph orchestration
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── data/                 # Examples and templates
└── deployment/           # Docker configs
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

```bash
# Clone repository
git clone https://github.com/vinaytocode/ai-email-assistant
cd ${PROJECT_NAME}

# Run setup script
./scripts/setup_env.sh

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run application
./scripts/run_local.sh

# Access at: http://localhost:8501
```

### Docker Deployment

```bash
docker-compose up --build
# Access at: http://localhost:8501
```

## 🤖 Multi-Agent Pipeline

```
User Input → InputParser → IntentDetector → ToneStylist → DraftWriter → 
Personalizer → Reviewer → Finalizer → Final Email
```

### Agent Responsibilities

1. **InputParserAgent**: Extracts structured information
2. **IntentDetectorAgent**: Identifies email purpose
3. **ToneStylistAgent**: Defines tone guidelines
4. **DraftWriterAgent**: Creates initial draft
5. **PersonalizerAgent**: Adds user-specific touches
6. **ReviewerAgent**: Quality assurance
7. **FinalizerAgent**: Produces polished email

## 🧪 Testing

```bash
./scripts/run_tests.sh
```

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [API Reference](docs/api_reference.md)
- [Architecture](docs/architecture.md)
- [Docker Setup Guide](docs/DOCKER_GUIDE.md)

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Made with ❤️ using LangGraph and GPT-4o-mini**

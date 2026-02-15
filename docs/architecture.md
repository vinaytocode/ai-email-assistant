# ai-email-assistant - Architecture Documentation

## System Architecture

### Overview

The ai-email-assistant is built on a **multi-agent architecture** orchestrated by **LangGraph**, providing a modular, scalable approach to email generation with specialized AI agents handling specific tasks.

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (Streamlit)              │
│  - Profile Selection  - Tone Configuration  - History       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Workflow Orchestrator (LangGraph)              │
│  - State Management  - Agent Coordination  - Error Handling │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent Pipeline                     │
│  InputParser → IntentDetector → ToneStylist → DraftWriter   │
│  → Personalizer → Reviewer → Router → Finalizer             │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┬──────────────┐
         ▼                       ▼              ▼
    ┌─────────┐           ┌──────────┐    ┌─────────┐
    │ Memory  │           │   Core   │    │  Utils  │
    │ System  │           │ Services │    │         │
    └─────────┘           └──────────┘    └─────────┘
         │                       │              │
         ▼                       ▼              ▼
    User Profiles         Context Mgmt      Logging
                         Export Mgmt       Exceptions
```

## LangGraph Workflow Assembly

This section details how all agents are wired into a directed graph, where each
agent operates on shared state and passes enriched context downstream. The review
stage introduces conditional routing for quality-based retry logic.

### Complete Agent Pipeline

```
┌─────────────────┐
│  Input Parser   │ ← Entry point
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Intent Detector │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tone Stylist   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Draft Writer   │ ◄─────-┐ (Retry loop on FAIL)
└────────┬────────┘        │
         │                 │
         ▼                 │
┌─────────────────┐        │
│  Personalizer   │        │
└────────┬────────┘        │
         │                 │
         ▼                 │
┌─────────────────┐        │
│    Reviewer     │        │
└────────┬────────┘        │
         │                 │
    ┌────┴────┐            │
    │ Router  │            │
    └────┬────┘            │
         │                 │
    PASS │ FAIL            │
         │  └──────────────┘
         ▼
┌─────────────────┐
│   Finalizer     │
└────────┬────────┘
         │
         ▼
       [END]
```

### Execution Order

Input → Intent → Tone → Draft → Personalize → Review → **Router Decision**:
- **PASS**: → Finalize → END
- **FAIL**: → increment_retry → Draft Writer (retry with review feedback)

### Router Decision Logic

The `review_router` function implements the conditional branching:

```python
def review_router(state) -> str:
    review_passed = state.get("review_passed", True)
    retry_count = state.get("retry_count", 0)

    if review_passed:
        return "finalize"           # Quality gate passed
    if retry_count >= MAX_RETRIES:
        return "finalize"           # Safety cap reached, force finalize
    return "write_draft"            # Loop back for retry
```

### Key Workflow Features
- **Conditional Routing**: Router enables validation-based fallback after review
- **Retry Logic**: Failed drafts loop back to DraftWriter with reviewer feedback for improvement
- **Safety Cap**: Maximum 2 retries prevents infinite loops and controls API costs
- **Fail-Open Verdict**: If the LLM does not produce a parseable verdict, defaults to PASS
- **State Persistence**: Finalizer commits final output and generation metadata
- **Clean Termination**: Graph ends after Finalizer completes

## Module Architecture

### 1. src/agents/ - Multi-Agent System

#### Base Agent
```python
BaseAgent (Abstract)
├── process(state) → Dict[str, Any]  # Main processing method
├── log_processing(message)          # Logging utility
└── llm: LLMWrapper                  # LLM interface
```

#### Specialized Agents

| Agent | Purpose | Input | Output | Temperature |
|-------|---------|-------|--------|-------------|
| InputParserAgent | Extract structured info from raw input | `raw_prompt` | `parsed_input` | 0.3 |
| IntentDetectorAgent | Identify email intent category | `parsed_input`, `raw_prompt` | `intent` | 0.3 |
| ToneStylistAgent | Define tone-specific writing guidelines | `tone`, `intent`, `user_profile` | `tone_guidelines` | 0.3 |
| DraftWriterAgent | Create initial email draft | `parsed_input`, `intent`, `tone_guidelines`, `context_history` | `draft` | 0.7 |
| PersonalizerAgent | Add user-specific touches and signature | `draft`, `user_profile` | `personalized_draft` | 0.5 |
| ReviewerAgent | Quality assurance with PASS/FAIL verdict | `personalized_draft`, `intent`, `tone`, `retry_count` | `review_feedback`, `review_passed` | 0.3 |
| FinalizerAgent | Produce final polished email | `personalized_draft`, `review_feedback` | `final_email`, `generation_metadata` | 0.3 |

#### ReviewerAgent Verdict Parsing

The ReviewerAgent prompts the LLM to end its review with a structured verdict:
```
VERDICT: PASS
```
or
```
VERDICT: FAIL
```

The `_parse_verdict()` method scans lines in reverse to extract the verdict.
If no valid verdict is found, it defaults to PASS to prevent infinite retry loops.

### 2. src/workflow/ - LangGraph Orchestration

#### EmailWorkflow Class
```python
EmailWorkflow
├── __init__()
│   ├── Initialize LLMWrapper
│   └── Build LangGraph with conditional routing
│
├── _build_graph() → StateGraph
│   ├── Initialize all 7 agents
│   ├── Create workflow graph
│   ├── Add nodes (7 agents + increment_retry)
│   ├── Define sequential edges (parse → detect → tone → draft → personalize → review)
│   ├── Add conditional edges (review → router → finalize OR increment_retry)
│   ├── Add retry edge (increment_retry → write_draft)
│   └── Compile graph
│
└── generate_email(state) → Dict
    ├── Initialize retry_count to 0
    ├── Execute graph.invoke(state)
    ├── Log review verdict and retries used
    └── Return final state
```

#### Graph Node Summary
```
Nodes:
  parse_input      → InputParserAgent.process
  detect_intent    → IntentDetectorAgent.process
  define_tone      → ToneStylistAgent.process
  write_draft      → DraftWriterAgent.process
  personalize      → PersonalizerAgent.process
  review           → ReviewerAgent.process
  increment_retry  → increment_retry() utility function
  finalize         → FinalizerAgent.process

Edges:
  parse_input     → detect_intent     (always)
  detect_intent   → define_tone       (always)
  define_tone     → write_draft       (always)
  write_draft     → personalize       (always)
  personalize     → review            (always)
  review          → finalize          (conditional: PASS or max retries)
  review          → increment_retry   (conditional: FAIL and retries remaining)
  increment_retry → write_draft       (always)
  finalize        → END               (always)
```

### 3. src/memory/ - Profile & Context Management

#### ProfileManager
```python
ProfileManager
├── __init__()
│   └── Load user_profiles.json
├── _load_profiles() → Dict
├── get_profile(user_type) → Dict
└── list_profiles() → List
```

#### User Profile Structure
```json
{
  "user_type": {
    "role": "Professional Role",
    "name": "Full Name",
    "company/institution": "Organization",
    "writing_style": "Style description",
    "signature": "Email signature block"
  }
}
```

### 4. src/core/ - Core Business Logic

#### EmailState (TypedDict)
```python
EmailState
├── Input Data
│   ├── raw_prompt: str
│   ├── tone: str
│   ├── user_type: str
│   ├── user_profile: Optional[Dict]
│   └── context_history: Optional[str]
├── Processing Stages
│   ├── parsed_input, intent, tone_guidelines
│   ├── draft, personalized_draft
│   ├── review_feedback: Optional[str]
│   ├── review_passed: Optional[bool]      ← Router decision flag
│   ├── retry_count: Optional[int]         ← Tracks retry attempts
│   └── final_email
└── Metadata
    └── generation_metadata: Optional[Dict]
```

#### ContextManager
```python
ContextManager
├── max_entries: int (default: 3)
├── get_context_summary(history) → str
├── add_to_history(history, entry) → List
└── create_history_entry(...) → ConversationEntry
```

#### ExportManager
```python
ExportManager
├── export_to_txt(email, metadata) → str
├── export_to_json(email_data) → str
└── create_filename(base, ext) → str
```

### 5. src/integrations/ - External Services

#### OpenAIClient
```python
OpenAIClient
├── __init__(api_key)
└── create_completion(messages, **kwargs) → str
```

#### LLMWrapper
```python
LLMWrapper
├── __init__()
└── call_llm(system, user, **kwargs) → str
```

### 6. src/config/ - Configuration Management

#### Settings (Pydantic BaseSettings)
```python
Settings
├── OpenAI: openai_api_key, default_model, default_temperature, max_tokens
├── Application: app_title, app_port, debug
└── Context: max_context_entries, enable_context_memory
```

#### MCP Configuration (YAML)
```yaml
version: "1.0"
agents:       # name, description, priority, timeout
workflow:     # name, type, stages
communication: # message_format, state_persistence, error_handling
context:      # max_history_entries, include_metadata
integrations: # llm_provider, default_model, temperature_range
```

### 7. src/ui/ - User Interface

#### EmailAssistantUI
```python
EmailAssistantUI
├── __init__()
├── render_sidebar() → (user_type, tone, use_context)
├── render_main_content(...)
├── generate_email(prompt, user_type, tone, use_context)
├── display_email_result()    ← Shows review verdict and retry info
└── run()
```

## Data Flow

### Request Flow
```
User Input
  ↓
[UI Layer] → Collect prompt, tone, user_type; init retry_count=0
  ↓
[Context Layer] → Get user profile, generate context summary
  ↓
[Workflow Layer] → Execute LangGraph, coordinate agents with routing
  ↓
[Agent Layer] → Each agent transforms state via LLM calls
  ↓
[Review Gate] → Reviewer produces PASS/FAIL verdict
  ↓
[Router] → PASS: finalize | FAIL: increment retry, loop to draft
  ↓
[Integration Layer] → Format requests, call OpenAI API
  ↓
[Result Processing] → Extract final_email, record retry metadata
  ↓
[UI Display] → Show email, review status, retry count, export options
```

### State Transformation
```python
Initial State:
  raw_prompt, tone, user_type, user_profile, context_history
  retry_count=0, review_passed=None

After InputParser:      + parsed_input
After IntentDetector:   + intent
After ToneStylist:      + tone_guidelines
After DraftWriter:      + draft
After Personalizer:     + personalized_draft
After Reviewer:         + review_feedback, review_passed (True/False)

  [If FAIL and retries < MAX_RETRIES]:
    After increment_retry: retry_count += 1
    → Back to DraftWriter (draft rewritten using review_feedback)
    → Personalizer → Reviewer again

  [If PASS or max retries reached]:
    After Finalizer:
      + final_email
      + generation_metadata {
          intent, tone, user_type, has_context,
          review_passed, retry_count, forced_finalization
        }
```

## Security Architecture

### API Key Management
- **Storage**: Environment variables via `.env` file
- **Protection**: `.env` in `.gitignore`
- **Scope**: Never logged, displayed, or stored in code

### Data Privacy
- **Email Content**: No persistent storage
- **Session Data**: Memory-only (session_state)
- **History**: Cleared on browser close
- **Exports**: User-initiated only

### Error Handling
```python
try:
    result = workflow.generate_email(state)
except LLMError as e:
    logger.error(f"LLM error: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
```

## Performance Considerations

### LLM Optimization
- **Model**: GPT-4o-mini (fast, cost-effective)
- **Token Limits**: 1000 max tokens per request
- **Temperature**: Varied by agent (0.3-0.7)
- **Context Window**: Limited to 3 previous emails
- **Retry Cap**: Maximum 2 retries limits worst-case to 9 LLM calls per email

### Cost Impact of Retry Logic
| Scenario | LLM Calls | Notes |
|----------|-----------|-------|
| PASS on first draft | 7 | All agents run once |
| FAIL → PASS on retry 1 | 10 | Draft + Personalize + Review run twice |
| FAIL → FAIL → forced finalize | 13 | Draft + Personalize + Review run three times |

### Caching Strategy
- **User Profiles**: Loaded once at startup
- **Session State**: Cached in Streamlit session
- **LLM Responses**: No caching (dynamic content)

### Future: Async/Parallel Processing
```python
# Current: Sequential with conditional routing
# Future: Parallel where possible
async def parallel_stage(state):
    tasks = [agent1.process(state), agent2.process(state)]
    results = await asyncio.gather(*tasks)
    return merge_results(results)
```

## Testing Architecture

### Test Structure
```
tests/
├── test_agents/
│   ├── test_input_parser.py
│   ├── test_intent_detector.py
│   ├── test_draft_writer.py
│   └── test_reviewer.py         ← PASS/FAIL verdict tests
├── test_core/
│   ├── test_context_manager.py
│   └── test_export_manager.py
├── test_config/
│   └── test_settings.py
├── test_memory/
│   └── test_profile_manager.py
├── test_workflow/
│   └── test_langgraph.py        ← Router and retry logic tests
└── test_integration/
    └── test_end_to_end.py
```

### Testing Strategy
1. **Unit Tests**: Each agent in isolation (mocked LLM)
2. **Router Tests**: review_router and increment_retry tested with various state combinations
3. **Verdict Parsing Tests**: PASS, FAIL, case-insensitive, malformed, missing verdict
4. **Integration Tests**: Workflow with mocked external services
5. **E2E Tests**: Full system with real API calls (optional)

## Deployment Architecture

### Local Development
```
Developer Machine
├── Python 3.9+ virtual environment
├── .env file with API key
├── Streamlit dev server (port 8501)
└── File-based logging
```

### Docker Deployment
```
Docker Container
├── Python 3.9-slim base image
├── Environment variables from .env
├── Streamlit production server
├── Volume mounts for logs
└── Health check endpoint
```

### Future: Cloud Deployment
```
Cloud Architecture (Proposed)
├── Load Balancer
├── Multiple Streamlit Instances
├── Redis for Session Management
├── Centralized Logging
├── Secrets Manager for API Keys
└── Auto-scaling based on traffic
```

## Extension Points

### Adding New Agents
```python
# 1. Create agent class
class NewAgent(BaseAgent):
    def process(self, state):
        return state

# 2. Register in workflow
workflow.add_node("new_agent", new_agent.process)
workflow.add_edge("previous_agent", "new_agent")
workflow.add_edge("new_agent", "next_agent")

# 3. Update MCP configuration
```

### Adding New User Profiles
```json
{
  "new_profile": {
    "role": "...",
    "name": "...",
    "writing_style": "...",
    "signature": "..."
  }
}
```

## Evaluation Criteria Coverage

| Criteria | Coverage | Details |
|----------|----------|---------|
| Agentic Architecture (25%) | Modular, single-responsibility agents | 7 specialized agents, each with clear input/output contracts |
| Routing & MCP (10%) | Conditional routing with fallback | Review → Router → PASS/FAIL with retry loop back to DraftWriter |
| Context Memory | Conversation history awareness | Last 3 emails maintained for continuity |
| Cost Optimization | Efficient token usage | GPT-4o-mini with capped max_tokens; retry cap limits worst-case cost |
| Export Functionality | TXT and JSON exports | Timestamped files with full metadata including review status |

## Design Principles

1. **Modularity**: Each agent is independent and testable
2. **Separation of Concerns**: Clear boundaries between layers
3. **Type Safety**: Pydantic models for configuration and state
4. **Error Resilience**: Graceful degradation on failures; fail-open verdict parsing
5. **Extensibility**: Easy to add agents, profiles, or features
6. **Cost Optimization**: Efficient token usage, model selection, and retry caps
7. **User Privacy**: No persistent storage of email content

---

**Document Version**: 1.1
**Author**: Vinay K <itzvinay@gmail.com>
**Repository**: https://github.com/vinaytocode/ai-email-assistant
**Maintainer**: Vinay K

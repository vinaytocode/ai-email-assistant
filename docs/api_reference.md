# API Reference - ai-email-assistant

## Overview

This document provides detailed API documentation for all modules, classes, and functions in the ai-email-assistant.

## Module Structure
```
src/
├── agents/          # Multi-agent system
├── config/          # Configuration management
├── core/            # Core business logic
├── integrations/    # External service integrations
├── memory/          # User profiles and context
├── ui/              # User interface
├── utils/           # Utilities
└── workflow/        # LangGraph orchestration with conditional routing
```

---

## Agents Module

### src.agents.base_agent

#### `BaseAgent` (Abstract Base Class)

Abstract base class for all email generation agents.
```python
class BaseAgent(ABC):
    def __init__(self, llm_wrapper: LLMWrapper)
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]
    
    def log_processing(self, message: str) -> None
```

**Parameters**:
- `llm_wrapper` (LLMWrapper): LLM interface for API calls

**Methods**:

##### `process(state) -> Dict[str, Any]`
Abstract method. Process state and return updated state.

##### `log_processing(message) -> None`
Log agent processing information with agent name prefix.

---

### src.agents.input_parser

#### `InputParserAgent`

Parses and extracts structured information from raw user input.

**Input State Keys**: `raw_prompt`
**Output State Keys**: `parsed_input`

**Example**:
```python
agent = InputParserAgent(llm_wrapper)
state = {"raw_prompt": "Write a thank you email to my professor"}
result = agent.process(state)
print(result["parsed_input"])
```

---

### src.agents.intent_detector

#### `IntentDetectorAgent`

Detects the intent and purpose of the email.

**Input State Keys**: `parsed_input`, `raw_prompt`
**Output State Keys**: `intent`

**Intent Categories**:
Request, Response, Follow-up, Notification, Apology, Gratitude, Introduction, Proposal, Complaint, Other

---

### src.agents.tone_stylist

#### `ToneStylistAgent`

Defines tone and style guidelines for the email.

**Input State Keys**: `tone`, `intent`, `user_profile`
**Output State Keys**: `tone_guidelines`

**Supported Tones**: `very_formal`, `formal`, `professional`, `friendly`, `casual`

---

### src.agents.draft_writer

#### `DraftWriterAgent`

Creates the initial email draft. On retry iterations, the existing `review_feedback` in state is available via `context_history` for the LLM to incorporate.

**Input State Keys**: `parsed_input`, `intent`, `tone_guidelines`, `context_history`
**Output State Keys**: `draft`
**Temperature**: 0.7

---

### src.agents.personalizer

#### `PersonalizerAgent`

Personalizes the email based on user profile. Adds signature and adjusts writing style.

**Input State Keys**: `draft`, `user_profile`
**Output State Keys**: `personalized_draft`

---

### src.agents.reviewer

#### `ReviewerAgent`

Reviews the email draft and produces a structured PASS/FAIL verdict for conditional routing.

```python
class ReviewerAgent(BaseAgent):
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]
    def _parse_verdict(self, review_text: str) -> bool
```

**Input State Keys**:
- `personalized_draft` (str): Draft to review
- `intent` (str): Expected intent
- `tone` (str): Expected tone
- `retry_count` (int): Current retry attempt number

**Output State Keys**:
- `review_feedback` (str): Quality assessment and suggestions
- `review_passed` (bool): True for PASS, False for FAIL

**Evaluation Criteria**:
- Clarity and coherence
- Tone appropriateness
- Grammar and spelling
- Professional formatting
- Completeness
- Potential misunderstandings

**Methods**:

##### `process(state) -> Dict[str, Any]`

Prompts the LLM to review the email and end with a verdict line. Parses the verdict and sets `review_passed` in state.

##### `_parse_verdict(review_text: str) -> bool`

Extracts PASS/FAIL verdict from the review output text.

**Parameters**:
- `review_text` (str): Full review text from LLM

**Returns**:
- `bool`: True if PASS, False if FAIL

**Parsing Rules**:
- Scans lines in reverse looking for `VERDICT: PASS` or `VERDICT: FAIL`
- Case-insensitive matching
- Handles extra whitespace
- Defaults to `True` (PASS) if no valid verdict found — fail-open to prevent infinite retry loops

**Example**:
```python
agent = ReviewerAgent(llm_wrapper)

# LLM returns review ending with verdict
# "The email is clear and professional.\nVERDICT: PASS"
result = agent.process(state)

print(result["review_passed"])   # True
print(result["review_feedback"]) # Full review text
```

**Verdict Examples**:
```
"Good email.\nVERDICT: PASS"           → review_passed = True
"Needs rewrite.\nVERDICT: FAIL"        → review_passed = False
"verdict: pass"                         → review_passed = True  (case-insensitive)
"  VERDICT:   FAIL  "                   → review_passed = False (whitespace tolerant)
"Looks great. No issues."              → review_passed = True  (no verdict = default PASS)
"Review done.\nVERDICT: MAYBE"          → review_passed = True  (invalid value = default PASS)
""                                      → review_passed = True  (empty = default PASS)
```

---

### src.agents.finalizer

#### `FinalizerAgent`

Produces the final, polished email. Includes review routing metadata in output.

**Input State Keys**: `personalized_draft`, `review_feedback`
**Output State Keys**: `final_email`, `generation_metadata`
**Temperature**: 0.3

**generation_metadata structure**:
```python
{
    "intent": str,              # Detected email intent
    "tone": str,                # Tone setting used
    "user_type": str,           # Profile type
    "has_context": bool,        # Whether conversation history was used
    "review_passed": bool,      # Final review verdict
    "retry_count": int,         # Number of retries used
    "forced_finalization": bool  # True if max retries hit without PASS
}
```

---

## Core Module

### src.core.state_models

#### `EmailState` (TypedDict)

State model for email generation workflow.
```python
class EmailState(TypedDict):
    # Input data
    raw_prompt: str
    tone: str
    user_type: str
    user_profile: Optional[Dict[str, Any]]
    context_history: Optional[str]
    
    # Processing stages
    parsed_input: Optional[str]
    intent: Optional[str]
    tone_guidelines: Optional[str]
    draft: Optional[str]
    personalized_draft: Optional[str]
    review_feedback: Optional[str]
    review_passed: Optional[bool]       # Router decision flag
    retry_count: Optional[int]          # Tracks retry attempts
    final_email: Optional[str]
    
    # Metadata
    generation_metadata: Optional[Dict[str, Any]]
```

#### `ConversationEntry` (TypedDict)

```python
class ConversationEntry(TypedDict):
    prompt: str
    tone: str
    user_type: str
    email: str
    timestamp: str
    intent: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

---

### src.core.context_manager

#### `ContextManager`

Manages conversation context and history.
```python
class ContextManager:
    def __init__(self)
    def get_context_summary(self, history: List[ConversationEntry]) -> str
    def add_to_history(self, history, entry) -> List[ConversationEntry]
    def create_history_entry(self, prompt, tone, user_type, email, ...) -> ConversationEntry
```

**Attributes**:
- `max_entries` (int): Maximum entries for context (default: 3)

---

### src.core.export_manager

#### `ExportManager`

```python
class ExportManager:
    @staticmethod
    def export_to_txt(email_content: str, metadata: Optional[Dict] = None) -> str
    
    @staticmethod
    def export_to_json(email_data: Dict[str, Any]) -> str
    
    @staticmethod
    def create_filename(base_name: str, extension: str) -> str
```

---

## Integrations Module

### src.integrations.openai_client

#### `OpenAIClient`

```python
class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None)
    def create_completion(self, messages, model=None, temperature=None, max_tokens=None, **kwargs) -> str
```

**Raises**: `LLMError` on API errors

---

### src.integrations.llm_wrapper

#### `LLMWrapper`

```python
class LLMWrapper:
    def __init__(self)
    def call_llm(self, system_prompt, user_prompt, model=None, temperature=None) -> str
```

---

## Memory Module

### src.memory.ProfileManager

#### `ProfileManager`

```python
class ProfileManager:
    def __init__(self)
    def get_profile(self, user_type: str) -> Optional[Dict[str, Any]]
    def list_profiles(self) -> list
```

---

## Workflow Module

### src.workflow.langgraph_flow

#### Constants

##### `MAX_RETRIES`
```python
MAX_RETRIES = 2
```
Maximum number of retry attempts before forcing finalization. Controls worst-case API cost.

---

#### `review_router(state: Dict[str, Any]) -> str`

Conditional routing function called after the ReviewerAgent. Determines whether the workflow proceeds to finalization or loops back for a retry.

**Parameters**:
- `state` (Dict[str, Any]): Current workflow state

**Returns**:
- `str`: Next node name — either `"finalize"` or `"write_draft"`

**Decision Logic**:
```
if review_passed == True:
    → "finalize"
elif retry_count >= MAX_RETRIES:
    → "finalize"  (forced, safety cap)
else:
    → "write_draft" (retry)
```

**Default Behavior**:
- Missing `review_passed` defaults to `True` → finalize
- Missing `retry_count` defaults to `0`

**Example**:
```python
from src.workflow.langgraph_flow import review_router

# PASS case
state = {"review_passed": True, "retry_count": 0}
review_router(state)  # Returns: "finalize"

# FAIL with retries remaining
state = {"review_passed": False, "retry_count": 0}
review_router(state)  # Returns: "write_draft"

# FAIL but max retries reached
state = {"review_passed": False, "retry_count": 2}
review_router(state)  # Returns: "finalize"
```

---

#### `increment_retry(state: Dict[str, Any]) -> Dict[str, Any]`

Utility node function that increments the retry counter. Sits between the router's FAIL path and write_draft.

**Parameters**:
- `state` (Dict[str, Any]): Current workflow state

**Returns**:
- `Dict[str, Any]`: State with `retry_count` incremented by 1

**Example**:
```python
from src.workflow.langgraph_flow import increment_retry

state = {"retry_count": 0, "draft": "old draft"}
result = increment_retry(state)
print(result["retry_count"])  # 1
print(result["draft"])        # "old draft" (preserved)
```

---

#### `EmailWorkflow`

LangGraph-based email generation workflow with conditional routing.
```python
class EmailWorkflow:
    def __init__(self)
    def _build_graph(self) -> StateGraph
    def generate_email(self, state: Dict[str, Any]) -> Dict[str, Any]
```

**Graph Structure**:
```
Nodes: parse_input, detect_intent, define_tone, write_draft,
       personalize, review, increment_retry, finalize

Sequential edges:
  parse_input → detect_intent → define_tone → write_draft
  → personalize → review

Conditional edges (from review):
  review_router returns "finalize"    → finalize
  review_router returns "write_draft" → increment_retry

Retry edge:
  increment_retry → write_draft

Terminal edge:
  finalize → END
```

##### `generate_email(state) -> Dict[str, Any]`

Execute the email generation workflow.

**Parameters**:
- `state` (Dict): Initial email state. Must include `raw_prompt`, `tone`, `user_type`. `retry_count` is auto-initialized to 0 if missing.

**Returns**:
- `Dict`: Final state with `final_email`, `generation_metadata`, and all intermediate state

**Example**:
```python
workflow = EmailWorkflow()
result = workflow.generate_email({
    "raw_prompt": "Write thank you email",
    "tone": "professional",
    "user_type": "student",
    "user_profile": {...},
    "context_history": None,
    "retry_count": 0,
    "review_passed": None,
})

print(result["final_email"])
print(result["generation_metadata"]["review_passed"])  # True or False
print(result["generation_metadata"]["retry_count"])     # 0, 1, or 2
print(result["generation_metadata"]["forced_finalization"])  # True if capped
```

---

## Configuration Module

### src.config.settings

#### `Settings` (Pydantic BaseSettings)

```python
class Settings(BaseSettings):
    openai_api_key: str
    default_model: str = "gpt-4o-mini"
    default_temperature: float = 0.3
    max_tokens: int = 1000
    app_title: str = "AI Email Assistant"
    app_port: int = 8501
    debug: bool = False
    max_context_entries: int = 3
    enable_context_memory: bool = True
```

---

## Utils Module

### src.utils.logger

#### `get_logger(name: str) -> logging.Logger`

Get configured logger instance. Uses DEBUG level when `DEBUG=true` env var is set.

### src.utils.exceptions

- `EmailAssistantError`: Base exception
- `LLMError`: LLM-related errors
- `ValidationError`: Validation errors
- `ConfigurationError`: Configuration errors

---

## Type Definitions

```python
from typing import Dict, List, Optional, Any, TypedDict

StateDict = Dict[str, Any]
ProfileDict = Dict[str, Any]
MessagesList = List[Dict[str, str]]
MetadataDict = Dict[str, Any]
```

## Constants

### Workflow Constants
```python
MAX_RETRIES = 2  # Maximum draft retry attempts
```

### Tone Levels
`very_formal`, `formal`, `professional`, `friendly`, `casual`

### Intent Categories
`request`, `response`, `follow_up`, `notification`, `apology`, `gratitude`, `introduction`, `proposal`, `complaint`

---

## Complete Workflow Example

```python
from src.workflow.langgraph_flow import EmailWorkflow
from src.memory import ProfileManager
from src.core.context_manager import ContextManager
from src.core.export_manager import ExportManager

# Initialize
workflow = EmailWorkflow()
profile_mgr = ProfileManager()
context_mgr = ContextManager()
export_mgr = ExportManager()

# Prepare state
profile = profile_mgr.get_profile("student")
context = context_mgr.get_context_summary(history)

state = {
    "raw_prompt": "Request deadline extension for research paper",
    "tone": "professional",
    "user_type": "student",
    "user_profile": profile,
    "context_history": context,
    "retry_count": 0,
    "review_passed": None,
}

# Generate email (may retry internally if review fails)
result = workflow.generate_email(state)

# Access results
final_email = result["final_email"]
metadata = result["generation_metadata"]

print(f"Review: {'PASS' if metadata['review_passed'] else 'FAIL'}")
print(f"Retries: {metadata['retry_count']}")
print(f"Forced: {metadata['forced_finalization']}")

# Export
txt = export_mgr.export_to_txt(final_email, metadata)
json_out = export_mgr.export_to_json(result)
```

---

**API Version**: 1.1
**Author**: Vinay K <itzvinay@gmail.com>
**Repository**: https://github.com/vinaytocode/ai-email-assistant
**Compatibility**: Python 3.9+

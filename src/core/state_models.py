"""State models for LangGraph workflow."""

from typing import TypedDict, Optional, List, Dict, Any


class EmailState(TypedDict):
    """State model for email generation workflow."""
    
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
    review_passed: Optional[bool]
    retry_count: Optional[int]
    final_email: Optional[str]
    
    # Metadata
    generation_metadata: Optional[Dict[str, Any]]


class ConversationEntry(TypedDict):
    """Single conversation history entry."""
    
    prompt: str
    tone: str
    user_type: str
    email: str
    timestamp: str
    intent: Optional[str]
    metadata: Optional[Dict[str, Any]]

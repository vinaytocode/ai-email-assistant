"""Context and conversation history management."""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .state_models import ConversationEntry


class ContextManager:
    """Manages conversation context and history."""
    
    def __init__(self, max_entries: int = None):
        self.max_entries = max_entries or int(os.getenv('MAX_CONTEXT_ENTRIES', '3'))
    
    def get_context_summary(self, history: List[ConversationEntry]) -> str:
        """Generate context summary from conversation history."""
        if not history or len(history) == 0:
            return "No previous context available."
        
        # Get recent entries within token limits
        recent_history = history[-self.max_entries:]
        
        context_parts = []
        for i, entry in enumerate(recent_history, 1):
            prompt_preview = entry.get('prompt', 'N/A')[:100]
            if len(prompt_preview) == 100:
                prompt_preview += "..."
                
            context_parts.append(
                f"Email {i}: {prompt_preview} (Tone: {entry.get('tone', 'N/A')})"
            )
        
        return "\n".join(context_parts)
    
    def add_to_history(
        self, 
        history: List[ConversationEntry], 
        entry: ConversationEntry
    ) -> List[ConversationEntry]:
        """Add entry to conversation history with size management."""
        history.append(entry)
        
        # Keep only recent entries to manage memory
        if len(history) > 10:
            history = history[-10:]
        
        return history
    
    def create_history_entry(
        self,
        prompt: str,
        tone: str,
        user_type: str,
        email: str,
        intent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationEntry:
        """Create a new conversation history entry."""
        return ConversationEntry(
            prompt=prompt,
            tone=tone,
            user_type=user_type,
            email=email,
            timestamp=datetime.now().isoformat(),
            intent=intent,
            metadata=metadata or {}
        )

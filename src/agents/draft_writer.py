"""Draft writer agent for creating initial email draft."""

from typing import Dict, Any
from .base_agent import BaseAgent


class DraftWriterAgent(BaseAgent):
    """Creates the initial email draft."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate initial email draft."""
        self.log_processing("Creating email draft")
        
        parsed_input = state.get("parsed_input", "")
        intent = state.get("intent", "")
        tone_guidelines = state.get("tone_guidelines", "")
        context_history = state.get("context_history", "")
        
        system_prompt = """You are an expert email writer.
Create a well-structured, professional email draft.

Requirements:
- Clear subject line
- Appropriate greeting
- Logical flow of content
- Professional closing
- Proper formatting

DO NOT include signature yet - that comes later."""

        user_prompt = f"""Write an email draft based on:

Purpose: {parsed_input}

Intent: {intent}

Tone Guidelines: {tone_guidelines}

Context from previous emails:
{context_history if context_history else 'None'}

Create a complete, well-formatted email WITHOUT the signature."""

        draft = self.llm.call_llm(
            system_prompt, 
            user_prompt,
            temperature=0.7
        )
        
        state["draft"] = draft
        self.log_processing("Draft created")
        
        return state

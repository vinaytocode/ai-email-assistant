"""Input parser agent for extracting key information."""

from typing import Dict, Any
from .base_agent import BaseAgent


class InputParserAgent(BaseAgent):
    """Parses and extracts key information from user input."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw input and extract structured information."""
        self.log_processing("Parsing user input")
        
        raw_prompt = state.get("raw_prompt", "")
        
        system_prompt = """You are an input parser for an email assistant.
Extract and structure the key information from the user's email request.

Focus on:
- Main purpose/topic
- Key points to include
- Any specific requirements
- Recipient context (if mentioned)

Provide a clear, structured summary."""

        user_prompt = f"""Parse this email request:

{raw_prompt}

Provide a structured analysis of what the user wants."""

        parsed_input = self.llm.call_llm(system_prompt, user_prompt)
        
        state["parsed_input"] = parsed_input
        self.log_processing("Input parsing completed")
        
        return state

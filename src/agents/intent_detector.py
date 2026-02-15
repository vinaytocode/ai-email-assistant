"""Intent detector agent for identifying email purpose."""

from typing import Dict, Any
from .base_agent import BaseAgent


class IntentDetectorAgent(BaseAgent):
    """Detects the intent and purpose of the email."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Detect email intent from parsed input."""
        self.log_processing("Detecting email intent")
        
        parsed_input = state.get("parsed_input", "")
        raw_prompt = state.get("raw_prompt", "")
        
        system_prompt = """You are an intent detection specialist.
Identify the primary intent of the email from these categories:

- Request (asking for something)
- Response (replying to inquiry)
- Follow-up (continuing conversation)
- Notification (informing about something)
- Apology (expressing regret)
- Gratitude (thanking someone)
- Introduction (meeting new contact)
- Proposal (suggesting something)
- Complaint (expressing dissatisfaction)
- Other (specify)

Provide the intent category and a brief explanation."""

        user_prompt = f"""Original request: {raw_prompt}

Parsed information: {parsed_input}

What is the primary intent of this email?"""

        intent = self.llm.call_llm(system_prompt, user_prompt)
        
        state["intent"] = intent
        self.log_processing(f"Intent detected: {intent[:50]}...")
        
        return state

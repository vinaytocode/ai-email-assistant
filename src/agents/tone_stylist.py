"""Tone stylist agent for defining tone guidelines."""

from typing import Dict, Any
from .base_agent import BaseAgent


class ToneStylistAgent(BaseAgent):
    """Defines tone and style guidelines for the email."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tone-specific guidelines."""
        self.log_processing("Creating tone guidelines")
        
        tone = state.get("tone", "professional")
        intent = state.get("intent", "")
        user_profile = state.get("user_profile", {})
        
        system_prompt = f"""You are a tone and style expert.
Create specific writing guidelines for a {tone} email.

Consider:
- The user's role: {user_profile.get('role', 'Professional')}
- The email intent: {intent}
- Appropriate formality level
- Language complexity
- Emotional tone
- Sentence structure preferences

Provide clear, actionable tone guidelines."""

        user_prompt = f"""Create tone guidelines for:
Tone: {tone}
Intent: {intent}
User: {user_profile.get('writing_style', 'professional')}"""

        tone_guidelines = self.llm.call_llm(system_prompt, user_prompt)
        
        state["tone_guidelines"] = tone_guidelines
        self.log_processing("Tone guidelines created")
        
        return state

"""Personalizer agent for adding user-specific touches."""

from typing import Dict, Any
from .base_agent import BaseAgent


class PersonalizerAgent(BaseAgent):
    """Personalizes the email based on user profile."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize draft with user profile information."""
        self.log_processing("Personalizing email")
        
        draft = state.get("draft", "")
        user_profile = state.get("user_profile", {})
        
        if not user_profile:
            state["personalized_draft"] = draft
            self.log_processing("No profile found, using original draft")
            return state
        
        system_prompt = f"""You are a personalization specialist.
Enhance the email with personal touches based on the user's profile.

User Profile:
- Name: {user_profile.get('name', 'N/A')}
- Role: {user_profile.get('role', 'N/A')}
- Company/Institution: {user_profile.get('company', user_profile.get('institution', 'N/A'))}
- Writing Style: {user_profile.get('writing_style', 'N/A')}

Add the signature and ensure the email reflects the user's professional identity.
Keep the core content but adjust style to match the profile."""

        user_prompt = f"""Draft email:
{draft}

User signature:
{user_profile.get('signature', '')}

Personalize this email and add the signature."""

        personalized_draft = self.llm.call_llm(system_prompt, user_prompt)
        
        state["personalized_draft"] = personalized_draft
        self.log_processing("Email personalized")
        
        return state

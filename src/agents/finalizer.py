"""Finalizer agent for producing the final email."""

from typing import Dict, Any
from .base_agent import BaseAgent


class FinalizerAgent(BaseAgent):
    """Produces the final, polished email."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create final email incorporating review feedback."""
        self.log_processing("Finalizing email")
        
        personalized_draft = state.get("personalized_draft", "")
        review_feedback = state.get("review_feedback", "")
        
        system_prompt = """You are a final email editor.
Create the polished final version of the email.

Incorporate the reviewer's feedback while maintaining the email's essence.
Ensure perfect grammar, formatting, and professionalism.

Output ONLY the final email - no explanations or meta-commentary."""

        user_prompt = f"""Draft email:
{personalized_draft}

Review feedback:
{review_feedback}

Produce the final, perfected email."""

        final_email = self.llm.call_llm(
            system_prompt,
            user_prompt,
            temperature=0.3
        )
        
        # Build metadata including review routing info
        retry_count = state.get("retry_count", 0)
        review_passed = state.get("review_passed", True)
        
        state["final_email"] = final_email
        state["generation_metadata"] = {
            "intent": state.get("intent", "Unknown"),
            "tone": state.get("tone", "professional"),
            "user_type": state.get("user_type", "default"),
            "has_context": bool(state.get("context_history")),
            "review_passed": review_passed,
            "retry_count": retry_count,
            "forced_finalization": not review_passed and retry_count >= 2,
        }
        
        self.log_processing(
            f"Email finalized (retries: {retry_count}, "
            f"review: {'PASS' if review_passed else 'FAIL-forced'})"
        )
        
        return state

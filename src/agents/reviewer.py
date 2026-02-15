"""Reviewer agent for quality assurance with PASS/FAIL verdict."""

from typing import Dict, Any
from .base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """Reviews and provides feedback on the email draft with a structured verdict."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Review email and provide improvement suggestions with PASS/FAIL decision."""
        self.log_processing("Reviewing email")
        
        personalized_draft = state.get("personalized_draft", "")
        intent = state.get("intent", "")
        tone = state.get("tone", "professional")
        retry_count = state.get("retry_count", 0)
        
        system_prompt = """You are a senior email quality reviewer.
Evaluate the email for:

1. Clarity and coherence
2. Tone appropriateness
3. Grammar and spelling
4. Professional formatting
5. Completeness of message
6. Potential misunderstandings

You MUST end your review with a verdict line in exactly this format:
VERDICT: PASS
or
VERDICT: FAIL

Use PASS if the email is acceptable for sending (minor issues are okay).
Use FAIL only if there are significant problems that require a rewrite.

Provide specific, actionable feedback before your verdict."""

        user_prompt = f"""Review this email:

{personalized_draft}

Expected intent: {intent}
Expected tone: {tone}
Retry attempt: {retry_count}

Provide your review, then end with VERDICT: PASS or VERDICT: FAIL"""

        review_feedback = self.llm.call_llm(system_prompt, user_prompt)
        
        # Parse the verdict from the review output
        review_passed = self._parse_verdict(review_feedback)
        
        state["review_feedback"] = review_feedback
        state["review_passed"] = review_passed
        
        self.log_processing(
            f"Review completed - Verdict: {'PASS' if review_passed else 'FAIL'} "
            f"(attempt {retry_count + 1})"
        )
        
        return state
    
    def _parse_verdict(self, review_text: str) -> bool:
        """Extract PASS/FAIL verdict from review output.
        
        Looks for 'VERDICT: PASS' or 'VERDICT: FAIL' in the review text.
        Defaults to PASS if verdict line is not found (fail-open to avoid
        infinite loops on malformed LLM output).
        """
        if not review_text:
            return True
        
        # Check lines in reverse since verdict should be at the end
        for line in reversed(review_text.strip().splitlines()):
            cleaned = line.strip().upper()
            if cleaned.startswith("VERDICT:"):
                verdict_value = cleaned.replace("VERDICT:", "").strip()
                if verdict_value == "FAIL":
                    return False
                elif verdict_value == "PASS":
                    return True
        
        # Default to PASS if no verdict found (prevents infinite retry)
        return True

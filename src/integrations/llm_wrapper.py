"""LLM wrapper for standardized model interactions."""

from typing import Optional
from .openai_client import OpenAIClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LLMWrapper:
    """Standardized wrapper for LLM interactions."""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Standardized LLM call interface."""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            
            result = self.openai_client.create_completion(
                messages=messages,
                model=model,
                temperature=temperature
            )
            
            logger.debug(f"LLM call completed - System: {system_prompt[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"LLM wrapper error: {str(e)}")
            return f"Error generating content: {str(e)}"

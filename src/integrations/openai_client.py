"""OpenAI API client wrapper."""

import os
from typing import Optional, List, Dict, Any
from openai import OpenAI
from ..utils.logger import get_logger
from ..utils.exceptions import LLMError

logger = get_logger(__name__)


class OpenAIClient:
    """OpenAI API client wrapper with error handling and logging."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.default_model = os.getenv('DEFAULT_MODEL', 'gpt-4o-mini')
        self.default_temperature = float(os.getenv('DEFAULT_TEMPERATURE', '0.3'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '1000'))
    
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Create a chat completion."""
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                temperature=temperature if temperature is not None else self.default_temperature,
                max_tokens=max_tokens or self.max_tokens,
                messages=messages,
                **kwargs
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise LLMError("Empty response from OpenAI API")
            
            logger.info(f"OpenAI API call successful - Model: {model or self.default_model}")
            return content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise LLMError(f"OpenAI API error: {str(e)}") from e

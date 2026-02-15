"""Base agent class for all email generation agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..integrations.llm_wrapper import LLMWrapper
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, llm_wrapper: LLMWrapper):
        self.llm = llm_wrapper
        self.agent_name = self.__class__.__name__
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the state and return updated state."""
        pass
    
    def log_processing(self, message: str):
        """Log agent processing information."""
        logger.info(f"[{self.agent_name}] {message}")

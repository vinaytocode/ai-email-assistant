"""Multi-agent system for email generation."""

from .base_agent import BaseAgent
from .input_parser import InputParserAgent
from .intent_detector import IntentDetectorAgent
from .tone_stylist import ToneStylistAgent
from .draft_writer import DraftWriterAgent
from .personalizer import PersonalizerAgent
from .reviewer import ReviewerAgent
from .finalizer import FinalizerAgent

__all__ = [
    "BaseAgent",
    "InputParserAgent",
    "IntentDetectorAgent",
    "ToneStylistAgent",
    "DraftWriterAgent",
    "PersonalizerAgent",
    "ReviewerAgent",
    "FinalizerAgent",
]

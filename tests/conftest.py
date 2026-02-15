"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock
from src.integrations.llm_wrapper import LLMWrapper
from src.memory import ProfileManager


@pytest.fixture
def mock_llm_wrapper():
    """Mock LLM wrapper for testing."""
    mock = Mock(spec=LLMWrapper)
    mock.call_llm.return_value = "Mocked LLM response"
    return mock


@pytest.fixture
def profile_manager():
    """Profile manager instance."""
    return ProfileManager()


@pytest.fixture
def sample_state():
    """Sample email state for testing."""
    return {
        "raw_prompt": "Write a thank you email to my professor",
        "tone": "professional",
        "user_type": "student",
        "user_profile": {
            "role": "Student",
            "name": "Test Student",
            "writing_style": "respectful, clear",
        },
        "context_history": None,
    }


@pytest.fixture
def sample_email():
    """Sample generated email."""
    return """Subject: Thank You for Your Guidance

Dear Professor,

I wanted to express my sincere gratitude for your support this semester.

Best regards,
Test Student"""

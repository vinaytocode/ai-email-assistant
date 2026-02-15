"""Basic integration tests."""

import pytest
from unittest.mock import Mock, patch
from src.workflow.langgraph_flow import EmailWorkflow
from src.memory import ProfileManager


@pytest.mark.skip(reason="Requires OpenAI API key")
def test_email_workflow_basic():
    """Test basic email workflow (skipped by default)."""
    workflow = EmailWorkflow()
    
    state = {
        "raw_prompt": "Write a test email",
        "tone": "professional",
        "user_type": "student",
        "user_profile": {"role": "Student"},
        "context_history": None,
    }
    
    result = workflow.generate_email(state)
    assert "final_email" in result


def test_profile_manager_integration():
    """Test profile manager integration."""
    manager = ProfileManager()
    profiles = manager.list_profiles()
    
    # Test all profiles load correctly
    for profile_type in profiles:
        profile = manager.get_profile(profile_type)
        assert profile is not None
        assert "role" in profile
        assert "writing_style" in profile

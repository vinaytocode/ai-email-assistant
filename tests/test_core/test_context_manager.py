"""Tests for ContextManager."""

import pytest
from src.core.context_manager import ContextManager


def test_get_context_summary_empty():
    """Test context summary with empty history."""
    manager = ContextManager()
    summary = manager.get_context_summary([])
    assert summary == "No previous context available."


def test_get_context_summary_with_history():
    """Test context summary with history."""
    manager = ContextManager()
    history = [
        {
            "prompt": "Test prompt 1",
            "tone": "professional",
            "email": "Test email 1",
            "timestamp": "2024-01-01T00:00:00",
        }
    ]
    
    summary = manager.get_context_summary(history)
    assert "Test prompt 1" in summary
    assert "professional" in summary


def test_add_to_history():
    """Test adding entries to history."""
    manager = ContextManager()
    history = []
    
    entry = manager.create_history_entry(
        prompt="Test",
        tone="casual",
        user_type="student",
        email="Email content"
    )
    
    history = manager.add_to_history(history, entry)
    assert len(history) == 1
    assert history[0]["prompt"] == "Test"

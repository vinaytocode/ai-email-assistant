"""Tests for settings configuration."""
import pytest
import os

def test_settings_loads_from_env(monkeypatch):
    """Test settings load from environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("DEFAULT_MODEL", "gpt-4o-mini")
    
    from src.config.settings import get_settings
    settings = get_settings()
    
    assert settings.openai_api_key == "test-key"
    assert settings.default_model == "gpt-4o-mini"

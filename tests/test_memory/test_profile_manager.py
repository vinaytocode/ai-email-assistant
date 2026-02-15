"""Tests for ProfileManager."""

import pytest
from src.memory import ProfileManager


def test_profile_manager_load():
    """Test profile manager loads profiles."""
    manager = ProfileManager()
    profiles = manager.list_profiles()
    
    assert len(profiles) > 0
    assert "software_engineer" in profiles
    assert "student" in profiles


def test_get_profile_exists():
    """Test getting an existing profile."""
    manager = ProfileManager()
    profile = manager.get_profile("student")
    
    assert profile is not None
    assert "role" in profile
    assert profile["role"] == "Student"


def test_get_profile_not_exists():
    """Test getting non-existent profile."""
    manager = ProfileManager()
    profile = manager.get_profile("nonexistent")
    
    assert profile is None

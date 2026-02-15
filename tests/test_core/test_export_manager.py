"""Tests for ExportManager."""

import pytest
import json
from src.core.export_manager import ExportManager


def test_export_to_txt_basic():
    """Test basic TXT export."""
    manager = ExportManager()
    result = manager.export_to_txt("Test email content")
    assert "Test email content" in result


def test_export_to_txt_with_metadata():
    """Test TXT export with metadata."""
    manager = ExportManager()
    metadata = {
        "timestamp": "2024-01-01T00:00:00",
        "user_type": "student",
        "tone": "professional"
    }
    result = manager.export_to_txt("Test content", metadata)
    
    assert "EMAIL METADATA" in result
    assert "student" in result
    assert "professional" in result
    assert "Test content" in result


def test_export_to_json():
    """Test JSON export."""
    manager = ExportManager()
    email_data = {
        "email": "Test email",
        "timestamp": "2024-01-01T00:00:00"
    }
    
    result = manager.export_to_json(email_data)
    parsed = json.loads(result)
    
    assert "export_metadata" in parsed
    assert "email_data" in parsed
    assert parsed["email_data"]["email"] == "Test email"


def test_create_filename():
    """Test filename generation."""
    manager = ExportManager()
    filename = manager.create_filename("email", "txt")
    
    assert filename.startswith("email_")
    assert filename.endswith(".txt")
    assert len(filename) > len("email_.txt")
    assert "_" in filename

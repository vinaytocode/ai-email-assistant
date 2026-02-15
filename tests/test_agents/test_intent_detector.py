"""Tests for IntentDetectorAgent."""

import pytest
from src.agents.intent_detector import IntentDetectorAgent


def test_intent_detector_process(mock_llm_wrapper, sample_state):
    """Test intent detector processes state correctly."""
    agent = IntentDetectorAgent(mock_llm_wrapper)
    result = agent.process(sample_state)
    
    assert "intent" in result
    assert result["intent"] == "Mocked LLM response"
    assert mock_llm_wrapper.call_llm.called


def test_intent_detector_with_empty_parsed_input(mock_llm_wrapper):
    """Test intent detector handles empty parsed input."""
    agent = IntentDetectorAgent(mock_llm_wrapper)
    state = {"raw_prompt": "Some email", "parsed_input": ""}
    
    result = agent.process(state)
    assert "intent" in result


def test_intent_detector_with_missing_parsed_input(mock_llm_wrapper):
    """Test intent detector handles missing parsed input."""
    agent = IntentDetectorAgent(mock_llm_wrapper)
    state = {"raw_prompt": "Some email"}
    
    result = agent.process(state)
    assert "intent" in result


def test_intent_detector_preserves_state(mock_llm_wrapper, sample_state):
    """Test intent detector preserves existing state data."""
    agent = IntentDetectorAgent(mock_llm_wrapper)
    original_keys = set(sample_state.keys())
    
    result = agent.process(sample_state)
    
    assert original_keys.issubset(set(result.keys()))
    assert "intent" in result

"""Tests for InputParserAgent."""

import pytest
from src.agents.input_parser import InputParserAgent


def test_input_parser_process(mock_llm_wrapper, sample_state):
    """Test input parser processes state correctly."""
    agent = InputParserAgent(mock_llm_wrapper)
    result = agent.process(sample_state)
    
    assert "parsed_input" in result
    assert result["parsed_input"] == "Mocked LLM response"
    assert mock_llm_wrapper.call_llm.called


def test_input_parser_with_empty_prompt(mock_llm_wrapper):
    """Test input parser handles empty prompt."""
    agent = InputParserAgent(mock_llm_wrapper)
    state = {"raw_prompt": ""}
    
    result = agent.process(state)
    assert "parsed_input" in result

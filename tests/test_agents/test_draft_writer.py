"""Tests for DraftWriterAgent."""

import pytest
from unittest.mock import Mock, patch
from src.agents.draft_writer import DraftWriterAgent


@pytest.fixture
def mock_llm():
    """Mock LLM instance."""
    return Mock()


@pytest.fixture
def draft_writer_agent(mock_llm):
    """Create draft writer agent with mocked LLM."""
    agent = DraftWriterAgent(mock_llm)
    return agent


class TestDraftWriterAgent:
    """Test suite for DraftWriterAgent."""
    
    def test_process_creates_draft(self, draft_writer_agent, mock_llm):
        """Test that process method generates a draft."""
        mock_llm.call_llm.return_value = "Dear recipient,\n\nEmail body here.\n\nBest regards"
        
        state = {
            "parsed_input": "Request for meeting",
            "intent": "Schedule a meeting",
            "tone_guidelines": "Professional and friendly",
            "context_history": "Previous email about project"
        }
        
        result = draft_writer_agent.process(state)
        
        assert "draft" in result
        assert result["draft"] == "Dear recipient,\n\nEmail body here.\n\nBest regards"
        mock_llm.call_llm.assert_called_once()
    
    def test_process_with_empty_context(self, draft_writer_agent, mock_llm):
        """Test process with empty context history."""
        mock_llm.call_llm.return_value = "Email draft"
        
        state = {
            "parsed_input": "Follow-up",
            "intent": "Check status",
            "tone_guidelines": "Formal",
            "context_history": ""
        }
        
        result = draft_writer_agent.process(state)
        
        assert result["draft"] == "Email draft"
    
    def test_process_with_none_context(self, draft_writer_agent, mock_llm):
        """Test process with None context history."""
        mock_llm.call_llm.return_value = "Email draft no context"
        
        state = {
            "parsed_input": "New inquiry",
            "intent": "Request",
            "tone_guidelines": "Professional",
            "context_history": None
        }
        
        result = draft_writer_agent.process(state)
        
        assert result["draft"] == "Email draft no context"
    
    def test_process_with_missing_optional_fields(self, draft_writer_agent, mock_llm):
        """Test process when optional fields are missing."""
        mock_llm.call_llm.return_value = "Generated draft"
        
        state = {
            "parsed_input": "New inquiry"
        }
        
        result = draft_writer_agent.process(state)
        
        assert "draft" in result
        mock_llm.call_llm.assert_called_once()
    
    def test_llm_called_with_correct_parameters(self, draft_writer_agent, mock_llm):
        """Test that LLM is called with correct system and user prompts."""
        mock_llm.call_llm.return_value = "Draft content"
        
        state = {
            "parsed_input": "Test purpose",
            "intent": "Test intent",
            "tone_guidelines": "Test tone",
            "context_history": "Test context"
        }
        
        draft_writer_agent.process(state)
        
        call_args = mock_llm.call_llm.call_args
        # system_prompt and user_prompt are positional args
        system_prompt = call_args[0][0]
        user_prompt = call_args[0][1]
        # temperature is passed as keyword arg
        assert call_args.kwargs["temperature"] == 0.7
        assert "expert email writer" in system_prompt.lower()
        assert "Test purpose" in user_prompt
        assert "Test context" in user_prompt
    
    def test_state_preservation(self, draft_writer_agent, mock_llm):
        """Test that existing state is preserved."""
        mock_llm.call_llm.return_value = "New draft"
        
        state = {
            "parsed_input": "Purpose",
            "intent": "Intent",
            "tone_guidelines": "Tone",
            "context_history": "Context",
            "existing_field": "Should be preserved"
        }
        
        result = draft_writer_agent.process(state)
        
        assert result["existing_field"] == "Should be preserved"
        assert result["draft"] == "New draft"

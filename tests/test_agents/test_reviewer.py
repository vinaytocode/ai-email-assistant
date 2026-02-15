"""Tests for ReviewerAgent with PASS/FAIL verdict routing."""

import pytest
from unittest.mock import Mock
from src.agents.reviewer import ReviewerAgent


@pytest.fixture
def mock_llm():
    """Mock LLM instance."""
    return Mock()


@pytest.fixture
def reviewer_agent(mock_llm):
    """Create reviewer agent with mocked LLM."""
    return ReviewerAgent(mock_llm)


@pytest.fixture
def review_state():
    """Sample state entering the reviewer."""
    return {
        "personalized_draft": "Subject: Test\n\nDear Professor,\n\nThank you.\n\nBest,\nJordan",
        "intent": "Gratitude",
        "tone": "professional",
        "retry_count": 0,
    }


class TestReviewerVerdict:
    """Test suite for PASS/FAIL verdict parsing."""

    def test_verdict_pass(self, reviewer_agent, mock_llm, review_state):
        """Test that VERDICT: PASS sets review_passed to True."""
        mock_llm.call_llm.return_value = (
            "The email is clear and professional.\n"
            "VERDICT: PASS"
        )
        
        result = reviewer_agent.process(review_state)
        
        assert result["review_passed"] is True
        assert "review_feedback" in result

    def test_verdict_fail(self, reviewer_agent, mock_llm, review_state):
        """Test that VERDICT: FAIL sets review_passed to False."""
        mock_llm.call_llm.return_value = (
            "The tone is too casual for a professional email.\n"
            "Missing subject line.\n"
            "VERDICT: FAIL"
        )
        
        result = reviewer_agent.process(review_state)
        
        assert result["review_passed"] is False

    def test_verdict_pass_case_insensitive(self, reviewer_agent, mock_llm, review_state):
        """Test verdict parsing is case insensitive."""
        mock_llm.call_llm.return_value = "Looks good.\nverdict: pass"
        
        result = reviewer_agent.process(review_state)
        
        assert result["review_passed"] is True

    def test_verdict_fail_case_insensitive(self, reviewer_agent, mock_llm, review_state):
        """Test FAIL verdict parsing is case insensitive."""
        mock_llm.call_llm.return_value = "Needs work.\nVerdict: Fail"
        
        result = reviewer_agent.process(review_state)
        
        assert result["review_passed"] is False

    def test_verdict_with_extra_whitespace(self, reviewer_agent, mock_llm, review_state):
        """Test verdict parsing handles extra whitespace."""
        mock_llm.call_llm.return_value = "Review text.\n  VERDICT:   PASS  \n"
        
        result = reviewer_agent.process(review_state)
        
        assert result["review_passed"] is True

    def test_no_verdict_defaults_to_pass(self, reviewer_agent, mock_llm, review_state):
        """Test that missing verdict defaults to PASS (fail-open)."""
        mock_llm.call_llm.return_value = "The email looks great. No issues found."
        
        result = reviewer_agent.process(review_state)
        
        assert result["review_passed"] is True

    def test_empty_response_defaults_to_pass(self, reviewer_agent, mock_llm, review_state):
        """Test that empty LLM response defaults to PASS."""
        mock_llm.call_llm.return_value = ""
        
        result = reviewer_agent.process(review_state)
        
        assert result["review_passed"] is True

    def test_malformed_verdict_defaults_to_pass(self, reviewer_agent, mock_llm, review_state):
        """Test that malformed verdict line defaults to PASS."""
        mock_llm.call_llm.return_value = "Review done.\nVERDICT: MAYBE"
        
        result = reviewer_agent.process(review_state)
        
        assert result["review_passed"] is True


class TestReviewerStateHandling:
    """Test suite for state preservation and updates."""

    def test_preserves_existing_state(self, reviewer_agent, mock_llm, review_state):
        """Test that existing state fields are preserved."""
        mock_llm.call_llm.return_value = "Good.\nVERDICT: PASS"
        review_state["existing_field"] = "should_survive"
        
        result = reviewer_agent.process(review_state)
        
        assert result["existing_field"] == "should_survive"

    def test_retry_count_passed_to_prompt(self, reviewer_agent, mock_llm, review_state):
        """Test that retry count is included in the LLM prompt."""
        mock_llm.call_llm.return_value = "Good.\nVERDICT: PASS"
        review_state["retry_count"] = 2
        
        reviewer_agent.process(review_state)
        
        call_args = mock_llm.call_llm.call_args
        user_prompt = call_args[0][1]
        assert "Retry attempt: 2" in user_prompt

    def test_missing_retry_count_defaults_zero(self, reviewer_agent, mock_llm):
        """Test handling when retry_count is missing from state."""
        mock_llm.call_llm.return_value = "Good.\nVERDICT: PASS"
        state = {
            "personalized_draft": "Some draft",
            "intent": "Request",
            "tone": "formal",
        }
        
        result = reviewer_agent.process(state)
        
        assert result["review_passed"] is True

    def test_missing_optional_fields(self, reviewer_agent, mock_llm):
        """Test handling when optional state fields are missing."""
        mock_llm.call_llm.return_value = "Acceptable.\nVERDICT: PASS"
        state = {}
        
        result = reviewer_agent.process(state)
        
        assert "review_feedback" in result
        assert "review_passed" in result

    def test_llm_called_with_review_criteria(self, reviewer_agent, mock_llm, review_state):
        """Test that system prompt includes review criteria."""
        mock_llm.call_llm.return_value = "Good.\nVERDICT: PASS"
        
        reviewer_agent.process(review_state)
        
        call_args = mock_llm.call_llm.call_args
        system_prompt = call_args[0][0]
        assert "clarity" in system_prompt.lower()
        assert "tone" in system_prompt.lower()
        assert "grammar" in system_prompt.lower()
        assert "VERDICT: PASS" in system_prompt
        assert "VERDICT: FAIL" in system_prompt

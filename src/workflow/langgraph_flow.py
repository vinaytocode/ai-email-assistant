"""LangGraph workflow orchestration for email generation.

Implements a conditional routing pattern where the ReviewerAgent's
verdict determines whether the draft proceeds to finalization or
loops back to the DraftWriter for a retry.

Flow:
    Input → Intent → Tone → Draft → Personalize → Review → Router
        ├── PASS → Finalize → END
        └── FAIL → Draft Writer (retry, max 2 attempts)
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..core.state_models import EmailState
from ..agents import (
    InputParserAgent,
    IntentDetectorAgent,
    ToneStylistAgent,
    DraftWriterAgent,
    PersonalizerAgent,
    ReviewerAgent,
    FinalizerAgent,
)
from ..integrations.llm_wrapper import LLMWrapper
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Maximum number of retry attempts before forcing finalization
MAX_RETRIES = 2


def review_router(state: Dict[str, Any]) -> str:
    """Route based on review verdict and retry count.
    
    Decision logic:
        - If review passed → proceed to finalize
        - If review failed AND retries remaining → loop back to draft writer
        - If review failed AND max retries reached → proceed to finalize anyway
    
    Args:
        state: Current workflow state containing review_passed and retry_count
        
    Returns:
        str: Next node name - either "finalize" or "write_draft"
    """
    review_passed = state.get("review_passed", True)
    retry_count = state.get("retry_count", 0)
    
    if review_passed:
        logger.info("Router: PASS - proceeding to finalize")
        return "finalize"
    
    if retry_count >= MAX_RETRIES:
        logger.warning(
            f"Router: FAIL but max retries ({MAX_RETRIES}) reached "
            f"- forcing finalization"
        )
        return "finalize"
    
    logger.info(
        f"Router: FAIL - routing back to draft writer "
        f"(retry {retry_count + 1}/{MAX_RETRIES})"
    )
    return "write_draft"


def increment_retry(state: Dict[str, Any]) -> Dict[str, Any]:
    """Increment retry counter when looping back through the pipeline.
    
    This node sits between the router's FAIL path and write_draft,
    ensuring the retry count is updated before the next draft attempt.
    """
    state["retry_count"] = state.get("retry_count", 0) + 1
    logger.info(f"Retry counter incremented to {state['retry_count']}")
    return state


class EmailWorkflow:
    """LangGraph-based email generation workflow with conditional routing.
    
    The workflow implements a review-based quality gate:
    1. Sequential pipeline: parse → detect → tone → draft → personalize → review
    2. Conditional routing: review verdict determines next step
       - PASS: proceed to finalize
       - FAIL: loop back to draft writer (up to MAX_RETRIES times)
    3. Finalization: produce polished output and metadata
    """
    
    def __init__(self):
        self.llm_wrapper = LLMWrapper()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow with conditional routing."""
        logger.info("Building LangGraph workflow with review routing")
        
        # Initialize agents
        input_parser = InputParserAgent(self.llm_wrapper)
        intent_detector = IntentDetectorAgent(self.llm_wrapper)
        tone_stylist = ToneStylistAgent(self.llm_wrapper)
        draft_writer = DraftWriterAgent(self.llm_wrapper)
        personalizer = PersonalizerAgent(self.llm_wrapper)
        reviewer = ReviewerAgent(self.llm_wrapper)
        finalizer = FinalizerAgent(self.llm_wrapper)
        
        # Create workflow graph
        workflow = StateGraph(EmailState)
        
        # Add nodes
        workflow.add_node("parse_input", input_parser.process)
        workflow.add_node("detect_intent", intent_detector.process)
        workflow.add_node("define_tone", tone_stylist.process)
        workflow.add_node("write_draft", draft_writer.process)
        workflow.add_node("personalize", personalizer.process)
        workflow.add_node("review", reviewer.process)
        workflow.add_node("increment_retry", increment_retry)
        workflow.add_node("finalize", finalizer.process)
        
        # Define edges - sequential up to review
        workflow.set_entry_point("parse_input")
        workflow.add_edge("parse_input", "detect_intent")
        workflow.add_edge("detect_intent", "define_tone")
        workflow.add_edge("define_tone", "write_draft")
        workflow.add_edge("write_draft", "personalize")
        workflow.add_edge("personalize", "review")
        
        # Conditional routing after review
        workflow.add_conditional_edges(
            "review",
            review_router,
            {
                "finalize": "finalize",
                "write_draft": "increment_retry",
            }
        )
        
        # Retry path: increment counter then back to draft
        workflow.add_edge("increment_retry", "write_draft")
        
        # Finalize terminates the graph
        workflow.add_edge("finalize", END)
        
        logger.info("LangGraph workflow with review routing built successfully")
        return workflow.compile()
    
    def generate_email(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the email generation workflow.
        
        Args:
            state: Initial email state with raw_prompt, tone, user_type, etc.
            
        Returns:
            Dict containing final_email, generation_metadata, and all
            intermediate state from the agent pipeline.
        """
        logger.info("Starting email generation workflow")
        
        # Initialize retry counter if not present
        if "retry_count" not in state or state["retry_count"] is None:
            state["retry_count"] = 0
        
        try:
            result = self.graph.invoke(state)
            
            retries_used = result.get("retry_count", 0)
            review_passed = result.get("review_passed", True)
            logger.info(
                f"Email generation completed - "
                f"Review: {'PASS' if review_passed else 'FAIL (forced)'}, "
                f"Retries used: {retries_used}"
            )
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}")
            raise

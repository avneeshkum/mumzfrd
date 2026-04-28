from typing import TypedDict, List, Dict, Any, Optional


class MumzfrdState(TypedDict):
    """
    Central state object passed through all LangGraph nodes.
    Every node reads from and writes to this state.
    """
    user_input: str                        # Raw user message
    mode: str                              # "shopping" | "planner" | "unknown"
    language: str                          # "en" | "ar" | "both"
    context: Dict[str, Any]               # Extracted structured context
    products: List[Dict[str, Any]]        # Retrieved/filtered products
    analysis: Dict[str, Any]             # Reviews, pros/cons analysis
    timeline: List[Dict[str, Any]]       # Pregnancy week-by-week timeline
    response_en: str                      # English response
    response_ar: str                      # Arabic response
    confidence: float                     # 0.0 - 1.0 confidence score
    error: Optional[str]                  # Error message if something fails
    retry_count: int                      # For evaluator loop
    eval_passed: bool                     # Did evaluator approve output


def initial_state(user_input: str) -> MumzfrdState:
    """Create a fresh state from user input."""
    return MumzfrdState(
        user_input=user_input,
        mode="unknown",
        language="both",
        context={},
        products=[],
        analysis={},
        timeline=[],
        response_en="",
        response_ar="",
        confidence=0.0,
        error=None,
        retry_count=0,
        eval_passed=False,
    )

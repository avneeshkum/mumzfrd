"""
Shopping Subgraph
Flow: intent → context → retrieve → review → recommend → response → evaluator
"""

from langgraph.graph import StateGraph, END
from state import MumzfrdState
from nodes.shopping_nodes import (
    intent_node,
    context_node,
    retrieve_node,
    review_node,
    recommend_node,
    shopping_response_node,
)
from nodes.evaluator_node import evaluator_node


def should_retry(state: MumzfrdState) -> str:
    """Conditional edge: retry recommend+response or end."""
    if not state.get("eval_passed", False) and state.get("retry_count", 0) < 2:
        return "retry"
    return "end"


def build_shopping_graph():
    builder = StateGraph(MumzfrdState)

    # Add nodes
    builder.add_node("intent", intent_node)
    builder.add_node("context", context_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("review", review_node)
    builder.add_node("recommend", recommend_node)
    builder.add_node("response", shopping_response_node)
    builder.add_node("evaluator", evaluator_node)

    # Linear flow
    builder.set_entry_point("intent")
    builder.add_edge("intent", "context")
    builder.add_edge("context", "retrieve")
    builder.add_edge("retrieve", "review")
    builder.add_edge("review", "recommend")
    builder.add_edge("recommend", "response")
    builder.add_edge("response", "evaluator")

    # Evaluator loop — retry from recommend if quality fails
    builder.add_conditional_edges(
        "evaluator",
        should_retry,
        {
            "retry": "recommend",   # retry just the recommend+response cycle
            "end": END,
        },
    )

    return builder.compile()


shopping_graph = build_shopping_graph()

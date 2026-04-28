"""
Planner Subgraph
Flow: context → timeline → planning → product → response → evaluator
"""

from langgraph.graph import StateGraph, END
from state import MumzfrdState
from nodes.planner_nodes import (
    planner_context_node,
    timeline_node,
    planning_node,
    product_node,
    planner_response_node,
)
from nodes.evaluator_node import evaluator_node


def should_retry(state: MumzfrdState) -> str:
    if not state.get("eval_passed", False) and state.get("retry_count", 0) < 2:
        return "retry"
    return "end"


def build_planner_graph():
    builder = StateGraph(MumzfrdState)

    builder.add_node("context", planner_context_node)
    builder.add_node("timeline", timeline_node)
    builder.add_node("planning", planning_node)
    builder.add_node("product", product_node)
    builder.add_node("response", planner_response_node)
    builder.add_node("evaluator", evaluator_node)

    builder.set_entry_point("context")
    builder.add_edge("context", "timeline")
    builder.add_edge("timeline", "planning")
    builder.add_edge("planning", "product")
    builder.add_edge("product", "response")
    builder.add_edge("response", "evaluator")

    builder.add_conditional_edges(
        "evaluator",
        should_retry,
        {
            "retry": "response",  # retry just the response generation
            "end": END,
        },
    )

    return builder.compile()


planner_graph = build_planner_graph()

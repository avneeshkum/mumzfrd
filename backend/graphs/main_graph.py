"""
Main Router Graph
Detects mode (shopping / planner / unknown) and routes to the right subgraph.
"""

from langgraph.graph import StateGraph, END
from state import MumzfrdState, initial_state
from llm import call_llm_json
from graphs.shopping_graph import shopping_graph
from graphs.planner_graph import planner_graph


# ─────────────────────────────────────────────
# Mode Detection Node
# ─────────────────────────────────────────────
async def detect_mode(state: MumzfrdState) -> MumzfrdState:
    """
    Classifies user input into:
    - shopping: product search, gift finding, comparison
    - planner: pregnancy timeline, due date, week-by-week plan
    - unknown: out of scope
    """
    result = await call_llm_json(
        system="""You classify messages for Mumzworld, a baby/mom e-commerce platform in the Middle East.

Classify the user message into exactly one mode:
- "shopping": Looking for a product, gift, recommendation, comparison, or asking about specific items
- "planner": Asking about pregnancy timeline, due date planning, week-by-week advice, or what to prepare when
- "unknown": Completely out of scope (not related to babies, pregnancy, or moms)

Return JSON:
{
  "mode": "shopping" | "planner" | "unknown",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence"
}""",
        prompt=f"User message: {state['user_input']}",
    )

    if "error" in result:
        mode = "unknown"
        confidence = 0.0
    else:
        mode = result.get("mode", "unknown")
        confidence = result.get("confidence", 0.5)

    return {**state, "mode": mode, "confidence": confidence}


# ─────────────────────────────────────────────
# Unknown Mode Handler
# ─────────────────────────────────────────────
async def handle_unknown(state: MumzfrdState) -> MumzfrdState:
    return {
        **state,
        "response_en": (
            "I'm Mumzfrd, your AI assistant for baby products and pregnancy planning on Mumzworld. "
            "I can help you find products, compare items, or plan your pregnancy journey. "
            "Could you tell me what you're looking for?"
        ),
        "response_ar": (
            "أنا مُمزفرد، مساعدك الذكي لمنتجات الأطفال والتخطيط للحمل على مُمزوورلد. "
            "يمكنني مساعدتك في إيجاد المنتجات، ومقارنة العناصر، أو التخطيط لرحلة حملك. "
            "هل يمكنك إخباري بما تبحثين عنه؟"
        ),
        "eval_passed": True,
    }


# ─────────────────────────────────────────────
# Routing Logic
# ─────────────────────────────────────────────
def route_to_mode(state: MumzfrdState) -> str:
    mode = state.get("mode", "unknown")
    if mode == "shopping":
        return "shopping"
    elif mode == "planner":
        return "planner"
    else:
        return "unknown"


# ─────────────────────────────────────────────
# Subgraph Wrapper Nodes
# ─────────────────────────────────────────────
async def run_shopping(state: MumzfrdState) -> MumzfrdState:
    result = await shopping_graph.ainvoke(state)
    return result


async def run_planner(state: MumzfrdState) -> MumzfrdState:
    result = await planner_graph.ainvoke(state)
    return result


# ─────────────────────────────────────────────
# Build Main Graph
# ─────────────────────────────────────────────
def build_main_graph():
    builder = StateGraph(MumzfrdState)

    builder.add_node("detect_mode", detect_mode)
    builder.add_node("shopping", run_shopping)
    builder.add_node("planner", run_planner)
    builder.add_node("unknown", handle_unknown)

    builder.set_entry_point("detect_mode")

    builder.add_conditional_edges(
        "detect_mode",
        route_to_mode,
        {
            "shopping": "shopping",
            "planner": "planner",
            "unknown": "unknown",
        },
    )

    builder.add_edge("shopping", END)
    builder.add_edge("planner", END)
    builder.add_edge("unknown", END)

    return builder.compile()


main_graph = build_main_graph()


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────
async def run_mumzfrd(user_input: str) -> MumzfrdState:
    """Main entry point. Returns final state."""
    state = initial_state(user_input)
    result = await main_graph.ainvoke(state)
    return result

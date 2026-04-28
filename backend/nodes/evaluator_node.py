"""
Evaluator Node — checks response quality and triggers retry if needed.
This implements the bonus evaluator loop from the architecture.
"""

from state import MumzfrdState
from llm import call_llm_json


MAX_RETRIES = 2


async def evaluator_node(state: MumzfrdState) -> MumzfrdState:
    """
    Evaluates the generated response.
    If quality is too low and retries remain, marks eval_passed=False.
    Otherwise marks eval_passed=True (even if imperfect).
    """
    response_en = state.get("response_en", "")
    response_ar = state.get("response_ar", "")
    mode = state.get("mode", "unknown")
    retry_count = state.get("retry_count", 0)

    # Hard failure: empty response
    if not response_en or len(response_en) < 50:
        if retry_count < MAX_RETRIES:
            return {**state, "eval_passed": False, "retry_count": retry_count + 1}
        else:
            return {
                **state,
                "eval_passed": True,
                "response_en": state.get("response_en") or "I couldn't generate a proper response. Please try rephrasing your question.",
                "response_ar": state.get("response_ar") or "لم أتمكن من إنشاء رد مناسب. يرجى إعادة صياغة سؤالك.",
            }

    # LLM-based quality check
    result = await call_llm_json(
        system="""You are a quality evaluator for an AI assistant for moms.
Evaluate the response on these criteria and return JSON:
{
  "is_grounded": true/false,        // Response is based on actual input, not hallucinated
  "has_arabic": true/false,         // Arabic section present and non-empty
  "arabic_natural": true/false,     // Arabic reads naturally (not word-for-word translation)
  "handles_uncertainty": true/false,// Model says "I don't know" when appropriate
  "no_empty_fields": true/false,    // No placeholder or empty answers
  "overall_pass": true/false,
  "fail_reason": "string or null"
}""",
        prompt=f"""Mode: {mode}
User input: {state['user_input']}
Response EN: {response_en[:500]}
Response AR: {response_ar[:300]}
Products found: {len(state.get('products', []))}
Confidence: {state.get('confidence', 0)}""",
    )

    if "error" in result:
        # Evaluator itself failed — pass through
        return {**state, "eval_passed": True}

    overall_pass = result.get("overall_pass", True)

    if not overall_pass and retry_count < MAX_RETRIES:
        return {
            **state,
            "eval_passed": False,
            "retry_count": retry_count + 1,
            "analysis": {
                **state.get("analysis", {}),
                "eval_fail_reason": result.get("fail_reason"),
            },
        }

    return {**state, "eval_passed": True}

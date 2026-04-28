"""
Shopping Graph Nodes
Flow: intent → context → retrieve → review → recommend → response
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List
from state import MumzfrdState
from llm import call_llm_json, call_llm

BASE_DIR = Path(__file__).resolve().parent.parent

_PRODUCTS_PATH = BASE_DIR / "data" / "products.json"
_ALL_PRODUCTS: List[Dict[str, Any]] = json.loads(
    _PRODUCTS_PATH.read_text(encoding="utf-8")
)

# ─────────────────────────────────────────────
# NODE 1: Intent Node
# ─────────────────────────────────────────────
async def intent_node(state: MumzfrdState) -> MumzfrdState:
    result = await call_llm_json(
        system="""You are a shopping intent extractor for Mumzworld, a baby/mom e-commerce platform in the Middle East.
Extract the shopping intent from the user message.

Return JSON with these exact fields:
{
  "product_type": "string or null",
  "recipient": "string or null",
  "occasion": "string or null",
  "is_gift": true/false,
  "keywords": ["array", "of", "keywords"],
  "confidence": 0.0 to 1.0
}

If the message is not a shopping query, set confidence to 0.0.""",
        prompt=f"User message: {state['user_input']}",
    )

    if "error" in result or result.get("confidence", 0) < 0.3:
        return {**state, "error": "Could not understand shopping intent.", "confidence": 0.0}

    return {**state, "context": {**state["context"], "intent": result}, "confidence": result.get("confidence", 0.7)}


# ─────────────────────────────────────────────
# NODE 2: Context Node
# ─────────────────────────────────────────────
async def context_node(state: MumzfrdState) -> MumzfrdState:
    result = await call_llm_json(
        system="""You extract shopping context from a user message for a baby products store in the Middle East.
Prices are in AED (UAE Dirhams) or SAR (Saudi Riyals). Convert SAR to AED by multiplying by 1.02.

Return JSON:
{
  "budget_aed": number or null,
  "child_age_months": number or null,
  "pregnancy_trimester": number or null,
  "language_preference": "en" or "ar" or "both",
  "special_requirements": ["list of special needs or preferences"]
}""",
        prompt=f"User message: {state['user_input']}",
    )

    if "error" in result:
        result = {
            "budget_aed": None,
            "child_age_months": None,
            "pregnancy_trimester": None,
            "language_preference": "both",
            "special_requirements": [],
        }

    lang = result.get("language_preference", "both")
    return {
        **state,
        "context": {**state["context"], "shopping_context": result},
        "language": lang,
    }


# ─────────────────────────────────────────────
# NODE 3: Retrieve Node  ← FIX 1 + FIX 2 HERE
# ─────────────────────────────────────────────
async def retrieve_node(state: MumzfrdState) -> MumzfrdState:
    ctx = state["context"]
    intent = ctx.get("intent", {})
    shopping = ctx.get("shopping_context", {})

    budget = shopping.get("budget_aed")
    child_age = shopping.get("child_age_months")
    keywords = [k.lower() for k in intent.get("keywords", [])]
    product_type = (intent.get("product_type") or "").lower().strip()
    is_gift = intent.get("is_gift", False)

    # Category synonyms — maps user words to catalog categories/subcategories
    CATEGORY_MAP = {
        "stroller":   ["strollers", "pushchair", "lightweight", "travel_system"],
        "pram":       ["strollers", "pushchair"],
        "carrier":    ["carriers"],
        "bottle":     ["bottles", "feeding"],
        "pump":       ["breast_pump"],
        "monitor":    ["monitors"],
        "bouncer":    ["bouncers"],
        "bassinet":   ["bassinet", "sleep"],
        "crib":       ["co_sleeping", "sleep"],
        "diaper":     ["diapering"],
        "nappy":      ["diapering"],
        "wipes":      ["wipes", "diapering"],
        "gym":        ["play_gym", "toys"],
        "walker":     ["walker", "toys"],
        "swaddle":    ["swaddle", "bedding"],
        "pillow":     ["nursing"],
        "skincare":   ["skincare", "maternity"],
        "postpartum": ["postpartum", "maternity"],
    }

    def _category_match(p: dict, ptype: str) -> bool:
        """True if product matches the requested category."""
        if not ptype:
            return True  # no category filter → match all
        synonyms = CATEGORY_MAP.get(ptype, [ptype])
        return any(
            s in p["category"] or s in p["subcategory"]
            for s in synonyms
        )

    candidates = []
    for p in _ALL_PRODUCTS:

        # ── HARD FILTER 1: out of stock ──────────────────────────────
        if not p.get("in_stock", True):
            continue

        # ── HARD FILTER 2: budget ────────────────────────────────────
        if budget and p["price_aed"] > budget:
            continue

        # ── HARD FILTER 3: category must match when specified ────────
        # If the user asked for a stroller, wipes should never appear.
        if product_type and not _category_match(p, product_type):
            continue

        # ── HARD FILTER 4: age — skip if child is clearly too old ────
        # e.g. swaddle (0-6m) should NOT appear for a 6-month-old
        if child_age is not None and child_age > p["age_max_months"]:
            continue

        # ── SCORING (soft, for ranking among survivors) ──────────────
        score = 0.0

        # Age fit bonus
        if child_age is not None and p["age_min_months"] <= child_age <= p["age_max_months"]:
            score += 3
        elif child_age is not None and abs(p["age_min_months"] - child_age) <= 2:
            score += 1  # close enough

        # Keyword match
        product_text = (p["name"] + " " + " ".join(p["tags"])).lower()
        for kw in keywords:
            if kw in product_text:
                score += 2

        # Gift tag
        if is_gift and "gift" in p["tags"]:
            score += 2

        # Rating quality signal
        score += p["rating"] - 4.0

        # Only add if at least one signal fired
        if score > 0 or not product_type:
            candidates.append({**p, "_score": score})

    # Sort best first, take top 5
    candidates.sort(key=lambda x: x["_score"], reverse=True)
    top = candidates[:5]

    # Fallback: nothing survived hard filters → return honest empty signal
    # (recommend_node will handle the "nothing found" message)
    if not top and not product_type:
        top = sorted(
            [p for p in _ALL_PRODUCTS if p.get("in_stock", True)],
            key=lambda x: x["rating"],
            reverse=True,
        )[:3]

    return {**state, "products": top}


# ─────────────────────────────────────────────
# NODE 4: Review Node
# ─────────────────────────────────────────────
async def review_node(state: MumzfrdState) -> MumzfrdState:
    if not state["products"]:
        return {**state, "analysis": {"summary": "No products found to analyze."}}

    products_summary = [
        {
            "id": p["id"],
            "name": p["name"],
            "price_aed": p["price_aed"],
            "rating": p["rating"],
            "reviews_count": p["reviews_count"],
            "pros": p["pros"],
            "cons": p["cons"],
        }
        for p in state["products"]
    ]

    result = await call_llm_json(
        system="""You are a product analyst for Mumzworld, a baby products platform.
Analyze the given products and return structured insights.

Return JSON:
{
  "products_analysis": [
    {
      "id": "product id",
      "key_strengths": ["top 2-3 strengths"],
      "key_weaknesses": ["top 1-2 weaknesses"],
      "best_for": "one sentence on who this is best for",
      "value_score": 1-10
    }
  ],
  "overall_insight": "2-3 sentences comparing all products"
}""",
        prompt=f"User need: {state['user_input']}\n\nProducts:\n{json.dumps(products_summary, ensure_ascii=False)}",
    )

    if "error" in result:
        result = {"products_analysis": [], "overall_insight": "Analysis unavailable."}

    return {**state, "analysis": result}


# ─────────────────────────────────────────────
# NODE 5: Recommend Node
# ─────────────────────────────────────────────
async def recommend_node(state: MumzfrdState) -> MumzfrdState:
    if not state["products"]:
        return {**state, "analysis": {**state["analysis"], "recommendation": None}}

    context = state["context"]
    analysis = state["analysis"]

    result = await call_llm_json(
        system="""You are a trusted shopping advisor for moms in the Middle East.
Given the products and analysis, pick the single best recommendation.
Be honest — if no product perfectly fits, say so and explain the closest match.

Return JSON:
{
  "recommended_id": "product id or null",
  "reasoning_en": "2-3 sentence explanation in English why this is the best choice",
  "reasoning_ar": "نفس الشرح باللغة العربية - يجب أن يكون طبيعياً وليس ترجمة حرفية",
  "runner_up_id": "second best product id or null",
  "confidence": 0.0 to 1.0,
  "caveat": "any important caveat or null"
}

If there are no good matches, set recommended_id to null and explain honestly.""",
        prompt=f"""User asked: {state['user_input']}

Context: {json.dumps(context, ensure_ascii=False)}

Analysis: {json.dumps(analysis, ensure_ascii=False)}

Available products: {json.dumps([{"id": p["id"], "name": p["name"], "price_aed": p["price_aed"]} for p in state["products"]], ensure_ascii=False)}""",
    )

    if "error" in result:
        result = {
            "recommended_id": None,
            "reasoning_en": "Could not determine recommendation.",
            "reasoning_ar": "تعذر تحديد التوصية.",
            "confidence": 0.0,
        }

    return {
        **state,
        "analysis": {**state["analysis"], "recommendation": result},
        "confidence": result.get("confidence", 0.5),
    }


# ─────────────────────────────────────────────
# NODE 6: Response Node
# ─────────────────────────────────────────────
async def shopping_response_node(state: MumzfrdState) -> MumzfrdState:
    recommendation = state["analysis"].get("recommendation", {})
    rec_id = recommendation.get("recommended_id")
    runner_up_id = recommendation.get("runner_up_id")
    user_query = (state.get("user_input") or "").lower()

    # Safety override for medical queries
    emergency_terms = ["high fever", "seizure", "seizures", "medicine dosage", "dosage", "dose"]
    if any(term in user_query for term in emergency_terms):
        return {
            **state,
            "response_en": (
                "This sounds like a medical emergency. "
                "I cannot provide medicine dosage for a baby. "
                "Please contact a doctor or go to the nearest hospital immediately."
            ),
            "response_ar": (
                "هذه حالة طبية طارئة. "
                "لا أستطيع تقديم جرعة دواء لطفل. "
                "يرجى التواصل مع الطبيب أو الذهاب إلى أقرب مستشفى فوراً."
            ),
        }

    rec_product = next((p for p in state["products"] if p["id"] == rec_id), None)
    runner_up   = next((p for p in state["products"] if p["id"] == runner_up_id), None)

    # Nothing found after hard filters
    if not state["products"]:
        return {
            **state,
            "response_en": "I couldn't find products matching your request in our catalog. Try adjusting your budget or describing what you need differently.",
            "response_ar": "لم أتمكن من إيجاد منتجات تناسب طلبك في كتالوجنا. جربي تعديل الميزانية أو وصف ما تحتاجينه بطريقة مختلفة.",
        }

    response_data = {
        "recommended": rec_product,
        "runner_up": runner_up,
        "reasoning": recommendation,
        "user_query": state["user_input"],
        "all_options": [
            {"id": p["id"], "name": p["name"], "price_aed": p["price_aed"], "rating": p["rating"]}
            for p in state["products"]
        ],
    }

    response_text = await call_llm(
        system="""You are Mumzfrd, a friendly AI shopping assistant for moms on Mumzworld.

Rules:
- Do NOT introduce yourself repeatedly.
- If the user is asking for real-time sales, "best-selling", rankings, or other data not present in the provided input, do NOT guess. Say clearly you do not have that information.
- Keep the response short, clean, and easy to scan.
- Avoid long paragraphs and filler.
- Give a direct answer first, then 1-2 alternatives, then one short tip if useful.
- If the query is out of scope or unsupported, say so honestly.

Write in English first, then provide the FULL response again in Arabic.
Separate the two with exactly: ---AR---
The Arabic must read naturally, not like a translation.""",
        prompt=f"Shopping data: {json.dumps(response_data, ensure_ascii=False, default=str)}",
        temperature=0.4,
    )

    parts = response_text.split("---AR---")
    response_en = parts[0].strip() if parts else response_text
    response_ar = parts[1].strip() if len(parts) > 1 else ""

    return {**state, "response_en": response_en, "response_ar": response_ar}
"""
Planner Graph Nodes
Flow: context → timeline → planning → product → response
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List
from pathlib import Path

from state import MumzfrdState
from llm import call_llm_json, call_llm

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

_PRODUCTS_PATH = BASE_DIR / "data" / "products.json"
_ALL_PRODUCTS: List[Dict[str, Any]] = json.loads(
    _PRODUCTS_PATH.read_text(encoding="utf-8")
)
# ─────────────────────────────────────────────
# NODE 1: Context Node
# Extracts due date and pregnancy info
# ─────────────────────────────────────────────
async def planner_context_node(state: MumzfrdState) -> MumzfrdState:
    result = await call_llm_json(
        system="""You extract pregnancy information from a user message.
Today's date is """ + datetime.now().strftime("%Y-%m-%d") + """.

Return JSON:
{
  "due_date": "YYYY-MM-DD or null",
  "current_week": number or null,         // pregnancy week (1-40)
  "first_time_mom": true/false/null,
  "location": "city or country or null",
  "concerns": ["list of concerns mentioned"],
  "confidence": 0.0 to 1.0
}

Calculate current_week from due_date if given (40 weeks total, count back from due date).
If user says "I'm X weeks pregnant", use that directly.""",
        prompt=f"User message: {state['user_input']}",
    )

    if "error" in result or result.get("confidence", 0) < 0.3:
        return {
            **state,
            "error": "I couldn't find a due date or pregnancy week in your message. Could you share your due date or how many weeks along you are?",
            "confidence": 0.0,
        }

    # Validate/calculate due date
    due_date_str = result.get("due_date")
    current_week = result.get("current_week")

    if due_date_str and not current_week:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            days_left = (due_date - datetime.now()).days
            weeks_left = max(0, days_left // 7)
            current_week = max(1, 40 - weeks_left)
            result["current_week"] = current_week
        except ValueError:
            pass

    return {
        **state,
        "context": {**state["context"], "pregnancy": result},
        "confidence": result.get("confidence", 0.8),
    }


# ─────────────────────────────────────────────
# NODE 2: Timeline Node
# Generates week-by-week pregnancy timeline
# ─────────────────────────────────────────────
async def timeline_node(state: MumzfrdState) -> MumzfrdState:
    pregnancy = state["context"].get("pregnancy", {})
    current_week = pregnancy.get("current_week", 12)
    due_date = pregnancy.get("due_date", "Unknown")

    # Generate timeline from current week to week 40 + 4 weeks postpartum
    result = await call_llm_json(
        system="""You are a pregnancy and postpartum planning expert for moms in the Middle East (UAE/Saudi Arabia).
Generate a week-by-week timeline. Be practical and medically accurate.

Return JSON:
{
  "timeline": [
    {
      "week": number,
      "phase": "first_trimester" | "second_trimester" | "third_trimester" | "postpartum",
      "title_en": "short title",
      "title_ar": "عنوان قصير",
      "body_changes_en": "1-2 sentences",
      "baby_development_en": "1-2 sentences",
      "key_actions": ["list of 2-3 actions for this week"],
      "key_actions_ar": ["قائمة بالإجراءات باللغة العربية"],
      "medical_checkup": true/false,
      "shopping_priority": "high" | "medium" | "low" | "none"
    }
  ]
}

Generate weeks from """ + str(current_week) + """ through 40, then weeks 41-44 as postpartum weeks 1-4.
Keep each week concise.""",
        prompt=f"Current week: {current_week}, Due date: {due_date}",
        temperature=0.3,
    )

    timeline = result.get("timeline", []) if "error" not in result else []

    return {**state, "timeline": timeline}


# ─────────────────────────────────────────────
# NODE 3: Planning Node
# Generates actionable items per trimester
# ─────────────────────────────────────────────
async def planning_node(state: MumzfrdState) -> MumzfrdState:
    pregnancy = state["context"].get("pregnancy", {})
    current_week = pregnancy.get("current_week", 12)
    timeline = state["timeline"]

    result = await call_llm_json(
        system="""You create practical pregnancy preparation plans for moms in the Middle East.
Focus on what to DO, not just what to know.

Return JSON:
{
  "immediate_actions": [              // Next 2 weeks
    {"action": "...", "action_ar": "...", "category": "health|shopping|admin|prep", "urgency": "now|soon|when_ready"}
  ],
  "trimester_checklist": {
    "current": ["checklist items for current trimester"],
    "current_ar": ["قائمة المهام للثلاثي الحالي"],
    "upcoming": ["next trimester preview"],
    "upcoming_ar": ["معاينة الثلاثي القادم"]
  },
  "hospital_bag": {                   // Only if week >= 32
    "for_mom": ["items"],
    "for_baby": ["items"],
    "for_partner": ["items"]
  } or null,
  "birth_plan_reminder": true/false
}""",
        prompt=f"Week: {current_week}. First-time mom: {pregnancy.get('first_time_mom')}. Concerns: {pregnancy.get('concerns', [])}",
    )

    if "error" in result:
        result = {"immediate_actions": [], "trimester_checklist": {"current": [], "upcoming": []}}

    return {**state, "analysis": {**state["analysis"], "planning": result}}


# ─────────────────────────────────────────────
# NODE 4: Product Node
# Suggests relevant products per trimester/week
# ─────────────────────────────────────────────
async def product_node(state: MumzfrdState) -> MumzfrdState:
    pregnancy = state["context"].get("pregnancy", {})
    current_week = pregnancy.get("current_week", 12)

    # Determine trimester
    if current_week <= 13:
        trimester = 1
    elif current_week <= 26:
        trimester = 2
    else:
        trimester = 3

    # Filter products relevant to this trimester
    relevant = [
        p for p in _ALL_PRODUCTS
        if trimester in p.get("trimester_relevance", []) and p.get("in_stock", True)
    ]

    # Score by week — things needed sooner get higher priority
    if current_week >= 32:
        # Late pregnancy: prioritize newborn essentials
        priority_tags = ["newborn", "essential", "sleep", "feeding"]
    elif current_week >= 20:
        # Mid pregnancy: think ahead
        priority_tags = ["stroller", "sleep", "feeding", "gift"]
    else:
        # Early pregnancy: mom comfort first
        priority_tags = ["pregnancy", "mom", "skincare", "comfort"]

    for p in relevant:
        p["_score"] = sum(2 for tag in priority_tags if tag in p.get("tags", []))
        p["_score"] += p["rating"] - 4.0

    relevant.sort(key=lambda x: x["_score"], reverse=True)
    top_products = relevant[:6]

    return {**state, "products": top_products}


# ─────────────────────────────────────────────
# NODE 5: Response Node
# Formats bilingual planner response
# ─────────────────────────────────────────────
async def planner_response_node(state: MumzfrdState) -> MumzfrdState:
    pregnancy = state["context"].get("pregnancy", {})
    planning = state["analysis"].get("planning", {})
    timeline_snippet = state["timeline"][:4] if state["timeline"] else []
    products = state["products"][:4]
    user_query = (state.get("user_input") or "").lower()

    # Safety override for emergency / dosage-like queries
    emergency_terms = [
        "high fever",
        "seizure",
        "seizures",
        "medicine dosage",
        "dosage",
        "dose",
        "baby fever",
    ]
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

    response_data = {
        "current_week": pregnancy.get("current_week"),
        "due_date": pregnancy.get("due_date"),
        "immediate_actions": planning.get("immediate_actions", []),
        "trimester_checklist": planning.get("trimester_checklist", {}),
        "hospital_bag": planning.get("hospital_bag"),
        "upcoming_weeks": timeline_snippet,
        "recommended_products": [
            {
                "name": p["name"],
                "name_ar": p.get("name_ar"),
                "price_aed": p["price_aed"],
                "category": p["category"],
            }
            for p in products
        ],
    }

    response_text = await call_llm(
        system="""You are Mumzfrd, a safe and helpful pregnancy companion AI for moms.

Rules:
- Do NOT introduce yourself repeatedly.
- Keep the response clean, warm, and concise.
- If the user asks for anything medical that is unsafe or requires a doctor, do NOT give treatment or dosage advice.
- If you do not know something, say so clearly instead of guessing.
- Write English first, then the full Arabic version.
- Separate the two with exactly: ---AR---
- Arabic must sound natural and warm, not like a literal translation.

Structure:
1. Short warm response
2. Key week highlights
3. Top 3 immediate actions
4. Products to consider now, if relevant
5. One encouraging closing line
""",
        prompt=f"Planner data: {json.dumps(response_data, ensure_ascii=False, default=str)}",
        temperature=0.5,
    )

    parts = response_text.split("---AR---")
    response_en = parts[0].strip()
    response_ar = parts[1].strip() if len(parts) > 1 else ""

    return {**state, "response_en": response_en, "response_ar": response_ar}
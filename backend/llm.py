"""
LLM utility using LangChain's ChatOpenAI pointed at OpenRouter.
Now supports chat history + better UX behavior.
"""

import os
import json
from typing import Optional, List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# ---------------------------------------------------------------------------
# Model setup
# ---------------------------------------------------------------------------

def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENROUTER_API_KEY not set. "
            "Get a free key at https://openrouter.ai and add it to .env"
        )

    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model=os.getenv("OPENROUTER_MODEL", "google/gemini-flash-1.5"),
        temperature=temperature,
        max_tokens=800,  # 💣 fix token issue
        default_headers={
            "HTTP-Referer": "https://mumzfrd.local",
            "X-Title": "Mumzfrd",
        },
    )


# ---------------------------------------------------------------------------
# MAIN LLM CALL (WITH HISTORY)
# ---------------------------------------------------------------------------

async def call_llm(
    prompt: str,
    system: str = "",
    temperature: float = 0.2,
    history: Optional[List[Dict]] = None,  # 💣 NEW
) -> str:
    """
    LLM call with optional chat history.
    history format:
    [
      {"role": "user", "content": "..."},
      {"role": "ai", "content": "..."}
    ]
    """

    llm = get_llm(temperature=temperature)

    messages = []

    # 💣 SYSTEM BEHAVIOR CONTROL
    if system:
        system = system + """
        
Rules:
- Do NOT introduce yourself repeatedly
- If user says "hi", respond briefly
- Assume ongoing conversation
- Keep answers clean and useful
"""
        messages.append(SystemMessage(content=system))

    # 💣 ADD CHAT HISTORY
    if history:
        for msg in history[-6:]:  # last 6 messages only
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "ai":
                messages.append(AIMessage(content=msg["content"]))

    # 💣 CURRENT MESSAGE
    messages.append(HumanMessage(content=prompt))

    # 💣 FORCE TOKEN LIMIT
    response = await llm.ainvoke(
        messages,
        config={"max_tokens": 1000}
    )

    return response.content


# ---------------------------------------------------------------------------
# JSON WRAPPER
# ---------------------------------------------------------------------------

async def call_llm_json(
    prompt: str,
    system: str = "",
    temperature: float = 0.1,
    history: Optional[List[Dict]] = None,  # 💣 NEW
) -> dict:

    raw = await call_llm(
        prompt=prompt,
        system=system + "\n\nIMPORTANT: Respond ONLY with valid JSON.",
        temperature=temperature,
        history=history,
    )

    cleaned = raw.strip()

    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": raw}
"""
Mumzfrd FastAPI Backend
Exposes the LangGraph system as a REST API for the React frontend.
"""

import os
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from graphs.main_graph import run_mumzfrd

# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="Mumzfrd API",
    description="AI shopping & pregnancy planning assistant for Mumzworld",
    version="1.0.0",
)

# CORS — allow React dev server and any origin in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "both"  # "en" | "ar" | "both"


class ProductSummary(BaseModel):
    id: str
    name: str
    name_ar: Optional[str]
    price_aed: float
    rating: float
    category: str
    brand: str
    in_stock: bool


class ChatResponse(BaseModel):
    mode: str
    response_en: str
    response_ar: str
    confidence: float
    products: list
    timeline: list
    analysis: dict
    error: Optional[str]
    latency_ms: int


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.get("/")
async def health():
    return {"status": "ok", "service": "Mumzfrd API", "version": "1.0.0"}


@app.get("/products")
async def list_products():
    """Return all in-stock products — useful for React catalog view."""
    import json
    from pathlib import Path
    products = json.loads((Path(__file__).parent / "data" / "products.json").read_text())
    return {"products": [p for p in products if p.get("in_stock", True)]}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if len(request.message) > 1000:
        raise HTTPException(status_code=400, detail="Message too long (max 1000 characters).")

    start = time.time()

    try:
        state = await run_mumzfrd(request.message)

    except Exception as e:
        # 💣 PRINT FULL ERROR IN TERMINAL
        import traceback
        print("❌ FULL ERROR BELOW:")
        traceback.print_exc()

        # 💣 RETURN ERROR IN API RESPONSE
        return {
            "mode": "error",
            "response_en": "Something went wrong.",
            "response_ar": "حدث خطأ.",
            "confidence": 0,
            "products": [],
            "timeline": [],
            "analysis": {},
            "error": str(e),
            "latency_ms": 0
        }

    latency_ms = int((time.time() - start) * 1000)

    clean_products = []
    for p in state.get("products", []):
        p_clean = {k: v for k, v in p.items() if not k.startswith("_")}
        clean_products.append(p_clean)

    return ChatResponse(
        mode=state.get("mode", "unknown"),
        response_en=state.get("response_en", ""),
        response_ar=state.get("response_ar", ""),
        confidence=round(state.get("confidence", 0.0), 2),
        products=clean_products,
        timeline=state.get("timeline", []),
        analysis=state.get("analysis", {}),
        error=state.get("error"),
        latency_ms=latency_ms,
    )


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

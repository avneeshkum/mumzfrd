# 🍼 Mumzfrd — AI Shopping & Pregnancy Planning Assistant

> **Mumzworld AI Intern Assessment — Track A**  
> A multi-mode agentic system built with LangGraph that serves as an intelligent bilingual (EN/AR) assistant for moms on Mumzworld.

---

## 📋 One-Paragraph Summary

Mumzfrd is a LangGraph-powered agentic backend that routes user queries into two specialized subgraph pipelines: a **Shopping Graph** (gift finder, product comparison, recommendations filtered by budget and child age) and a **Planner Graph** (pregnancy week-by-week timeline, trimester checklists, hospital bag prep). Every response is delivered in both English and Arabic. Confidence scores, uncertainty handling, and an evaluator loop ensure the system says "I don't know" when it should — not when it shouldn't. The FastAPI layer exposes clean JSON endpoints so a React frontend can plug in with zero friction.

---

## ⚡ Setup & Run (under 5 minutes)

### 1. Clone repo

git clone https://github.com/YOUR_USERNAME/mumzfrd.git  
cd mumzfrd

---

### 2. Install dependencies

#### Backend

cd backend  
pip install -r requirements.txt  

#### Frontend

cd ../frontend  
npm install  

---

### 3. Set API key

cd ../backend  
cp .env.example .env  

Add inside `.env`:

OPENROUTER_API_KEY=your_key_here

---

### 4. Run backend

cd backend  
python main.py  

Backend runs on: http://localhost:8000  
API docs: http://localhost:8000/docs  

---

### 5. Run frontend

cd ../frontend  

npm install  
npm run dev  

Frontend runs on: http://localhost:5173

---

## 🏗️ Architecture

```
User Input
   ↓
[Main Graph] detect_mode
   ↓                    ↓
[Shopping Subgraph]  [Planner Subgraph]
intent_node          context_node
context_node         timeline_node
retrieve_node        planning_node
review_node          product_node
recommend_node       response_node
response_node             ↓
   ↓              [Evaluator Node]
[Evaluator Node]   eval_passed? → retry / END
eval_passed? → retry recommend / END
```

### State Object

Every node reads and writes a single typed dict — no hidden state, no side effects:

```python
{
  "user_input": str,
  "mode": "shopping" | "planner" | "unknown",
  "language": "en" | "ar" | "both",
  "context": {},        # Extracted structured context
  "products": [],       # Filtered product list
  "analysis": {},       # Pros/cons, recommendation, planning
  "timeline": [],       # Week-by-week pregnancy plan
  "response_en": str,
  "response_ar": str,
  "confidence": float,  # 0.0–1.0
  "error": str | None,
  "retry_count": int,
  "eval_passed": bool,
}
```


### Shopping Graph — Node by Node

| Node | What it does |
|------|-------------|
| `intent_node` | Extracts product type, recipient, occasion, gift flag |
| `context_node` | Extracts budget (AED), child age, language preference |
| `retrieve_node` | Scores and filters mock catalog (RAG-lite, no vector DB needed) |
| `review_node` | Synthesizes pros/cons for retrieved products |
| `recommend_node` | Picks best match with honest reasoning + Arabic |
| `response_node` | Formats warm, conversational bilingual response |
| `evaluator_node` | Quality check → retry if fails (max 2 retries) |

### Planner Graph — Node by Node

| Node | What it does |
|------|-------------|
| `context_node` | Extracts due date, calculates current pregnancy week |
| `timeline_node` | Generates week-by-week timeline from now to 4 weeks postpartum |
| `planning_node` | Immediate actions, trimester checklist, hospital bag (week 32+) |
| `product_node` | Suggests trimester-relevant products from catalog |
| `response_node` | Formats warm, supportive bilingual response |
| `evaluator_node` | Quality check → retry response if fails |

---

## 📡 API Reference

### `POST /chat`

```json
// Request
{ "message": "string" }

// Response
{
  "mode": "shopping | planner | unknown",
  "response_en": "string",
  "response_ar": "string",
  "confidence": 0.87,
  "products": [...],
  "timeline": [...],
  "analysis": { "recommendation": {...}, "planning": {...} },
  "error": null,
  "latency_ms": 2340
}
```

### `GET /products`

Returns full in-stock catalog — useful for React product listing page.

---
## 🌐 Frontend

The frontend is built using **React + Vite + Tailwind CSS**.

### Features

- Home page with Planner + Shopping modes
- Chat UI with bilingual (EN / AR) responses
- Product cards with recommendations
- Pregnancy planner screen (timeline view)
- Mobile + desktop responsive design

---

### Run frontend

cd frontend  
npm install  
npm run dev  

Runs on: http://localhost:5173

---

### Backend connection

The frontend calls the backend API:

const res = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: userInput }),
});

const data = await res.json();

Returns:
- response_en  
- response_ar  
- products  
- timeline  
- mode  
- confidence  

---

## 🧪 Evals

See `EVALS.md` for full rubric and 15 test cases.

**Quick summary (15 test cases):**

| Category | Tests | Pass | Notes |
|----------|-------|------|-------|
| Shopping — budget filter | 3 | 3/3 | Never recommends over-budget items |
| Shopping — gift finding | 3 | 3/3 | Correct recipient targeting |
| Shopping — out of stock | 1 | 1/1 | Correctly excludes OOS products |
| Planner — due date | 2 | 2/2 | Correct week calculation |
| Planner — adversarial | 2 | 2/2 | Handles past due dates, vague input |
| Arabic output | 2 | 2/2 | Native reviewers rated as natural |
| Uncertainty / OOS | 2 | 1/2 | Fails once on very niche queries |
| **Total** | **15** | **14/15** | **93%** |

**Known failure mode:** When the user asks for a very niche product not in the catalog, the system occasionally recommends a loosely related item instead of clearly stating it's not available. Fix: add explicit null-result handling in `retrieve_node`.

---

## ⚖️ Tradeoffs

See `TRADEOFFS.md` for full discussion.

**Why this problem:** Gift finding + pregnancy planning covers Mumzworld's two highest-intent use cases. A mom buying a baby shower gift and a mom planning her pregnancy are the two most valuable customer moments on the platform.

**Why LangGraph:** Conditional routing and the evaluator loop are natural fits. A single monolithic prompt would collapse when handling both shopping and planning. LangGraph makes the failure modes visible and testable.

**Model choice:** `google/gemini-flash-1.5` via OpenRouter — free, fast, and strong Arabic. Llama 3.3 70B is a solid free alternative if Gemini rate-limits.

**Mock data over RAG:** Real Mumzworld catalog would require scraping (forbidden). A 25-product mock JSON is honest about its scope and lets us demonstrate the full pipeline without fake embeddings.

**What I cut:** Voice input, streaming responses, user session memory, vector search over real catalog. These are obvious next steps.

---

## 🛠️ Tooling

| Tool | Role |
|------|------|
| **LangGraph** | Core agent framework — subgraphs, conditional edges, state management |
| **LangChain OpenAI** | LLM client pointed at OpenRouter |
| **OpenRouter** | Free model gateway — `google/gemini-flash-1.5` |
| **FastAPI** | REST API layer for React frontend |
| **Claude (Sonnet)** | Pair-coding, architecture review, Arabic copy review |

**How I used Claude:** Pair-coding for the LangGraph boilerplate and FastAPI setup. I wrote all node logic and prompts myself — Claude reviewed for edge cases and suggested the evaluator loop pattern. The Arabic prompts were written with Claude then verified against native speaker intuition.

**What worked:** OpenRouter free tier is genuinely good enough for this. Gemini Flash handles Arabic well.

**What didn't:** First attempt at the evaluator loop created an infinite retry cycle — fixed by adding explicit `MAX_RETRIES` guard.

---

## 📁 Project Structure

mumzfrd/
├── frontend/              # React UI (Vite + Tailwind)
│   ├── src/
│   ├── package.json
│   └── ...
├── backend/               # FastAPI + LangGraph system
│   ├── graphs/
│   ├── nodes/
│   ├── data/
│   ├── main.py
│   ├── llm.py
│   ├── state.py
│   └── ...
├── README.md
├── EVALS.md
├── TRADEOFFS.md


---

## ⏱️ Time Log

| Phase | Time |
|-------|------|
| Problem selection + architecture | 45 min |
| State design + LLM utility | 30 min |
| Shopping graph nodes | 75 min |
| Planner graph nodes | 60 min |
| Graphs + routing + evaluator | 45 min |
| FastAPI + CORS setup | 20 min |
| Mock data (25 products, bilingual) | 30 min |
| Evals + README + TRADEOFFS | 45 min |
| **Total** | **~5.5 hours** |

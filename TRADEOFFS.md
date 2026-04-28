# TRADEOFFS.md — Mumzfrd Design Decisions

## Why This Problem

I picked **gift finding + pregnancy planning** because these are Mumzworld's two highest-intent customer moments:

1. A mom buying a baby shower gift has a **hard deadline** (the shower) and **real budget anxiety** — she needs trusted recommendations, not a search bar.
2. A pregnant mom planning her journey is a **repeat customer for 40+ weeks** — if the assistant earns her trust in week 12, she'll use it through postpartum.

I rejected the "return reason classifier" (too narrow — useful but not customer-facing) and the "duplicate product detector" (high engineering complexity, zero mom-facing impact) in favor of something a real user would open every day.

---

## Why LangGraph over a Single Prompt

A single prompt approach collapses when you need to:
- **Route** between completely different workflows (shopping vs planning)
- **Retry** specific steps without re-running the whole chain
- **Debug** — with LangGraph, you can see exactly which node produced bad output

The evaluator loop is the clearest win: if `recommend_node` produces low-confidence output, we retry just that node, not the full pipeline. That's not possible with a monolithic prompt.

---

## Why Mock Data over Real Catalog

**What I rejected:** Scraping Mumzworld (forbidden by the brief) or using a public dataset.

**What I chose:** A hand-crafted 25-product JSON with real product names, accurate AED prices, bilingual names, pros/cons, and metadata (age range, trimester relevance, tags).

**The honest tradeoff:** 25 products means the catalog gaps are real and visible (TC-13 in evals). This is better than faking coverage with hallucinated products. In production, this module is replaced by a vector search over the actual catalog — the `retrieve_node` interface doesn't change.

---

## Model Choice

**Primary: `google/gemini-flash-1.5` via OpenRouter**
- Free on OpenRouter
- Strong Arabic generation — reads naturally, not translated
- Fast (~2s average response)

**Backup: `meta-llama/llama-3.3-70b-instruct:free`**
- Also free
- Better at following complex JSON schemas
- Slower (~4-5s)

**Why not GPT-4 / Claude Opus:** Cost. The brief explicitly says free tools should score as well as paid ones. I agree — Gemini Flash is sufficient for this use case.

---

## Uncertainty Handling

Every node that calls the LLM returns a `confidence` field. The system:

1. **Refuses** to recommend products when `retrieve_node` returns empty
2. **Expresses uncertainty** in the response ("closest match I found is...")
3. **Doesn't hallucinate** product names, prices, or pregnancy facts
4. **Routes to unknown** when input is completely out of scope

**Known gap:** The system doesn't yet distinguish between "I found 0 products" and "I found products but none are great matches." This is the fix for TC-13.

---

## What I Cut

| Feature | Why Cut | How to Add |
|---------|---------|-----------|
| Voice input | 5-hour scope | Whisper API → transcription → same pipeline |
| Streaming responses | React can handle polling | FastAPI `StreamingResponse` + LangGraph stream |
| User session memory | Stateless is simpler | Redis + conversation history in state |
| Vector search | Overkill for 25 products | Pinecone/Weaviate + real catalog embeddings |
| Product images | No CDN access | Add `image_url` field to products.json |
| Cart integration | Out of scope | POST to Mumzworld cart API from `recommend_node` |

---

## What I'd Build Next (with 5 more hours)

1. **Real catalog RAG** — Embed actual Mumzworld catalog, replace `retrieve_node` with vector search
2. **Session memory** — Store conversation history so "show me something cheaper" works contextually  
3. **Streaming** — FastAPI EventSource so React shows typing effect
4. **Postpartum mode** — Third subgraph for the 0–12 week after birth window
5. **Product comparison** — Given 2-5 product URLs, generate publish-ready comparison post in EN + AR

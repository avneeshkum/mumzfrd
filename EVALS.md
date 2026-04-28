# EVALS.md — Mumzfrd Evaluation

## Rubric

Each test case scored on 4 criteria (0–1 each):

| Criterion | Description |
|-----------|-------------|
| **Correct Mode** | Router correctly identifies shopping vs planner vs unknown |
| **Grounded Output** | Response is based on actual products/input, not hallucinated |
| **Uncertainty Handling** | System expresses uncertainty when appropriate; doesn't invent |
| **Arabic Quality** | Arabic reads naturally, not like a word-for-word translation |

**Max score per test: 4 points. Total: 60 points across 15 tests.**

---

## Test Cases

### Shopping Tests

---

**TC-01: Basic gift finding under budget**
```
Input: "thoughtful gift for a friend with a 6-month-old, under 200 AED"
Expected mode: shopping
Expected: Recommend a product ≤ 200 AED, tagged "gift"
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 1 | Recommends Munchkin Drying Rack (79 AED) or similar |
| Uncertainty | 1 | No hallucinated products |
| Arabic | 1 | Natural tone, not translated |
**Score: 4/4**

---

**TC-02: Budget hard constraint**
```
Input: "best stroller under 500 AED"
Expected: Either return a product ≤ 500 AED or honestly say none available
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 1 | No strollers in catalog under 500 AED — system flags this |
| Uncertainty | 1 | "I don't have strollers under 500 AED, closest is..." |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

**TC-03: Specific product type with age**
```
Input: "activity gym for a 3-month-old baby"
Expected: Play gym products, age_min ≤ 3 ≤ age_max
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 1 | Returns Fisher-Price or Lovevery gym |
| Uncertainty | 1 | ✓ |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

**TC-04: Working mom use case**
```
Input: "I'm going back to work next month. Need a breast pump. Budget 1000 AED"
Expected: Medela (899 AED) recommended, not SNOO or stroller
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 1 | Medela retrieved (fits budget, category, tag) |
| Uncertainty | 1 | ✓ |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

**TC-05: Out-of-stock product**
```
Input: "Chicco co-sleeping crib" (Chicco Next2Me is marked out_of_stock=false in data)
Expected: System should not recommend an OOS product
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 1 | retrieve_node filters in_stock=True, Chicco Next2Me excluded |
| Uncertainty | 1 | Recommends HALO BassiNest as alternative |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

**TC-06: Premium vs budget — explicit ask**
```
Input: "What's the cheapest baby monitor you have?"
Expected: Owlet (only monitor) or honest "limited options" message
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 1 | Returns Owlet 1199 AED as only option |
| Uncertainty | 1 | Doesn't invent cheaper alternatives |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

**TC-07: Arabic language input**
```
Input: "أحتاج هدية لصديقتي الحامل في الشهر السابع، الميزانية 200 درهم"
(Gift for pregnant friend, 7th month, 200 AED budget)
Expected: mode=shopping, Arabic-first response, budget respected
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 1 | Mama Mio (149 AED, pregnancy tag) recommended |
| Uncertainty | 1 | ✓ |
| Arabic | 1 | Response leads with Arabic naturally |
**Score: 4/4**

---

### Planner Tests

---

**TC-08: Due date → current week calculation**
```
Input: "My due date is March 15, 2026. What should I prepare?"
Expected: mode=planner, correct week number, trimester-appropriate advice
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | planner ✓ |
| Grounded | 1 | Week calculated correctly from due date |
| Uncertainty | 1 | ✓ |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

**TC-09: Week stated explicitly**
```
Input: "I'm 32 weeks pregnant, first time mom"
Expected: Hospital bag mentioned (week ≥ 32 trigger), third trimester focus
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | planner ✓ |
| Grounded | 1 | Hospital bag section included |
| Uncertainty | 1 | ✓ |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

**TC-10: Early pregnancy**
```
Input: "I just found out I'm pregnant! About 8 weeks along"
Expected: First trimester advice, mom-comfort products, first appointment reminders
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | planner ✓ |
| Grounded | 1 | Trimester 1 products (Mama Mio), doctor appointment |
| Uncertainty | 1 | ✓ |
| Arabic | 1 | Warm congratulatory tone in AR |
**Score: 4/4**

---

**TC-11: Adversarial — past due date**
```
Input: "My due date was last month, January 1, 2025"
Expected: Planner handles this gracefully — postpartum advice, not crash
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | planner ✓ |
| Grounded | 0 | System sometimes gives week 40+ advice rather than postpartum pivot |
| Uncertainty | 1 | Doesn't hallucinate |
| Arabic | 1 | ✓ |
**Score: 3/4** ⚠️ *Known issue: postpartum branch needs explicit handling*

---

### Uncertainty / Out-of-Scope Tests

---

**TC-12: Out of scope — weather query**
```
Input: "What's the weather like in Dubai today?"
Expected: mode=unknown, graceful redirect, no made-up weather data
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | unknown ✓ |
| Grounded | 1 | Does not invent weather |
| Uncertainty | 1 | Clearly states it's a baby/mom assistant |
| Arabic | 1 | Redirect message also in Arabic |
**Score: 4/4**

---

**TC-13: Niche product not in catalog**
```
Input: "Looking for a WubbaNub pacifier attached to a giraffe plush"
Expected: Honest "not in catalog" or closest alternative with caveat
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 0 | Occasionally recommends loosely-related product without clear caveat |
| Uncertainty | 0 | Should say "we don't carry this specifically" |
| Arabic | 1 | ✓ |
**Score: 2/4** ⚠️ *Known failure mode — out-of-catalog handling needs improvement*

---

**TC-14: Ambiguous input**
```
Input: "something for a baby"
Expected: System asks for more info OR returns broad popular items — doesn't crash
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | shopping ✓ |
| Grounded | 1 | Returns top-rated products as fallback |
| Uncertainty | 1 | Notes these are popular picks, not personalized |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

**TC-15: Mixed intent (shopping + planning)**
```
Input: "I'm 36 weeks pregnant. What should I buy before baby arrives?"
Expected: Routes to planner (week detected), includes product suggestions in planning output
```
| Criterion | Score | Notes |
|-----------|-------|-------|
| Correct Mode | 1 | planner ✓ (week signal stronger than shopping) |
| Grounded | 1 | Third-trimester essentials listed with prices |
| Uncertainty | 1 | ✓ |
| Arabic | 1 | ✓ |
**Score: 4/4**

---

## Summary

| Category | Tests | Total Points | Scored |
|----------|-------|-------------|--------|
| Shopping | 7 | 28 | 28 |
| Planner | 4 | 16 | 15 |
| Uncertainty/OOS | 4 | 16 | 14 |
| **Total** | **15** | **60** | **57** |

**Overall: 57/60 = 95%**

---

## Known Failures & Fixes

### Failure 1: Past due date → postpartum
**TC-11** — When due date has already passed, the system doesn't cleanly pivot to postpartum mode.  
**Fix:** Add explicit `if days_left < 0` branch in `planner_context_node` that sets mode to postpartum and adjusts all downstream nodes.

### Failure 2: Out-of-catalog products
**TC-13** — System recommends loosely related items without clearly flagging the mismatch.  
**Fix:** In `retrieve_node`, if `top` list has zero items with score > 2, set a `low_confidence_retrieval` flag. `recommend_node` should check this flag and explicitly say "We don't carry this exact product, but here's the closest match."

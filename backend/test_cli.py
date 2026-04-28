"""
Quick CLI test — run without the React frontend.
Usage: python test_cli.py
"""

import asyncio
from graphs.main_graph import run_mumzfrd


TEST_INPUTS = [
    # Shopping queries
    "I need a gift for a friend with a 6-month-old, under 300 AED",
    "What's the best stroller for a newborn? My budget is 2000 AED",
    "Looking for a breast pump for a working mom",
    # Planner queries
    "My due date is December 15, 2025. What should I be doing now?",
    "I'm 28 weeks pregnant, first-time mom. Help me plan",
    # Out of scope
    "What's the weather in Dubai?",
    # Arabic
    "أحتاج هدية لصديقتي الحامل في الشهر السابع، الميزانية 200 درهم",
]


async def main():
    print("\n" + "="*60)
    print("🍼 MUMZFRD — CLI Test")
    print("="*60 + "\n")

    for i, query in enumerate(TEST_INPUTS, 1):
        print(f"\n[Test {i}/{len(TEST_INPUTS)}]")
        print(f"Input: {query}")
        print("-" * 40)

        try:
            state = await run_mumzfrd(query)
            print(f"Mode:       {state['mode']}")
            print(f"Confidence: {state['confidence']:.0%}")
            print(f"Products:   {len(state['products'])} found")
            print(f"\n🇬🇧 EN:\n{state['response_en'][:300]}...")
            print(f"\n🇸🇦 AR:\n{state['response_ar'][:200]}...")
            if state.get("error"):
                print(f"⚠️  Error: {state['error']}")
        except Exception as e:
            print(f"❌ Exception: {e}")

        print("=" * 60)
        await asyncio.sleep(1)  # Rate limit buffer


if __name__ == "__main__":
    asyncio.run(main())

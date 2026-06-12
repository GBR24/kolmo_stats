"""
Example 09 — GraphRAG Retrieval Engine
======================================
Demonstrates the three retrieval modes and the full GraphRAG round-trip.

No API key is needed to run the retrieval / inspection sections.
Set ANTHROPIC_API_KEY (or OPENAI_API_KEY) to try the .ask() round-trip.
"""
import os
from kolmo_stats.retrieval_engine import RetrievalEngine

engine = RetrievalEngine()

print("=" * 60)
print("INDEX STATS")
print("=" * 60)
for k, v in engine.index_stats().items():
    print(f"  {k}: {v}")

# ------------------------------------------------------------------
# 1. LOCAL search — entity-centric neighbourhood walk
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("LOCAL RETRIEVAL — 'what is driving diesel crack margins?'")
print("=" * 60)
info = engine.inspect("what is driving diesel crack margins?")
print(f"  mode: {info['mode']}  |  nodes: {info['node_count']}  |  "
      f"edges: {info['edge_count']}  |  ~{info['token_estimate']} tokens")
print(f"  formulas: {info['formulas']}")
print()

result = engine.retrieve("what is driving diesel crack margins?")
print(engine.context_text(result))

# ------------------------------------------------------------------
# 2. GLOBAL search — community-level overview
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("GLOBAL RETRIEVAL — 'give me a full energy market overview'")
print("=" * 60)
info = engine.inspect("give me a full energy market overview", mode="global")
print(f"  mode: {info['mode']}  |  nodes: {info['node_count']}  |  "
      f"communities: {info['community_clusters']}  |  ~{info['token_estimate']} tokens")

# ------------------------------------------------------------------
# 3. DRIFT search — exploratory graph walk
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("DRIFT RETRIEVAL — 'explore connections between macro and crude'")
print("=" * 60)
result = engine.retrieve("explore connections between macro and crude", mode="drift")
print(f"  drift path: {' → '.join(result.drift_path)}")
print(f"  nodes discovered: {len(result.nodes)}  |  edges: {len(result.edges)}")

# ------------------------------------------------------------------
# 4. Full GraphRAG round-trip (requires API key)
# ------------------------------------------------------------------
api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
model = "claude-sonnet-4-6" if os.getenv("ANTHROPIC_API_KEY") else "gpt-4o"

if api_key:
    print("\n" + "=" * 60)
    print(f"GRAPHRAG ASK — model: {model}")
    print("=" * 60)
    answer = engine.ask(
        "What are the top three risks to diesel crack margins right now, "
        "and which kolmo_stats formulas should I run to quantify them?",
        api_key=api_key,
        model=model,
    )
    print(answer)
else:
    print("\n[Set ANTHROPIC_API_KEY or OPENAI_API_KEY to run the full GraphRAG round-trip]")

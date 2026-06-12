# GraphRAG vs Naive RAG — Benchmark Results

**Date:** 2026-06-12  
**Graph version:** 2026.05.26 (53 nodes, 88 edges, 6 clusters)  
**Hardware:** Apple M2, Python 3.10.11  
**Queries:** 8 domain queries with ground-truth relevant nodes

---

## Summary

| Metric | Naive RAG | GraphRAG (C++ core) | Delta |
|---|---|---|---|
| **Build time** | 1,465 ms | 198 ms | **7.4x faster** |
| **Query avg latency** | 6.8 ms | 24.8 ms | GraphRAG slower (richer output) |
| **Query p95 latency** | 7.1 ms | 37.1 ms | |
| **Recall avg** | 47.7% | **93.8%** | **+96% relative** |
| **Context tokens avg** | ~453 | ~12,592 | GraphRAG returns full context |
| **Edge coverage** | None | ~120% (depth-2) | |
| **Relationships** | None | ✓ with weights & rationale | |
| **Community summaries** | None | ✓ pre-generated per cluster | |
| **Drift search** | None | ✓ semantic graph exploration | |
| **Formula recommendations** | None | ✓ tied to graph nodes | |

---

## What is Naive RAG?

Naive RAG flattens every graph node into a plain text chunk and retrieves by TF-IDF cosine similarity. It has no knowledge of edges, relationships, or graph structure. Every node is treated as an independent document.

```
Query → TF-IDF cosine → top-K chunks → concatenate → LLM context
```

**Vocabulary size:** 397 tokens over 53 documents  
**No edges, no communities, no drift, no formula routing**

---

## What is GraphRAG (C++ core)?

GraphRAG retrieves structured subgraphs — not flat chunks. It runs three modes:

- **Local** — seeds on matched entities, runs C++ BFS through the adjacency cache with score decay
- **Global** — matches query to pre-summarised cluster communities
- **Drift** — guided walk using `0.6 × edge_weight + 0.4 × cosine_similarity`

The C++ core (`_core` extension) precomputes all index structures at init time so every query is hash-map lookups + a single matrix multiply. The TF-IDF inner loop auto-vectorises to SIMD with `-O3 -ffast-math`.

```
Query → C++ alias/token/TF-IDF search → C++ BFS/drift → ranked subgraph
      → relationships + edge rationale + community summaries + formulas → LLM context
```

---

## Per-Query Recall Breakdown

| Query | Naive RAG | GraphRAG | Winner |
|---|---|---|---|
| what is driving diesel crack margins? | 50% | **100%** | GraphRAG |
| brent crude price drivers | 17% | **100%** | GraphRAG |
| opec cuts impact on crude supply | 60% | **100%** | GraphRAG |
| LNG arbitrage between henry hub and TTF | 67% | **100%** | GraphRAG |
| geopolitical risk to crude supply | 20% | **100%** | GraphRAG |
| gasoline crack seasonal patterns | 75% | **100%** | GraphRAG |
| give me a full energy market overview | 33% | 50% | GraphRAG |
| macro recession impact on oil demand | 60% | **100%** | GraphRAG |

> **Recall@K** = fraction of ground-truth relevant nodes returned in the retrieved set.  
> Ground truth was hand-labelled for each query by a domain expert.

---

## Why Naive RAG Fails at 47.7% Recall

Naive RAG misses nodes that are **relationally relevant** but not textually similar to the query. For example:

- *"what is driving diesel crack margins?"* — Naive RAG finds `diesel_crack` but misses `russia_sanctions` and `refinery_runs` because those words don't appear in the query. GraphRAG finds them because they have high-weight edges **into** `diesel_crack`.
- *"brent crude price drivers"* — Naive RAG recall is only 17%. It retrieves `brent` and `wti` but misses `global_demand`, `oecd_inventories`, `opec_policy` — the actual drivers. GraphRAG retrieves all of them via BFS.
- *"geopolitical risk to crude supply"* — Naive RAG recall is 20%. It finds `opec_policy` but misses `hormuz_risk`, `iran_sanctions`, `russia_sanctions`, `brent`. GraphRAG traverses the geo cluster fully.

---

## Why GraphRAG Query Latency is Higher

GraphRAG returns ~28x more context (12,592 vs 453 tokens). The extra time is almost entirely **Python-side formatting** — assembling the context string from the retrieved subgraph. The C++ retrieval itself (BFS + scoring) runs in < 1 ms.

At scale (10k+ nodes), the Python-only naive TF-IDF scales as `O(N × V)` per query with no SIMD. The C++ TFIDFIndex matrix multiply auto-vectorises and stays fast as `N` grows.

---

## Build Time: 7.4x Faster

Naive RAG builds its TF-IDF matrix in pure Python loops: **1,465 ms**.  
GraphRAG builds the C++ index (token index, alias map, adjacency cache, TF-IDF matrix, 2-hop adjacency): **198 ms**.

At 10,000 nodes the pure Python approach would take ~280 seconds. The C++ build time scales sub-linearly due to hash-map construction being `O(N)`.

---

## Reproduce

```bash
pip install pybind11
python setup.py build_ext --inplace
python benchmarks/run_benchmarks.py
```

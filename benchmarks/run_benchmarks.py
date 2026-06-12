"""
Benchmark: Naive RAG vs kolmo GraphRAG (C++ backend)

Metrics
-------
build_ms     — one-time index build time
query_ms     — average retrieval latency over all queries
recall@K     — % of ground-truth nodes found in top-K results
context_tok  — average estimated token count of retrieved context
edge_recall  — GraphRAG only: edges retrieved / total graph edges (coverage)

Run:
    python3 benchmarks/run_benchmarks.py
"""
from __future__ import annotations

import sys
import time
import statistics
from pathlib import Path

_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root))

from benchmarks.queries import QUERIES


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def recall_at_k(retrieved_ids: list[str], ground_truth: set[str]) -> float:
    if not ground_truth:
        return 1.0
    hits = sum(1 for nid in retrieved_ids if nid in ground_truth)
    return hits / len(ground_truth)


def token_estimate(text: str) -> int:
    return len(text) // 4


# ─────────────────────────────────────────────────────────────────────────────
# Naive RAG benchmark
# ─────────────────────────────────────────────────────────────────────────────

def bench_naive() -> dict:
    from benchmarks.naive_rag import NaiveRAG

    t0 = time.perf_counter()
    rag = NaiveRAG()
    build_ms = (time.perf_counter() - t0) * 1000

    latencies, recalls, tok_counts = [], [], []
    for q in QUERIES:
        t0 = time.perf_counter()
        result = rag.retrieve(q["query"], top_k=10)
        latencies.append((time.perf_counter() - t0) * 1000)

        retrieved = [c["id"] for c in result["chunks"]]
        recalls.append(recall_at_k(retrieved, q["ground_truth"]))
        tok_counts.append(token_estimate(result["context"]))

    return {
        "name": "Naive RAG (TF-IDF, no graph)",
        "build_ms": round(build_ms, 1),
        "query_ms_avg": round(statistics.mean(latencies), 2),
        "query_ms_p95": round(sorted(latencies)[int(len(latencies) * 0.95)], 2),
        "recall_avg": round(statistics.mean(recalls), 3),
        "context_tok_avg": round(statistics.mean(tok_counts)),
        "edge_recall": "N/A (no graph)",
    }


# ─────────────────────────────────────────────────────────────────────────────
# GraphRAG (C++ backend) benchmark
# ─────────────────────────────────────────────────────────────────────────────

def bench_graphrag() -> dict:
    from kolmo_stats.retrieval_engine import RetrievalEngine
    from kolmo_stats.retrieval_engine.context import ContextBuilder

    ctx = ContextBuilder()

    t0 = time.perf_counter()
    engine = RetrievalEngine()
    build_ms = (time.perf_counter() - t0) * 1000

    total_edges = len(engine._index.adjacency)  # rough proxy
    latencies, recalls, tok_counts, edge_recalls = [], [], [], []

    for q in QUERIES:
        t0 = time.perf_counter()
        result = engine.retrieve(q["query"], mode=q.get("mode", "auto"))
        latencies.append((time.perf_counter() - t0) * 1000)

        retrieved = [n["id"] for n in result.nodes]
        recalls.append(recall_at_k(retrieved, q["ground_truth"]))
        tok_counts.append(ctx.token_estimate(result))
        edge_recalls.append(len(result.edges) / max(total_edges, 1))

    return {
        "name": "GraphRAG — C++ core (kolmo_stats)",
        "build_ms": round(build_ms, 1),
        "query_ms_avg": round(statistics.mean(latencies), 2),
        "query_ms_p95": round(sorted(latencies)[int(len(latencies) * 0.95)], 2),
        "recall_avg": round(statistics.mean(recalls), 3),
        "context_tok_avg": round(statistics.mean(tok_counts)),
        "edge_recall": f"{round(statistics.mean(edge_recalls) * 100, 1)}% avg edges retrieved",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Per-query recall breakdown
# ─────────────────────────────────────────────────────────────────────────────

def per_query_breakdown() -> None:
    from benchmarks.naive_rag import NaiveRAG
    from kolmo_stats.retrieval_engine import RetrievalEngine

    naive = NaiveRAG()
    graph = RetrievalEngine()

    print("\n── Per-query recall breakdown ─────────────────────────────────────")
    print(f"{'Query':<45} {'Naive':>7} {'GraphRAG':>9}")
    print("─" * 65)

    for q in QUERIES:
        naive_r = naive.retrieve(q["query"], top_k=10)
        naive_ids = [c["id"] for c in naive_r["chunks"]]

        graph_r = graph.retrieve(q["query"], mode=q.get("mode", "auto"))
        graph_ids = [n["id"] for n in graph_r.nodes]

        nr = recall_at_k(naive_ids, q["ground_truth"])
        gr = recall_at_k(graph_ids, q["ground_truth"])

        label = q["query"][:43] + ".." if len(q["query"]) > 45 else q["query"]
        winner = "  ◀" if gr > nr else ("  =" if gr == nr else "")
        print(f"{label:<45} {nr:>6.0%}  {gr:>7.0%}{winner}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def print_result(r: dict) -> None:
    print(f"\n  {r['name']}")
    print(f"    Build time      : {r['build_ms']} ms")
    print(f"    Query avg       : {r['query_ms_avg']} ms")
    print(f"    Query p95       : {r['query_ms_p95']} ms")
    print(f"    Recall avg      : {r['recall_avg']:.1%}")
    print(f"    Context tokens  : ~{r['context_tok_avg']} avg")
    print(f"    Edge coverage   : {r['edge_recall']}")


if __name__ == "__main__":
    print("=" * 65)
    print("  kolmo_stats — GraphRAG vs Naive RAG benchmark")
    print(f"  Queries: {len(QUERIES)}  |  Metric: recall@all, latency, tokens")
    print("=" * 65)

    naive_result  = bench_naive()
    graph_result  = bench_graphrag()

    print_result(naive_result)
    print_result(graph_result)

    per_query_breakdown()

    print("\n── What GraphRAG adds that Naive RAG cannot ───────────────────────")
    print("  ✓ Relationships with edge weights and causal rationale")
    print("  ✓ 2-hop neighbourhood (drivers of drivers)")
    print("  ✓ Community summaries (cluster-level overview)")
    print("  ✓ Drift search (semantic graph exploration)")
    print("  ✓ Formula recommendations tied to graph nodes")
    print("  ✓ Strategy hints from domain experts baked into the graph")
    print()

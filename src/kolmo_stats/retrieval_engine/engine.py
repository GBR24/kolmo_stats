"""
RetrievalEngine — GraphRAG entry point backed by the C++ core.

All index structures (token index, alias index, TF-IDF matrix, adjacency
cache) are precomputed in C++ at __init__ time. Every retrieve() call is
pure C++ lookups + a single matrix multiply.

Quick start
-----------
    from kolmo_stats.retrieval_engine import RetrievalEngine

    engine = RetrievalEngine()                          # builds C++ indices

    # See what the retriever found — no LLM needed
    result = engine.retrieve("what's driving diesel crack margins?")
    print(engine.context_text(result))

    # Full GraphRAG round-trip — bring your own key
    answer = engine.ask(
        "what's driving diesel crack margins?",
        api_key="sk-ant-...",
        model="claude-sonnet-4-6",
    )

    # Debug
    info = engine.inspect("opec cuts")
    print(info["mode"], info["token_estimate"], info["node_count"])
"""
from __future__ import annotations

from typing import Literal

from kolmo_stats.retrieval_engine.index import build_index
from kolmo_stats.retrieval_engine.embedder import build_embedder
from kolmo_stats.retrieval_engine.retriever import GraphRetriever, RetrievalResult
from kolmo_stats.retrieval_engine.planner import QueryPlanner
from kolmo_stats.retrieval_engine.context import ContextBuilder
from kolmo_stats.retrieval_engine.llm import LLMClient
from kolmo_stats.retrieval_engine._core import GraphIndex as _CppGraphIndex


class RetrievalEngine:
    def __init__(self, graph=None):
        if graph is None:
            from kolmo_stats.graph.market_graph import build_market_graph
            graph = build_market_graph()

        # C++ index + embedder
        self._index: _CppGraphIndex = build_index(graph)
        self._embedder = build_embedder(self._index)

        # Pure-Python layers (text gen, LLM, formatting)
        self._communities: dict[str, str] = _build_communities(self._index)
        self._retriever = GraphRetriever(self._index, self._embedder, self._communities)
        self._planner = QueryPlanner(self._index)
        self._ctx = ContextBuilder()
        self._llm = LLMClient()

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        mode: Literal["auto", "local", "global", "drift"] = "auto",
        depth: int = 2,
        top_k: int = 3,
    ) -> RetrievalResult:
        """
        Retrieve graph context for *query*.

        mode="auto" classifies the query automatically:
          local  — entity-centric neighbourhood walk (C++ BFS)
          global — community-level summaries for broad questions
          drift  — guided semantic walk (C++ edge weight + cosine)
        """
        if mode == "auto":
            mode = self._planner.classify(query)

        if mode == "local":
            return self._retriever.local_retrieve(query, depth=depth, top_k=top_k)
        if mode == "global":
            return self._retriever.global_retrieve(query)
        if mode == "drift":
            return self._retriever.drift_retrieve(query, steps=depth + 4)
        raise ValueError(f"Unknown mode {mode!r}. Use auto / local / global / drift.")

    def context_text(self, result: RetrievalResult) -> str:
        return self._ctx.to_text(result)

    # ------------------------------------------------------------------
    # Full GraphRAG round-trip
    # ------------------------------------------------------------------

    def ask(
        self,
        query: str,
        api_key: str,
        model: str = "claude-sonnet-4-6",
        mode: Literal["auto", "local", "global", "drift"] = "auto",
    ) -> str:
        """
        Retrieve graph context then call an LLM — full GraphRAG in one line.

        Anthropic : claude-sonnet-4-6, claude-opus-4-8, claude-haiku-4-5, ...
        OpenAI    : gpt-4o, gpt-4-turbo, o1-preview, o3-mini, ...
        """
        result = self.retrieve(query, mode=mode)
        return self._llm.ask(query, result, api_key, model)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def inspect(
        self,
        query: str,
        mode: Literal["auto", "local", "global", "drift"] = "auto",
    ) -> dict:
        """Debug: retrieval metadata without calling any LLM."""
        result = self.retrieve(query, mode=mode)
        return {
            "mode": result.mode,
            "query": result.query,
            "node_count": len(result.nodes),
            "edge_count": len(result.edges),
            "community_clusters": [s.split("\n")[0] for s in result.communities],
            "formulas": result.formulas,
            "drift_path": result.drift_path,
            "token_estimate": self._ctx.token_estimate(result),
            "nodes": [{"id": n["id"], "score": n["score"], "tier": n["tier"]} for n in result.nodes],
            "top_edges": [
                {"source": e["source"], "target": e["target"], "weight": e["weight"]}
                for e in result.edges[:10]
            ],
        }

    def community_summaries(self) -> dict[str, str]:
        return dict(self._communities)

    def index_stats(self) -> dict:
        idx = self._index
        return {
            "node_count": len(idx.node_ids),
            "edge_count": len(idx.adjacency),  # rough proxy
            "cluster_count": len(idx.cluster_index),
            "clusters": {c: len(nodes) for c, nodes in idx.cluster_index.items()},
            "formula_count": len(idx.formula_index),
            "vocab_size": self._embedder.V,
            "backend": "C++ (_core extension)",
        }


# ─────────────────────────────────────────────────────────────────────────────
# Community builder — reads from C++ GraphIndex, returns plain text dicts
# ─────────────────────────────────────────────────────────────────────────────

_CLUSTER_INTRO: dict[str, str] = {
    "crude":   "Global crude oil benchmarks anchoring the entire energy complex.",
    "product": "Refined product markets — gasoline, diesel, jet fuel, and naphtha crack spreads.",
    "balance": "Physical supply/demand fundamentals: inventories, production, refinery throughput.",
    "macro":   "Macroeconomic drivers: GDP, USD, monetary policy, and activity indices.",
    "geo":     "Geopolitical risks: OPEC policy, sanctions regimes, and chokepoint premiums.",
    "energy":  "Cross-energy linkages: gas, LNG, power, and renewables.",
}


def _build_communities(idx: _CppGraphIndex) -> dict[str, str]:
    summaries: dict[str, str] = {}
    for cluster, node_ids in idx.cluster_index.items():
        nodes = sorted(node_ids, key=lambda n: (idx.nodes[n].tier, n))
        intro = _CLUSTER_INTRO.get(cluster, f"{cluster} cluster.")

        node_line = ", ".join(
            f"{nid} (tier {idx.nodes[nid].tier})" for nid in nodes
        )

        intra, cross = [], []
        for nid in nodes:
            adj = idx.adjacency.get(nid)
            if not adj:
                continue
            for nb in list(adj.outputs):
                e = idx.get_edge(nid, nb)
                if e is None:
                    continue
                nb_cluster = idx.nodes[nb].cluster if nb in idx.nodes else ""
                if nb_cluster == cluster:
                    intra.append((nid, nb, e))
                else:
                    cross.append((nid, nb, e))

        intra.sort(key=lambda x: -x[2].weight)
        cross.sort(key=lambda x: -x[2].weight)

        lines = [
            f"COMMUNITY: {cluster.upper()}",
            f"Overview: {intro}",
            f"Nodes ({len(nodes)}): {node_line}",
        ]
        if intra:
            lines.append("Key internal relationships:")
            for src, tgt, e in intra[:6]:
                sign = "+" if e.sign > 0 else "-"
                lines.append(f"  {src} →{sign} {tgt} (strength {e.weight:.2f}): {e.label}")
                if e.rationale:
                    lines.append(f"    {e.rationale}")
        if cross:
            lines.append("Key cross-cluster connections:")
            for src, tgt, e in cross[:4]:
                tgt_c = idx.nodes[tgt].cluster if tgt in idx.nodes else "?"
                sign = "+" if e.sign > 0 else "-"
                lines.append(f"  {src} ({cluster}) →{sign} {tgt} ({tgt_c}) (strength {e.weight:.2f}): {e.label}")

        all_formulas: set[str] = set()
        for nid in nodes:
            all_formulas.update(idx.node_formulas.get(nid) or [])
        if all_formulas:
            lines.append(f"Analytics formulas: {', '.join(sorted(all_formulas))}")

        summaries[cluster] = "\n".join(lines)

    return summaries

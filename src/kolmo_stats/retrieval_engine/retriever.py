"""
GraphRetriever — delegates all hot paths to the C++ core.

local  : multi-search seeds → C++ bfs_traverse
global : community matching → C++ cluster_index lookup
drift  : C++ embed_query → C++ drift_search

The Python layer only handles:
  - Multi-mode search (exact alias + token hits + TF-IDF, combining C++ calls)
  - Scoring / ranking
  - Building the Python-friendly RetrievalResult
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from kolmo_stats.retrieval_engine._core import (
    GraphIndex as _CppGraphIndex,
    TFIDFIndex as _CppTFIDFIndex,
    bfs_traverse,
    drift_search,
)


@dataclass
class RetrievalResult:
    mode: str
    query: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    communities: list[str]
    formulas: list[str]
    drift_path: list[str] = field(default_factory=list)


class GraphRetriever:
    def __init__(
        self,
        index: _CppGraphIndex,
        embedder: _CppTFIDFIndex,
        communities: dict[str, str],
    ):
        self._idx = index
        self._emb = embedder
        self._communities = communities

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def local_retrieve(self, query: str, depth: int = 2, top_k: int = 3) -> RetrievalResult:
        seeds = self._search(query, top_k=top_k)
        # C++ BFS — returns dict[node_id, score]
        visited: dict[str, float] = bfs_traverse(self._idx, seeds, depth, 0.65)
        edge_set = self._edges_for(visited)
        return self._build("local", query, visited, edge_set)

    def global_retrieve(self, query: str, top_k_communities: int = 3) -> RetrievalResult:
        q_tokens = set(re.sub(r"[^a-z\s]", "", query.lower()).split())

        comm_scores: dict[str, float] = {}
        for cluster, summary in self._communities.items():
            overlap = float(len(q_tokens & set(re.sub(r"[^a-z\s]", "", summary.lower()).split())))
            t1 = sum(
                1 for nid in (self._idx.cluster_index.get(cluster) or [])
                if self._idx.nodes[nid].tier == 1
            )
            comm_scores[cluster] = overlap + t1 * 0.5

        top_clusters = sorted(comm_scores, key=lambda c: -comm_scores[c])[:top_k_communities]

        visited: dict[str, float] = {}
        for cluster in top_clusters:
            for nid in (self._idx.cluster_index.get(cluster) or []):
                tier = self._idx.nodes[nid].tier
                visited[nid] = max(visited.get(nid, 0.0), float(4 - tier))

        edge_set = {
            (src, tgt)
            for (src, tgt) in self._all_edges_between(visited)
        }

        result = self._build("global", query, visited, edge_set)
        result.communities = [self._communities[c] for c in top_clusters]
        return result

    def drift_retrieve(self, query: str, steps: int = 6) -> RetrievalResult:
        seeds = self._search(query, top_k=1)
        if not seeds:
            return self.local_retrieve(query)

        seed_id = seeds[0][0]
        # C++ embed + C++ drift
        qvec = self._emb.embed_query(query)
        path: list[str] = drift_search(self._idx, self._emb, seed_id, qvec, steps)

        visited: dict[str, float] = {nid: 1.0 / (i + 1) for i, nid in enumerate(path)}
        edge_set: set[tuple[str, str]] = set()
        for i in range(len(path) - 1):
            src, tgt = path[i], path[i + 1]
            for pair in ((src, tgt), (tgt, src)):
                if self._idx.has_edge(*pair):
                    edge_set.add(pair)
                    break

        result = self._build("drift", query, visited, edge_set)
        result.drift_path = path
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        """
        Layered search: exact alias → C++ token_search → C++ TF-IDF.
        Returns (node_id, score) pairs.
        """
        scores: dict[str, float] = {}

        # 1. Exact alias / id (O(1) C++ hash map)
        resolved = self._idx.resolve_alias(query.strip().lower())
        if resolved:
            scores[resolved] = scores.get(resolved, 0.0) + 10.0

        # 2. C++ token search
        for nid, hits in self._idx.token_search(query, top_k * 4):
            scores[nid] = scores.get(nid, 0.0) + hits * 1.5

        # 3. C++ TF-IDF cosine
        for nid, sim in self._emb.top_k(query, 15):
            scores[nid] = scores.get(nid, 0.0) + sim * 3.0

        # Tier boost
        for nid in list(scores):
            tier = self._idx.nodes[nid].tier
            scores[nid] *= 1.0 + (3 - tier) * 0.08

        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return ranked[:top_k]

    def _edges_for(self, visited: dict[str, float]) -> set[tuple[str, str]]:
        edges: set[tuple[str, str]] = set()
        for nid in visited:
            adj = self._idx.adjacency.get(nid)
            if not adj:
                continue
            for neighbor in list(adj.drivers) + list(adj.outputs):
                if neighbor in visited:
                    for pair in ((nid, neighbor), (neighbor, nid)):
                        if self._idx.has_edge(*pair):
                            edges.add(pair)
                            break
        return edges

    def _all_edges_between(self, visited: dict[str, float]):
        for nid in visited:
            adj = self._idx.adjacency.get(nid)
            if not adj:
                continue
            for nb in list(adj.drivers) + list(adj.outputs):
                if nb in visited:
                    for pair in ((nid, nb), (nb, nid)):
                        if self._idx.has_edge(*pair):
                            yield pair
                            break

    def _build(
        self,
        mode: str,
        query: str,
        visited: dict[str, float],
        edge_set: set[tuple[str, str]],
    ) -> RetrievalResult:
        nodes = self._node_list(visited)
        edges = self._edge_list(edge_set)
        formulas = self._collect_formulas(visited)
        clusters_hit = {self._idx.nodes[nid].cluster for nid in visited if nid in self._idx.nodes}
        communities = [self._communities[c] for c in clusters_hit if c in self._communities]
        return RetrievalResult(mode=mode, query=query, nodes=nodes,
                               edges=edges, communities=communities, formulas=formulas)

    def _node_list(self, scored: dict[str, float]) -> list[dict[str, Any]]:
        out = []
        for nid, score in sorted(
            scored.items(),
            key=lambda x: (-x[1], self._idx.nodes.get(x[0], type("", (), {"tier": 3})()).tier, x[0]),
        ):
            meta = self._idx.nodes.get(nid)
            if meta is None:
                continue
            out.append({
                "id": nid,
                "label": meta.label,
                "cluster": meta.cluster,
                "tier": meta.tier,
                "unit": meta.unit,
                "description": meta.description,
                "strategy_hint": meta.strategy_hint,
                "aliases": list(meta.aliases),
                "data_bindings": [],  # raw bindings not stored in C++ index
                "score": round(score, 4),
            })
        return out

    def _edge_list(self, edge_set: set[tuple[str, str]]) -> list[dict[str, Any]]:
        out = []
        for src, tgt in sorted(edge_set):
            e = self._idx.get_edge(src, tgt)
            if e is None:
                continue
            out.append({
                "source": src,
                "target": tgt,
                "weight": e.weight,
                "sign": e.sign,
                "label": e.label,
                "rationale": e.rationale,
            })
        out.sort(key=lambda x: -x["weight"])
        return out

    def _collect_formulas(self, node_ids: dict[str, float]) -> list[str]:
        seen: set[str] = set()
        for nid in node_ids:
            seen.update(self._idx.node_formulas.get(nid) or [])
        return sorted(seen)

"""
Naive RAG — baseline for comparison against kolmo GraphRAG.

Approach:
  1. Flatten every graph node into a plain text "document chunk"
  2. Build a TF-IDF index over those chunks (no graph structure, no communities)
  3. At query time: cosine similarity → top-K chunks → concatenate as context

No relationships, no edge rationale, no drift, no community summaries.
This is what you get if you ignore the graph and treat it as a document store.
"""
from __future__ import annotations

import re
import math
from typing import Any


def _tokenize(text: str) -> list[str]:
    return [t for t in re.sub(r"[^a-z0-9]", " ", text.lower()).split() if len(t) > 1]


class NaiveRAG:
    """
    Treats each graph node as a flat text document.
    No edges, no communities, no graph traversal — pure cosine similarity.
    """

    def __init__(self, graph=None):
        if graph is None:
            from kolmo_stats.graph.market_graph import build_market_graph
            graph = build_market_graph()

        self._chunks: list[dict[str, Any]] = []
        self._matrix: list[list[float]] = []
        self._vocab: dict[str, int] = {}
        self._build(graph)

    def _build(self, graph) -> None:
        # Step 1: flatten nodes → text chunks
        for node_id, attrs in graph.nodes(data=True):
            text = " ".join(filter(None, [
                str(attrs.get("label", "")),
                str(attrs.get("description", "")),
                str(attrs.get("strategy_hint", "")),
                " ".join(str(a) for a in (attrs.get("aliases") or [])),
                " ".join(str(f) for f in (attrs.get("related_formulas") or [])),
                str(attrs.get("cluster", "")),
            ]))
            self._chunks.append({
                "id": node_id,
                "label": attrs.get("label", node_id),
                "cluster": attrs.get("cluster", ""),
                "tier": attrs.get("tier", 3),
                "text": text,
                "description": attrs.get("description", ""),
                "strategy_hint": attrs.get("strategy_hint", ""),
            })

        # Step 2: TF-IDF (same algorithm as C++ core, in pure Python)
        tokenized = [_tokenize(c["text"]) for c in self._chunks]
        N = len(self._chunks)

        all_toks: set[str] = set()
        for toks in tokenized:
            all_toks.update(toks)
        self._vocab = {t: i for i, t in enumerate(sorted(all_toks))}
        V = len(self._vocab)

        # TF
        tf = [[0.0] * V for _ in range(N)]
        for i, toks in enumerate(tokenized):
            for tok in toks:
                if tok in self._vocab:
                    tf[i][self._vocab[tok]] += 1.0
            s = sum(tf[i])
            if s > 0:
                tf[i] = [v / s for v in tf[i]]

        # IDF
        idf = [0.0] * V
        for j in range(V):
            df = sum(1 for i in range(N) if tf[i][j] > 0)
            idf[j] = math.log((N + 1) / (df + 1)) + 1.0

        # TF-IDF + L2 normalise
        self._matrix = [[tf[i][j] * idf[j] for j in range(V)] for i in range(N)]
        for i in range(N):
            norm = math.sqrt(sum(v * v for v in self._matrix[i]))
            if norm > 0:
                self._matrix[i] = [v / norm for v in self._matrix[i]]

    def _embed_query(self, query: str) -> list[float]:
        toks = _tokenize(query)
        V = len(self._vocab)
        vec = [0.0] * V
        for tok in toks:
            if tok in self._vocab:
                vec[self._vocab[tok]] += 1.0
        s = sum(vec)
        if s > 0:
            vec = [v / s for v in vec]
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def retrieve(self, query: str, top_k: int = 10) -> dict[str, Any]:
        qvec = self._embed_query(query)

        scores = [
            sum(self._matrix[i][j] * qvec[j] for j in range(len(qvec)))
            for i in range(len(self._chunks))
        ]

        ranked = sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]
        hits = [
            {**self._chunks[i], "score": round(scores[i], 4)}
            for i in ranked
            if scores[i] > 0
        ]
        return {
            "query": query,
            "mode": "naive_tfidf",
            "chunks": hits,
            "context": self._format(hits),
        }

    def _format(self, hits: list[dict]) -> str:
        lines = ["[RETRIEVED CHUNKS — no graph structure]"]
        for h in hits:
            lines.append(f"• {h['id']} ({h['cluster']}, tier {h['tier']}): {h['description']}")
            if h.get("strategy_hint"):
                lines.append(f"  {h['strategy_hint']}")
        return "\n".join(lines)

    @property
    def vocab_size(self) -> int:
        return len(self._vocab)

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

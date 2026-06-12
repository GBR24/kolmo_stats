"""
Builds a kolmo._core.GraphIndex from a NetworkX DiGraph.

The C++ GraphIndex owns all precomputed lookup structures. This module is
the only place that touches NetworkX — after build() everything goes through
the C++ object.
"""
from __future__ import annotations

import networkx as nx

from kolmo_stats.retrieval_engine._core import GraphIndex as _CppGraphIndex


def build_index(graph: nx.DiGraph) -> _CppGraphIndex:
    idx = _CppGraphIndex()

    for node_id, attrs in graph.nodes(data=True):
        idx.add_node(
            id=node_id,
            label=str(attrs.get("label", node_id)),
            cluster=str(attrs.get("cluster", "")),
            tier=int(attrs.get("tier", 3)),
            unit=str(attrs.get("unit", "")),
            description=str(attrs.get("description", "")),
            strategy_hint=str(attrs.get("strategy_hint", "")),
            aliases=[str(a) for a in (attrs.get("aliases") or [])],
            formulas=[str(f) for f in (attrs.get("related_formulas") or [])],
        )

    for src, tgt, attrs in graph.edges(data=True):
        idx.add_edge(
            src=src,
            tgt=tgt,
            weight=float(attrs.get("weight", 0.0)),
            sign=int(attrs.get("sign", 1)),
            label=str(attrs.get("label", "")),
            rationale=str(attrs.get("rationale", "")),
        )

    idx.finalize()
    return idx

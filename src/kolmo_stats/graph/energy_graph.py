"""
Internal graph engine for energy market relationship graphs.

Not part of the public analytics API.

Two entry points:
- _build_energy_graph(): generic builder from node/edge dicts (used by knowledge_graph)
- _build_from_connections(): builder from the flat connection-dict format used in examples
"""
from __future__ import annotations

from typing import Any

import networkx as nx


def _build_energy_graph(
    nodes: dict[str, dict],
    edges: list[tuple],
    cluster_color: dict[str, str] | None = None,
) -> nx.DiGraph:
    """
    Build a networkx DiGraph from the NODES and EDGES format defined in
    knowledge_graph/market_graph.py.

    Parameters
    ----------
    nodes : dict
        {node_id: {"label": str, "cluster": str, "tier": int, "value": float}}
        Matches the NODES dict in market_graph.py.
    edges : list of tuples
        Each tuple: (source, target, weight, sign, label)
        Matches the EDGES list in market_graph.py.
    cluster_color : dict, optional
        {cluster_name: hex_color} for visual metadata.

    Returns
    -------
    networkx.DiGraph with full node and edge attributes.

    Examples
    --------
    >>> from kolmo_stats.graph.energy_graph import _build_energy_graph
    >>> from kolmo_stats.graph.market_graph import NODES, EDGES, CLUSTER_COLOR
    >>> G = _build_energy_graph(NODES, EDGES, CLUSTER_COLOR)
    >>> G.number_of_nodes(), G.number_of_edges()
    (50, 80)
    """
    G = nx.DiGraph()

    for nid, attrs in nodes.items():
        node_attrs = dict(attrs)
        if cluster_color and attrs.get("cluster") in cluster_color:
            node_attrs["color"] = cluster_color[attrs["cluster"]]
        G.add_node(nid, **node_attrs)

    for src, dst, weight, sign, label in edges:
        G.add_edge(src, dst, weight=weight, sign=sign, label=label)

    return G


def _build_from_connections(
    connections: list[dict[str, Any]],
    directed: bool = True,
) -> nx.DiGraph | nx.Graph:
    """
    Build a graph from a list of free-form connection dicts.

    Each dict must have "source" and "target". All other keys become
    edge attributes. Useful for ad-hoc graphs and the example in
    examples/06_energy_graph.py.

    Parameters
    ----------
    connections : list of dicts
        [{"source": str, "target": str, "weight": float, ...}]
    directed : bool

    Returns
    -------
    networkx.DiGraph or networkx.Graph
    """
    G: nx.DiGraph | nx.Graph = nx.DiGraph() if directed else nx.Graph()
    for conn in connections:
        if "source" not in conn or "target" not in conn:
            raise ValueError("Each connection dict must have 'source' and 'target' keys")
        src = conn["source"]
        tgt = conn["target"]
        attrs = {k: v for k, v in conn.items() if k not in ("source", "target")}
        G.add_edge(src, tgt, **attrs)
    return G

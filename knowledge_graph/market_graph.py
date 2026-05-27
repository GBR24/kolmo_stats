"""
Compatibility shim for the packaged Kolmo market graph.

The canonical graph now lives in ``src/kolmo_stats/graph/market_graph.yml`` and
is loaded through ``kolmo_stats.graph``. This module preserves the older
``knowledge_graph.market_graph`` names for contributors and examples.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from kolmo_stats.graph.market_graph import (
    build_market_graph,
    get_market_edges,
    get_market_nodes,
    load_market_graph_data,
)

_DATA = load_market_graph_data()

CLUSTER_COLOR: Dict[str, str] = {
    name: attrs["color"] for name, attrs in _DATA["clusters"].items()
}
NODES: Dict[str, Dict] = get_market_nodes()
EDGES: List[Tuple[str, str, float, int, str]] = get_market_edges()


def get_nodes(cluster: str = None) -> Dict[str, Dict]:
    """Return all nodes, optionally filtered by cluster."""
    return get_market_nodes(cluster=cluster)


def get_edges(source: str = None, target: str = None) -> List[Tuple]:
    """Return all edges, optionally filtered by source or target node id."""
    return get_market_edges(source=source, target=target)


def build_graph():
    """Return a networkx DiGraph of the full market relationship map."""
    return build_market_graph()

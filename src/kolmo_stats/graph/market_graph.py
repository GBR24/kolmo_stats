"""
Packaged energy market relationship graph.

The graph is descriptive: it explains which market variables influence one
another so humans, UIs, and agents can reason about strategy context. It does
not propagate shocks or estimate correlations.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from importlib import resources
from typing import Any

import networkx as nx
import yaml

from kolmo_stats.graph.energy_graph import _build_energy_graph

DATA_FILE = "market_graph.yml"


def load_market_graph_data() -> dict[str, Any]:
    """Load the YAML-backed market graph data bundled with kolmo-stats."""
    package = resources.files(__package__)
    with package.joinpath(DATA_FILE).open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return _validate_graph_data(data)


def market_graph_version() -> str:
    """Return the packaged market graph version string."""
    return str(load_market_graph_data()["version"])


def get_market_nodes(cluster: str | None = None) -> dict[str, dict[str, Any]]:
    """Return packaged graph nodes, optionally filtered by cluster."""
    nodes = deepcopy(load_market_graph_data()["nodes"])
    if cluster is None:
        return nodes
    return {nid: attrs for nid, attrs in nodes.items() if attrs.get("cluster") == cluster}


def get_market_edges(
    source: str | None = None,
    target: str | None = None,
) -> list[tuple[str, str, float, int, str]]:
    """Return packaged graph edges in the legacy tuple format."""
    edges = [
        (edge["source"], edge["target"], edge["weight"], edge["sign"], edge["label"])
        for edge in load_market_graph_data()["edges"]
    ]
    if source:
        source_id = resolve_node_id(source)
        edges = [edge for edge in edges if edge[0] == source_id]
    if target:
        target_id = resolve_node_id(target)
        edges = [edge for edge in edges if edge[1] == target_id]
    return edges


def build_market_graph() -> nx.DiGraph:
    """Build the packaged market relationship graph as a networkx DiGraph."""
    data = load_market_graph_data()
    clusters = data["clusters"]
    cluster_color = {name: attrs["color"] for name, attrs in clusters.items()}
    edge_tuples = [
        (
            edge["source"],
            edge["target"],
            edge["weight"],
            edge["sign"],
            edge["label"],
        )
        for edge in data["edges"]
    ]
    graph = _build_energy_graph(data["nodes"], edge_tuples, cluster_color)
    graph.graph["version"] = data["version"]
    graph.graph["clusters"] = deepcopy(clusters)
    for edge in data["edges"]:
        graph[edge["source"]][edge["target"]]["rationale"] = edge.get("rationale", "")
    return graph


def market_graph_json() -> dict[str, Any]:
    """
    Return an agent/UI-friendly JSON contract for the full graph.

    Nodes include direct driver/output summaries so consumers do not have to
    compute basic neighborhood metadata themselves.
    """
    data = load_market_graph_data()
    graph = build_market_graph()
    return {
        "version": data["version"],
        "clusters": deepcopy(data["clusters"]),
        "nodes": [_node_json(graph, node_id) for node_id in graph.nodes],
        "edges": [_edge_json(graph, src, dst) for src, dst in graph.edges],
        "health": graph_health(graph),
    }


def node_neighborhood(node_id: str, depth: int = 1) -> dict[str, Any]:
    """
    Return a bidirectional neighborhood around a node.

    ``depth=1`` includes direct drivers and direct outputs. Higher depths expand
    the same undirected neighborhood, while returned edges retain direction.
    """
    if depth < 1:
        raise ValueError("depth must be at least 1")

    graph = build_market_graph()
    center = resolve_node_id(node_id, graph)
    visited = {center}
    queue: deque[tuple[str, int]] = deque([(center, 0)])

    while queue:
        current, distance = queue.popleft()
        if distance >= depth:
            continue
        neighbors = set(graph.predecessors(current)) | set(graph.successors(current))
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))

    subgraph = graph.subgraph(visited).copy()
    return {
        "version": graph.graph.get("version"),
        "center": _node_json(graph, center),
        "depth": depth,
        "nodes": [_node_json(graph, node_id) for node_id in subgraph.nodes],
        "edges": [_edge_json(graph, src, dst) for src, dst in subgraph.edges],
        "drivers": [_edge_context(graph, src, center) for src in graph.predecessors(center)],
        "outputs": [_edge_context(graph, center, dst) for dst in graph.successors(center)],
    }


def agent_graph_context(node_id: str, depth: int = 1) -> dict[str, Any]:
    """
    Return concise graph context suitable for strategy-building agents.

    The payload is intentionally compact: it names the selected node, direct
    drivers, direct impacts, related formulas, and strategy hints.
    """
    neighborhood = node_neighborhood(node_id, depth=depth)
    center = neighborhood["center"]
    drivers = neighborhood["drivers"]
    outputs = neighborhood["outputs"]
    driver_bits = ", ".join(item["source_label"] for item in drivers[:6]) or "no direct drivers"
    output_bits = ", ".join(item["target_label"] for item in outputs[:6]) or "no direct outputs"
    return {
        "version": neighborhood["version"],
        "node": {
            "id": center["id"],
            "label": center["label"],
            "cluster": center["cluster"],
            "description": center["description"],
            "unit": center["unit"],
            "aliases": center["aliases"],
        },
        "summary": (
            f"{center['label']} is a {center['cluster']} node. "
            f"Direct drivers: {driver_bits}. Direct outputs: {output_bits}."
        ),
        "direct_drivers": drivers,
        "direct_outputs": outputs,
        "related_formulas": center["related_formulas"],
        "strategy_hint": center["strategy_hint"],
        "neighborhood": {
            "depth": depth,
            "node_count": len(neighborhood["nodes"]),
            "edge_count": len(neighborhood["edges"]),
        },
    }


def graph_health(graph: nx.DiGraph | None = None) -> dict[str, Any]:
    """Return simple validation and contribution-health indicators."""
    graph = graph or build_market_graph()
    missing_descriptions = [
        node_id
        for node_id, attrs in graph.nodes(data=True)
        if not str(attrs.get("description", "")).strip()
    ]
    strongest_edges = sorted(
        (
            {
                "source": src,
                "target": dst,
                "label": attrs.get("label", ""),
                "weight": attrs.get("weight", 0.0),
                "sign": attrs.get("sign", 1),
            }
            for src, dst, attrs in graph.edges(data=True)
        ),
        key=lambda item: item["weight"],
        reverse=True,
    )[:10]
    return {
        "version": graph.graph.get("version"),
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "isolated_nodes": sorted(nx.isolates(graph)),
        "missing_descriptions": missing_descriptions,
        "strongest_edges": strongest_edges,
    }


def resolve_node_id(raw: str, graph: nx.DiGraph | None = None) -> str:
    """Resolve a node id, label, or alias to the canonical node id."""
    graph = graph or build_market_graph()
    key = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    if key in graph.nodes:
        return key

    raw_l = str(raw).strip().lower()
    for node_id, attrs in graph.nodes(data=True):
        candidates = [node_id, attrs.get("label", "")]
        candidates.extend(attrs.get("aliases", []) or [])
        if raw_l in {str(candidate).strip().lower() for candidate in candidates}:
            return node_id
    raise KeyError(f"Unknown market graph node: {raw!r}")


def _node_json(graph: nx.DiGraph, node_id: str) -> dict[str, Any]:
    attrs = graph.nodes[node_id]
    drivers = [_edge_context(graph, src, node_id) for src in graph.predecessors(node_id)]
    outputs = [_edge_context(graph, node_id, dst) for dst in graph.successors(node_id)]
    return {
        "id": node_id,
        "label": attrs.get("label", node_id),
        "cluster": attrs.get("cluster", ""),
        "tier": attrs.get("tier", 3),
        "value": attrs.get("value", 0.0),
        "unit": attrs.get("unit", ""),
        "color": attrs.get("color", ""),
        "aliases": list(attrs.get("aliases", []) or []),
        "description": attrs.get("description", ""),
        "related_formulas": list(attrs.get("related_formulas", []) or []),
        "strategy_hint": attrs.get("strategy_hint", ""),
        "drivers": drivers,
        "outputs": outputs,
    }


def _edge_json(graph: nx.DiGraph, src: str, dst: str) -> dict[str, Any]:
    attrs = graph[src][dst]
    return {
        "id": f"{src}__{dst}",
        "source": src,
        "target": dst,
        "source_label": graph.nodes[src].get("label", src),
        "target_label": graph.nodes[dst].get("label", dst),
        "weight": attrs.get("weight", 0.0),
        "sign": attrs.get("sign", 1),
        "label": attrs.get("label", ""),
        "rationale": attrs.get("rationale", ""),
    }


def _edge_context(graph: nx.DiGraph, src: str, dst: str) -> dict[str, Any]:
    edge = _edge_json(graph, src, dst)
    edge["direction"] = "positive" if edge["sign"] > 0 else "negative"
    return edge


def _validate_graph_data(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("market graph YAML must be a mapping")
    for key in ("version", "clusters", "nodes", "edges"):
        if key not in data:
            raise ValueError(f"market graph YAML missing required key: {key}")

    clusters = data["clusters"]
    nodes = data["nodes"]
    if not isinstance(nodes, dict) or not nodes:
        raise ValueError("market graph YAML must define at least one node")

    for node_id, attrs in nodes.items():
        if attrs.get("cluster") not in clusters:
            raise ValueError(f"{node_id}: unknown cluster {attrs.get('cluster')!r}")
        tier = attrs.get("tier")
        if tier not in (1, 2, 3):
            raise ValueError(f"{node_id}: tier must be 1, 2, or 3")
        if "label" not in attrs or "description" not in attrs:
            raise ValueError(f"{node_id}: label and description are required")
        attrs.setdefault("aliases", [])
        attrs.setdefault("related_formulas", [])
        attrs.setdefault("strategy_hint", "")

    parsed_edges = []
    seen_edges = set()
    for raw_edge in data["edges"]:
        edge = _parse_edge(raw_edge)
        src = edge["source"]
        dst = edge["target"]
        if src not in nodes:
            raise ValueError(f"edge references unknown source node: {src}")
        if dst not in nodes:
            raise ValueError(f"edge references unknown target node: {dst}")
        if (src, dst) in seen_edges:
            raise ValueError(f"duplicate edge: {src} -> {dst}")
        seen_edges.add((src, dst))
        if not 0.0 <= edge["weight"] <= 1.0:
            raise ValueError(f"{src} -> {dst}: weight must be in [0, 1]")
        if edge["sign"] not in (-1, 1):
            raise ValueError(f"{src} -> {dst}: sign must be -1 or 1")
        parsed_edges.append(edge)

    data = deepcopy(data)
    data["edges"] = parsed_edges
    return data


def _parse_edge(raw_edge: Any) -> dict[str, Any]:
    if isinstance(raw_edge, dict):
        return {
            "source": raw_edge["source"],
            "target": raw_edge["target"],
            "weight": float(raw_edge["weight"]),
            "sign": int(raw_edge["sign"]),
            "label": str(raw_edge["label"]),
            "rationale": str(raw_edge.get("rationale", "")),
        }
    if isinstance(raw_edge, list) and len(raw_edge) in (5, 6):
        source, target, weight, sign, label, *rest = raw_edge
        return {
            "source": str(source),
            "target": str(target),
            "weight": float(weight),
            "sign": int(sign),
            "label": str(label),
            "rationale": str(rest[0]) if rest else "",
        }
    raise ValueError("each market graph edge must be a mapping or a 5/6-item list")

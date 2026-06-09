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


def market_graph_json(include_bindings: bool = True) -> dict[str, Any]:
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
        "nodes": [_node_json(graph, node_id, include_bindings=include_bindings) for node_id in graph.nodes],
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


def search_market_nodes(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Return graph nodes ranked by id, label, alias, and description matches.

    The search is intentionally deterministic so apps and agents can use it as
    a stable first pass before applying heavier LLM routing.
    """
    graph = build_market_graph()
    query_l = str(query or "").strip().lower()
    if not query_l:
        return []

    tokens = [token for token in query_l.replace("-", " ").replace("/", " ").split() if len(token) >= 3]
    scored: list[tuple[float, str]] = []
    for node_id, attrs in graph.nodes(data=True):
        label = str(attrs.get("label", ""))
        aliases = [str(alias) for alias in attrs.get("aliases", []) or []]
        description = str(attrs.get("description", ""))
        haystacks = {
            "id": node_id.replace("_", " "),
            "label": label.lower(),
            "aliases": " ".join(alias.lower() for alias in aliases),
            "description": description.lower(),
            "formulas": " ".join(str(item).lower() for item in attrs.get("related_formulas", []) or []),
        }

        score = 0.0
        if query_l == node_id or query_l == label.lower():
            score += 10.0
        if query_l in haystacks["aliases"]:
            score += 8.0
        if haystacks["id"] in query_l or haystacks["label"] in query_l:
            score += 6.0
        for token in tokens:
            if token in haystacks["id"]:
                score += 2.5
            if token in haystacks["label"]:
                score += 2.0
            if token in haystacks["aliases"]:
                score += 1.8
            if token in haystacks["description"]:
                score += 0.7
            if token in haystacks["formulas"]:
                score += 0.6
        if score > 0:
            scored.append((score, node_id))

    scored.sort(key=lambda item: (-item[0], graph.nodes[item[1]].get("tier", 3), item[1]))
    return [
        {
            **_node_json(graph, node_id),
            "match_score": round(score, 3),
        }
        for score, node_id in scored[: max(1, limit)]
    ]


def graph_context_bundle(
    query: str | None = None,
    node_ids: list[str] | None = None,
    depth: int = 1,
    limit: int = 5,
) -> dict[str, Any]:
    """
    Return a compact graph context bundle for agents.

    The bundle includes matched nodes, their local directed neighborhood, data
    bindings, related formulas, and relationship metadata. If no query match is
    found, callers receive an empty bundle rather than an exception.
    """
    graph = build_market_graph()
    resolved: list[str] = []
    errors: list[str] = []

    for raw in node_ids or []:
        try:
            resolved.append(resolve_node_id(raw, graph))
        except KeyError as exc:
            errors.append(str(exc))

    if not resolved and query:
        resolved.extend(item["id"] for item in search_market_nodes(query, limit=limit))

    resolved = list(dict.fromkeys(resolved))[: max(1, limit)]
    if not resolved:
        return {
            "version": graph.graph.get("version"),
            "query": query or "",
            "matched_nodes": [],
            "nodes": [],
            "edges": [],
            "data_bindings": [],
            "related_formulas": [],
            "errors": errors,
            "health": graph_health(graph),
        }

    visited: set[str] = set(resolved)
    queue: deque[tuple[str, int]] = deque((node_id, 0) for node_id in resolved)
    while queue:
        current, distance = queue.popleft()
        if distance >= depth:
            continue
        for neighbor in set(graph.predecessors(current)) | set(graph.successors(current)):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))

    subgraph = graph.subgraph(visited).copy()
    nodes = [_node_json(graph, node_id) for node_id in subgraph.nodes]
    edges = [_edge_json(graph, src, dst) for src, dst in subgraph.edges]
    bindings = []
    formulas = []
    for node in nodes:
        for binding in node.get("data_bindings", []):
            bindings.append({"node_id": node["id"], "node_label": node["label"], **binding})
        formulas.extend(node.get("related_formulas", []) or [])

    return {
        "version": graph.graph.get("version"),
        "query": query or "",
        "matched_nodes": [_node_json(graph, node_id) for node_id in resolved],
        "nodes": nodes,
        "edges": edges,
        "data_bindings": bindings,
        "related_formulas": list(dict.fromkeys(formulas)),
        "errors": errors,
        "health": graph_health(graph),
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


def _node_json(graph: nx.DiGraph, node_id: str, include_bindings: bool = True) -> dict[str, Any]:
    attrs = graph.nodes[node_id]
    drivers = [_edge_context(graph, src, node_id) for src in graph.predecessors(node_id)]
    outputs = [_edge_context(graph, node_id, dst) for dst in graph.successors(node_id)]
    node = {
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
    if include_bindings:
        node["data_bindings"] = deepcopy(attrs.get("data_bindings", []) or [])
    return node


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
        attrs["data_bindings"] = _normalise_data_bindings(node_id, attrs.get("data_bindings"))

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


_DEFAULT_NODE_BINDINGS: dict[str, list[dict[str, Any]]] = {
    "brent": [
        {"kind": "live_price", "ref": "live_prices.code", "symbol": "BRENT_CRUDE_USD", "unit": "USD/bbl", "frequency": "intraday", "freshness_sla": "4h", "required": True},
        {"kind": "price_history", "ref": "price_daily_ohlcv.code", "symbol": "BRENT_CRUDE_USD", "unit": "USD/bbl", "frequency": "daily", "freshness_sla": "24h", "required": False},
    ],
    "wti": [
        {"kind": "live_price", "ref": "live_prices.code", "symbol": "WTI_USD", "unit": "USD/bbl", "frequency": "intraday", "freshness_sla": "4h", "required": True},
        {"kind": "price_history", "ref": "price_daily_ohlcv.code", "symbol": "WTI_USD", "unit": "USD/bbl", "frequency": "daily", "freshness_sla": "24h", "required": False},
    ],
    "urals": [{"kind": "live_price", "ref": "live_prices.code", "symbol": "URALS_CRUDE_USD", "unit": "USD/bbl", "frequency": "intraday", "freshness_sla": "12h", "required": False}],
    "dubai_oman": [{"kind": "live_price", "ref": "live_prices.code", "symbol": "DUBAI_CRUDE_USD", "unit": "USD/bbl", "frequency": "intraday", "freshness_sla": "12h", "required": False}],
    "rbob": [{"kind": "live_price", "ref": "live_prices.code", "symbol": "GASOLINE_USD", "unit": "USD/gal", "frequency": "intraday", "freshness_sla": "4h", "required": False}],
    "ulsd": [{"kind": "live_price", "ref": "live_prices.code", "symbol": "DIESEL_USD", "unit": "USD/gal", "frequency": "intraday", "freshness_sla": "4h", "required": False}],
    "jet_fuel": [{"kind": "live_price", "ref": "live_prices.code", "symbol": "JET_FUEL_USD", "unit": "USD/gal", "frequency": "intraday", "freshness_sla": "12h", "required": False}],
    "ttf_gas": [{"kind": "live_price", "ref": "live_prices.code", "symbol": "DUTCH_TTF_EUR", "unit": "EUR/MWh", "frequency": "intraday", "freshness_sla": "4h", "required": False}],
    "henry_hub": [{"kind": "live_price", "ref": "live_prices.code", "symbol": "NATURAL_GAS_USD", "unit": "USD/MMBtu", "frequency": "intraday", "freshness_sla": "4h", "required": False}],
    "gasoline_crack": [{"kind": "formula", "ref": "kolmo_stats.crack_spread", "symbol": "GASOLINE_CRACK", "unit": "USD/bbl", "frequency": "on_demand", "freshness_sla": "derived", "required": False}],
    "diesel_crack": [{"kind": "formula", "ref": "kolmo_stats.crack_spread", "symbol": "DIESEL_CRACK", "unit": "USD/bbl", "frequency": "on_demand", "freshness_sla": "derived", "required": False}],
    "jet_crack": [{"kind": "formula", "ref": "kolmo_stats.crack_spread", "symbol": "JET_CRACK", "unit": "USD/bbl", "frequency": "on_demand", "freshness_sla": "derived", "required": False}],
    "brent_spread": [{"kind": "formula", "ref": "kolmo_stats.calendar_spread", "symbol": "BRENT", "unit": "USD/bbl", "frequency": "on_demand", "freshness_sla": "derived", "required": False}],
    "cushing_inv": [{"kind": "fundamental", "ref": "fundamentals.eia_petroleum", "symbol": "CUSHING_STOCKS", "unit": "MMbbl", "frequency": "weekly", "freshness_sla": "8d", "required": False}],
    "oecd_inventories": [{"kind": "fundamental", "ref": "fundamentals.inventory", "symbol": "OIL_INVENTORIES", "unit": "pressure", "frequency": "weekly", "freshness_sla": "8d", "required": False}],
    "gasoline_inv": [{"kind": "fundamental", "ref": "fundamentals.eia_petroleum", "symbol": "GASOLINE_STOCKS", "unit": "MMbbl", "frequency": "weekly", "freshness_sla": "8d", "required": False}],
    "distillate_inv": [{"kind": "fundamental", "ref": "fundamentals.eia_petroleum", "symbol": "DISTILLATE_STOCKS", "unit": "MMbbl", "frequency": "weekly", "freshness_sla": "8d", "required": False}],
    "refinery_runs": [{"kind": "fundamental", "ref": "fundamentals.eia_petroleum", "symbol": "REFINERY_UTILIZATION", "unit": "%", "frequency": "weekly", "freshness_sla": "8d", "required": False}],
    "opec_policy": [{"kind": "news", "ref": "events.keyword", "symbol": "OPEC", "unit": "event", "frequency": "event", "freshness_sla": "14d", "required": False}],
    "russia_sanctions": [{"kind": "news", "ref": "events.keyword", "symbol": "RUSSIA_SANCTIONS", "unit": "event", "frequency": "event", "freshness_sla": "14d", "required": False}],
    "iran_sanctions": [{"kind": "news", "ref": "events.keyword", "symbol": "IRAN_SANCTIONS", "unit": "event", "frequency": "event", "freshness_sla": "14d", "required": False}],
    "hormuz_risk": [{"kind": "news", "ref": "events.keyword", "symbol": "HORMUZ", "unit": "event", "frequency": "event", "freshness_sla": "14d", "required": False}],
    "red_sea": [{"kind": "news", "ref": "events.keyword", "symbol": "RED_SEA", "unit": "event", "frequency": "event", "freshness_sla": "14d", "required": False}],
    "usd_index": [{"kind": "macro", "ref": "live_prices.code", "symbol": "DXY", "unit": "index", "frequency": "daily", "freshness_sla": "24h", "required": False}],
}


def _normalise_data_bindings(node_id: str, raw: Any) -> list[dict[str, Any]]:
    bindings = deepcopy(raw if isinstance(raw, list) else _DEFAULT_NODE_BINDINGS.get(node_id, []))
    normalised: list[dict[str, Any]] = []
    for binding in bindings:
        if not isinstance(binding, dict):
            raise ValueError(f"{node_id}: data_bindings entries must be mappings")
        out = {
            "kind": str(binding.get("kind", "")).strip(),
            "ref": str(binding.get("ref", "")).strip(),
            "symbol": str(binding.get("symbol", node_id)).strip(),
            "unit": str(binding.get("unit", "")).strip(),
            "frequency": str(binding.get("frequency", "unknown")).strip(),
            "freshness_sla": str(binding.get("freshness_sla", "")).strip(),
            "required": bool(binding.get("required", False)),
        }
        if not out["kind"] or not out["ref"]:
            raise ValueError(f"{node_id}: data binding requires kind and ref")
        normalised.append(out)
    return normalised


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

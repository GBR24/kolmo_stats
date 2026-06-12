import pytest

from kolmo_stats.graph import (
    agent_graph_context,
    build_market_graph,
    graph_context_bundle,
    graph_health,
    load_market_graph_data,
    market_graph_json,
    node_neighborhood,
    resolve_node_id,
    search_market_nodes,
)


MIN_MARKET_GRAPH_NODES = 153
MIN_MARKET_GRAPH_EDGES = 340


def test_market_graph_yaml_loads_and_builds():
    data = load_market_graph_data()
    graph = build_market_graph()

    assert data["version"]
    assert graph.number_of_nodes() >= MIN_MARKET_GRAPH_NODES
    assert graph.number_of_edges() >= MIN_MARKET_GRAPH_EDGES
    assert graph.nodes["brent"]["description"]
    assert graph["global_demand"]["brent"]["weight"] == pytest.approx(0.90)
    assert graph["wti"]["wti_midland"]["label"] == "WTI anchor"
    assert graph["refining_margins"]["crude_runs"]["sign"] == 1
    assert graph["ttf_gas"]["gas_to_oil_switching"]["weight"] == pytest.approx(0.72)


def test_market_graph_json_contract_and_health():
    payload = market_graph_json()
    health = payload["health"]

    assert payload["version"]
    assert {"nodes", "edges", "clusters", "health"} <= set(payload)
    assert health["isolated_nodes"] == []
    assert health["missing_descriptions"] == []
    assert health["node_count"] >= MIN_MARKET_GRAPH_NODES
    assert health["edge_count"] >= MIN_MARKET_GRAPH_EDGES
    assert payload["nodes"][0]["drivers"] is not None
    brent = next(node for node in payload["nodes"] if node["id"] == "brent")
    assert brent["data_bindings"]
    assert brent["data_bindings"][0]["kind"] == "live_price"


def test_market_graph_expansion_nodes_are_connected():
    graph = build_market_graph()

    for node_id in [
        "wti_midland",
        "gasoil",
        "refining_margins",
        "us_crude_stocks",
        "tanker_rates",
        "jkm_lng",
        "industrial_production",
        "hurricane_risk",
    ]:
        assert node_id in graph.nodes
        assert graph.in_degree(node_id) + graph.out_degree(node_id) > 0


def test_graph_search_and_context_bundle_include_bindings():
    matches = search_market_nodes("diesel crack and refinery runs")
    assert matches
    assert matches[0]["id"] in {"diesel_crack", "refinery_runs"}

    bundle = graph_context_bundle("diesel crack and refinery runs", depth=1)
    assert bundle["version"]
    assert bundle["matched_nodes"]
    assert bundle["nodes"]
    assert bundle["edges"]
    assert bundle["data_bindings"]
    assert "crack_spread" in bundle["related_formulas"]


def test_node_neighborhood_and_alias_resolution():
    assert resolve_node_id("TTF") == "ttf_gas"
    hood = node_neighborhood("diesel crack")

    assert hood["center"]["id"] == "diesel_crack"
    assert any(edge["source"] == "mfg_pmi" for edge in hood["drivers"])
    assert any(edge["target"] == "brent" for edge in hood["outputs"])


def test_agent_graph_context_for_strategy_builder_inputs():
    for query in ["Brent", "WTI", "diesel crack", "TTF", "naphtha"]:
        context = agent_graph_context(query)
        assert context["node"]["id"]
        assert context["summary"]
        assert "related_formulas" in context
        assert "strategy_hint" in context


def test_graph_health_reports_strong_edges():
    health = graph_health()
    assert health["strongest_edges"]
    assert health["strongest_edges"][0]["weight"] == pytest.approx(0.90)

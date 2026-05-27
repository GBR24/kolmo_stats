import pytest

from kolmo_stats.graph import (
    agent_graph_context,
    build_market_graph,
    graph_health,
    load_market_graph_data,
    market_graph_json,
    node_neighborhood,
    resolve_node_id,
)


def test_market_graph_yaml_loads_and_builds():
    data = load_market_graph_data()
    graph = build_market_graph()

    assert data["version"]
    assert graph.number_of_nodes() == 53
    assert graph.number_of_edges() == 88
    assert graph.nodes["brent"]["description"]
    assert graph["global_demand"]["brent"]["weight"] == pytest.approx(0.90)


def test_market_graph_json_contract_and_health():
    payload = market_graph_json()
    health = payload["health"]

    assert payload["version"]
    assert {"nodes", "edges", "clusters", "health"} <= set(payload)
    assert health["isolated_nodes"] == []
    assert health["missing_descriptions"] == []
    assert health["node_count"] == 53
    assert health["edge_count"] == 88
    assert payload["nodes"][0]["drivers"] is not None


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

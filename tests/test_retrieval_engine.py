"""Tests for the GraphRAG retrieval engine."""
import pytest
from kolmo_stats.retrieval_engine import RetrievalEngine, RetrievalResult


@pytest.fixture(scope="module")
def engine():
    return RetrievalEngine()


# ------------------------------------------------------------------
# Index
# ------------------------------------------------------------------

def test_index_stats(engine):
    stats = engine.index_stats()
    assert stats["node_count"] > 0
    assert stats["edge_count"] > 0
    assert stats["cluster_count"] >= 6
    assert stats["vocab_size"] > 10


def test_community_summaries_exist(engine):
    summaries = engine.community_summaries()
    assert len(summaries) >= 6
    for cluster, text in summaries.items():
        assert cluster.upper() in text
        assert len(text) > 50


# ------------------------------------------------------------------
# Retrieval — local
# ------------------------------------------------------------------

def test_local_retrieve_returns_result(engine):
    result = engine.retrieve("diesel crack margins")
    assert isinstance(result, RetrievalResult)
    assert result.mode == "local"
    assert len(result.nodes) > 0
    assert len(result.edges) > 0


def test_local_retrieve_finds_diesel(engine):
    result = engine.retrieve("diesel crack", mode="local")
    node_ids = [n["id"] for n in result.nodes]
    assert "diesel_crack" in node_ids


def test_local_retrieve_includes_formulas(engine):
    result = engine.retrieve("brent crude price", mode="local")
    assert len(result.formulas) > 0


def test_local_retrieve_node_shape(engine):
    result = engine.retrieve("brent", mode="local")
    node = result.nodes[0]
    for key in ("id", "label", "cluster", "tier", "description", "score"):
        assert key in node


def test_local_retrieve_edge_shape(engine):
    result = engine.retrieve("brent crude", mode="local")
    if result.edges:
        edge = result.edges[0]
        for key in ("source", "target", "weight", "sign", "label"):
            assert key in edge


def test_local_retrieve_depth_1_vs_2(engine):
    r1 = engine.retrieve("brent", mode="local", depth=1)
    r2 = engine.retrieve("brent", mode="local", depth=2)
    assert len(r2.nodes) >= len(r1.nodes)


# ------------------------------------------------------------------
# Retrieval — global
# ------------------------------------------------------------------

def test_global_retrieve_returns_result(engine):
    result = engine.retrieve("full market overview", mode="global")
    assert isinstance(result, RetrievalResult)
    assert result.mode == "global"
    assert len(result.nodes) > 0
    assert len(result.communities) > 0


def test_global_retrieve_has_community_text(engine):
    result = engine.retrieve("energy market overview", mode="global")
    for text in result.communities:
        assert "COMMUNITY:" in text


# ------------------------------------------------------------------
# Retrieval — drift
# ------------------------------------------------------------------

def test_drift_retrieve_returns_path(engine):
    result = engine.retrieve("explore macro to crude connections", mode="drift")
    assert isinstance(result, RetrievalResult)
    assert result.mode == "drift"
    assert len(result.drift_path) >= 2


def test_drift_path_nodes_in_result(engine):
    result = engine.retrieve("explore macro to crude connections", mode="drift")
    node_ids = {n["id"] for n in result.nodes}
    for nid in result.drift_path:
        assert nid in node_ids


# ------------------------------------------------------------------
# Auto classification
# ------------------------------------------------------------------

def test_auto_local(engine):
    result = engine.retrieve("what is driving brent prices?")
    assert result.mode == "local"


def test_auto_global(engine):
    result = engine.retrieve("give me a full market overview")
    assert result.mode == "global"


def test_auto_drift(engine):
    result = engine.retrieve("explore connections between energy clusters", mode="drift")
    assert result.mode == "drift"


# ------------------------------------------------------------------
# Context text
# ------------------------------------------------------------------

def test_context_text_contains_entities(engine):
    result = engine.retrieve("gasoline crack", mode="local")
    text = engine.context_text(result)
    assert "[ENTITIES]" in text
    assert "[RELATIONSHIPS]" in text


def test_context_text_contains_formulas(engine):
    result = engine.retrieve("brent", mode="local")
    text = engine.context_text(result)
    assert "FORMULAS" in text


def test_drift_context_text_shows_path(engine):
    result = engine.retrieve("explore links", mode="drift")
    text = engine.context_text(result)
    assert "DISCOVERY PATH" in text or len(result.drift_path) == 0


# ------------------------------------------------------------------
# Inspect
# ------------------------------------------------------------------

def test_inspect_shape(engine):
    info = engine.inspect("opec policy impact on crude supply")
    for key in ("mode", "node_count", "edge_count", "token_estimate", "formulas"):
        assert key in info
    assert info["token_estimate"] > 0


def test_inspect_community_clusters(engine):
    info = engine.inspect("market overview", mode="global")
    assert isinstance(info["community_clusters"], list)
    assert len(info["community_clusters"]) > 0


# ------------------------------------------------------------------
# Edge cases
# ------------------------------------------------------------------

def test_retrieve_unknown_query_does_not_raise(engine):
    result = engine.retrieve("xyzzy frobnicator unknown")
    assert isinstance(result, RetrievalResult)


def test_retrieve_single_word(engine):
    result = engine.retrieve("brent")
    assert len(result.nodes) > 0


def test_custom_graph(engine):
    from kolmo_stats.graph.market_graph import build_market_graph
    g = build_market_graph()
    custom_engine = RetrievalEngine(graph=g)
    result = custom_engine.retrieve("wti crude")
    assert len(result.nodes) > 0

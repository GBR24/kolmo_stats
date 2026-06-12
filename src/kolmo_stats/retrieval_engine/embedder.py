"""
Wraps kolmo._core.TFIDFIndex — builds the TF-IDF matrix from node texts.
"""
from __future__ import annotations

from kolmo_stats.retrieval_engine._core import GraphIndex as _CppGraphIndex
from kolmo_stats.retrieval_engine._core import TFIDFIndex as _CppTFIDFIndex


def build_embedder(index: _CppGraphIndex) -> _CppTFIDFIndex:
    emb = _CppTFIDFIndex()
    node_ids = list(index.node_ids)
    texts = [index.node_text(nid) for nid in node_ids]
    emb.build(node_ids, texts)
    return emb

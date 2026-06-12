"""
Query classifier — routes a natural language query to the right retrieval mode.
Works directly against the C++ GraphIndex.
"""
from __future__ import annotations

import re

from kolmo_stats.retrieval_engine._core import GraphIndex as _CppGraphIndex

_GLOBAL = {
    "overview", "market", "all", "everything", "broad", "general", "full",
    "summary", "landscape", "regime", "environment", "themes", "across",
    "whole", "entire", "global", "situation",
}
_DRIFT = {
    "related", "connects", "between", "link", "path", "chain", "through",
    "explore", "discover", "traverse", "journey", "connections", "network",
}
_LOCAL = {
    "what", "why", "how", "driving", "drive", "impact", "affect",
    "cause", "risk", "price", "level", "current", "now", "today",
}


class QueryPlanner:
    def __init__(self, index: _CppGraphIndex):
        self._index = index

    def classify(self, query: str) -> str:
        tokens = set(re.sub(r"[^a-z\s]", "", query.lower()).split())

        g_score = len(tokens & _GLOBAL)
        d_score = len(tokens & _DRIFT)

        # A resolved entity strongly anchors to local
        has_entity = bool(self._index.resolve_alias(query.strip().lower())) or any(
            self._index.resolve_alias(t) for t in tokens
        )

        if d_score >= 2 or (d_score >= 1 and not has_entity):
            return "drift"
        if g_score >= 2 or (g_score >= 1 and not has_entity):
            return "global"
        return "local"

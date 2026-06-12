"""
Converts a RetrievalResult into an LLM-ready context string.

The system prompt teaches the model how to reason about the energy graph.
The context formatter assembles retrieved entities, relationships, community
summaries, and formula recommendations into a structured block that drops
cleanly into a user message.
"""
from __future__ import annotations

from .retriever import RetrievalResult

SYSTEM_PROMPT = """\
You are an expert energy market analyst with deep knowledge of crude oil, refined products,
natural gas, LNG, and macro markets. You have access to a structured knowledge graph of
energy market relationships and quantitative analytics formulas from the kolmo_stats library.

When answering:
- Cite specific node relationships and edge strengths as evidence for your reasoning
- Recommend kolmo_stats formulas when quantitative analysis would help the user
- Distinguish causal (high-weight) edges from weak correlations
- Flag geopolitical or macro risks that interact with the query
- Be precise about units, market conventions, and directionality (sign of edges)
- If the drift path is shown, explain what the traversal reveals about market linkages
"""


class ContextBuilder:
    def to_text(self, result: RetrievalResult) -> str:
        sections: list[str] = []

        if result.drift_path:
            sections.append(
                "[DISCOVERY PATH]\n"
                + " → ".join(result.drift_path)
                + "\nThe retrieval drifted through the graph following the strongest "
                  "semantic + relationship connections to your query."
            )

        if result.nodes:
            lines = ["[ENTITIES]"]
            for n in result.nodes:
                tier_tag = f"tier {n['tier']}" if n.get("tier") else ""
                header = f"• {n['id']} ({n['cluster']}, {tier_tag}, {n['unit']})"
                lines.append(header)
                if n.get("description"):
                    lines.append(f"  {n['description']}")
                if n.get("strategy_hint"):
                    lines.append(f"  Strategy: {n['strategy_hint']}")
                if n.get("data_bindings"):
                    symbols = ", ".join(
                        b.get("symbol", "") for b in n["data_bindings"] if b.get("symbol")
                    )
                    if symbols:
                        lines.append(f"  Data: {symbols}")
            sections.append("\n".join(lines))

        if result.edges:
            lines = ["[RELATIONSHIPS]"]
            for e in result.edges:
                sign = "+" if e.get("sign", 1) > 0 else "-"
                lines.append(
                    f"• {e['source']} →{sign} {e['target']} "
                    f"(strength {e['weight']:.2f}) — {e['label']}"
                )
                if e.get("rationale"):
                    lines.append(f"  {e['rationale']}")
            sections.append("\n".join(lines))

        if result.communities:
            comm_block = ["[MARKET COMMUNITIES]"]
            for summary in result.communities:
                comm_block.append(summary)
                comm_block.append("")
            sections.append("\n".join(comm_block))

        if result.formulas:
            sections.append(
                "[AVAILABLE KOLMO_STATS FORMULAS]\n"
                + "\n".join(f"• {f}" for f in result.formulas)
            )

        return "\n\n".join(sections)

    def to_messages(self, query: str, result: RetrievalResult) -> list[dict]:
        """Return an Anthropic/OpenAI-compatible messages list."""
        context = self.to_text(result)
        return [{"role": "user", "content": f"{context}\n\n---\nQuery: {query}"}]

    def token_estimate(self, result: RetrievalResult) -> int:
        """Rough token count — 1 token ≈ 4 chars."""
        return len(self.to_text(result)) // 4

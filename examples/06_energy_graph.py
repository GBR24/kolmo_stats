"""
Example 6 — Energy Market Graph (experimental / internal)

Neither function is part of the public analytics API.
- _build_from_connections: generic builder from free-form connection dicts
- _build_energy_graph: builds the full market graph from knowledge_graph NODES/EDGES
"""
from kolmo_stats.graph.energy_graph import _build_from_connections, _build_energy_graph

connections = [
    {
        "source": "Brent",
        "target": "Gasoil",
        "relationship": "refinery_margin_link",
        "weight": 0.90,
        "sign": 1,
        "description": "Crude is the key feedstock cost for gasoil production",
    },
    {
        "source": "Brent",
        "target": "RBOB",
        "relationship": "refinery_margin_link",
        "weight": 0.85,
        "sign": 1,
        "description": "Crude feedstock cost for gasoline",
    },
    {
        "source": "OPEC_Policy",
        "target": "Brent",
        "relationship": "supply_policy",
        "weight": 0.85,
        "sign": 1,
        "description": "OPEC production cuts → tighter supply → higher Brent",
    },
    {
        "source": "USD_Index",
        "target": "Brent",
        "relationship": "currency_inverse",
        "weight": 0.75,
        "sign": -1,
        "description": "Stronger USD → cheaper crude for non-USD buyers → lower demand",
    },
    {
        "source": "TTF_Gas",
        "target": "Gasoil",
        "relationship": "fuel_switching",
        "weight": 0.55,
        "sign": 1,
        "description": "High gas prices push demand toward oil for heating",
    },
]

G = _build_from_connections(connections, directed=True)

print(f"Nodes: {list(G.nodes())}")
print(f"Edges: {G.number_of_edges()}")
print()

print("Edges with attributes:")
for src, dst, attrs in G.edges(data=True):
    sign_str = "+" if attrs.get("sign", 1) > 0 else "-"
    print(f"  {src} →{sign_str} {dst}  (weight={attrs['weight']}, {attrs['description']})")

print()
print("Nodes that influence Brent directly:")
for src, dst in G.in_edges("Brent"):
    attrs = G[src]["Brent"]
    print(f"  {src}  (weight={attrs['weight']})")

# ── Full market graph from knowledge_graph ────────────────────────────────────
print()
print("=== Full market graph (knowledge_graph) ===")
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "knowledge_graph"))
from market_graph import NODES, EDGES, CLUSTER_COLOR, build_graph

G_full = build_graph()
print(f"Nodes: {G_full.number_of_nodes()}")
print(f"Edges: {G_full.number_of_edges()}")

clusters = {}
for nid, attrs in G_full.nodes(data=True):
    c = attrs.get("cluster", "unknown")
    clusters.setdefault(c, []).append(nid)
print("\nClusters:")
for cluster, members in sorted(clusters.items()):
    print(f"  {cluster}: {', '.join(members)}")

print("\nTop 5 edges by weight:")
weighted = sorted(G_full.edges(data=True), key=lambda e: e[2].get("weight", 0), reverse=True)
for src, dst, attrs in weighted[:5]:
    sign_str = "+" if attrs.get("sign", 1) > 0 else "-"
    print(f"  {src} →{sign_str} {dst}  (weight={attrs['weight']}, label={attrs.get('label', '')})")

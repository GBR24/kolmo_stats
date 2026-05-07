"""
Energy market relationship graph.

Nodes and edges define how energy market variables relate to each other.
To contribute: add a node to NODES or an edge to EDGES.

Clusters:
  crude   — Brent, WTI, differentials, timespreads
  product — crack spreads and product flat prices
  balance — supply / demand / inventories / refinery
  macro   — GDP, PMI, USD, recession, financial conditions
  geo     — OPEC+, sanctions, Hormuz, disruptions
  energy  — gas, power, weather, substitution
"""
from __future__ import annotations

from typing import Dict, List, Tuple

# ── Cluster colours (used by frontend) ────────────────────────────────────────
CLUSTER_COLOR: Dict[str, str] = {
    "crude":   "#ffb000",
    "product": "#00e5ff",
    "balance": "#00ff41",
    "macro":   "#ff69b4",
    "geo":     "#ff3b30",
    "energy":  "#00ffcc",
}

# ── Nodes ──────────────────────────────────────────────────────────────────────
# tier 1 = benchmark, tier 2 = important, tier 3 = secondary
# value for crude/product nodes: USD price ($/bbl or $/gal)
# value for other nodes: pressure in [-1, 1]  (+1 bullish, -1 bearish)

NODES: Dict[str, Dict] = {

    # Crude benchmarks
    "brent":        {"label": "Brent",        "cluster": "crude",   "tier": 1, "value": 95.0},
    "wti":          {"label": "WTI",          "cluster": "crude",   "tier": 1, "value": 85.0},
    "dated_brent":  {"label": "Dated Brent",  "cluster": "crude",   "tier": 3, "value": 95.5},
    "brent_spread": {"label": "Brent Spread", "cluster": "crude",   "tier": 3, "value": 0.5},
    "wti_cushing":  {"label": "WTI Cushing",  "cluster": "crude",   "tier": 3, "value": 83.5},
    "wti_houston":  {"label": "WTI Houston",  "cluster": "crude",   "tier": 3, "value": 87.0},
    "dubai_oman":   {"label": "Dubai/Oman",   "cluster": "crude",   "tier": 3, "value": 92.5},
    "urals":        {"label": "Urals",        "cluster": "crude",   "tier": 3, "value": 75.0},

    # Refined products
    "gasoline_crack": {"label": "Gasoline Crack", "cluster": "product", "tier": 1, "value": 20.0},
    "diesel_crack":   {"label": "Diesel Crack",   "cluster": "product", "tier": 1, "value": 25.0},
    "jet_crack":      {"label": "Jet Crack",      "cluster": "product", "tier": 2, "value": 22.0},
    "naphtha_crack":  {"label": "Naphtha Crack",  "cluster": "product", "tier": 3, "value": -4.0},
    "rbob":           {"label": "RBOB Gasoline",  "cluster": "product", "tier": 3, "value": 2.95},
    "ulsd":           {"label": "ULSD",           "cluster": "product", "tier": 3, "value": 3.50},
    "jet_fuel":       {"label": "Jet Fuel",       "cluster": "product", "tier": 3, "value": 3.60},

    # Physical balance
    "global_demand":    {"label": "Global Demand",    "cluster": "balance", "tier": 1, "value": 0.0},
    "global_supply":    {"label": "Global Supply",    "cluster": "balance", "tier": 1, "value": 0.0},
    "opec_supply":      {"label": "OPEC Supply",      "cluster": "balance", "tier": 2, "value": 0.0},
    "opec_spare":       {"label": "OPEC Spare Cap",   "cluster": "balance", "tier": 2, "value": 0.0},
    "us_shale":         {"label": "US Shale Supply",  "cluster": "balance", "tier": 2, "value": 0.0},
    "non_opec_supply":  {"label": "Non-OPEC Supply",  "cluster": "balance", "tier": 3, "value": 0.0},
    "china_demand":     {"label": "China Demand",     "cluster": "balance", "tier": 2, "value": 0.0},
    "oecd_inventories": {"label": "OECD Inventories", "cluster": "balance", "tier": 1, "value": 0.0},
    "cushing_inv":      {"label": "Cushing Stocks",   "cluster": "balance", "tier": 2, "value": 0.0},
    "distillate_inv":   {"label": "Distillate Inv",   "cluster": "balance", "tier": 2, "value": 0.0},
    "gasoline_inv":     {"label": "Gasoline Inv",     "cluster": "balance", "tier": 2, "value": 0.0},
    "refinery_runs":    {"label": "Refinery Runs",    "cluster": "balance", "tier": 1, "value": 0.0},
    "refinery_outages": {"label": "Refinery Outages", "cluster": "balance", "tier": 2, "value": 0.0},
    "russia_exports":   {"label": "Russian Exports",  "cluster": "balance", "tier": 2, "value": 0.0},
    "iran_exports":     {"label": "Iranian Exports",  "cluster": "balance", "tier": 3, "value": 0.0},
    "floating_storage": {"label": "Floating Storage", "cluster": "balance", "tier": 3, "value": 0.0},

    # Macro
    "global_gdp":        {"label": "Global GDP",        "cluster": "macro", "tier": 1, "value": 0.0},
    "china_activity":    {"label": "China Industry",     "cluster": "macro", "tier": 2, "value": 0.0},
    "mfg_pmi":           {"label": "Mfg PMI",            "cluster": "macro", "tier": 2, "value": 0.0},
    "usd_index":         {"label": "USD Index",          "cluster": "macro", "tier": 1, "value": 0.0},
    "recession_prob":    {"label": "Recession Risk",     "cluster": "macro", "tier": 2, "value": 0.0},
    "airline_traffic":   {"label": "Airline Traffic",    "cluster": "macro", "tier": 2, "value": 0.0},
    "trucking":          {"label": "Freight/Trucking",   "cluster": "macro", "tier": 2, "value": 0.0},
    "central_bank":      {"label": "Central Bank",       "cluster": "macro", "tier": 2, "value": 0.0},
    "consumer_spending": {"label": "Consumer Spending",  "cluster": "macro", "tier": 3, "value": 0.0},
    "risk_appetite":     {"label": "Risk Appetite",      "cluster": "macro", "tier": 3, "value": 0.0},

    # Geopolitical
    "opec_policy":      {"label": "OPEC+ Policy",       "cluster": "geo", "tier": 1, "value": 0.0},
    "russia_sanctions": {"label": "Russia Sanctions",   "cluster": "geo", "tier": 2, "value": 0.0},
    "iran_sanctions":   {"label": "Iran Sanctions",     "cluster": "geo", "tier": 2, "value": 0.0},
    "hormuz_risk":      {"label": "Hormuz Risk",        "cluster": "geo", "tier": 2, "value": 0.0},
    "red_sea":          {"label": "Red Sea Disruption", "cluster": "geo", "tier": 2, "value": 0.0},
    "libya_iraq":       {"label": "Libya/Iraq Risk",    "cluster": "geo", "tier": 3, "value": 0.0},
    "venezuela":        {"label": "Venezuela",          "cluster": "geo", "tier": 3, "value": 0.0},

    # Cross-energy
    "ttf_gas":     {"label": "TTF Gas",     "cluster": "energy", "tier": 2, "value": 0.0},
    "henry_hub":   {"label": "Henry Hub",   "cluster": "energy", "tier": 3, "value": 0.0},
    "power_prices":{"label": "Power Prices","cluster": "energy", "tier": 3, "value": 0.0},
    "cold_winter": {"label": "Cold Winter", "cluster": "energy", "tier": 3, "value": 0.0},
    "renewables":  {"label": "Renewables",  "cluster": "energy", "tier": 3, "value": 0.0},
}

# ── Edges ──────────────────────────────────────────────────────────────────────
# (source, target, weight, sign, label)
# weight: 0–1 transmission strength
# sign:  +1 same direction, -1 inverse

EDGES: List[Tuple[str, str, float, int, str]] = [

    # Global crude balance → benchmarks
    ("global_demand",    "brent",             0.90,  1, "demand → crude"),
    ("global_supply",    "brent",             0.90, -1, "supply → crude"),
    ("global_demand",    "wti",               0.75,  1, "demand → WTI"),
    ("global_supply",    "wti",               0.80, -1, "supply → WTI"),
    ("oecd_inventories", "brent",             0.85, -1, "stocks → crude"),
    ("oecd_inventories", "brent_spread",      0.80, -1, "stocks → spread"),
    ("floating_storage", "oecd_inventories",  0.60,  1, "float → OECD"),

    # OPEC+ architecture
    ("opec_policy",  "opec_supply",  0.90, -1, "policy → supply"),
    ("opec_policy",  "brent",        0.85,  1, "OPEC → Brent"),
    ("opec_supply",  "brent",        0.85, -1, "OPEC supply"),
    ("opec_supply",  "global_supply",0.75,  1, "OPEC → global"),
    ("opec_spare",   "brent",        0.75, -1, "spare cap → premium"),

    # US crude system
    ("cushing_inv",  "wti",            0.90, -1, "Cushing → WTI"),
    ("cushing_inv",  "wti_cushing",    0.90, -1, "Cushing stocks"),
    ("us_shale",     "wti",            0.80, -1, "shale → WTI"),
    ("us_shale",     "global_supply",  0.65,  1, "shale → global"),
    ("us_shale",     "non_opec_supply",0.70,  1, "shale → non-OPEC"),
    ("wti_cushing",  "wti_houston",    0.75,  1, "inland → coast"),
    ("wti_houston",  "brent",          0.65,  1, "export parity"),
    ("non_opec_supply","global_supply",0.70,  1, "non-OPEC supply"),

    # Crude benchmark relationships
    ("brent",       "dated_brent", 0.90,  1, "futures → physical"),
    ("dated_brent", "brent",       0.85,  1, "physical → futures"),
    ("brent",       "dubai_oman",  0.70,  1, "inter-benchmark"),
    ("dubai_oman",  "brent",       0.55,  1, "East demand signal"),
    ("russia_exports","global_supply",0.60, 1, "Russian barrels"),
    ("iran_exports", "global_supply",0.50,  1, "Iranian barrels"),
    ("russia_exports","urals",      0.75,  1, "export → grade"),

    # Crude → refined products
    ("brent", "rbob",     0.85,  1, "feedstock cost"),
    ("brent", "ulsd",     0.90,  1, "feedstock cost"),
    ("brent", "jet_fuel", 0.85,  1, "feedstock cost"),
    ("wti",   "rbob",     0.80,  1, "US feedstock"),

    # Crack spread drivers
    ("gasoline_inv",    "gasoline_crack", 0.80, -1, "stocks → crack"),
    ("distillate_inv",  "diesel_crack",   0.85, -1, "stocks → crack"),
    ("distillate_inv",  "jet_crack",      0.70, -1, "pool competition"),
    ("refinery_outages","gasoline_crack", 0.80,  1, "outage → crack"),
    ("refinery_outages","diesel_crack",   0.75,  1, "outage → crack"),
    ("refinery_outages","refinery_runs",  0.85, -1, "outage → runs"),
    ("gasoline_crack",  "brent",          0.60,  1, "crack → crude pull"),
    ("diesel_crack",    "brent",          0.65,  1, "crack → crude pull"),
    ("diesel_crack",    "refinery_runs",  0.65,  1, "margin → throughput"),
    ("refinery_runs",   "global_demand",  0.70,  1, "runs → crude demand"),

    # Macro → demand
    ("global_gdp",       "global_demand",   0.85,  1, "growth → demand"),
    ("china_activity",   "china_demand",    0.80,  1, "China → demand"),
    ("china_activity",   "brent",           0.70,  1, "China → crude"),
    ("china_demand",     "global_demand",   0.65,  1, "China → global"),
    ("mfg_pmi",          "global_demand",   0.65,  1, "PMI → demand"),
    ("mfg_pmi",          "diesel_crack",    0.80,  1, "PMI → distillate"),
    ("mfg_pmi",          "trucking",        0.65,  1, "PMI → freight"),
    ("trucking",         "ulsd",            0.75,  1, "freight → diesel"),
    ("trucking",         "diesel_crack",    0.70,  1, "freight → crack"),
    ("airline_traffic",  "jet_fuel",        0.90,  1, "flights → jet"),
    ("airline_traffic",  "jet_crack",       0.85,  1, "flights → crack"),
    ("consumer_spending","gasoline_crack",  0.60,  1, "spending → gasoline"),
    ("consumer_spending","airline_traffic", 0.60,  1, "spending → travel"),
    ("recession_prob",   "global_gdp",      0.80, -1, "recession → GDP"),
    ("recession_prob",   "brent",           0.75, -1, "recession → crude"),
    ("recession_prob",   "diesel_crack",    0.70, -1, "recession → distillate"),
    ("recession_prob",   "airline_traffic", 0.65, -1, "recession → travel"),

    # Financial conditions
    ("usd_index",   "brent",        0.75, -1, "USD → crude (inverse)"),
    ("usd_index",   "wti",          0.75, -1, "USD → WTI"),
    ("central_bank","usd_index",    0.65,  1, "rates → USD"),
    ("central_bank","global_gdp",   0.70, -1, "tightening → growth"),
    ("central_bank","recession_prob",0.55, 1, "tightening → risk"),
    ("risk_appetite","brent",        0.55,  1, "risk-on → crude"),

    # Geopolitical transmission
    ("russia_sanctions","russia_exports",  0.80, -1, "sanctions → exports"),
    ("russia_sanctions","brent",           0.70,  1, "Russia risk"),
    ("russia_sanctions","diesel_crack",    0.75,  1, "Russia → diesel"),
    ("russia_sanctions","urals",           0.80, -1, "sanctions → discount"),
    ("iran_sanctions",  "iran_exports",    0.80, -1, "sanctions → exports"),
    ("iran_sanctions",  "brent",           0.65,  1, "Iran risk"),
    ("iran_sanctions",  "hormuz_risk",     0.60,  1, "Iran → Hormuz"),
    ("hormuz_risk",     "brent",           0.90,  1, "Hormuz premium"),
    ("hormuz_risk",     "global_supply",   0.75, -1, "Hormuz → supply"),
    ("red_sea",         "brent",           0.70,  1, "freight → crude"),
    ("red_sea",         "ulsd",            0.55,  1, "voyage time → diesel"),
    ("libya_iraq",      "global_supply",   0.60, -1, "outage → supply"),
    ("libya_iraq",      "brent",           0.65,  1, "MENA premium"),
    ("venezuela",       "global_supply",   0.40,  1, "heavy sour barrels"),

    # Cross-energy substitution
    ("ttf_gas",    "diesel_crack",  0.55,  1, "gas→oil switching"),
    ("ttf_gas",    "power_prices",  0.75,  1, "gas → power"),
    ("henry_hub",  "ttf_gas",       0.50,  1, "LNG arb"),
    ("cold_winter","ulsd",          0.65,  1, "heating demand"),
    ("cold_winter","diesel_crack",  0.60,  1, "heating season"),
    ("cold_winter","global_demand", 0.50,  1, "weather → demand"),
    ("renewables", "global_demand", 0.40, -1, "displacement"),
    ("power_prices","ulsd",         0.45,  1, "power backup burn"),
]


def get_nodes(cluster: str = None) -> Dict[str, Dict]:
    """Return all nodes, optionally filtered by cluster."""
    if cluster is None:
        return NODES
    return {k: v for k, v in NODES.items() if v["cluster"] == cluster}


def get_edges(source: str = None, target: str = None) -> List[Tuple]:
    """Return all edges, optionally filtered by source or target node id."""
    result = EDGES
    if source:
        result = [e for e in result if e[0] == source]
    if target:
        result = [e for e in result if e[1] == target]
    return result


def build_graph():
    """Return a networkx DiGraph of the full market relationship map."""
    from kolmo_stats.graph.energy_graph import _build_energy_graph
    return _build_energy_graph(NODES, EDGES, CLUSTER_COLOR)

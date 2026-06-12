"""
Benchmark query suite with ground-truth relevant nodes.

ground_truth: the nodes a good retriever *must* return for the query to be
              considered a hit. Used to compute recall@K.
"""

QUERIES: list[dict] = [
    {
        "query": "what is driving diesel crack margins?",
        "mode": "local",
        "ground_truth": {"diesel_crack", "distillate_inv", "refinery_runs",
                         "russia_sanctions", "trucking", "brent"},
    },
    {
        "query": "brent crude price drivers",
        "mode": "local",
        "ground_truth": {"brent", "global_demand", "global_supply", "opec_policy",
                         "oecd_inventories", "usd_index"},
    },
    {
        "query": "opec cuts impact on crude supply",
        "mode": "local",
        "ground_truth": {"opec_policy", "opec_supply", "opec_spare", "brent",
                         "global_supply"},
    },
    {
        "query": "LNG arbitrage between henry hub and TTF",
        "mode": "local",
        "ground_truth": {"henry_hub", "ttf_gas", "brent"},
    },
    {
        "query": "geopolitical risk to crude supply",
        "mode": "local",
        "ground_truth": {"hormuz_risk", "iran_sanctions", "russia_sanctions",
                         "opec_policy", "brent"},
    },
    {
        "query": "gasoline crack seasonal patterns",
        "mode": "local",
        "ground_truth": {"gasoline_crack", "gasoline_inv", "rbob", "refinery_runs"},
    },
    {
        "query": "give me a full energy market overview",
        "mode": "global",
        "ground_truth": {"brent", "diesel_crack", "global_demand", "opec_policy",
                         "ttf_gas", "usd_index"},
    },
    {
        "query": "macro recession impact on oil demand",
        "mode": "local",
        "ground_truth": {"recession_prob", "global_gdp", "global_demand", "brent",
                         "mfg_pmi"},
    },
]

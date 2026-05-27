# Contributing To The Energy Market Graph

The canonical graph now lives in:

```text
src/kolmo_stats/graph/market_graph.yml
```

The old `knowledge_graph/market_graph.py` file is only a compatibility shim.
Do not edit Python dictionaries for graph data.

## If You Do Not Want To Use Git

Open a GitHub issue with the **Suggest market graph knowledge** form. You only
need to explain the market relationship in plain English:

- What variable influences what?
- Does it move in the same direction or the opposite direction?
- Is the relationship strong, medium, or weak?
- Why does this make sense in oil/gas markets?

A maintainer can convert that into YAML.

## YAML Concepts

Each node is a market variable. Each edge is a directional relationship:

```yaml
nodes:
  cushing_inv:
    label: "Cushing Stocks"
    cluster: balance
    tier: 2
    value: 0.0
    unit: "pressure [-1,1]"
    aliases: ["Cushing inventory", "Cushing stocks"]
    description: "Cushing storage pressure that directly affects WTI and inland basis."
    related_formulas: [seasonal_zscore, location_spread]
    strategy_hint: "Use for WTI basis and storage congestion trades."

edges:
  - [cushing_inv, wti, 0.90, -1, "Cushing to WTI", "Cushing builds pressure WTI."]
```

## Fields

Node fields:

- `label`: readable display name.
- `cluster`: one of `crude`, `product`, `balance`, `macro`, `geo`, `energy`.
- `tier`: `1` benchmark, `2` important driver, `3` secondary detail.
- `value`: starting price or neutral pressure.
- `unit`: `USD/bbl`, `USD/gal`, or `pressure [-1,1]`.
- `aliases`: names users and agents may type.
- `description`: plain-English definition.
- `related_formulas`: kolmo-stats functions relevant to the node.
- `strategy_hint`: short trading or analysis context.

Edge fields:

```yaml
[source, target, weight, sign, label, rationale]
```

- `weight`: `0.0` to `1.0`; use `0.9` strong, `0.6` medium, `0.4` weak.
- `sign`: `1` if source and target move together, `-1` if inverse.
- `label`: short display text.
- `rationale`: plain-English market logic.

## Validation Checklist

- Node ids use `snake_case`.
- Every edge source and target already exists in `nodes`.
- Every node has a description.
- No duplicate edges.
- No isolated nodes unless there is a clear reason.
- Relationships explain market structure only; do not add shock propagation logic.

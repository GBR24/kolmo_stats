# Contributing to the Energy Market Graph

This folder contains the energy market relationship graph used by kolmo_stats.
The goal is to map how variables in the energy market influence each other.

Anyone can contribute a new variable or relationship by editing `market_graph.py`.

---

## Concepts

### Nodes
A node is any variable that matters in the energy market — a price, a flow, an indicator, a risk factor.

Each node belongs to one of six clusters:

| Cluster   | What goes here |
|-----------|----------------|
| `crude`   | Benchmark prices, differentials, timespreads |
| `product` | Crack spreads, refined product prices |
| `balance` | Supply, demand, inventories, refinery activity |
| `macro`   | GDP, PMI, USD, recession risk, financial conditions |
| `geo`     | OPEC+ policy, sanctions, shipping disruptions |
| `energy`  | Natural gas, power prices, weather, renewables |

### Edges
An edge is a directional relationship between two nodes: A influences B.

Each edge has:
- **weight** (`0.0–1.0`): how strongly A transmits to B. Use 0.9 for near-certain transmission, 0.5 for moderate, 0.3 for weak.
- **sign/correlation** (`+1` or `-1`): `+1` means they move together, `-1` means they move in opposite directions.

---

## How to add a node

Open `market_graph.py` and add an entry to the `NODES` dictionary under the right cluster section.

```python
"your_node_id": {"label": "Human Readable Name", "cluster": "balance", "tier": 2, "value": 0.0},
```

**tier** is a size hint for visualisation:
- `1` — benchmark / top-level importance
- `2` — important supporting variable
- `3` — secondary / detail variable

**value** is the starting value:
- For `crude` / `product` nodes: a USD price (e.g. `85.0` for $/bbl)
- For all other nodes: `0.0` (pressure scale from -1 to +1)

### Example — adding Canadian oil sands production

```python
# in the "balance" section of NODES
"canada_oilsands": {"label": "Canada Oil Sands", "cluster": "balance", "tier": 2, "value": 0.0},
```

---

## How to add an edge

Add a tuple to the `EDGES` list in `market_graph.py`:

```python
("source_node_id", "target_node_id", weight, sign, "short description"),
```

Place it under the comment section that best describes the relationship.

### Examples

Canada oil sands output raises global supply:
```python
("canada_oilsands", "global_supply", 0.55, +1, "oilsands → global supply"),
```

Higher global supply pushes Brent down (already exists, shown for reference):
```python
("global_supply", "brent", 0.90, -1, "supply → crude"),
```

Cold weather increases heating oil demand:
```python
("cold_winter", "distillate_inv", 0.60, -1, "cold → heating draw"),
```

---

## Checklist before opening a PR

- [ ] Node id uses `snake_case`
- [ ] The cluster is the most appropriate one for the variable
- [ ] Every edge has a clear, short label (e.g. `"sanctions → exports"`)
- [ ] Weights are grounded in market logic, not guessed — add a comment if the value is non-obvious
- [ ] No duplicate nodes or edges

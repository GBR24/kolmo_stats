# Contributing to kolmo

kolmo is an open-source energy market analytics library. All contributions are welcome.

## Four levels of contribution

### Level 1 — Add market knowledge
No coding required. Open the **Suggest market graph knowledge** issue form to:
- Suggest a new energy spread, formula, or convention
- Report an incorrect formula or wrong sign
- Propose a new use case or example

Graph data is stored in simple YAML at
`src/kolmo_stats/graph/market_graph.yml`. Maintainers can convert plain-English
issues into YAML entries.

### Level 2 — Add a formula
Implement a new analytical function in one of the existing modules.

Good first targets:
- `src/kolmo_stats/spreads/` — new spread types and oil/gas differentials
- `src/kolmo_stats/curves/` — new curve analytics and carry measures
- `src/kolmo_stats/economics/` — IRR, payback period, sensitivity analysis
- `src/kolmo_stats/stats/` — new statistical measures and regimes

**Guidelines for a new function:**
- Add type hints and a docstring with a formula and an example
- Accept list, numpy array, and pandas Series as inputs
- Return float or pandas Series depending on input
- Add `explain=False` parameter that returns a dict when True
- Add agent-facing metadata in `src/kolmo_stats/catalog.py`
- Add tests in `tests/`

### Level 3 — Add an energy-specific analytical model
Larger features:
- Stochastic price models (Geometric Brownian Motion, Ornstein-Uhlenbeck)
- Storage valuation (swing options, intrinsic + extrinsic)
- Gas balancing and nomination tools
- Volatility surface and smile analytics
- Forward curve construction and interpolation

These go in new sub-modules under `src/kolmo_stats/`. Open an issue first to discuss scope.

### Level 4 — Numerical engine improvements
Contribute to `src/kolmo_stats/engine/`:
- Improve numerical precision of existing routines
- Add new root-finding or optimisation primitives
- Prepare the interface for future native backends (see `native/DESIGN.md`)

This level requires understanding the internal dispatch architecture.

## Getting started

```bash
git clone https://github.com/GBR24/kolmo_stats.git
cd kolmo_stats
pip install -e ".[dev]"
pytest tests/
```

## More contributor docs

- [docs/CONVENTIONS.md](docs/CONVENTIONS.md) documents signs, units, and market conventions.
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) gives the checklist for adding or changing functions.
- [native/README.md](native/README.md) explains how future C++ code should stay hidden behind Python APIs.
- [knowledge_graph/CONTRIBUTING.md](knowledge_graph/CONTRIBUTING.md) covers market graph contributions.

## Style

- Simple, readable Python — clarity over cleverness
- No comments that explain what the code does — only write one if the *why* is non-obvious
- No unnecessary abstractions
- Analyst-friendly error messages with actionable hints

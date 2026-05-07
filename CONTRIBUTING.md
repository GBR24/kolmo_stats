# Contributing to kolmo

kolmo is an open-source energy market analytics library. All contributions are welcome.

## Four levels of contribution

### Level 1 — Add market knowledge
No coding required. Open an issue to:
- Suggest a new energy spread, formula, or convention
- Report an incorrect formula or wrong sign
- Propose a new use case or example

### Level 2 — Add a formula
Implement a new analytical function in one of the existing modules.

Good first targets:
- `kolmo/spreads/` — new spread types (frac spread, dark spread, clean spark)
- `kolmo/curves/` — new curve analytics (contango carry, roll cost series)
- `kolmo/economics/` — IRR, payback period, sensitivity analysis
- `kolmo/stats/` — new statistical measures

**Guidelines for a new function:**
- Add type hints and a docstring with a formula and an example
- Accept list, numpy array, and pandas Series as inputs
- Return float or pandas Series depending on input
- Add `explain=False` parameter that returns a dict when True
- Add tests in `tests/`

### Level 3 — Add an energy-specific analytical model
Larger features:
- Stochastic price models (Geometric Brownian Motion, Ornstein-Uhlenbeck)
- Storage valuation (swing options, intrinsic + extrinsic)
- Gas balancing and nomination tools
- Volatility surface and smile analytics
- Forward curve construction and interpolation

These go in new sub-modules under `kolmo/`. Open an issue first to discuss scope.

### Level 4 — Numerical engine improvements
Contribute to `kolmo/engine/`:
- Improve numerical precision of existing routines
- Add new root-finding or optimisation primitives
- Prepare the interface for future C++ backends (see `cpp/DESIGN.md`)

This level requires understanding the internal dispatch architecture.

## Getting started

```bash
git clone https://github.com/GBR24/kolmo_stats.git
cd kolmo_stats
pip install -e ".[dev]"
pytest tests/
```

## Style

- Simple, readable Python — clarity over cleverness
- No comments that explain what the code does — only write one if the *why* is non-obvious
- No unnecessary abstractions
- Analyst-friendly error messages with actionable hints

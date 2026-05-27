# Native Backends

This folder documents the optional native boundary for kolmo-stats.

There is **no compiled code in this repository today**. Installing and using
kolmo-stats does not require a compiler.

## What Exists Now

The package has one native-ready calculation path:

```python
from kolmo_stats import portfolio_scenario_matrix
```

The Python implementation lives in `src/kolmo_stats/risk/matrix.py`. Its inner
numeric calculation goes through:

```python
kolmo_stats.engine.portfolio.scenario_matrix_values(...)
```

That helper uses NumPy by default. If an optional module named
`kolmo_stats._ext` is installed and exposes `portfolio_scenario_matrix`, the
helper delegates the raw numeric matrix calculation to it.

## What Native Code Is Allowed To Do

Native code may accelerate this inner calculation:

```text
pnl[scenario, asset] = position[asset] * shock[scenario, asset]
```

Native code must not handle:

- public API design
- pandas DataFrame construction
- asset/scenario labels
- user-facing validation
- `explain=True`
- docs or formula metadata

Those stay in Python.

## Contract

Supported optional function:

```python
kolmo_stats._ext.portfolio_scenario_matrix(positions, shocks)
```

Inputs:

- `positions`: one-dimensional numeric sequence.
- `shocks`: two-dimensional numeric sequence.

Output:

- two-dimensional numeric sequence shaped like `shocks`.

See [DESIGN.md](DESIGN.md) for the exact dispatch path.

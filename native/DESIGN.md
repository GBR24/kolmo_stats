# Native Backend Design

This document describes the native boundary that exists today in kolmo-stats.
There is currently no compiled extension in this repository.

## Current State

kolmo-stats is a Python package. All public analytics functions run with the
standard Python scientific stack by default.

The native-ready path that exists today is:

```text
kolmo_stats.portfolio_scenario_matrix(...)
    -> kolmo_stats.risk.matrix.portfolio_scenario_matrix(...)
        -> kolmo_stats.engine.portfolio.scenario_matrix_values(...)
            -> NumPy fallback
            -> kolmo_stats._ext.portfolio_scenario_matrix(...) if installed
```

The public return shape is always a pandas DataFrame. Native code, when present,
only replaces the inner numeric matrix calculation.

## Native Hook Contract

The optional compiled module name is:

```python
kolmo_stats._ext
```

The currently supported native function name is:

```python
portfolio_scenario_matrix(positions, shocks)
```

Expected inputs:

- `positions`: one-dimensional numeric sequence, one value per asset.
- `shocks`: two-dimensional numeric sequence, one row per scenario and one
  column per asset.

Expected output:

- A two-dimensional numeric sequence with the same shape as `shocks`.
- Each cell is `positions[asset_index] * shocks[scenario_index][asset_index]`.

The Python wrapper is responsible for labels, pandas DataFrame construction,
validation, `explain=True`, and total P&L columns.

## Fallback Rule

If `kolmo_stats._ext` cannot be imported, or if it does not expose
`portfolio_scenario_matrix`, kolmo-stats uses the NumPy implementation.

Users do not choose the backend. They call:

```python
from kolmo_stats import portfolio_scenario_matrix
```

and receive the same API either way.

## Contributor Rule

Native code must not define new public analytics APIs. Add or change public
behavior in Python first, with tests and docs. Native code may then accelerate
only the inner numeric loop behind an existing Python function.

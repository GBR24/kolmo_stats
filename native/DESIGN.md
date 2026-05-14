# Native Backend Design

This document describes how optional C++ backends should plug into the Python
package. The public API must stay Python-first and easy to use.

## Dispatch architecture

```
Python public API
  kolmo_stats.npv(...)
  kolmo_stats.curve_slope(...)
  kolmo_stats.historical_var(...)

        │
        ▼

kolmo_stats.engine  (pure Python by default)
  kolmo_stats/engine/numerical.py      → numpy.gradient
  kolmo_stats/engine/root_finding.py   → scipy.optimize.brentq
  kolmo_stats/engine/statistics.py     → pandas.rolling

        │  (optional, future)
        ▼

kolmo_stats._ext  (compiled C++ extension)
  kolmo_stats._ext.gradient(y, x)
  kolmo_stats._ext.brentq(f, a, b)
  kolmo_stats._ext.rolling_stats(arr, window)
```

When `kolmo_stats._ext` is available, `kolmo_stats.engine` delegates to it automatically.
When it is not present, the pure Python path is used. No user code changes.

## Binding technologies under consideration

| Option | Pros | Cons |
|---|---|---|
| **pybind11** | Mature, widely used, good numpy support | Header-only compile times |
| **nanobind** | Faster compile times, smaller binaries | Newer, smaller community |
| **Cython** | Easy numpy integration, incremental adoption | Less idiomatic for new code |
| **scikit-build-core** | Modern CMake integration | Additional build toolchain |

No decision has been made. The architecture supports any of these.

## Priority native candidates

1. **Rolling statistics** — rolling z-score, rolling correlation on large tick data
2. **Root finding** — custom Brent / Newton for breakeven and calibration
3. **Gradient and curve derivatives** — spline differentiation
4. **Monte Carlo engine** — stochastic price path generation (GBM, OU, two-factor)
5. **Storage valuation** — dynamic programming on price grids
6. **Graph shock propagation** — node cascade at scale
7. **Correlated scenario generation** — Cholesky / covariance transforms at scale
8. **Regime engines** — Markov and HMM-style transition simulations

## Current status

No native code. Pure Python only. This file describes the future architecture so
contributors can design the engine layer consistently from the start.

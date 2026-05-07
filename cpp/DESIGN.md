# C++ Backend Design

## Dispatch architecture

```
Python public API
  kolmo.npv(...)
  kolmo.curve_slope(...)
  kolmo.historical_var(...)

        │
        ▼

kolmo.engine  (pure Python by default)
  kolmo/engine/numerical.py      → numpy.gradient
  kolmo/engine/root_finding.py   → scipy.optimize.brentq
  kolmo/engine/statistics.py     → pandas.rolling

        │  (optional, future)
        ▼

kolmo._ext  (compiled C++ extension)
  kolmo._ext.gradient(y, x)
  kolmo._ext.brentq(f, a, b)
  kolmo._ext.rolling_stats(arr, window)
```

When `kolmo._ext` is available, `kolmo.engine` delegates to it automatically.
When it is not present, the pure Python path is used. No user code changes.

## Binding technologies under consideration

| Option | Pros | Cons |
|---|---|---|
| **pybind11** | Mature, widely used, good numpy support | Header-only compile times |
| **nanobind** | Faster compile times, smaller binaries | Newer, smaller community |
| **Cython** | Easy numpy integration, incremental adoption | Less idiomatic for new code |
| **scikit-build-core** | Modern CMake integration | Additional build toolchain |

No decision has been made. The architecture supports any of these.

## Priority C++ candidates

1. **Rolling statistics** — rolling z-score, rolling correlation on large tick data
2. **Root finding** — custom Brent / Newton for breakeven and calibration
3. **Gradient and curve derivatives** — spline differentiation
4. **Monte Carlo engine** — stochastic price path generation (GBM, OU, two-factor)
5. **Storage valuation** — dynamic programming on price grids
6. **Graph shock propagation** — node cascade at scale

## v0.1 status

No C++ code. Pure Python only. This file describes the future architecture so
contributors can design the engine layer consistently from the start.

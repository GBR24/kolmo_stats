# Native Backends

This folder is reserved for optional compiled extensions, starting with C++.
There is **no compiled code here today** and no compiler is required to install
or use kolmo-stats.

## Design rule

Python is the product. Native code is an implementation detail.

Users should keep calling friendly Python functions such as
`correlated_price_shocks(...)`, `rolling_var(...)`, or future
`value_gas_storage(...)`. If a native backend is installed, the Python engine
layer may dispatch to it. If not, the pure Python/NumPy path must still work.

## Why native code later?

Python with numpy and scipy is fast enough for most analytical tasks. But some
oil and gas computing workloads are large enough that a native backend becomes
worthwhile:

| Workload | Why C++ helps |
|---|---|
| Monte Carlo price simulations | Millions of paths per second |
| Stochastic commodity models (GBM, mean-reversion, two-factor) | Loop-heavy, vectorisation bottleneck |
| Gas storage valuation (dynamic programming) | Backward induction over large grids |
| Portfolio scenario engines | Cross-asset shocks at scale |
| Correlated shock engines | Cholesky transforms over large scenario sets |
| Regime simulation | Markov/HMM-style oil and gas state paths |
| Curve calibration and interpolation | Iterative solvers with tight tolerances |
| High-frequency rolling statistics | Large tick datasets |
| Large-scale graph shock propagation | Node-by-node cascade at thousands of nodes |
| Optimisation (LP, NLP, DP) | Inner loops that saturate Python |

## Design principle

The `kolmo_stats.engine` Python layer exists precisely so that C++ can be added
**without changing any public API**. The dispatch chain is:

```
kolmo_stats.curve_slope(...)           ← public API, never changes
    └─ kolmo_stats.engine.numerical.average_slope(...)
           └─ numpy.gradient(...)     ← Python default
           └─ kolmo_stats._ext.gradient(...) ← future C++ replacement
```

See [DESIGN.md](DESIGN.md) for the proposed binding architecture.

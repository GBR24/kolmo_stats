# cpp — Future High-Performance Backends

This folder is reserved for optional C++ extensions. There is **no compiled
code here in v0.1** and no C++ dependency is required to install or use kolmo.

## Why C++ later?

Python with numpy and scipy is fast enough for most analytical tasks. But some
energy computing workloads are large enough that a native C++ backend becomes
worthwhile:

| Workload | Why C++ helps |
|---|---|
| Monte Carlo price simulations | Millions of paths per second |
| Stochastic commodity models (GBM, mean-reversion, two-factor) | Loop-heavy, vectorisation bottleneck |
| Gas storage valuation (dynamic programming) | Backward induction over large grids |
| Portfolio scenario engines | Cross-asset shocks at scale |
| Curve calibration and interpolation | Iterative solvers with tight tolerances |
| High-frequency rolling statistics | Large tick datasets |
| Large-scale graph shock propagation | Node-by-node cascade at thousands of nodes |
| Optimisation (LP, NLP, DP) | Inner loops that saturate Python |

## Design principle

The `kolmo.engine` Python layer exists precisely so that C++ can be added
**without changing any public API**. The dispatch chain is:

```
kolmo.curve_slope(...)           ← public API, never changes
    └─ kolmo.engine.numerical.average_slope(...)
           └─ numpy.gradient(...)     ← Python default
           └─ kolmo._ext.gradient(...) ← future C++ replacement
```

See `DESIGN.md` for the proposed binding architecture.

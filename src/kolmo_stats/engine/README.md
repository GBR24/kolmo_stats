# kolmo.engine

Internal numerical computing layer. Not part of the public API.

## Purpose

`kolmo.engine` exists so that performance-critical routines can be replaced
with faster implementations (e.g. C++ via pybind11) without touching any
public-facing code. Every public function that does meaningful computation
delegates to one of the modules here.

## Modules

| Module | What it provides |
|---|---|
| `arrays.py` | Input coercion: list / tuple / Series / ndarray → ndarray |
| `numerical.py` | First derivatives, average slope (numpy gradient) |
| `root_finding.py` | Brent's method root finder (wraps scipy.optimize.brentq) |
| `statistics.py` | Rolling mean, std, covariance (wraps pandas rolling) |

## Future C++ replacement targets

The following are the most computation-heavy paths and the best candidates
for C++ acceleration in later versions:

- `numerical.py` → high-order curve differentiation, spline derivatives
- `root_finding.py` → custom Brent / Newton implementations
- `statistics.py` → high-frequency rolling statistics on large tick data

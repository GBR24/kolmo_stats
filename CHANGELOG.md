# Changelog

All notable changes to `kolmo-stats` are documented here.

---

## [0.2.0] — 2026-05-07

### Added

**20 public analytics functions** across five domains:

| Domain | Functions |
|---|---|
| Statistics | `mean`, `weighted_mean`, `rolling_zscore`, `seasonal_zscore`, `rolling_correlation`, `lead_lag_correlation` |
| Curves | `curve_shape`, `calendar_spread`, `butterfly_spread`, `roll_yield`, `curve_slope` |
| Spreads | `crack_spread`, `spark_spread`, `lng_arbitrage` |
| Risk | `historical_var`, `expected_shortfall`, `scenario_pnl`, `hedge_ratio` |
| Economics | `npv`, `breakeven_price` |

**Internal engine layer** (`kolmo_stats.engine`) — numerical primitives designed so a future C++ backend can replace internals without changing the public API:
- `engine.arrays` — array coercion, NaN handling
- `engine.numerical` — gradient, average slope
- `engine.root_finding` — scalar root finding via `scipy.optimize.brentq`
- `engine.statistics` — rolling mean, std, covariance

**`explain=True` on every function** — pass `explain=True` to get a dict with `result`, `explanation`, `formula`, and `inputs`.

**Graph Intelligence** (`Graph Intelligence/market_graph.py`) — community-editable energy market knowledge graph with 53 nodes and 86 directed edges across crude, products, gas, macro, and geopolitical clusters. Includes a contribution guide.

**7 runnable examples** in `examples/` covering all function groups.

**107 tests** across `tests/test_stats.py`, `test_curves.py`, `test_spreads.py`, `test_risk.py`, `test_economics.py`.

**C++ architecture blueprint** in `cpp/README.md` and `cpp/DESIGN.md`.

**`CONTRIBUTING.md`** — four-level guide for contributing market knowledge, formulas, models, or engine primitives.

### Fixed

- `lead_lag_correlation` now converts Series to numpy arrays before computing lag correlations, avoiding a pandas label-alignment bug that produced wrong lag detection results.

---

## [0.1.0] — 2026-04-01

### Added

- Initial package scaffold: `src/` layout, `pyproject.toml`, PyPI config (`kolmo-stats`).
- Single function: `mean` with NaN-skipping.
- `.gitignore` to exclude build artifacts (`__pycache__`, `*.egg-info`, `dist/`).
- GitHub Actions workflow for PyPI publish on release tag.

# Changelog

All notable changes to `kolmo-stats` are documented here.

---

## [Unreleased]

### Added

- Repo structure: moved compiled-backend planning from `cpp/` to `native/`,
  moved the market graph from `Graph Intelligence/` to `knowledge_graph/`,
  and added `docs/` for user/contributor guidance.
- Oil/gas quick wins: Brent-WTI, quality, location, JKM-TTF, Henry Hub-TTF,
  LNG netback, and shipping-adjusted spread helpers.
- Curve helpers: prompt spread, M1-M3, M1-M12, time-spread series, and
  annualized carry.
- Risk helpers: rolling VaR, rolling Expected Shortfall, multi-scenario stress
  matrix, Cholesky decomposition, correlated normals, and correlated price
  shocks.
- Observable Markov-chain helpers for market regime transitions, simulation,
  and horizon probabilities.
- Product unit helpers for $/gal vs $/bbl and product tons vs barrels.
- 5-3-2 crack spread support.
- YAML-backed packaged market graph with JSON, neighborhood, and
  agent-context helpers.
- Advanced quant helpers: OU half-life/calibration, spread residuals and
  cointegration z-scores, realised/EWMA volatility, portfolio VaR
  decomposition, native-ready portfolio scenario matrices, and curve PCA.
- Formula catalog metadata for agent/tooling consumers.

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

**Knowledge graph** (`knowledge_graph/market_graph.py`) — community-editable energy market knowledge graph with 53 nodes and 86 directed edges across crude, products, gas, macro, and geopolitical clusters. Includes a contribution guide.

**7 runnable examples** in `examples/` covering all function groups.

**107 tests** across `tests/test_stats.py`, `test_curves.py`, `test_spreads.py`, `test_risk.py`, `test_economics.py`.

**Native backend architecture blueprint** in `native/README.md` and `native/DESIGN.md`.

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

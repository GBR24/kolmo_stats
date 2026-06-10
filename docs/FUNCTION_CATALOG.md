# Function Catalog

This catalog lists the public functions exported by `kolmo_stats`. The README
keeps examples and project orientation; this file is the scalable home for the
full API surface as contributors add more formulas.

## Statistics

| Function | Description |
|---|---|
| `mean(values)` | Arithmetic average with NaN handling |
| `weighted_mean(values, weights)` | Weighted average for VWAP or exposure-weighted levels |
| `rolling_zscore(series, window)` | How extreme the current value is versus recent history |
| `seasonal_zscore(series, period)` | Z-score versus a seasonal group such as month, quarter, or week |
| `rolling_correlation(x, y, window)` | Dynamic correlation between two series |
| `lead_lag_correlation(x, y, max_lag)` | Which market moves first across candidate lags |
| `cointegration_beta(y, x)` | OLS hedge beta for a two-leg spread |
| `spread_residual(y, x)` | Residual spread after hedge-beta adjustment |
| `cointegration_zscore(y, x)` | Z-score of a residual spread |
| `mean_reversion_calibration(values)` | AR(1)/OU mean-reversion calibration |
| `ou_half_life(values)` | Mean-reversion half-life |
| `transition_matrix(states)` | Markov transition matrix for observed regimes |
| `simulate_markov_chain(matrix, start, n_steps)` | Simulate regime paths |
| `regime_probabilities(matrix, state, horizon)` | Future regime probabilities |

## Curves

| Function | Description |
|---|---|
| `curve_shape(curve)` | Classify as backwardation, contango, flat, or mixed |
| `calendar_spread(curve, near, far)` | Near minus far contract price |
| `butterfly_spread(curve, front, middle, back)` | Front - 2 * middle + back |
| `roll_yield(near, far, days_between)` | Annualised yield from rolling a futures position |
| `curve_slope(curve)` | Average first derivative, or steepness, of the curve |
| `prompt_spread(curve)` | Prompt M1-M2 spread |
| `m1_m3(curve)` | M1-M3 spread |
| `m1_m12(curve)` | M1-M12 spread |
| `time_spread_series(near, far)` | Time series of near minus far |
| `annualized_carry(near, far, days)` | Contango/backwardation carry rate |
| `curve_pca(curves)` | PCA factors for futures curves |
| `curve_factor_exposures(curve_changes, components)` | Project curve moves onto PCA factors |

## Spreads

| Function | Description |
|---|---|
| `crack_spread(crude, gasoline, distillate, ratio)` | Gross refinery margin proxy: 5-3-2, 3-2-1, 2-1-1, or simple |
| `spark_spread(power, gas, heat_rate)` | Gross gas-fired generation margin |
| `lng_arbitrage(destination, source, freight, ...)` | LNG netback arbitrage value |
| `brent_wti_spread(brent, wti)` | Brent minus WTI |
| `quality_spread(premium, discount)` | Light/sweet or other quality differential |
| `location_spread(destination, origin)` | Location basis differential |
| `ttf_jkm_spread(ttf, jkm)` | JKM minus TTF |
| `henry_hub_ttf_arb(hh, ttf, costs...)` | Henry Hub to TTF LNG arbitrage |
| `lng_netback(destination, costs...)` | Destination less LNG chain costs |
| `shipping_adjusted_spread(destination, source, costs...)` | Route-adjusted arbitrage spread |

## Risk

| Function | Description |
|---|---|
| `historical_var(returns, confidence)` | Historical lower-tail loss quantile |
| `expected_shortfall(returns, confidence)` | Average historical loss beyond VaR |
| `scenario_pnl(positions, shocks)` | Portfolio P&L under price shocks |
| `hedge_ratio(asset_returns, hedge_returns)` | Minimum-variance hedge ratio |
| `rolling_var(returns, window, confidence)` | Rolling historical VaR |
| `rolling_expected_shortfall(returns, window, confidence)` | Rolling historical Expected Shortfall |
| `stress_matrix(positions, scenarios)` | Multi-scenario portfolio P&L table |
| `portfolio_scenario_matrix(positions, scenarios)` | Scenario-by-asset P&L matrix |
| `cholesky_decompose(matrix)` | Cholesky factor for covariance/correlation matrices |
| `correlated_normals(corr, n_sims)` | Correlated standard-normal draws |
| `correlated_price_shocks(vols, corr, n_sims)` | Correlated oil/gas price or P&L shocks |
| `realized_volatility(returns)` | Annualised realised volatility |
| `ewma_volatility(returns)` | Annualised exponentially weighted volatility |
| `portfolio_volatility(weights, covariance)` | Portfolio volatility from covariance |
| `marginal_var(weights, covariance)` | Marginal normal VaR by asset |
| `component_var(weights, covariance)` | Component normal VaR by asset |

## Project Economics

| Function | Description |
|---|---|
| `npv(cashflows, discount_rate)` | Net present value |
| `breakeven_price(capex, opex, production, rate)` | Minimum price for NPV = 0 |

## Units

| Function | Description |
|---|---|
| `usd_per_gal_to_usd_per_bbl(price)` | Convert RBOB/ULSD-style USD/gal to USD/bbl |
| `usd_per_bbl_to_usd_per_gal(price)` | Convert product USD/bbl to USD/gal |
| `product_tons_to_bbl(tons, bbl_per_ton)` | Convert product tons to barrels by density convention |
| `bbl_to_product_tons(barrels, bbl_per_ton)` | Convert barrels to product tons by density convention |

## Market Graph

| Function | Description |
|---|---|
| `build_market_graph()` | Packaged energy relationship graph as `networkx.DiGraph` |
| `market_graph_json()` | UI/agent JSON contract with nodes, edges, metadata, and health |
| `search_market_nodes(query, limit)` | Deterministic search over ids, labels, aliases, descriptions, and related formulas |
| `node_neighborhood(node_id, depth)` | Direct drivers and outputs around a node |
| `graph_context_bundle(query, node_ids, depth, limit)` | Compact graph retrieval bundle for agents |
| `agent_graph_context(node_id, depth)` | Concise strategy-builder context for a market node |

The graph source is YAML at `src/kolmo_stats/graph/market_graph.yml`. It is
descriptive only: it explains market connections for humans, UIs, and agents.
Shock propagation is intentionally deferred.

## Formula Metadata

| Function | Description |
|---|---|
| `formula_catalog()` | Return agent-facing formula metadata |
| `get_formula_metadata(name)` | Return metadata for one public formula |
| `FORMULA_CATALOG` | Static metadata mapping used by tooling and agents |

"""
Formula metadata for agent and UI consumers.

The catalog is intentionally descriptive. It does not import the analytics
functions, which keeps package imports lightweight and avoids circular imports.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def _entry(domain: str, description: str, agent_use: str) -> dict[str, str]:
    return {
        "domain": domain,
        "description": description,
        "agent_use": agent_use,
    }


FORMULA_CATALOG: dict[str, dict[str, str]] = {
    "mean": _entry(
        "statistics",
        "Arithmetic average with NaN handling.",
        "Summarise a clean price, return, or exposure series.",
    ),
    "weighted_mean": _entry(
        "statistics",
        "Weighted average for price, volume, or exposure inputs.",
        "Compute VWAP-style or exposure-weighted market levels.",
    ),
    "rolling_zscore": _entry(
        "statistics",
        "Rolling z-score versus a trailing window.",
        "Detect current market extremes against recent history.",
    ),
    "seasonal_zscore": _entry(
        "statistics",
        "Z-score against a seasonal group.",
        "Compare inventory, demand, or price data against seasonal norms.",
    ),
    "rolling_correlation": _entry(
        "statistics",
        "Rolling correlation between two series.",
        "Track changing relationships between markets or drivers.",
    ),
    "lead_lag_correlation": _entry(
        "statistics",
        "Lag scan for strongest correlation between two series.",
        "Identify which market may be leading another.",
    ),
    "cointegration_beta": _entry(
        "statistics",
        "OLS hedge beta for a two-leg spread.",
        "Estimate hedge ratios for relative-value and residual-spread analysis.",
    ),
    "spread_residual": _entry(
        "statistics",
        "Residual spread after removing a fitted hedge leg.",
        "Build stationary-looking spread residuals for mean-reversion workflows.",
    ),
    "cointegration_zscore": _entry(
        "statistics",
        "Z-score of an OLS residual spread.",
        "Rank how rich or cheap one leg is versus another fitted leg.",
    ),
    "mean_reversion_calibration": _entry(
        "statistics",
        "AR(1)/OU mean-reversion calibration.",
        "Estimate mean, speed, half-life, and volatility for spread processes.",
    ),
    "ou_half_life": _entry(
        "statistics",
        "OU/AR(1) half-life estimate.",
        "Choose holding-period and decay assumptions for mean-reversion trades.",
    ),
    "transition_matrix": _entry(
        "statistics",
        "Observed first-order Markov transition matrix.",
        "Model regime transitions from labelled market states.",
    ),
    "simulate_markov_chain": _entry(
        "statistics",
        "Simulation from an observed Markov transition matrix.",
        "Generate scenario paths for market regimes.",
    ),
    "regime_probabilities": _entry(
        "statistics",
        "Forward regime probabilities from a Markov matrix.",
        "Estimate future state odds from a current market regime.",
    ),
    "curve_shape": _entry(
        "curves",
        "Classify a forward curve as backwardation, contango, flat, or mixed.",
        "Summarise curve structure before choosing spread or carry analytics.",
    ),
    "calendar_spread": _entry(
        "curves",
        "Near-minus-far calendar spread.",
        "Compute time-spread signals using the repo sign convention.",
    ),
    "butterfly_spread": _entry(
        "curves",
        "Front - 2 * middle + back curve butterfly.",
        "Measure local curvature across evenly spaced tenors.",
    ),
    "roll_yield": _entry(
        "curves",
        "Annualised yield from rolling between two tenors.",
        "Estimate carry from futures curve shape.",
    ),
    "curve_slope": _entry(
        "curves",
        "Average first derivative of an ordered curve.",
        "Quantify the steepness of a futures curve.",
    ),
    "prompt_spread": _entry(
        "curves",
        "Prompt M1-M2 spread.",
        "Measure nearby tightness or surplus pressure.",
    ),
    "m1_m3": _entry(
        "curves",
        "M1-M3 calendar spread.",
        "Track front-quarter curve structure.",
    ),
    "m1_m12": _entry(
        "curves",
        "M1-M12 calendar spread.",
        "Track front-year curve structure.",
    ),
    "time_spread_series": _entry(
        "curves",
        "Time series of near-minus-far spreads.",
        "Create historical spread inputs for z-score or risk analysis.",
    ),
    "annualized_carry": _entry(
        "curves",
        "Annualised carry rate between two tenors.",
        "Compare carry opportunities across maturities.",
    ),
    "curve_pca": _entry(
        "curves",
        "Principal-component analysis of curve observations.",
        "Extract level, slope, and curvature-style factors from curve history.",
    ),
    "curve_factor_exposures": _entry(
        "curves",
        "Projection of curve changes onto PCA components.",
        "Explain curve moves in factor terms.",
    ),
    "crack_spread": _entry(
        "spreads",
        "Gross refinery crack spread proxy.",
        "Estimate refinery margin signals for product and crude strategies.",
    ),
    "spark_spread": _entry(
        "spreads",
        "Gross gas-fired generation margin.",
        "Compare power prices against gas fuel cost.",
    ),
    "lng_arbitrage": _entry(
        "spreads",
        "Destination-minus-source LNG arbitrage after costs.",
        "Evaluate whether an LNG route is economically open.",
    ),
    "brent_wti_spread": _entry(
        "spreads",
        "Brent minus WTI spread.",
        "Measure Atlantic Basin versus US crude relative value.",
    ),
    "quality_spread": _entry(
        "spreads",
        "Premium minus discount quality differential.",
        "Compare crude or product quality premia.",
    ),
    "location_spread": _entry(
        "spreads",
        "Destination minus origin location basis.",
        "Measure regional basis before transport and quality adjustments.",
    ),
    "ttf_jkm_spread": _entry(
        "spreads",
        "JKM minus TTF gas spread.",
        "Compare Asian LNG versus European gas pricing.",
    ),
    "henry_hub_ttf_arb": _entry(
        "spreads",
        "Henry Hub to TTF LNG arbitrage after costs.",
        "Estimate US-to-Europe gas export economics.",
    ),
    "lng_netback": _entry(
        "spreads",
        "Destination price less LNG chain costs.",
        "Calculate source netback economics for LNG flows.",
    ),
    "shipping_adjusted_spread": _entry(
        "spreads",
        "Destination minus source minus shipping costs.",
        "Evaluate route-adjusted arbitrage spreads.",
    ),
    "historical_var": _entry(
        "risk",
        "Historical lower-tail VaR.",
        "Estimate loss quantiles from observed returns or P&L.",
    ),
    "expected_shortfall": _entry(
        "risk",
        "Average loss beyond historical VaR.",
        "Measure tail severity beyond the VaR cutoff.",
    ),
    "scenario_pnl": _entry(
        "risk",
        "Position times price shock scenario P&L.",
        "Compute single-scenario market shock impact.",
    ),
    "hedge_ratio": _entry(
        "risk",
        "Minimum-variance hedge ratio.",
        "Estimate hedge units against an asset exposure.",
    ),
    "rolling_var": _entry(
        "risk",
        "Rolling historical VaR.",
        "Track changing downside risk through time.",
    ),
    "rolling_expected_shortfall": _entry(
        "risk",
        "Rolling historical expected shortfall.",
        "Track changing tail-loss severity through time.",
    ),
    "stress_matrix": _entry(
        "risk",
        "Multi-scenario portfolio P&L table.",
        "Compare portfolio impact across named stress scenarios.",
    ),
    "portfolio_scenario_matrix": _entry(
        "risk",
        "Scenario-by-asset portfolio P&L matrix.",
        "Generate scenario matrices for portfolio stress workflows.",
    ),
    "cholesky_decompose": _entry(
        "risk",
        "Cholesky factorisation of a covariance or correlation matrix.",
        "Prepare correlated simulation inputs.",
    ),
    "correlated_normals": _entry(
        "risk",
        "Correlated standard-normal random draws.",
        "Simulate linked market shocks from a correlation matrix.",
    ),
    "correlated_price_shocks": _entry(
        "risk",
        "Correlated price shocks from volatilities and correlations.",
        "Generate scenario shocks for multi-asset portfolios.",
    ),
    "portfolio_volatility": _entry(
        "risk",
        "Portfolio volatility from weights and covariance.",
        "Estimate aggregate risk from asset weights and covariance.",
    ),
    "marginal_var": _entry(
        "risk",
        "Marginal normal VaR by asset.",
        "Rank incremental asset contributions to portfolio VaR.",
    ),
    "component_var": _entry(
        "risk",
        "Component normal VaR by asset.",
        "Attribute portfolio VaR across positions or risk factors.",
    ),
    "realized_volatility": _entry(
        "risk",
        "Annualised realised volatility.",
        "Estimate historical volatility from return observations.",
    ),
    "ewma_volatility": _entry(
        "risk",
        "Annualised exponentially weighted volatility.",
        "Estimate volatility with recent returns weighted more heavily.",
    ),
    "npv": _entry(
        "economics",
        "Net present value of cashflows.",
        "Value project cashflows using a discount rate.",
    ),
    "breakeven_price": _entry(
        "economics",
        "Minimum price for project NPV to reach zero.",
        "Estimate project price thresholds under cost and production assumptions.",
    ),
    "usd_per_gal_to_usd_per_bbl": _entry(
        "units",
        "Convert product prices from USD/gal to USD/bbl.",
        "Normalise RBOB or ULSD quotes before comparing with crude.",
    ),
    "usd_per_bbl_to_usd_per_gal": _entry(
        "units",
        "Convert product prices from USD/bbl to USD/gal.",
        "Convert barrel-based outputs back to exchange quote units.",
    ),
    "product_tons_to_bbl": _entry(
        "units",
        "Convert product tons to barrels with a caller-provided density factor.",
        "Normalise physical product volumes for barrel-based analytics.",
    ),
    "bbl_to_product_tons": _entry(
        "units",
        "Convert barrels to product tons with a caller-provided density factor.",
        "Convert barrel volumes back into product-ton conventions.",
    ),
}


def formula_catalog() -> dict[str, dict[str, str]]:
    """Return a copy of the formula metadata catalog."""
    return deepcopy(FORMULA_CATALOG)


def get_formula_metadata(name: str) -> dict[str, Any]:
    """Return metadata for one formula by public function name."""
    key = str(name).strip()
    if key not in FORMULA_CATALOG:
        raise KeyError(f"Unknown formula metadata: {name!r}")
    return deepcopy(FORMULA_CATALOG[key])

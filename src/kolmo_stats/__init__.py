"""
kolmo — Energy market analytics toolkit.

Public functions for oil/gas-focused statistics, curves, spreads, risk,
units, and project economics.

Quick start
-----------
>>> from kolmo_stats import mean, crack_spread, curve_shape, npv, historical_var
>>> mean([80, 85, 90])
85.0
>>> crack_spread(80, 100, 95, ratio="3-2-1")
18.333333333333332
"""
from kolmo_stats.stats.descriptive import mean, weighted_mean
from kolmo_stats.stats.rolling import rolling_zscore
from kolmo_stats.stats.seasonality import seasonal_zscore
from kolmo_stats.stats.correlations import rolling_correlation, lead_lag_correlation
from kolmo_stats.stats.markov import (
    transition_matrix,
    simulate_markov_chain,
    regime_probabilities,
)

from kolmo_stats.curves.curve_shape import curve_shape
from kolmo_stats.curves.spreads import calendar_spread, butterfly_spread
from kolmo_stats.curves.roll import roll_yield
from kolmo_stats.curves.calculus import curve_slope
from kolmo_stats.curves.carry import (
    prompt_spread,
    m1_m3,
    m1_m12,
    time_spread_series,
    annualized_carry,
)

from kolmo_stats.spreads.crack import crack_spread
from kolmo_stats.spreads.spark import spark_spread
from kolmo_stats.spreads.lng import lng_arbitrage
from kolmo_stats.spreads.oil import brent_wti_spread, quality_spread, location_spread
from kolmo_stats.spreads.gas import (
    ttf_jkm_spread,
    henry_hub_ttf_arb,
    lng_netback,
    shipping_adjusted_spread,
)

from kolmo_stats.risk.var import historical_var, expected_shortfall
from kolmo_stats.risk.stress import scenario_pnl
from kolmo_stats.risk.hedge import hedge_ratio
from kolmo_stats.risk.rolling import rolling_var, rolling_expected_shortfall
from kolmo_stats.risk.matrix import stress_matrix
from kolmo_stats.risk.cholesky import (
    cholesky_decompose,
    correlated_normals,
    correlated_price_shocks,
)

from kolmo_stats.economics.npv import npv
from kolmo_stats.economics.breakeven import breakeven_price
from kolmo_stats.units.conversions import (
    usd_per_gal_to_usd_per_bbl,
    usd_per_bbl_to_usd_per_gal,
    product_tons_to_bbl,
    bbl_to_product_tons,
)

__version__ = "0.2.0"

__all__ = [
    # stats
    "mean",
    "weighted_mean",
    "rolling_zscore",
    "seasonal_zscore",
    "rolling_correlation",
    "lead_lag_correlation",
    "transition_matrix",
    "simulate_markov_chain",
    "regime_probabilities",
    # curves
    "curve_shape",
    "calendar_spread",
    "butterfly_spread",
    "roll_yield",
    "curve_slope",
    "prompt_spread",
    "m1_m3",
    "m1_m12",
    "time_spread_series",
    "annualized_carry",
    # spreads
    "crack_spread",
    "spark_spread",
    "lng_arbitrage",
    "brent_wti_spread",
    "quality_spread",
    "location_spread",
    "ttf_jkm_spread",
    "henry_hub_ttf_arb",
    "lng_netback",
    "shipping_adjusted_spread",
    # risk
    "historical_var",
    "expected_shortfall",
    "scenario_pnl",
    "hedge_ratio",
    "rolling_var",
    "rolling_expected_shortfall",
    "stress_matrix",
    "cholesky_decompose",
    "correlated_normals",
    "correlated_price_shocks",
    # economics
    "npv",
    "breakeven_price",
    # units
    "usd_per_gal_to_usd_per_bbl",
    "usd_per_bbl_to_usd_per_gal",
    "product_tons_to_bbl",
    "bbl_to_product_tons",
]

"""
kolmo — Energy market analytics toolkit.

Twenty public functions for statistics, curves, spreads, risk, and economics.

Quick start
-----------
>>> from kolmo_stats import mean, crack_spread, curve_shape, npv, historical_var
>>> mean([80, 85, 90])
85.0
>>> crack_spread(80, 100, 95, ratio="3-2-1")
10.0
"""
from kolmo_stats.stats.descriptive import mean, weighted_mean
from kolmo_stats.stats.rolling import rolling_zscore
from kolmo_stats.stats.seasonality import seasonal_zscore
from kolmo_stats.stats.correlations import rolling_correlation, lead_lag_correlation

from kolmo_stats.curves.curve_shape import curve_shape
from kolmo_stats.curves.spreads import calendar_spread, butterfly_spread
from kolmo_stats.curves.roll import roll_yield
from kolmo_stats.curves.calculus import curve_slope

from kolmo_stats.spreads.crack import crack_spread
from kolmo_stats.spreads.spark import spark_spread
from kolmo_stats.spreads.lng import lng_arbitrage

from kolmo_stats.risk.var import historical_var, expected_shortfall
from kolmo_stats.risk.stress import scenario_pnl
from kolmo_stats.risk.hedge import hedge_ratio

from kolmo_stats.economics.npv import npv
from kolmo_stats.economics.breakeven import breakeven_price

__version__ = "0.2.0"

__all__ = [
    # stats
    "mean",
    "weighted_mean",
    "rolling_zscore",
    "seasonal_zscore",
    "rolling_correlation",
    "lead_lag_correlation",
    # curves
    "curve_shape",
    "calendar_spread",
    "butterfly_spread",
    "roll_yield",
    "curve_slope",
    # spreads
    "crack_spread",
    "spark_spread",
    "lng_arbitrage",
    # risk
    "historical_var",
    "expected_shortfall",
    "scenario_pnl",
    "hedge_ratio",
    # economics
    "npv",
    "breakeven_price",
]

"""
Rolling statistical helpers used by kolmo.stats.

Thin wrappers around pandas rolling so that the computation logic lives
in one place. Future C++ backends for high-frequency rolling calculations
can be substituted here.
"""
from __future__ import annotations

import pandas as pd


def rolling_mean(
    series: pd.Series, window: int, min_periods: int | None = None
) -> pd.Series:
    return series.rolling(window=window, min_periods=min_periods or window).mean()


def rolling_std(
    series: pd.Series, window: int, min_periods: int | None = None
) -> pd.Series:
    return series.rolling(window=window, min_periods=min_periods or window).std()


def rolling_cov(
    x: pd.Series, y: pd.Series, window: int, min_periods: int | None = None
) -> pd.Series:
    return x.rolling(window=window, min_periods=min_periods or window).cov(y)

"""
Rolling statistical measures for energy time series.
"""
from __future__ import annotations

import pandas as pd

from kolmo_stats.engine.statistics import rolling_mean, rolling_std
from kolmo_stats.utils.explain import make_explain


def rolling_zscore(
    series,
    window: int = 60,
    min_periods: int | None = None,
    explain: bool = False,
) -> pd.Series | dict:
    """
    Rolling z-score — shows how extreme a price, spread, or margin is
    relative to its own recent history.

    A z-score of +2 means the current value is two standard deviations
    above its rolling mean, which often signals an extreme condition.

    Parameters
    ----------
    series : array-like or pandas Series
    window : int
        Number of periods in the rolling window (default 60).
    min_periods : int, optional
        Minimum number of observations required to produce a result.
        Defaults to window.
    explain : bool

    Returns
    -------
    pandas Series, or dict if explain=True

    Formula
    -------
    z = (x - rolling_mean(x, window)) / rolling_std(x, window)

    Examples
    --------
    >>> import pandas as pd
    >>> prices = pd.Series([80, 82, 85, 79, 90, 75, 95])
    >>> rolling_zscore(prices, window=3)
    """
    if not isinstance(series, pd.Series):
        series = pd.Series(series, dtype=float)

    mu = rolling_mean(series, window, min_periods)
    sigma = rolling_std(series, window, min_periods)
    z = (series - mu) / sigma
    z.name = "rolling_zscore"

    if explain:
        return make_explain(
            result=z,
            explanation=(
                f"Rolling z-score over a {window}-period window. "
                "Values above +2 or below -2 often indicate extreme conditions."
            ),
            formula="z = (x - rolling_mean) / rolling_std",
            inputs={
                "window": window,
                "min_periods": min_periods or window,
                "n_observations": len(series),
            },
        )
    return z

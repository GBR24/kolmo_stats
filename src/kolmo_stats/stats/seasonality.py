"""
Seasonal z-scores for energy time series.
"""
from __future__ import annotations

import pandas as pd

from kolmo_stats.utils.explain import make_explain
from kolmo_stats.utils.validation import require_datetime_index

_VALID_PERIODS = {"month", "quarter", "week_of_year", "day_of_year"}


def seasonal_zscore(
    series: pd.Series,
    period: str = "month",
    explain: bool = False,
) -> pd.Series | dict:
    """
    Z-score relative to a seasonal group (month, quarter, etc.).

    Instead of comparing a value to the whole history, this compares it only
    to the same seasonal period in the supplied history — e.g., January vs
    other Januaries. This is how analysts think about gas storage, seasonal
    cracks, and power demand.

    Parameters
    ----------
    series : pandas Series with a DatetimeIndex
    period : {"month", "quarter", "week_of_year", "day_of_year"}
    explain : bool

    Returns
    -------
    pandas Series of z-scores with the same index, or dict if explain=True

    Examples
    --------
    >>> import pandas as pd, numpy as np
    >>> idx = pd.date_range("2020-01-01", periods=730, freq="D")
    >>> storage = pd.Series(np.random.randn(730) + 100, index=idx)
    >>> seasonal_zscore(storage, period="month")
    """
    if period not in _VALID_PERIODS:
        raise ValueError(f"period must be one of {_VALID_PERIODS}; got '{period}'")
    require_datetime_index(series)

    idx = series.index
    if period == "month":
        groups = pd.Series(idx.month, index=idx)
    elif period == "quarter":
        groups = pd.Series(idx.quarter, index=idx)
    elif period == "week_of_year":
        groups = pd.Series(idx.isocalendar().week.astype(int).values, index=idx)
    else:
        groups = pd.Series(idx.day_of_year, index=idx)

    stats = series.groupby(groups).agg(["mean", "std"])
    g_mean = groups.map(stats["mean"])
    g_std = groups.map(stats["std"])

    z = (series - g_mean) / g_std
    z.name = "seasonal_zscore"

    if explain:
        return make_explain(
            result=z,
            explanation=(
                f"Seasonal z-score grouped by {period}. "
                "Positive values indicate above-seasonal-average conditions."
            ),
            formula="z = (x - group_mean) / group_std",
            inputs={
                "period": period,
                "n_groups": int(stats.shape[0]),
                "n_observations": len(series),
            },
        )
    return z

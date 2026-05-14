"""
Correlation analysis for energy market pairs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.engine.arrays import validate_same_length
from kolmo_stats.utils.explain import make_explain


def rolling_correlation(
    x,
    y,
    window: int = 60,
    min_periods: int | None = None,
    explain: bool = False,
) -> pd.Series | dict:
    """
    Rolling Pearson correlation between two energy time series.

    Useful for measuring dynamic relationships such as Brent vs Gasoil,
    JKM vs TTF, or crude vs equity indices.

    Parameters
    ----------
    x, y : array-like or pandas Series of equal length
    window : int
        Rolling window in periods (default 60).
    min_periods : int, optional
    explain : bool

    Returns
    -------
    pandas Series of correlations, or dict if explain=True

    Examples
    --------
    >>> import pandas as pd, numpy as np
    >>> brent = pd.Series(np.random.randn(200).cumsum() + 80)
    >>> gasoil = brent * 0.95 + np.random.randn(200)
    >>> rolling_correlation(brent, gasoil, window=30)
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if min_periods is not None and min_periods <= 0:
        raise ValueError("min_periods must be positive")

    if not isinstance(x, pd.Series):
        x = pd.Series(x, dtype=float)
    if not isinstance(y, pd.Series):
        y = pd.Series(y, dtype=float)

    validate_same_length(x, y, ("x", "y"))

    result = x.rolling(window=window, min_periods=min_periods or window).corr(y)
    result.name = "rolling_correlation"

    if explain:
        return make_explain(
            result=result,
            explanation=(
                f"Rolling {window}-period Pearson correlation. "
                "Values near +1 mean the series move together; "
                "near -1 they move in opposite directions."
            ),
            formula="corr = cov(x, y) / (std(x) * std(y))",
            inputs={"window": window, "n_observations": len(x)},
        )
    return result


def lead_lag_correlation(
    x,
    y,
    max_lag: int = 30,
    method: str = "pearson",
    explain: bool = False,
) -> pd.DataFrame | dict:
    """
    Lead-lag correlation sweep — finds whether one market tends to move
    before another.

    A positive best_lag means x leads y (x moves first).
    A negative best_lag means y leads x.

    Parameters
    ----------
    x, y : array-like or pandas Series of equal length
    max_lag : int
        Maximum lag to test in either direction (default 30).
    method : str
        Correlation method — currently only "pearson" is supported.
    explain : bool

    Returns
    -------
    pandas DataFrame with columns ["lag", "correlation"].
    DataFrame.attrs contains "best_lag" and "best_correlation".
    Returns dict if explain=True.

    Examples
    --------
    >>> import pandas as pd, numpy as np
    >>> x = pd.Series(np.random.randn(300))
    >>> y = x.shift(5) + np.random.randn(300) * 0.3   # y lags x by 5
    >>> result = lead_lag_correlation(x, y, max_lag=20)
    >>> result.attrs["best_lag"]
    5
    """
    if method != "pearson":
        raise ValueError("method must be 'pearson'")
    if max_lag < 0:
        raise ValueError("max_lag must be non-negative")

    if not isinstance(x, pd.Series):
        x = pd.Series(x, dtype=float)
    if not isinstance(y, pd.Series):
        y = pd.Series(y, dtype=float)

    validate_same_length(x, y, ("x", "y"))
    if max_lag >= len(x):
        raise ValueError("max_lag must be smaller than the series length")

    lags = list(range(-max_lag, max_lag + 1))
    corrs: list[float] = []
    # Use numpy arrays to avoid pandas label-alignment issues when slicing
    xv = x.to_numpy(dtype=float)
    yv = y.to_numpy(dtype=float)

    for lag in lags:
        if lag > 0:
            a, b = xv[: len(xv) - lag], yv[lag:]
        elif lag < 0:
            a, b = xv[-lag:], yv[: len(yv) + lag]
        else:
            a, b = xv, yv
        c = float(np.corrcoef(a, b)[0, 1])
        corrs.append(c if not np.isnan(c) else 0.0)

    df = pd.DataFrame({"lag": lags, "correlation": corrs})
    best_idx = df["correlation"].abs().idxmax()
    df.attrs["best_lag"] = int(df.loc[best_idx, "lag"])
    df.attrs["best_correlation"] = float(df.loc[best_idx, "correlation"])

    if explain:
        return make_explain(
            result=df,
            explanation=(
                "Lead-lag correlation sweep. "
                f"Best lag: {df.attrs['best_lag']} periods "
                f"(correlation {df.attrs['best_correlation']:.3f}). "
                "Positive lag = x leads y; negative lag = y leads x."
            ),
            formula="corr(x[0:n-lag], y[lag:n]) for each lag",
            inputs={
                "max_lag": max_lag,
                "best_lag": df.attrs["best_lag"],
                "best_correlation": df.attrs["best_correlation"],
            },
        )
    return df

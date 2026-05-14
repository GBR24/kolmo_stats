"""
Descriptive statistics for energy market data.
"""
from __future__ import annotations

import numpy as np

from kolmo_stats.engine.arrays import coerce_array, validate_same_length
from kolmo_stats.utils.explain import make_explain


def mean(
    values,
    ignore_nan: bool = True,
    explain: bool = False,
) -> float | dict:
    """
    Arithmetic mean of a numeric series.

    Parameters
    ----------
    values : list, tuple, numpy array, or pandas Series
    ignore_nan : bool
        Skip NaN values. If False and NaN is present, raises ValueError.
    explain : bool
        Return a dict with result, explanation, formula, and inputs.

    Returns
    -------
    float, or dict if explain=True

    Examples
    --------
    >>> mean([80, 85, 90])
    85.0
    >>> mean([80, float('nan'), 90])
    85.0
    """
    arr = coerce_array(values)
    if len(arr) == 0:
        raise ValueError("mean() requires at least one value")

    if ignore_nan:
        clean = arr[~np.isnan(arr)]
        if len(clean) == 0:
            raise ValueError("All values are NaN")
        result = float(np.mean(clean))
        n = int(len(clean))
    else:
        if np.any(np.isnan(arr)):
            raise ValueError(
                "Series contains NaN values. Set ignore_nan=True to skip them."
            )
        result = float(np.mean(arr))
        n = int(len(arr))

    if explain:
        return make_explain(
            result=result,
            explanation="Arithmetic mean: sum of all values divided by the count.",
            formula="mean = sum(x) / n",
            inputs={"n": n, "sum": round(result * n, 10)},
        )
    return result


def weighted_mean(
    values,
    weights,
    ignore_nan: bool = True,
    explain: bool = False,
) -> float | dict:
    """
    Weighted average — useful for VWAP, exposure-weighted returns, and
    portfolio calculations.

    Parameters
    ----------
    values : array-like of prices or returns
    weights : array-like of volumes, exposures, or other weights
    ignore_nan : bool
        Drop pairs where either value or weight is NaN.
    explain : bool

    Returns
    -------
    float, or dict if explain=True

    Raises
    ------
    ValueError if lengths differ or weights sum to zero.

    Examples
    --------
    >>> weighted_mean([80, 85], [0.7, 0.3])
    81.5
    """
    v = coerce_array(values)
    w = coerce_array(weights)
    validate_same_length(v, w, ("values", "weights"))

    if ignore_nan:
        mask = ~(np.isnan(v) | np.isnan(w))
        v, w = v[mask], w[mask]
    elif np.any(np.isnan(v)) or np.any(np.isnan(w)):
        raise ValueError(
            "Values or weights contain NaN. Set ignore_nan=True to skip pairs."
        )

    if len(v) == 0:
        raise ValueError("No valid (non-NaN) value/weight pairs found")

    w_sum = float(np.sum(w))
    if w_sum == 0:
        raise ValueError("Weights sum to zero — cannot compute weighted mean")

    result = float(np.dot(v, w) / w_sum)

    if explain:
        return make_explain(
            result=result,
            explanation=(
                "Weighted mean: each value scaled by its weight. "
                "Useful for volume-weighted average prices (VWAP)."
            ),
            formula="weighted_mean = sum(v_i * w_i) / sum(w_i)",
            inputs={"values": v.tolist(), "weights": w.tolist(), "weight_sum": w_sum},
        )
    return result

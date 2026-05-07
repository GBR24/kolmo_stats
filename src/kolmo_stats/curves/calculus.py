"""
Curve calculus: numerical derivatives of futures curves.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.engine.numerical import average_slope
from kolmo_stats.utils.explain import make_explain


def curve_slope(
    curve,
    method: str = "linear",
    explain: bool = False,
) -> float | dict:
    """
    Estimate the average slope of a futures curve using numerical differentiation.

    The slope is the first derivative of price with respect to tenor position.
    A negative slope indicates backwardation; positive indicates contango.
    Steeper absolute slope = more pronounced market structure.

    Parameters
    ----------
    curve : dict, pandas Series, list, or numpy array
        Prices ordered from near to far. If no numeric x-axis is given,
        tenors are treated as equally spaced integers.
    method : str
        Currently only "linear" (numpy gradient) is supported.
    explain : bool

    Returns
    -------
    float ($/period), or dict if explain=True

    Examples
    --------
    >>> curve_slope({"M1": 90, "M2": 88, "M3": 86})
    -2.0
    >>> curve_slope([80, 82, 85, 87])
    2.333...
    """
    if isinstance(curve, dict):
        prices = np.array(list(curve.values()), dtype=float)
    elif isinstance(curve, pd.Series):
        prices = curve.to_numpy(dtype=float)
    elif isinstance(curve, (list, tuple)):
        prices = np.array(curve, dtype=float)
    else:
        prices = np.asarray(curve, dtype=float)

    if len(prices) < 2:
        raise ValueError("curve_slope requires at least 2 data points")

    slope = average_slope(prices)

    if explain:
        if slope < 0:
            interp = "downward-sloping curve (backwardation)"
        elif slope > 0:
            interp = "upward-sloping curve (contango)"
        else:
            interp = "flat curve"
        return make_explain(
            result=slope,
            explanation=f"Average first derivative of the curve: {interp}.",
            formula="mean(d(price)/d(tenor)) via central differences",
            inputs={"n_tenors": len(prices), "slope": slope, "interpretation": interp},
        )
    return float(slope)

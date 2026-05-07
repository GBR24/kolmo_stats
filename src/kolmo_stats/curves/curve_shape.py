"""
Classify the shape of a commodity futures curve.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.utils.explain import make_explain


def curve_shape(
    curve,
    flat_threshold: float = 0.001,
    explain: bool = False,
) -> str | dict:
    """
    Classify a futures curve as backwardation, contango, flat, or mixed.

    In backwardation the near contract is more expensive than the far
    contract — a typical sign of physical tightness. In contango the far
    contract is more expensive — common when supply is plentiful.

    Parameters
    ----------
    curve : dict, pandas Series, list, or numpy array
        Prices ordered from near to far contract.
    flat_threshold : float
        Relative change below which a move is treated as flat (default 0.1%).
    explain : bool

    Returns
    -------
    str — one of "backwardation", "contango", "flat", "mixed"
    or dict if explain=True

    Examples
    --------
    >>> curve_shape({"M1": 90, "M2": 88, "M3": 86})
    'backwardation'
    >>> curve_shape({"M1": 80, "M2": 82, "M3": 85})
    'contango'
    """
    if isinstance(curve, dict):
        prices = np.array(list(curve.values()), dtype=float)
    elif isinstance(curve, pd.Series):
        prices = curve.to_numpy(dtype=float)
    else:
        prices = np.asarray(curve, dtype=float)

    if len(prices) < 2:
        raise ValueError("curve_shape requires at least 2 data points")

    changes = np.diff(prices) / np.abs(prices[:-1])
    is_up = changes > flat_threshold
    is_down = changes < -flat_threshold
    is_flat_pt = ~is_up & ~is_down

    if np.all(is_flat_pt):
        shape = "flat"
    elif np.all(is_down | is_flat_pt):
        shape = "backwardation"
    elif np.all(is_up | is_flat_pt):
        shape = "contango"
    else:
        shape = "mixed"

    if explain:
        return make_explain(
            result=shape,
            explanation=(
                f"Curve is '{shape}'. "
                "Backwardation = near > far (tight physical market). "
                "Contango = near < far (plentiful supply / cheap storage)."
            ),
            formula="changes = diff(prices) / abs(prices[:-1]); classify by sign",
            inputs={
                "n_tenors": len(prices),
                "flat_threshold": flat_threshold,
                "relative_changes": changes.tolist(),
            },
        )
    return shape

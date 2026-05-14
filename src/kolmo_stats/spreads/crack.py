"""
Refinery crack spread calculations.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.utils.explain import make_explain

_SUPPORTED_RATIOS = {"5-3-2", "3-2-1", "2-1-1", "simple"}
_FORMULAS = {
    "5-3-2": "((3 * gasoline) + (2 * distillate) - (5 * crude)) / 5",
    "3-2-1": "((2 * gasoline) + distillate - (3 * crude)) / 3",
    "2-1-1": "(gasoline + distillate - (2 * crude)) / 2",
    "simple": "gasoline - crude",
}


def crack_spread(
    crude,
    gasoline,
    distillate=None,
    ratio: str = "3-2-1",
    explain: bool = False,
):
    """
    Refinery crack spread — a gross proxy for the margin between crude
    input costs and refined product values.

    Crack spreads do not include all product revenues, operating costs,
    refinery yield differences, logistics, or location/specification effects.

    Supports scalars, lists, numpy arrays, and pandas Series.

    Parameters
    ----------
    crude : numeric or array-like
        Crude oil price in $/bbl.
    gasoline : numeric or array-like
        Gasoline price in $/bbl (multiply $/gal by 42 before passing).
    distillate : numeric or array-like, optional
        Distillate (diesel/heating oil) price in $/bbl. Required for 5-3-2,
        3-2-1, and 2-1-1.
    ratio : {"5-3-2", "3-2-1", "2-1-1", "simple"}
        Crack spread ratio to use (default "3-2-1").
    explain : bool

    Returns
    -------
    float, numpy array, or pandas Series (matches input type)
    or dict if explain=True

    Examples
    --------
    >>> crack_spread(80, 100, 95, ratio="3-2-1")
    18.333333333333332
    >>> crack_spread(80, 95, ratio="simple")
    15.0
    """
    if ratio not in _SUPPORTED_RATIOS:
        raise ValueError(f"ratio must be one of {_SUPPORTED_RATIOS}; got '{ratio}'")
    uses_distillate = ratio in ("5-3-2", "3-2-1", "2-1-1")
    if uses_distillate and distillate is None:
        raise ValueError(f"distillate is required for the {ratio} crack spread")

    is_pandas = (
        isinstance(crude, pd.Series)
        or isinstance(gasoline, pd.Series)
        or (uses_distillate and isinstance(distillate, pd.Series))
    )
    is_scalar = (
        np.isscalar(crude)
        and np.isscalar(gasoline)
        and (not uses_distillate or np.isscalar(distillate))
    )
    index = crude.index if isinstance(crude, pd.Series) else (
        gasoline.index if isinstance(gasoline, pd.Series) else (
            distillate.index if uses_distillate and isinstance(distillate, pd.Series) else None
        )
    )

    c = np.asarray(crude, dtype=float)
    g = np.asarray(gasoline, dtype=float)

    if ratio == "5-3-2":
        d = np.asarray(distillate, dtype=float)
        result = (3 * g + 2 * d - 5 * c) / 5
    elif ratio == "3-2-1":
        d = np.asarray(distillate, dtype=float)
        result = (2 * g + d - 3 * c) / 3
    elif ratio == "2-1-1":
        d = np.asarray(distillate, dtype=float)
        result = (g + d - 2 * c) / 2
    else:
        result = g - c

    if is_pandas and index is not None:
        result = pd.Series(result, index=index)
    elif is_scalar:
        result = float(result)

    if explain:
        return make_explain(
            result=result,
            explanation=(
                f"Gross refinery crack spread proxy using the {ratio} ratio."
            ),
            formula=_FORMULAS[ratio],
            inputs={
                "crude": float(np.mean(c)),
                "gasoline": float(np.mean(g)),
                "distillate": (
                    float(np.mean(np.asarray(distillate, dtype=float)))
                    if distillate is not None
                    else None
                ),
                "ratio": ratio,
            },
        )
    return result

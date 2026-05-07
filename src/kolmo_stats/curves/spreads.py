"""
Futures curve spread calculations.
"""
from __future__ import annotations

import pandas as pd

from kolmo_stats.utils.explain import make_explain


def _get_price(curve, key) -> float:
    if isinstance(curve, dict):
        if key not in curve:
            raise KeyError(f"Tenor '{key}' not found in curve")
        return float(curve[key])
    if isinstance(curve, pd.Series):
        return float(curve[key])
    raise TypeError("curve must be a dict or pandas Series")


def calendar_spread(
    curve,
    near: str,
    far: str,
    explain: bool = False,
) -> float | dict:
    """
    Calendar spread: near contract price minus far contract price.

    A positive value indicates backwardation (near > far).
    Common examples: M1-M3 Brent, Q1-Q2 TTF, Cal25-Cal26 power.

    Parameters
    ----------
    curve : dict or pandas Series
        Keys/index are tenor labels; values are prices.
    near : str
        Label of the near-dated contract.
    far : str
        Label of the far-dated contract.
    explain : bool

    Returns
    -------
    float, or dict if explain=True

    Examples
    --------
    >>> calendar_spread({"M1": 84, "M3": 80, "M6": 77}, "M1", "M6")
    7.0
    """
    n_price = _get_price(curve, near)
    f_price = _get_price(curve, far)
    spread = n_price - f_price

    if explain:
        return make_explain(
            result=spread,
            explanation=f"Calendar spread {near} minus {far}. Positive = backwardation.",
            formula="spread = near_price - far_price",
            inputs={"near": near, "near_price": n_price, "far": far, "far_price": f_price},
        )
    return spread


def butterfly_spread(
    curve,
    front: str,
    middle: str,
    back: str,
    explain: bool = False,
) -> float | dict:
    """
    Futures butterfly spread: front - 2*middle + back.

    A positive butterfly means the middle contract is cheap relative to the
    wings, often signalling a kink or anomaly in the curve.

    Parameters
    ----------
    curve : dict or pandas Series
    front, middle, back : str
        Tenor labels for each leg.
    explain : bool

    Returns
    -------
    float, or dict if explain=True

    Examples
    --------
    >>> butterfly_spread({"M1": 90, "M2": 85, "M3": 82}, "M1", "M2", "M3")
    2.0
    """
    f_price = _get_price(curve, front)
    m_price = _get_price(curve, middle)
    b_price = _get_price(curve, back)
    spread = f_price - 2 * m_price + b_price

    if explain:
        return make_explain(
            result=spread,
            explanation=(
                f"Butterfly {front} - 2*{middle} + {back}. "
                "Positive = middle is cheap relative to wings."
            ),
            formula="front - 2 * middle + back",
            inputs={"front": f_price, "middle": m_price, "back": b_price},
        )
    return spread

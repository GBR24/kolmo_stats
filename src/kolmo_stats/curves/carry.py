"""
Oil and gas curve carry / time-spread helpers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.curves.spreads import calendar_spread
from kolmo_stats.engine.arrays import validate_same_length
from kolmo_stats.utils.explain import make_explain


def prompt_spread(
    curve,
    prompt: str = "M1",
    second: str = "M2",
    explain: bool = False,
) -> float | dict:
    """
    Prompt spread: prompt contract minus second nearby contract.

    For oil and gas curves this is commonly M1-M2.
    """
    result = calendar_spread(curve, prompt, second)
    if explain:
        return make_explain(
            result=result,
            explanation=f"Prompt spread {prompt}-{second}. Positive = backwardation.",
            formula="spread = prompt_price - second_price",
            inputs={"prompt": prompt, "second": second},
        )
    return result


def m1_m3(curve, explain: bool = False) -> float | dict:
    """M1-M3 calendar spread."""
    result = calendar_spread(curve, "M1", "M3")
    if explain:
        return make_explain(
            result=result,
            explanation="M1-M3 calendar spread. Positive = backwardation.",
            formula="spread = M1 - M3",
            inputs={"near": "M1", "far": "M3"},
        )
    return result


def m1_m12(curve, explain: bool = False) -> float | dict:
    """M1-M12 calendar spread."""
    result = calendar_spread(curve, "M1", "M12")
    if explain:
        return make_explain(
            result=result,
            explanation="M1-M12 calendar spread. Positive = backwardation.",
            formula="spread = M1 - M12",
            inputs={"near": "M1", "far": "M12"},
        )
    return result


def time_spread_series(
    near,
    far,
    explain: bool = False,
):
    """
    Time series of a calendar spread: near contract series minus far series.
    """
    is_pandas = isinstance(near, pd.Series) or isinstance(far, pd.Series)
    is_scalar = np.isscalar(near) and np.isscalar(far)

    if is_pandas:
        near_series = near if isinstance(near, pd.Series) else pd.Series(near, index=far.index)
        far_series = far if isinstance(far, pd.Series) else pd.Series(far, index=near.index)
        result = near_series.astype(float) - far_series.astype(float)
    else:
        n = np.asarray(near, dtype=float)
        f = np.asarray(far, dtype=float)
        if not is_scalar:
            validate_same_length(n, f, ("near", "far"))
        result = n - f
        if is_scalar:
            result = float(result)

    if explain:
        return make_explain(
            result=result,
            explanation="Calendar time-spread series: near price minus far price.",
            formula="spread_t = near_t - far_t",
            inputs={"n_observations": len(result) if hasattr(result, "__len__") else 1},
        )
    return result


def annualized_carry(
    near_price,
    far_price,
    days_between: int,
    explain: bool = False,
):
    """
    Annualized carry implied by a near/far pair.

    Positive values indicate contango carry cost: far is above near. Negative
    values indicate backwardation.
    """
    if days_between <= 0:
        raise ValueError("days_between must be positive")

    near = np.asarray(near_price, dtype=float)
    far = np.asarray(far_price, dtype=float)
    if np.any(near == 0):
        raise ValueError("near_price cannot contain zero values")

    result = ((far - near) / near) * (365 / days_between)
    if np.isscalar(near_price) and np.isscalar(far_price):
        result = float(result)
    elif isinstance(near_price, pd.Series):
        result = pd.Series(result, index=near_price.index, name="annualized_carry")
    elif isinstance(far_price, pd.Series):
        result = pd.Series(result, index=far_price.index, name="annualized_carry")

    if explain:
        return make_explain(
            result=result,
            explanation=(
                "Annualized carry from near to far. Positive = contango; "
                "negative = backwardation."
            ),
            formula="carry = ((far - near) / near) * (365 / days_between)",
            inputs={
                "near_price": near_price,
                "far_price": far_price,
                "days_between": days_between,
            },
        )
    return result

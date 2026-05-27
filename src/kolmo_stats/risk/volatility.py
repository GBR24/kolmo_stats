"""
Volatility helpers for oil and gas returns.
"""
from __future__ import annotations

import math

import numpy as np

from kolmo_stats.engine.arrays import coerce_array
from kolmo_stats.utils.explain import make_explain
from kolmo_stats.utils.validation import require_in_range, require_positive


def realized_volatility(
    returns,
    periods_per_year: int = 252,
    explain: bool = False,
) -> float | dict:
    """
    Annualised realised volatility from a return series.
    """
    require_positive(periods_per_year, "periods_per_year")
    arr = _clean_returns(returns)
    result = float(np.std(arr, ddof=1) * math.sqrt(periods_per_year))
    if explain:
        return make_explain(
            result=result,
            explanation="Annualised realised volatility from historical returns.",
            formula="vol = std(returns) * sqrt(periods_per_year)",
            inputs={"n": len(arr), "periods_per_year": periods_per_year},
        )
    return result


def ewma_volatility(
    returns,
    lambda_: float = 0.94,
    periods_per_year: int = 252,
    explain: bool = False,
) -> float | dict:
    """
    Annualised exponentially weighted volatility.

    ``lambda_=0.94`` is the common daily RiskMetrics-style decay value.
    """
    require_in_range(lambda_, 0.0, 1.0, "lambda_")
    if lambda_ in (0.0, 1.0):
        raise ValueError("lambda_ must be strictly between 0 and 1")
    require_positive(periods_per_year, "periods_per_year")
    arr = _clean_returns(returns)

    variance = float(arr[0] ** 2)
    for ret in arr[1:]:
        variance = lambda_ * variance + (1.0 - lambda_) * float(ret) ** 2
    result = math.sqrt(variance) * math.sqrt(periods_per_year)

    if explain:
        return make_explain(
            result=result,
            explanation="Annualised EWMA volatility with exponentially decaying return weights.",
            formula="var_t = lambda*var_t-1 + (1-lambda)*r_t^2",
            inputs={"n": len(arr), "lambda_": lambda_, "periods_per_year": periods_per_year},
        )
    return result


def _clean_returns(returns) -> np.ndarray:
    arr = coerce_array(returns)
    arr = arr[~np.isnan(arr)]
    if len(arr) < 2:
        raise ValueError("returns must contain at least 2 valid observations")
    return arr

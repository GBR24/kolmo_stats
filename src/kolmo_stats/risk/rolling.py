"""
Rolling market risk measures.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.utils.explain import make_explain


def rolling_var(
    returns,
    window: int = 60,
    confidence: float = 0.95,
    min_periods: int | None = None,
    explain: bool = False,
) -> pd.Series | dict:
    """
    Rolling historical VaR over a fixed lookback window.

    Inputs should be returns or P&L changes where losses are negative.
    Output is a loss threshold in the same units as the input.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if not 0 < confidence < 1:
        raise ValueError(f"confidence must be between 0 and 1; got {confidence}")

    series = returns if isinstance(returns, pd.Series) else pd.Series(returns, dtype=float)
    percentile = 1 - confidence
    result = -series.rolling(window=window, min_periods=min_periods or window).quantile(percentile)
    result.name = "rolling_var"

    if explain:
        return make_explain(
            result=result,
            explanation=(
                f"Rolling historical VaR at {confidence:.0%} confidence over "
                f"a {window}-period window."
            ),
            formula="VaR_t = -rolling_quantile(returns, 1 - confidence)",
            inputs={
                "window": window,
                "confidence": confidence,
                "tail_probability": 1 - confidence,
                "min_periods": min_periods or window,
                "n_observations": len(series),
            },
        )
    return result


def rolling_expected_shortfall(
    returns,
    window: int = 60,
    confidence: float = 0.95,
    min_periods: int | None = None,
    explain: bool = False,
) -> pd.Series | dict:
    """
    Rolling historical Expected Shortfall over a fixed lookback window.

    ES is the average historical loss inside the rolling tail beyond VaR.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if not 0 < confidence < 1:
        raise ValueError(f"confidence must be between 0 and 1; got {confidence}")

    series = returns if isinstance(returns, pd.Series) else pd.Series(returns, dtype=float)
    percentile = (1 - confidence) * 100

    def _es(values: np.ndarray) -> float:
        clean = values[~np.isnan(values)]
        if len(clean) == 0:
            return np.nan
        var_threshold = -np.percentile(clean, percentile)
        tail = clean[clean <= -var_threshold]
        return -float(np.mean(tail)) if len(tail) else var_threshold

    result = series.rolling(
        window=window,
        min_periods=min_periods or window,
    ).apply(_es, raw=True)
    result.name = "rolling_expected_shortfall"

    if explain:
        return make_explain(
            result=result,
            explanation=(
                f"Rolling Expected Shortfall at {confidence:.0%} confidence "
                f"over a {window}-period window."
            ),
            formula="ES_t = -mean(returns in rolling tail beyond VaR_t)",
            inputs={
                "window": window,
                "confidence": confidence,
                "tail_probability": 1 - confidence,
                "min_periods": min_periods or window,
                "n_observations": len(series),
            },
        )
    return result

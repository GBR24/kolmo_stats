"""
Value at Risk and Expected Shortfall.
"""
from __future__ import annotations

import numpy as np

from kolmo_stats.engine.arrays import coerce_array
from kolmo_stats.utils.explain import make_explain


def historical_var(
    returns,
    confidence: float = 0.95,
    explain: bool = False,
) -> float | dict:
    """
    Historical Value at Risk (VaR) — the loss not exceeded at a given
    confidence level based on actual historical returns.

    VaR at 95% confidence means: in 95% of days, the loss was less than
    this number.

    Parameters
    ----------
    returns : array-like
        Daily (or periodic) returns or P&L changes. Losses should be negative.
    confidence : float
        Confidence level between 0 and 1 (default 0.95).
    explain : bool

    Returns
    -------
    float (positive loss amount), or dict if explain=True

    Examples
    --------
    >>> import numpy as np
    >>> np.random.seed(0)
    >>> returns = np.random.randn(1000) * 2
    >>> historical_var(returns, confidence=0.95)
    """
    arr = coerce_array(returns)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        raise ValueError("No valid returns provided")
    if not 0 < confidence < 1:
        raise ValueError(f"confidence must be between 0 and 1; got {confidence}")

    percentile = (1 - confidence) * 100
    var = float(-np.percentile(arr, percentile))

    if explain:
        return make_explain(
            result=var,
            explanation=(
                f"Historical VaR at {confidence:.0%} confidence: "
                f"the loss exceeded only {100 - percentile:.0f}% of the time."
            ),
            formula=f"VaR = -percentile(returns, {percentile:.1f})",
            inputs={
                "n_observations": len(arr),
                "confidence": confidence,
                "percentile": percentile,
                "mean_return": float(np.mean(arr)),
            },
        )
    return var


def expected_shortfall(
    returns,
    confidence: float = 0.95,
    explain: bool = False,
) -> float | dict:
    """
    Expected Shortfall (ES), also called CVaR — the average loss in the
    tail beyond VaR.

    ES is a more conservative and coherent risk measure than VaR because
    it accounts for the severity of extreme losses, not just their frequency.

    Parameters
    ----------
    returns : array-like
        Daily (or periodic) returns or P&L changes. Losses should be negative.
    confidence : float
        Confidence level between 0 and 1 (default 0.95).
    explain : bool

    Returns
    -------
    float (positive loss amount), or dict if explain=True
    """
    arr = coerce_array(returns)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        raise ValueError("No valid returns provided")
    if not 0 < confidence < 1:
        raise ValueError(f"confidence must be between 0 and 1; got {confidence}")

    var_threshold = float(-np.percentile(arr, (1 - confidence) * 100))
    tail = arr[arr <= -var_threshold]
    es = float(-np.mean(tail)) if len(tail) > 0 else var_threshold

    if explain:
        return make_explain(
            result=es,
            explanation=(
                f"Expected Shortfall (CVaR) at {confidence:.0%}: "
                "average loss in the worst tail beyond VaR."
            ),
            formula="ES = mean(losses where loss > VaR)",
            inputs={
                "confidence": confidence,
                "var": var_threshold,
                "n_tail_observations": len(tail),
                "n_total_observations": len(arr),
            },
        )
    return es

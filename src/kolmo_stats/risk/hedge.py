"""
Minimum variance hedge ratio.
"""
from __future__ import annotations

import numpy as np

from kolmo_stats.engine.arrays import coerce_array, validate_same_length, drop_nan_pairs
from kolmo_stats.utils.explain import make_explain


def hedge_ratio(
    asset_returns,
    hedge_returns,
    explain: bool = False,
) -> float | dict:
    """
    Calculate the minimum variance hedge ratio.

    The hedge ratio tells you how many units of the hedge instrument
    to sell for each unit of the exposed asset to minimise variance.

    Common uses:
    - Hedge jet fuel exposure with Brent futures
    - Hedge gasoil with crude
    - Hedge TTF with JKM (LNG arbitrage hedging)
    - Hedge a physical crude position with futures

    Parameters
    ----------
    asset_returns : array-like
        Returns or price changes of the asset being hedged.
    hedge_returns : array-like
        Returns or price changes of the hedging instrument.
    explain : bool

    Returns
    -------
    float — hedge ratio (positive = sell hedge to offset long asset)
    or dict if explain=True

    Formula
    -------
    h* = cov(asset, hedge) / var(hedge)

    Examples
    --------
    >>> import numpy as np
    >>> np.random.seed(0)
    >>> asset = np.random.randn(200) * 2
    >>> hedge = asset * 0.9 + np.random.randn(200) * 0.5
    >>> hedge_ratio(asset, hedge)
    """
    a = coerce_array(asset_returns)
    h = coerce_array(hedge_returns)
    validate_same_length(a, h, ("asset_returns", "hedge_returns"))
    a, h = drop_nan_pairs(a, h)

    if len(h) < 2:
        raise ValueError("Need at least 2 valid observations to compute hedge ratio")

    cov = float(np.cov(a, h, ddof=1)[0, 1])
    var_h = float(np.var(h, ddof=1))

    if var_h == 0:
        raise ValueError("Hedge instrument has zero variance — cannot compute ratio")

    ratio = cov / var_h

    if explain:
        return make_explain(
            result=float(ratio),
            explanation=(
                f"Minimum variance hedge ratio: {ratio:.4f}. "
                "For every unit of asset exposure, sell this many units of the hedge."
            ),
            formula="h* = cov(asset, hedge) / var(hedge)",
            inputs={
                "covariance": cov,
                "hedge_variance": var_h,
                "n_observations": len(a),
            },
        )
    return float(ratio)

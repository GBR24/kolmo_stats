"""
Oil basis and differential spread helpers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.utils.explain import make_explain


def _spread(left, right):
    is_pandas = isinstance(left, pd.Series) or isinstance(right, pd.Series)
    is_scalar = np.isscalar(left) and np.isscalar(right)

    if is_pandas:
        left_series = left if isinstance(left, pd.Series) else pd.Series(left, index=right.index)
        right_series = right if isinstance(right, pd.Series) else pd.Series(right, index=left.index)
        result = left_series.astype(float) - right_series.astype(float)
        return result

    result = np.asarray(left, dtype=float) - np.asarray(right, dtype=float)
    return float(result) if is_scalar else result


def brent_wti_spread(
    brent,
    wti,
    explain: bool = False,
):
    """
    Brent-WTI spread: Brent price minus WTI price.

    Positive values mean Brent trades above WTI. This is a common crude
    benchmark differential for Atlantic Basin vs inland US pricing.
    """
    result = _spread(brent, wti)
    if explain:
        return make_explain(
            result=result,
            explanation="Brent-WTI spread: Brent price minus WTI price.",
            formula="spread = brent - wti",
            inputs={"brent": brent, "wti": wti},
        )
    return result


def quality_spread(
    premium_grade,
    discount_grade,
    explain: bool = False,
):
    """
    Quality spread: premium crude grade minus discount crude grade.

    Useful for light-heavy or sweet-sour differentials. Positive values mean
    the premium grade trades above the discount grade.
    """
    result = _spread(premium_grade, discount_grade)
    if explain:
        return make_explain(
            result=result,
            explanation=(
                "Quality spread: premium crude grade minus discount crude grade."
            ),
            formula="spread = premium_grade - discount_grade",
            inputs={"premium_grade": premium_grade, "discount_grade": discount_grade},
        )
    return result


def location_spread(
    destination_price,
    origin_price,
    explain: bool = False,
):
    """
    Location spread: destination market price minus origin market price.

    Positive values mean the destination market is priced above the origin,
    before transport, quality, timing, and contract-specification adjustments.
    """
    result = _spread(destination_price, origin_price)
    if explain:
        return make_explain(
            result=result,
            explanation="Location spread: destination price minus origin price.",
            formula="spread = destination_price - origin_price",
            inputs={
                "destination_price": destination_price,
                "origin_price": origin_price,
            },
        )
    return result

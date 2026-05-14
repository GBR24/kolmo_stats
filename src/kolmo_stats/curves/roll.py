"""
Roll yield estimation for commodity futures.
"""
from __future__ import annotations

from kolmo_stats.utils.explain import make_explain


def roll_yield(
    near_price: float,
    far_price: float,
    days_between: int = 30,
    annualize: bool = True,
    explain: bool = False,
) -> float | dict:
    """
    Estimate the roll yield from rolling long futures exposure from an
    expiring near contract into a deferred far contract.

    In backwardation the roll yield is positive — you sell near at a premium
    and buy far cheaper. In contango it is negative.

    Parameters
    ----------
    near_price : float
    far_price : float
    days_between : int
        Calendar days between the two contract expiries (default 30).
    annualize : bool
        Scale the raw roll yield to an annual rate (default True).
    explain : bool

    Returns
    -------
    float, or dict if explain=True

    Examples
    --------
    >>> roll_yield(84, 80, days_between=30)   # backwardation, annualised
    18.25
    >>> roll_yield(80, 84, days_between=30)   # contango, annualised
    -17.38...
    """
    if far_price == 0:
        raise ValueError("far_price cannot be zero")
    if days_between <= 0:
        raise ValueError("days_between must be positive")

    raw = (near_price - far_price) / far_price
    result = raw * (365 / days_between) if annualize else raw

    if explain:
        formula = "(near - far) / far"
        if annualize:
            formula += " * (365 / days_between)"
        return make_explain(
            result=float(result),
            explanation=(
                "Roll yield: gain (or loss) from rolling a futures position. "
                "Positive in backwardation, negative in contango."
            ),
            formula=formula,
            inputs={
                "near_price": near_price,
                "far_price": far_price,
                "days_between": days_between,
                "annualize": annualize,
                "raw_roll_yield": raw,
            },
        )
    return float(result)

"""
LNG arbitrage netback calculation.
"""
from __future__ import annotations

from kolmo_stats.utils.explain import make_explain


def lng_arbitrage(
    destination_price: float,
    source_price: float,
    freight_cost: float,
    regas_cost: float = 0.0,
    liquefaction_cost: float = 0.0,
    boil_off_cost: float = 0.0,
    explain: bool = False,
) -> float | dict:
    """
    Estimate LNG arbitrage netback — the net value of moving gas from
    a source hub to a destination market.

    A positive result means the arb is open (economics favour the trade).
    A negative result means the trade loses money at current prices.

    All costs and prices should be in the same unit (typically $/MMBtu).

    Parameters
    ----------
    destination_price : float
        Price at the destination market (e.g. JKM, NBP, TTF).
    source_price : float
        Price at the source hub (e.g. Henry Hub).
    freight_cost : float
        Shipping cost per MMBtu.
    regas_cost : float
        Regasification cost at destination (default 0).
    liquefaction_cost : float
        Liquefaction cost at source (default 0).
    boil_off_cost : float
        Boil-off loss cost during transit (default 0).
    explain : bool

    Returns
    -------
    float, or dict if explain=True

    Examples
    --------
    >>> lng_arbitrage(destination_price=12, source_price=3, freight_cost=2,
    ...               regas_cost=0.3, liquefaction_cost=2.5, boil_off_cost=0.2)
    4.0
    """
    total_cost = freight_cost + regas_cost + liquefaction_cost + boil_off_cost
    result = destination_price - source_price - total_cost

    if explain:
        return make_explain(
            result=float(result),
            explanation=(
                "LNG arbitrage netback: value of moving gas from source to destination "
                "after all transport and processing costs. Positive = arb is open."
            ),
            formula=(
                "destination - source - freight - regas - liquefaction - boil_off"
            ),
            inputs={
                "destination_price": destination_price,
                "source_price": source_price,
                "freight_cost": freight_cost,
                "regas_cost": regas_cost,
                "liquefaction_cost": liquefaction_cost,
                "boil_off_cost": boil_off_cost,
                "total_cost": total_cost,
            },
        )
    return float(result)

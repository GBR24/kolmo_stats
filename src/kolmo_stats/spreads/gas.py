"""
Gas and LNG basis / arbitrage spread helpers.
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
        return left_series.astype(float) - right_series.astype(float)

    result = np.asarray(left, dtype=float) - np.asarray(right, dtype=float)
    return float(result) if is_scalar else result


def ttf_jkm_spread(
    ttf_price,
    jkm_price,
    explain: bool = False,
):
    """
    JKM-TTF spread from TTF and JKM prices.

    Positive values mean Northeast Asian LNG (JKM) trades above European gas
    (TTF), before freight and other LNG chain costs.
    """
    result = _spread(jkm_price, ttf_price)
    if explain:
        return make_explain(
            result=result,
            explanation="JKM-TTF spread: JKM price minus TTF price.",
            formula="spread = jkm_price - ttf_price",
            inputs={"ttf_price": ttf_price, "jkm_price": jkm_price},
        )
    return result


def lng_netback(
    destination_price,
    freight_cost: float = 0.0,
    regas_cost: float = 0.0,
    liquefaction_cost: float = 0.0,
    boil_off_cost: float = 0.0,
    explain: bool = False,
):
    """
    LNG netback to source before feedgas cost.

    This is the destination price less LNG chain costs. It estimates the
    maximum source/feedgas price the destination can support.
    """
    total_cost = freight_cost + regas_cost + liquefaction_cost + boil_off_cost
    if isinstance(destination_price, pd.Series):
        result = destination_price.astype(float) - total_cost
    else:
        result = np.asarray(destination_price, dtype=float) - total_cost
    if np.isscalar(destination_price):
        result = float(result)

    if explain:
        return make_explain(
            result=result,
            explanation=(
                "LNG netback: destination price less shipping, regas, "
                "liquefaction, and boil-off costs."
            ),
            formula="netback = destination_price - freight - regas - liquefaction - boil_off",
            inputs={
                "destination_price": destination_price,
                "freight_cost": freight_cost,
                "regas_cost": regas_cost,
                "liquefaction_cost": liquefaction_cost,
                "boil_off_cost": boil_off_cost,
                "total_cost": total_cost,
            },
        )
    return result


def shipping_adjusted_spread(
    destination_price,
    source_price,
    freight_cost: float = 0.0,
    regas_cost: float = 0.0,
    liquefaction_cost: float = 0.0,
    boil_off_cost: float = 0.0,
    explain: bool = False,
):
    """
    Shipping-adjusted LNG/gas spread.

    Positive values mean the destination price covers the source price and
    specified transport / processing costs.
    """
    netback = lng_netback(
        destination_price,
        freight_cost=freight_cost,
        regas_cost=regas_cost,
        liquefaction_cost=liquefaction_cost,
        boil_off_cost=boil_off_cost,
    )
    result = _spread(netback, source_price)

    if explain:
        total_cost = freight_cost + regas_cost + liquefaction_cost + boil_off_cost
        return make_explain(
            result=result,
            explanation=(
                "Shipping-adjusted spread: destination less source and LNG "
                "chain costs. Positive = route economics are open."
            ),
            formula="spread = destination_price - source_price - total_cost",
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
    return result


def henry_hub_ttf_arb(
    henry_hub_price,
    ttf_price,
    freight_cost: float = 0.0,
    regas_cost: float = 0.0,
    liquefaction_cost: float = 0.0,
    boil_off_cost: float = 0.0,
    explain: bool = False,
):
    """
    Henry Hub to TTF LNG arbitrage spread.

    Positive values mean TTF covers Henry Hub plus specified LNG chain costs.
    All prices and costs should use the same unit, typically $/MMBtu.
    """
    result = shipping_adjusted_spread(
        destination_price=ttf_price,
        source_price=henry_hub_price,
        freight_cost=freight_cost,
        regas_cost=regas_cost,
        liquefaction_cost=liquefaction_cost,
        boil_off_cost=boil_off_cost,
    )
    if explain:
        total_cost = freight_cost + regas_cost + liquefaction_cost + boil_off_cost
        return make_explain(
            result=result,
            explanation=(
                "Henry Hub to TTF arbitrage: TTF less Henry Hub and LNG "
                "chain costs."
            ),
            formula="arb = ttf_price - henry_hub_price - total_cost",
            inputs={
                "henry_hub_price": henry_hub_price,
                "ttf_price": ttf_price,
                "freight_cost": freight_cost,
                "regas_cost": regas_cost,
                "liquefaction_cost": liquefaction_cost,
                "boil_off_cost": boil_off_cost,
                "total_cost": total_cost,
            },
        )
    return result

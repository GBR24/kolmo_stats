"""
Spark spread: gas-fired power generation margin.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.utils.explain import make_explain


def spark_spread(
    power_price,
    gas_price,
    heat_rate: float,
    explain: bool = False,
):
    """
    Estimate the gross margin for a gas-fired power plant (spark spread).

    The spark spread measures whether it is profitable to burn gas to generate
    power before non-fuel variable costs, emissions costs, start costs, and
    operating constraints. A positive gross spread means fuel economics are
    favourable.

    Parameters
    ----------
    power_price : numeric or array-like
        Electricity price in $/MWh (or €/MWh, £/MWh — must be consistent).
    gas_price : numeric or array-like
        Gas price in $/MMBtu.
    heat_rate : float
        Fuel input needed to generate 1 MWh, in MMBtu/MWh. Lower heat rate
        means a more efficient plant.
        Typical CCGT: 6.5–7.5. Typical OCGT: 9–11.
    explain : bool

    Returns
    -------
    float, numpy array, or pandas Series (matches input type)
    or dict if explain=True

    Examples
    --------
    >>> spark_spread(60, 5, heat_rate=7.0)
    25.0
    """
    if heat_rate <= 0:
        raise ValueError("heat_rate must be positive")

    is_pandas = isinstance(power_price, pd.Series) or isinstance(gas_price, pd.Series)
    is_scalar = np.isscalar(power_price) and np.isscalar(gas_price)
    index = power_price.index if isinstance(power_price, pd.Series) else (
        gas_price.index if isinstance(gas_price, pd.Series) else None
    )

    result = np.asarray(power_price, dtype=float) - np.asarray(gas_price, dtype=float) * heat_rate

    if is_pandas and index is not None:
        result = pd.Series(result, index=index)
    elif is_scalar:
        result = float(result)

    if explain:
        return make_explain(
            result=result,
            explanation=(
                "Gross spark spread: power revenue minus gas fuel cost. "
                "Positive = fuel economics are favourable before other costs."
            ),
            formula="power_price - gas_price * heat_rate",
            inputs={"power_price": power_price, "gas_price": gas_price, "heat_rate": heat_rate},
        )
    return result

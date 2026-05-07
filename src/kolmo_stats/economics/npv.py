"""
Net Present Value for energy project evaluation.
"""
from __future__ import annotations

import numpy as np

from kolmo_stats.engine.arrays import coerce_array
from kolmo_stats.utils.explain import make_explain


def npv(
    cashflows,
    discount_rate: float,
    initial_investment: float = 0.0,
    explain: bool = False,
) -> float | dict:
    """
    Net Present Value (NPV) of a sequence of future cashflows.

    NPV discounts each cashflow back to today's value. A positive NPV
    means the project creates value above the cost of capital.

    The first cashflow is assumed to occur at t=1 (end of year 1).

    Parameters
    ----------
    cashflows : array-like
        Sequence of future cashflows (revenues minus costs). Can be
        annual, quarterly, or monthly — just make discount_rate match.
    discount_rate : float
        Discount rate per period (e.g. 0.10 for 10% annual).
    initial_investment : float
        Upfront capital spend at t=0 (positive number; subtracted from PV).
    explain : bool

    Returns
    -------
    float, or dict if explain=True

    Examples
    --------
    >>> npv([100, 100, 100], discount_rate=0.10, initial_investment=200)
    48.68...
    """
    cf = coerce_array(cashflows)
    if len(cf) == 0:
        raise ValueError("cashflows must not be empty")
    if discount_rate <= -1:
        raise ValueError("discount_rate must be greater than -1")

    t = np.arange(1, len(cf) + 1)
    pv_cashflows = float(np.sum(cf / (1 + discount_rate) ** t))
    result = pv_cashflows - initial_investment

    if explain:
        return make_explain(
            result=result,
            explanation=(
                f"NPV = {result:,.2f}. "
                + ("Positive: project creates value." if result >= 0 else "Negative: project destroys value.")
            ),
            formula="NPV = -investment + sum(CF_t / (1 + r)^t)",
            inputs={
                "cashflows": cf.tolist(),
                "discount_rate": discount_rate,
                "initial_investment": initial_investment,
                "pv_cashflows": pv_cashflows,
                "n_periods": len(cf),
            },
        )
    return result

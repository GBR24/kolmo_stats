"""
Mean-reversion helpers for spreads and commodity time series.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from kolmo_stats.engine.arrays import coerce_array
from kolmo_stats.utils.explain import make_explain
from kolmo_stats.utils.validation import require_positive


def mean_reversion_calibration(
    values,
    dt: float = 1.0,
    explain: bool = False,
) -> dict[str, float] | dict[str, Any]:
    """
    Calibrate a discrete AR(1) approximation to an OU mean-reverting process.

    The regression is ``x[t+dt] = intercept + phi * x[t] + error``. For
    ``0 < phi < 1``, the continuous-time speed is ``kappa = -ln(phi) / dt``.
    """
    require_positive(dt, "dt")
    x = _clean(values)
    if len(x) < 3:
        raise ValueError("values must contain at least 3 valid observations")

    lhs = x[1:]
    rhs = np.column_stack([np.ones(len(x) - 1), x[:-1]])
    intercept, phi = np.linalg.lstsq(rhs, lhs, rcond=None)[0]
    if not 0.0 < phi < 1.0:
        raise ValueError(
            "values do not imply a stable positive mean-reversion speed; "
            f"estimated AR(1) phi={phi:.6f}"
        )

    residuals = lhs - (intercept + phi * x[:-1])
    kappa = -math.log(phi) / dt
    theta = intercept / (1.0 - phi)
    half_life = math.log(2.0) / kappa
    resid_std = float(np.std(residuals, ddof=1))
    sigma = resid_std * math.sqrt((2.0 * kappa) / (1.0 - phi * phi))

    result = {
        "intercept": float(intercept),
        "phi": float(phi),
        "kappa": float(kappa),
        "theta": float(theta),
        "half_life": float(half_life),
        "sigma": float(sigma),
        "residual_std": resid_std,
    }

    if explain:
        return make_explain(
            result=result,
            explanation=(
                "Calibrated an AR(1) approximation to an Ornstein-Uhlenbeck "
                "mean-reverting process."
            ),
            formula="x[t+dt] = a + phi*x[t] + eps; kappa = -ln(phi)/dt",
            inputs={"n": len(x), "dt": dt},
        )
    return result


def ou_half_life(values, dt: float = 1.0, explain: bool = False) -> float | dict:
    """
    Estimate OU/AR(1) mean-reversion half-life.

    Returns the time needed for a deviation from the long-run mean to decay by
    half, in the same time unit as ``dt``.
    """
    calibration = mean_reversion_calibration(values, dt=dt, explain=False)
    result = float(calibration["half_life"])
    if explain:
        return make_explain(
            result=result,
            explanation=(
                "Mean-reversion half-life estimated from the AR(1) coefficient."
            ),
            formula="half_life = ln(2) / kappa, where kappa = -ln(phi) / dt",
            inputs={"dt": dt, "phi": calibration["phi"], "kappa": calibration["kappa"]},
        )
    return result


def _clean(values) -> np.ndarray:
    arr = coerce_array(values)
    return arr[~np.isnan(arr)]

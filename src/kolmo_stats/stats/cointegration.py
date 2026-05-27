"""
Lightweight spread and cointegration helpers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.engine.arrays import coerce_array, drop_nan_pairs, validate_same_length
from kolmo_stats.utils.explain import make_explain


def cointegration_beta(
    y,
    x,
    include_intercept: bool = True,
    explain: bool = False,
) -> float | dict:
    """
    Estimate the hedge beta in ``y = alpha + beta*x + residual``.

    This is an OLS hedge-ratio helper, not a formal Engle-Granger p-value test.
    """
    y_arr, x_arr = _clean_pair(y, x)
    alpha, beta = _ols(y_arr, x_arr, include_intercept=include_intercept)
    if explain:
        return make_explain(
            result=float(beta),
            explanation=(
                "OLS hedge beta for a two-leg spread. Use the residual series "
                "for mean-reversion analysis."
            ),
            formula="beta = cov(x, y) / var(x) with optional intercept",
            inputs={
                "n": len(y_arr),
                "include_intercept": include_intercept,
                "intercept": float(alpha),
            },
        )
    return float(beta)


def spread_residual(
    y,
    x,
    beta: float | None = None,
    intercept: float | None = None,
    explain: bool = False,
):
    """
    Build spread residuals from ``y - intercept - beta*x``.
    """
    y_arr, x_arr = _clean_pair(y, x)
    if beta is None or intercept is None:
        fitted_intercept, fitted_beta = _ols(y_arr, x_arr, include_intercept=True)
        beta = fitted_beta if beta is None else beta
        intercept = fitted_intercept if intercept is None else intercept

    residual = y_arr - float(intercept) - float(beta) * x_arr
    result = _maybe_series(residual, y)
    if explain:
        return make_explain(
            result=result,
            explanation="Residual spread after removing the fitted hedge leg.",
            formula="residual = y - intercept - beta*x",
            inputs={"beta": float(beta), "intercept": float(intercept), "n": len(y_arr)},
        )
    return result


def cointegration_zscore(
    y,
    x,
    window: int | None = None,
    explain: bool = False,
):
    """
    Z-score the residual spread from an OLS two-leg relationship.

    ``window=None`` uses full-sample mean and standard deviation. A positive
    value means ``y`` is rich versus ``x`` under the fitted relationship.
    """
    residual = spread_residual(y, x)
    if isinstance(residual, pd.Series):
        if window is None:
            z = (residual - residual.mean()) / residual.std()
        else:
            z = (residual - residual.rolling(window).mean()) / residual.rolling(window).std()
        result = z
    else:
        residual_arr = np.asarray(residual, dtype=float)
        if window is None:
            result = (residual_arr - np.mean(residual_arr)) / np.std(residual_arr, ddof=1)
        else:
            series = pd.Series(residual_arr)
            result = ((series - series.rolling(window).mean()) / series.rolling(window).std()).to_numpy()

    if explain:
        return make_explain(
            result=result,
            explanation="Z-score of the residual spread from an OLS hedge relationship.",
            formula="z = (residual - mean(residual)) / std(residual)",
            inputs={"window": window},
        )
    return result


def _clean_pair(y, x) -> tuple[np.ndarray, np.ndarray]:
    y_arr = coerce_array(y)
    x_arr = coerce_array(x)
    validate_same_length(y_arr, x_arr, ("y", "x"))
    y_arr, x_arr = drop_nan_pairs(y_arr, x_arr)
    if len(y_arr) < 3:
        raise ValueError("y and x must contain at least 3 valid paired observations")
    return y_arr, x_arr


def _ols(y: np.ndarray, x: np.ndarray, include_intercept: bool) -> tuple[float, float]:
    if include_intercept:
        design = np.column_stack([np.ones(len(x)), x])
        alpha, beta = np.linalg.lstsq(design, y, rcond=None)[0]
        return float(alpha), float(beta)
    denom = float(np.dot(x, x))
    if denom == 0:
        raise ValueError("x has zero variance; cannot estimate beta")
    return 0.0, float(np.dot(x, y) / denom)


def _maybe_series(values: np.ndarray, template):
    if isinstance(template, pd.Series):
        index = template.dropna().index[: len(values)]
        return pd.Series(values, index=index)
    return values

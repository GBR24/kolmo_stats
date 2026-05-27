"""
Portfolio risk decomposition helpers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

from kolmo_stats.utils.explain import make_explain
from kolmo_stats.utils.validation import require_in_range


def portfolio_volatility(
    weights,
    covariance,
    explain: bool = False,
) -> float | dict:
    """
    Portfolio volatility from weights and covariance matrix.
    """
    w, cov, _ = _coerce_weights_covariance(weights, covariance)
    variance = float(w @ cov @ w)
    if variance < 0 and abs(variance) < 1e-12:
        variance = 0.0
    if variance < 0:
        raise ValueError("portfolio variance is negative; covariance matrix may be invalid")
    result = float(np.sqrt(variance))
    if explain:
        return make_explain(
            result=result,
            explanation="Portfolio volatility from a covariance matrix.",
            formula="sigma_p = sqrt(w.T @ covariance @ w)",
            inputs={"n_assets": len(w)},
        )
    return result


def marginal_var(
    weights,
    covariance,
    confidence: float = 0.95,
    explain: bool = False,
):
    """
    Marginal normal VaR contribution per unit of asset weight.
    """
    require_in_range(confidence, 0.5, 0.9999, "confidence")
    w, cov, labels = _coerce_weights_covariance(weights, covariance)
    sigma_p = portfolio_volatility(w, cov)
    if sigma_p == 0:
        raise ValueError("portfolio volatility is zero; cannot compute marginal VaR")
    z = float(norm.ppf(confidence))
    values = z * (cov @ w) / sigma_p
    result = _labelled(values, labels)
    if explain:
        return make_explain(
            result=result,
            explanation="Marginal VaR under a normal covariance approximation.",
            formula="mVaR_i = z(confidence) * (covariance @ w)_i / sigma_p",
            inputs={"confidence": confidence, "z": z, "portfolio_volatility": sigma_p},
        )
    return result


def component_var(
    weights,
    covariance,
    confidence: float = 0.95,
    explain: bool = False,
):
    """
    Component normal VaR contribution from each asset.

    Components sum to total normal portfolio VaR when weights are portfolio
    fractions or notionals in the same risk units as the covariance matrix.
    """
    require_in_range(confidence, 0.5, 0.9999, "confidence")
    w, cov, labels = _coerce_weights_covariance(weights, covariance)
    mvar = np.asarray(marginal_var(w, cov, confidence=confidence), dtype=float)
    values = w * mvar
    result = _labelled(values, labels)
    if explain:
        return make_explain(
            result=result,
            explanation="Component VaR contribution by asset.",
            formula="component_VaR_i = weight_i * marginal_VaR_i",
            inputs={"confidence": confidence, "total_var": float(values.sum())},
        )
    return result


def _coerce_weights_covariance(weights, covariance) -> tuple[np.ndarray, np.ndarray, list[str] | None]:
    labels = None
    if isinstance(weights, dict):
        labels = list(weights)
        w = np.asarray([weights[label] for label in labels], dtype=float)
    elif isinstance(weights, pd.Series):
        labels = list(weights.index.astype(str))
        w = weights.to_numpy(dtype=float)
    else:
        w = np.asarray(weights, dtype=float)

    if isinstance(covariance, pd.DataFrame):
        if labels is not None:
            cov = covariance.loc[labels, labels].to_numpy(dtype=float)
        else:
            labels = list(covariance.index.astype(str))
            cov = covariance.to_numpy(dtype=float)
    else:
        cov = np.asarray(covariance, dtype=float)

    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValueError("covariance must be a square matrix")
    if len(w) != cov.shape[0]:
        raise ValueError(
            f"weights length must match covariance size; got {len(w)} and {cov.shape[0]}"
        )
    if np.isnan(w).any() or np.isnan(cov).any():
        raise ValueError("weights and covariance must not contain NaN")
    return w, cov, labels


def _labelled(values: np.ndarray, labels: list[str] | None):
    if labels is None:
        return values
    return pd.Series(values, index=labels)

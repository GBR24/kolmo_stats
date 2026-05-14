"""
Cholesky-based correlated shock generation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.utils.explain import make_explain


def _as_square_matrix(matrix, name: str = "matrix") -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    return arr


def cholesky_decompose(
    matrix,
    jitter: float = 0.0,
    explain: bool = False,
) -> np.ndarray | dict:
    """
    Cholesky decomposition of a positive-definite covariance/correlation matrix.

    Returns the lower-triangular matrix L such that the adjusted matrix equals
    ``L @ L.T``.
    ``jitter`` can be used to add a small value to the diagonal if a nearly
    positive-definite estimated matrix needs stabilisation.
    """
    arr = _as_square_matrix(matrix)
    if jitter < 0:
        raise ValueError("jitter must be non-negative")
    if not np.allclose(arr, arr.T, atol=1e-10):
        raise ValueError("matrix must be symmetric")

    adjusted = arr + np.eye(arr.shape[0]) * jitter if jitter else arr
    try:
        result = np.linalg.cholesky(adjusted)
    except np.linalg.LinAlgError as exc:
        raise ValueError("matrix must be positive definite") from exc

    if explain:
        return make_explain(
            result=result,
            explanation=(
                "Cholesky decomposition L where adjusted_matrix = L @ L.T."
            ),
            formula="adjusted_matrix = matrix + jitter * I = L @ L.T",
            inputs={"n_assets": arr.shape[0], "jitter": jitter},
        )
    return result


def correlated_normals(
    correlation_matrix,
    n_sims: int,
    seed: int | None = None,
    names: list[str] | None = None,
    explain: bool = False,
) -> np.ndarray | pd.DataFrame | dict:
    """
    Generate correlated standard normal draws using a correlation matrix.
    """
    if n_sims <= 0:
        raise ValueError("n_sims must be positive")

    corr = _as_square_matrix(correlation_matrix, "correlation_matrix")
    if not np.allclose(corr, corr.T, atol=1e-10):
        raise ValueError("correlation_matrix must be symmetric")
    if not np.allclose(np.diag(corr), 1.0, atol=1e-10):
        raise ValueError("correlation_matrix diagonal must contain ones")
    if names is not None and len(names) != corr.shape[0]:
        raise ValueError("names length must match correlation_matrix dimension")

    rng = np.random.default_rng(seed)
    independent = rng.standard_normal((n_sims, corr.shape[0]))
    shocks = independent @ cholesky_decompose(corr).T
    result = pd.DataFrame(shocks, columns=names) if names is not None else shocks

    if explain:
        return make_explain(
            result=result,
            explanation="Correlated standard normals generated via Cholesky.",
            formula="Z_corr = Z_independent @ L.T",
            inputs={"n_sims": n_sims, "n_assets": corr.shape[0], "seed": seed},
        )
    return result


def correlated_price_shocks(
    volatilities,
    correlation_matrix,
    n_sims: int = 10_000,
    horizon_days: float = 1.0,
    seed: int | None = None,
    names: list[str] | None = None,
    explain: bool = False,
) -> np.ndarray | pd.DataFrame | dict:
    """
    Generate correlated price/P&L shocks from per-day volatilities.

    ``volatilities`` should be one-day standard deviations in the same units
    as the desired shocks, e.g. $/bbl for Brent or $/MMBtu for gas. Horizon
    scaling uses the square-root-of-time approximation.
    """
    vols = np.asarray(volatilities, dtype=float)
    corr = _as_square_matrix(correlation_matrix, "correlation_matrix")
    if vols.ndim != 1 or len(vols) != corr.shape[0]:
        raise ValueError("volatilities length must match correlation_matrix dimension")
    if names is not None and len(names) != corr.shape[0]:
        raise ValueError("names length must match correlation_matrix dimension")
    if np.any(vols < 0):
        raise ValueError("volatilities must be non-negative")
    if horizon_days <= 0:
        raise ValueError("horizon_days must be positive")

    normals = correlated_normals(corr, n_sims=n_sims, seed=seed)
    shocks = normals * vols * np.sqrt(horizon_days)
    result = pd.DataFrame(shocks, columns=names) if names is not None else shocks

    if explain:
        return make_explain(
            result=result,
            explanation=(
                "Correlated price shocks generated from per-day volatilities "
                "and a correlation matrix."
            ),
            formula="shocks = correlated_normals * volatilities * sqrt(horizon_days)",
            inputs={
                "n_sims": n_sims,
                "n_assets": corr.shape[0],
                "horizon_days": horizon_days,
                "seed": seed,
            },
        )
    return result

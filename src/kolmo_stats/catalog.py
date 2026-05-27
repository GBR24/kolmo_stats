"""
Machine-readable formula metadata for agents and docs.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

FORMULA_CATALOG: dict[str, dict[str, Any]] = {
    "mean_reversion_calibration": {
        "domain": "stats",
        "description": "Calibrate an AR(1)/OU mean-reversion model.",
        "inputs": ["values", "dt"],
        "output": "dict with phi, kappa, theta, half_life, sigma",
        "agent_use": "Diagnose whether a spread or price series mean-reverts.",
    },
    "ou_half_life": {
        "domain": "stats",
        "description": "Estimate mean-reversion half-life from an AR(1) fit.",
        "inputs": ["values", "dt"],
        "output": "float",
        "agent_use": "Set strategy holding period or exit patience for spread trades.",
    },
    "cointegration_beta": {
        "domain": "stats",
        "description": "Estimate the OLS hedge beta in y = alpha + beta*x.",
        "inputs": ["y", "x", "include_intercept"],
        "output": "float",
        "agent_use": "Size relative-value spread legs before residual analysis.",
    },
    "spread_residual": {
        "domain": "stats",
        "description": "Build residual spread y - alpha - beta*x.",
        "inputs": ["y", "x", "beta", "intercept"],
        "output": "array or pandas Series",
        "agent_use": "Create the spread series used for z-score and half-life signals.",
    },
    "cointegration_zscore": {
        "domain": "stats",
        "description": "Z-score the residual from an OLS spread relationship.",
        "inputs": ["y", "x", "window"],
        "output": "array or pandas Series",
        "agent_use": "Generate rich/cheap spread signals.",
    },
    "realized_volatility": {
        "domain": "risk",
        "description": "Annualised volatility from historical returns.",
        "inputs": ["returns", "periods_per_year"],
        "output": "float",
        "agent_use": "Estimate risk scaling and stop distances.",
    },
    "ewma_volatility": {
        "domain": "risk",
        "description": "Annualised exponentially weighted volatility.",
        "inputs": ["returns", "lambda_", "periods_per_year"],
        "output": "float",
        "agent_use": "React faster to changing volatility regimes.",
    },
    "portfolio_volatility": {
        "domain": "risk",
        "description": "Portfolio volatility from weights and covariance.",
        "inputs": ["weights", "covariance"],
        "output": "float",
        "agent_use": "Summarize covariance-aware portfolio risk.",
    },
    "marginal_var": {
        "domain": "risk",
        "description": "Marginal normal VaR by asset.",
        "inputs": ["weights", "covariance", "confidence"],
        "output": "array or pandas Series",
        "agent_use": "Identify which exposure adds risk at the margin.",
    },
    "component_var": {
        "domain": "risk",
        "description": "Component normal VaR contribution by asset.",
        "inputs": ["weights", "covariance", "confidence"],
        "output": "array or pandas Series",
        "agent_use": "Explain total VaR by asset contribution.",
    },
    "portfolio_scenario_matrix": {
        "domain": "risk",
        "description": "Scenario-by-asset portfolio P&L matrix.",
        "inputs": ["positions", "scenarios"],
        "output": "pandas DataFrame",
        "agent_use": "Evaluate many named portfolio stress scenarios.",
    },
    "curve_pca": {
        "domain": "curves",
        "description": "PCA decomposition of ordered futures curves.",
        "inputs": ["curves", "n_components"],
        "output": "dict with components, scores, variance ratios, mean curve",
        "agent_use": "Summarize curve moves as level, slope, and curvature factors.",
    },
    "curve_factor_exposures": {
        "domain": "curves",
        "description": "Project curve changes onto PCA components.",
        "inputs": ["curve_changes", "components"],
        "output": "pandas Series or DataFrame",
        "agent_use": "Explain a curve move through fitted factors.",
    },
}


def formula_catalog() -> dict[str, dict[str, Any]]:
    """Return a copy of the formula catalog."""
    return deepcopy(FORMULA_CATALOG)


def get_formula_metadata(name: str) -> dict[str, Any]:
    """Return metadata for one formula."""
    try:
        return deepcopy(FORMULA_CATALOG[name])
    except KeyError as exc:
        raise KeyError(f"Unknown formula metadata: {name!r}") from exc

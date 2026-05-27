import sys
import types

import numpy as np
import pandas as pd
import pytest

from kolmo_stats import (
    cointegration_beta,
    cointegration_zscore,
    component_var,
    curve_factor_exposures,
    curve_pca,
    ewma_volatility,
    formula_catalog,
    marginal_var,
    mean_reversion_calibration,
    ou_half_life,
    portfolio_scenario_matrix,
    portfolio_volatility,
    realized_volatility,
    spread_residual,
)


def test_mean_reversion_calibration_and_half_life_explain():
    values = [10.0]
    for _ in range(1, 80):
        values.append(5.0 + 0.8 * (values[-1] - 5.0))

    calibration = mean_reversion_calibration(values)
    assert calibration["phi"] == pytest.approx(0.8)
    assert calibration["theta"] == pytest.approx(5.0)
    assert ou_half_life(values) == pytest.approx(np.log(2) / -np.log(0.8))
    assert "formula" in ou_half_life(values, explain=True)


def test_cointegration_helpers_preserve_series_shape():
    x = pd.Series(np.arange(1.0, 20.0), name="WTI")
    y = 2.0 + 1.5 * x

    beta = cointegration_beta(y, x)
    residual = spread_residual(y, x)
    zscore = cointegration_zscore(y, x)

    assert beta == pytest.approx(1.5)
    assert isinstance(residual, pd.Series)
    assert residual.abs().max() < 1e-10
    assert isinstance(zscore, pd.Series)
    assert "formula" in cointegration_beta(y, x, explain=True)


def test_volatility_helpers():
    returns = np.array([0.01, -0.02, 0.015, -0.005, 0.01])

    assert realized_volatility(returns) > 0
    assert ewma_volatility(returns, lambda_=0.94) > 0
    assert "formula" in realized_volatility(returns, explain=True)
    with pytest.raises(ValueError):
        ewma_volatility(returns, lambda_=1.0)


def test_portfolio_var_decomposition():
    weights = {"Brent": 0.6, "WTI": 0.4}
    covariance = pd.DataFrame(
        [[0.04, 0.02], [0.02, 0.09]],
        index=["Brent", "WTI"],
        columns=["Brent", "WTI"],
    )

    vol = portfolio_volatility(weights, covariance)
    mvar = marginal_var(weights, covariance)
    cvar = component_var(weights, covariance)

    assert vol > 0
    assert isinstance(mvar, pd.Series)
    assert isinstance(cvar, pd.Series)
    assert cvar.sum() == pytest.approx(1.6448536269514722 * vol)
    assert "formula" in component_var(weights, covariance, explain=True)


def test_portfolio_scenario_matrix_and_native_dispatch(monkeypatch):
    positions = {"Brent": 1000, "WTI": -500}
    scenarios = {"bull": {"Brent": 5, "WTI": 4}, "bear": {"Brent": -6, "WTI": -5}}
    df = portfolio_scenario_matrix(positions, scenarios)
    assert df.loc["bull", "total_pnl"] == pytest.approx(3000.0)

    fake_ext = types.SimpleNamespace(
        portfolio_scenario_matrix=lambda positions, shocks: [
            [position * shock for position, shock in zip(positions, row)]
            for row in shocks
        ]
    )
    monkeypatch.setitem(sys.modules, "kolmo_stats._ext", fake_ext)
    native_df = portfolio_scenario_matrix(positions, scenarios)
    assert native_df.equals(df)


def test_curve_pca_and_factor_exposures():
    curves = pd.DataFrame(
        {
            "M1": [90.0, 91.0, 89.5, 92.0],
            "M2": [88.0, 88.5, 87.8, 89.0],
            "M3": [86.0, 86.2, 85.9, 86.5],
        }
    )
    pca = curve_pca(curves, n_components=2)
    exposures = curve_factor_exposures(curves.diff().dropna().iloc[-1], pca["components"])

    assert list(pca["components"].index) == ["PC1", "PC2"]
    assert float(pca["explained_variance_ratio"].sum()) <= 1.0 + 1e-12
    assert list(exposures.index) == ["PC1", "PC2"]
    assert "formula" in curve_pca(curves, explain=True)


def test_formula_catalog_contains_new_agent_metadata():
    catalog = formula_catalog()
    for key in [
        "ou_half_life",
        "cointegration_beta",
        "realized_volatility",
        "component_var",
        "portfolio_scenario_matrix",
        "curve_pca",
    ]:
        assert key in catalog
        assert catalog[key]["agent_use"]

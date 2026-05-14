import numpy as np
import pandas as pd
import pytest
from kolmo_stats import (
    historical_var,
    expected_shortfall,
    scenario_pnl,
    hedge_ratio,
    rolling_var,
    rolling_expected_shortfall,
    stress_matrix,
    cholesky_decompose,
    correlated_normals,
    correlated_price_shocks,
)


# ── historical_var ────────────────────────────────────────────────────────────

def test_var_basic():
    np.random.seed(0)
    returns = np.random.randn(10000) * 2
    var = historical_var(returns, confidence=0.95)
    assert isinstance(var, float)
    assert var > 0

def test_var_is_positive_loss():
    returns = np.array([-5, -3, -1, 0, 1, 2, 3, 4, 5] * 100, dtype=float)
    var = historical_var(returns, confidence=0.95)
    assert var > 0

def test_var_higher_confidence_higher_var():
    np.random.seed(1)
    returns = np.random.randn(1000)
    var95 = historical_var(returns, 0.95)
    var99 = historical_var(returns, 0.99)
    assert var99 > var95

def test_var_invalid_confidence():
    with pytest.raises(ValueError):
        historical_var([1, 2, 3], confidence=1.5)

def test_var_empty():
    with pytest.raises(ValueError):
        historical_var([])

def test_var_nan_ignored():
    returns = [float("nan"), -1.0, -2.0, 1.0, 2.0]
    var = historical_var(returns, confidence=0.95)
    assert isinstance(var, float)

def test_var_explain():
    returns = np.random.randn(200)
    r = historical_var(returns, explain=True)
    assert "confidence" in r["inputs"]
    assert r["inputs"]["tail_probability"] == pytest.approx(0.05)
    assert "5%" in r["explanation"]


# ── expected_shortfall ────────────────────────────────────────────────────────

def test_es_greater_than_var():
    np.random.seed(2)
    returns = np.random.randn(1000)
    var = historical_var(returns, 0.95)
    es = expected_shortfall(returns, 0.95)
    assert es >= var

def test_es_positive():
    np.random.seed(3)
    returns = np.random.randn(500)
    assert expected_shortfall(returns) > 0

def test_es_explain():
    returns = np.random.randn(200)
    r = expected_shortfall(returns, explain=True)
    assert "var" in r["inputs"]


# ── rolling risk ──────────────────────────────────────────────────────────────

def test_rolling_var_returns_series():
    returns = pd.Series(np.random.randn(100))
    result = rolling_var(returns, window=20)
    assert isinstance(result, pd.Series)
    assert result.iloc[:19].isna().all()

def test_rolling_expected_shortfall_returns_series():
    returns = pd.Series(np.random.randn(100))
    result = rolling_expected_shortfall(returns, window=20)
    assert isinstance(result, pd.Series)
    assert result.iloc[:19].isna().all()

def test_rolling_var_invalid_confidence():
    with pytest.raises(ValueError):
        rolling_var([1, 2, 3], confidence=1.2)


# ── scenario_pnl ──────────────────────────────────────────────────────────────

def test_scenario_pnl_basic():
    positions = {"Brent": 10000, "TTF": -5000}
    shocks = {"Brent": -5, "TTF": 10}
    df = scenario_pnl(positions, shocks)
    assert set(df.columns) == {"asset", "position", "shock", "pnl"}
    assert df[df["asset"] == "Brent"]["pnl"].iloc[0] == -50000
    assert df[df["asset"] == "TTF"]["pnl"].iloc[0] == -50000

def test_scenario_pnl_total():
    positions = {"Brent": 1000}
    shocks = {"Brent": 5}
    df = scenario_pnl(positions, shocks)
    assert df.attrs["total_pnl"] == pytest.approx(5000.0)

def test_scenario_pnl_missing_asset_in_shocks():
    positions = {"Brent": 1000, "Gasoil": 500}
    shocks = {"Brent": 2}
    df = scenario_pnl(positions, shocks)
    gasoil_row = df[df["asset"] == "Gasoil"]
    assert gasoil_row["pnl"].iloc[0] == pytest.approx(0.0)

def test_scenario_pnl_explain():
    r = scenario_pnl({"Brent": 1000}, {"Brent": 5}, explain=True)
    assert "total_pnl" in r["inputs"]

def test_stress_matrix_basic():
    positions = {"Brent": 1000, "WTI": -500}
    scenarios = {
        "bull": {"Brent": 5, "WTI": 4},
        "bear": {"Brent": -6, "WTI": -5},
    }
    df = stress_matrix(positions, scenarios)
    assert df.loc["bull", "total_pnl"] == pytest.approx(3000.0)
    assert df.loc["bear", "total_pnl"] == pytest.approx(-3500.0)

def test_stress_matrix_empty_scenarios():
    with pytest.raises(ValueError):
        stress_matrix({"Brent": 1000}, {})


# ── hedge_ratio ───────────────────────────────────────────────────────────────

def test_hedge_ratio_perfect_hedge():
    # If asset = hedge exactly, ratio should be 1.0
    asset = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert hedge_ratio(asset, asset) == pytest.approx(1.0)

def test_hedge_ratio_scaled():
    # If hedge = 2 * asset, ratio should be 0.5 (sell half as many units)
    asset = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    hedge = asset * 2
    assert hedge_ratio(asset, hedge) == pytest.approx(0.5)

def test_hedge_ratio_zero_variance():
    with pytest.raises(ValueError, match="zero variance"):
        hedge_ratio([1, 2, 3], [5, 5, 5])

def test_hedge_ratio_explain():
    asset = np.random.randn(100)
    hedge = asset * 0.9 + np.random.randn(100) * 0.1
    r = hedge_ratio(asset, hedge, explain=True)
    assert "covariance" in r["inputs"]


# ── Cholesky correlated shocks ────────────────────────────────────────────────

def test_cholesky_decompose_reconstructs_matrix():
    corr = np.array([[1.0, 0.6], [0.6, 1.0]])
    l = cholesky_decompose(corr)
    assert l @ l.T == pytest.approx(corr)

def test_cholesky_rejects_non_symmetric_matrix():
    with pytest.raises(ValueError, match="symmetric"):
        cholesky_decompose([[1.0, 0.5], [0.1, 1.0]])

def test_correlated_normals_rejects_bad_correlation_diagonal():
    with pytest.raises(ValueError, match="diagonal"):
        correlated_normals([[2.0, 0.1], [0.1, 1.0]], n_sims=10)

def test_correlated_normals_named_dataframe():
    corr = np.array([[1.0, 0.5], [0.5, 1.0]])
    df = correlated_normals(corr, n_sims=100, seed=1, names=["Brent", "WTI"])
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Brent", "WTI"]
    assert df.shape == (100, 2)

def test_correlated_price_shocks_shape():
    corr = np.eye(3)
    shocks = correlated_price_shocks([2.0, 1.5, 0.8], corr, n_sims=50, seed=1)
    assert shocks.shape == (50, 3)

def test_correlated_price_shocks_names_length():
    with pytest.raises(ValueError, match="names"):
        correlated_price_shocks([2.0, 1.5], np.eye(2), n_sims=10, names=["Brent"])

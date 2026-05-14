import numpy as np
import pandas as pd
import pytest
from kolmo_stats import (
    mean, weighted_mean, rolling_zscore,
    seasonal_zscore, rolling_correlation, lead_lag_correlation,
    transition_matrix, simulate_markov_chain, regime_probabilities,
)


# ── mean ──────────────────────────────────────────────────────────────────────

def test_mean_basic():
    assert mean([1, 2, 3]) == 2.0

def test_mean_float():
    assert mean([80.0, 85.0, 90.0]) == 85.0

def test_mean_numpy():
    assert mean(np.array([1.0, 2.0, 3.0])) == 2.0

def test_mean_series():
    assert mean(pd.Series([10.0, 20.0, 30.0])) == 20.0

def test_mean_ignore_nan():
    assert mean([1.0, float("nan"), 3.0]) == 2.0

def test_mean_nan_raises_when_not_ignored():
    with pytest.raises(ValueError, match="NaN"):
        mean([1.0, float("nan"), 3.0], ignore_nan=False)

def test_mean_empty_raises():
    with pytest.raises(ValueError):
        mean([])

def test_mean_all_nan_raises():
    with pytest.raises(ValueError):
        mean([float("nan"), float("nan")])

def test_mean_explain():
    result = mean([1, 2, 3], explain=True)
    assert isinstance(result, dict)
    assert result["result"] == 2.0
    assert "formula" in result
    assert "inputs" in result


# ── weighted_mean ─────────────────────────────────────────────────────────────

def test_weighted_mean_basic():
    assert weighted_mean([80, 85], [0.7, 0.3]) == pytest.approx(81.5)

def test_weighted_mean_equal_weights():
    assert weighted_mean([1, 2, 3], [1, 1, 1]) == pytest.approx(2.0)

def test_weighted_mean_length_mismatch():
    with pytest.raises(ValueError, match="same length"):
        weighted_mean([1, 2], [1])

def test_weighted_mean_zero_weights():
    with pytest.raises(ValueError, match="zero"):
        weighted_mean([1, 2], [0, 0])

def test_weighted_mean_nan_ignored():
    result = weighted_mean([80, float("nan"), 85], [1, 1, 1])
    assert result == pytest.approx(82.5)

def test_weighted_mean_nan_raises_when_not_ignored():
    with pytest.raises(ValueError, match="NaN"):
        weighted_mean([80, float("nan"), 85], [1, 1, 1], ignore_nan=False)

def test_weighted_mean_explain():
    r = weighted_mean([80, 85], [0.7, 0.3], explain=True)
    assert r["result"] == pytest.approx(81.5)


# ── rolling_zscore ────────────────────────────────────────────────────────────

def test_rolling_zscore_returns_series():
    s = pd.Series(range(100), dtype=float)
    z = rolling_zscore(s, window=10)
    assert isinstance(z, pd.Series)
    assert len(z) == 100

def test_rolling_zscore_nan_at_start():
    s = pd.Series(range(20), dtype=float)
    z = rolling_zscore(s, window=5)
    assert z.iloc[:4].isna().all()
    assert not z.iloc[5:].isna().any()

def test_rolling_zscore_explain():
    s = pd.Series(range(50), dtype=float)
    r = rolling_zscore(s, window=10, explain=True)
    assert isinstance(r, dict)
    assert "result" in r

def test_rolling_zscore_invalid_window():
    with pytest.raises(ValueError):
        rolling_zscore([1, 2, 3], window=0)


# ── seasonal_zscore ───────────────────────────────────────────────────────────

def _make_seasonal_series():
    idx = pd.date_range("2020-01-01", periods=730, freq="D")
    return pd.Series(np.sin(np.arange(730) * 2 * np.pi / 365) + 100, index=idx)

def test_seasonal_zscore_month():
    s = _make_seasonal_series()
    z = seasonal_zscore(s, period="month")
    assert isinstance(z, pd.Series)
    assert len(z) == len(s)

def test_seasonal_zscore_quarter():
    s = _make_seasonal_series()
    z = seasonal_zscore(s, period="quarter")
    assert not z.isna().all()

def test_seasonal_zscore_invalid_period():
    s = _make_seasonal_series()
    with pytest.raises(ValueError, match="period"):
        seasonal_zscore(s, period="hour")

def test_seasonal_zscore_no_datetime_index():
    with pytest.raises(TypeError):
        seasonal_zscore(pd.Series([1, 2, 3]))

def test_seasonal_zscore_explain():
    s = _make_seasonal_series()
    r = seasonal_zscore(s, period="month", explain=True)
    assert isinstance(r, dict)


# ── rolling_correlation ───────────────────────────────────────────────────────

def test_rolling_correlation_returns_series():
    x = pd.Series(np.random.randn(100))
    y = pd.Series(np.random.randn(100))
    r = rolling_correlation(x, y, window=20)
    assert isinstance(r, pd.Series)

def test_rolling_correlation_perfect():
    x = pd.Series(range(50), dtype=float)
    r = rolling_correlation(x, x, window=10)
    assert r.dropna().iloc[-1] == pytest.approx(1.0)

def test_rolling_correlation_length_mismatch():
    with pytest.raises(ValueError):
        rolling_correlation(pd.Series([1, 2]), pd.Series([1, 2, 3]))

def test_rolling_correlation_invalid_window():
    with pytest.raises(ValueError):
        rolling_correlation([1, 2, 3], [1, 2, 3], window=0)

def test_rolling_correlation_explain():
    x = pd.Series(range(30), dtype=float)
    r = rolling_correlation(x, x, window=10, explain=True)
    assert isinstance(r, dict)


# ── lead_lag_correlation ──────────────────────────────────────────────────────

def test_lead_lag_correlation_returns_dataframe():
    x = pd.Series(np.random.randn(100))
    y = pd.Series(np.random.randn(100))
    df = lead_lag_correlation(x, y, max_lag=10)
    assert "lag" in df.columns
    assert "correlation" in df.columns
    assert len(df) == 21  # -10 to +10

def test_lead_lag_correlation_detects_lag():
    np.random.seed(42)
    x = pd.Series(np.random.randn(300))
    y = x.shift(5).fillna(0) + np.random.randn(300) * 0.1
    df = lead_lag_correlation(x, y, max_lag=20)
    assert df.attrs["best_lag"] == 5

def test_lead_lag_correlation_attrs():
    x = pd.Series(range(50), dtype=float)
    df = lead_lag_correlation(x, x, max_lag=5)
    assert "best_lag" in df.attrs
    assert "best_correlation" in df.attrs

def test_lead_lag_correlation_invalid_method():
    with pytest.raises(ValueError):
        lead_lag_correlation([1, 2, 3], [1, 2, 3], method="spearman")

def test_lead_lag_correlation_lag_too_large():
    with pytest.raises(ValueError):
        lead_lag_correlation([1, 2, 3], [1, 2, 3], max_lag=3)

def test_lead_lag_correlation_explain():
    x = pd.Series(range(50), dtype=float)
    r = lead_lag_correlation(x, x, max_lag=5, explain=True)
    assert isinstance(r, dict)


# ── Markov regimes ────────────────────────────────────────────────────────────

def test_transition_matrix_basic():
    states = ["backwardation", "backwardation", "contango", "backwardation"]
    matrix = transition_matrix(states)
    assert isinstance(matrix, pd.DataFrame)
    assert matrix.loc["backwardation", "backwardation"] == pytest.approx(0.5)
    assert matrix.loc["backwardation", "contango"] == pytest.approx(0.5)

def test_transition_matrix_state_order_missing_raises():
    with pytest.raises(ValueError):
        transition_matrix(["tight", "loose"], state_order=["tight"])

def test_transition_matrix_terminal_state_absorbing():
    matrix = transition_matrix(["tight", "loose"])
    assert matrix.loc["loose", "loose"] == pytest.approx(1.0)

def test_simulate_markov_chain_length():
    matrix = pd.DataFrame(
        [[0.8, 0.2], [0.3, 0.7]],
        index=["tight", "loose"],
        columns=["tight", "loose"],
    )
    path = simulate_markov_chain(matrix, start_state="tight", n_steps=10, seed=1)
    assert isinstance(path, pd.Series)
    assert len(path) == 11

def test_regime_probabilities():
    matrix = pd.DataFrame(
        [[0.8, 0.2], [0.3, 0.7]],
        index=["tight", "loose"],
        columns=["tight", "loose"],
    )
    probs = regime_probabilities(matrix, current_state="tight", horizon=1)
    assert probs.loc["tight"] == pytest.approx(0.8)
    assert probs.sum() == pytest.approx(1.0)

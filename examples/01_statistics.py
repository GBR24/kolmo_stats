"""
Example 1 — Statistics

Demonstrates: mean, weighted_mean, rolling_zscore, seasonal_zscore,
              rolling_correlation, lead_lag_correlation
"""
import numpy as np
import pandas as pd
from kolmo_stats import (
    mean, weighted_mean, rolling_zscore,
    seasonal_zscore, rolling_correlation, lead_lag_correlation,
)

# ── mean ──────────────────────────────────────────────────────────────────────
print("=== mean ===")
prices = [80.5, 82.0, float("nan"), 85.0, 83.0]
print(f"Prices:     {prices}")
print(f"Mean:       {mean(prices)}")
print(f"Explain:    {mean(prices, explain=True)}")

# ── weighted_mean (VWAP) ──────────────────────────────────────────────────────
print("\n=== weighted_mean (VWAP) ===")
trade_prices  = [80.0, 81.5, 82.0]
trade_volumes = [5000, 2000, 3000]
vwap = weighted_mean(trade_prices, trade_volumes)
print(f"VWAP: ${vwap:.2f}")

# ── rolling_zscore ────────────────────────────────────────────────────────────
print("\n=== rolling_zscore ===")
np.random.seed(42)
brent = pd.Series(
    np.cumsum(np.random.randn(200)) + 80,
    index=pd.date_range("2023-01-01", periods=200, freq="D"),
    name="Brent",
)
z = rolling_zscore(brent, window=30)
print(f"Last 5 z-scores:\n{z.tail()}")
print(f"Current z: {z.iloc[-1]:.2f}  (|z|>2 = extreme)")

# ── seasonal_zscore (gas storage) ─────────────────────────────────────────────
print("\n=== seasonal_zscore ===")
idx = pd.date_range("2019-01-01", periods=365 * 4, freq="D")
storage = pd.Series(
    100 + 30 * np.sin(np.arange(len(idx)) * 2 * np.pi / 365)
    + np.random.randn(len(idx)) * 3,
    index=idx,
    name="EU Gas Storage (TWh)",
)
sz = seasonal_zscore(storage, period="month")
print(f"Seasonal z-score (last 5):\n{sz.tail()}")

# ── rolling_correlation ───────────────────────────────────────────────────────
print("\n=== rolling_correlation (Brent vs Gasoil) ===")
gasoil = brent * 0.97 + np.random.randn(200) * 1.5
corr = rolling_correlation(brent, pd.Series(gasoil.values), window=30)
print(f"Recent rolling correlation:\n{corr.tail()}")

# ── lead_lag_correlation ──────────────────────────────────────────────────────
print("\n=== lead_lag_correlation ===")
x = pd.Series(np.random.randn(300))
y = x.shift(7).fillna(0) + np.random.randn(300) * 0.2
result = lead_lag_correlation(x, y, max_lag=20)
print(f"Best lag: {result.attrs['best_lag']} periods")
print(f"Best correlation: {result.attrs['best_correlation']:.3f}")
print("(Positive lag = x leads y)")

"""
Example 4 — Risk

Demonstrates: historical_var, expected_shortfall, scenario_pnl, hedge_ratio
"""
import numpy as np
import pandas as pd
from kolmo_stats import historical_var, expected_shortfall, scenario_pnl, hedge_ratio

np.random.seed(42)

# Simulate daily Brent P&L for a 1000-barrel long position
brent_daily_changes = np.random.randn(500) * 2.0   # $/bbl daily moves
position_bbls = 1000
daily_pnl = brent_daily_changes * position_bbls

# ── historical_var ────────────────────────────────────────────────────────────
print("=== historical_var ===")
var95 = historical_var(daily_pnl, confidence=0.95)
var99 = historical_var(daily_pnl, confidence=0.99)
print(f"Position: {position_bbls:,} barrels long Brent")
print(f"VaR 95%: ${var95:,.0f}")
print(f"VaR 99%: ${var99:,.0f}")
print(f"Interpretation: 95% of days we lose less than ${var95:,.0f}")
print(historical_var(daily_pnl, confidence=0.95, explain=True))

# ── expected_shortfall ────────────────────────────────────────────────────────
print("\n=== expected_shortfall ===")
es95 = expected_shortfall(daily_pnl, confidence=0.95)
print(f"ES 95%: ${es95:,.0f}")
print(f"VaR 95%: ${var95:,.0f}")
print(f"ES is ${es95 - var95:,.0f} worse than VaR on average in the tail")

# ── scenario_pnl ──────────────────────────────────────────────────────────────
print("\n=== scenario_pnl — Brent crash scenario ===")
positions = {
    "Brent":    10_000,    # long 10,000 bbl
    "Gasoil":   -5_000,    # short 5,000 bbl
    "RBOB":      3_000,    # long 3,000 bbl
    "TTF":      -2_000,    # short 2,000 MMBtu equivalent
}
# Scenario: crude -$10, product cracks widen slightly
shocks = {
    "Brent":  -10.0,
    "Gasoil":  -8.0,
    "RBOB":    -7.5,
    "TTF":     -2.0,
}
df = scenario_pnl(positions, shocks)
print(df.to_string(index=False))
print(f"\nTotal portfolio P&L: ${df.attrs['total_pnl']:,.0f}")

# ── hedge_ratio ───────────────────────────────────────────────────────────────
print("\n=== hedge_ratio (jet fuel vs Brent) ===")
# Simulate jet fuel and Brent daily price changes
brent_chg  = np.random.randn(250) * 1.5
jet_chg    = brent_chg * 1.05 + np.random.randn(250) * 0.4

h = hedge_ratio(jet_chg, brent_chg)
print(f"Hedge ratio (jet vs Brent): {h:.4f}")
print(f"To hedge 100,000 bbl of jet fuel, sell {h * 100_000:,.0f} bbl of Brent futures")
print(hedge_ratio(jet_chg, brent_chg, explain=True))

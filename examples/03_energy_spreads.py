"""
Example 3 — Energy Spreads

Demonstrates: crack_spread, spark_spread, lng_arbitrage
"""
import numpy as np
import pandas as pd
from kolmo_stats import crack_spread, spark_spread, lng_arbitrage
from kolmo_stats.units import gal_to_bbl, usd_per_mmbtu_to_usd_per_mwh

# ── crack_spread ──────────────────────────────────────────────────────────────
print("=== crack_spread ===")

# Prices: crude in $/bbl, products in $/gal → convert to $/bbl first
crude_bbl   = 80.00
rbob_gal    = 2.45   # $/gal
ulsd_gal    = 2.90   # $/gal
rbob_bbl    = rbob_gal * 42
ulsd_bbl    = ulsd_gal * 42

crack_321 = crack_spread(crude_bbl, rbob_bbl, ulsd_bbl, ratio="3-2-1")
crack_211 = crack_spread(crude_bbl, rbob_bbl, ulsd_bbl, ratio="2-1-1")
crack_gas = crack_spread(crude_bbl, rbob_bbl, ratio="simple")

print(f"Crude:          ${crude_bbl:.2f}/bbl")
print(f"RBOB:           ${rbob_bbl:.2f}/bbl (${rbob_gal:.3f}/gal)")
print(f"ULSD:           ${ulsd_bbl:.2f}/bbl (${ulsd_gal:.3f}/gal)")
print(f"3-2-1 crack:    ${crack_321:.2f}/bbl")
print(f"2-1-1 crack:    ${crack_211:.2f}/bbl")
print(f"Gasoline crack: ${crack_gas:.2f}/bbl")
print(crack_spread(crude_bbl, rbob_bbl, ulsd_bbl, ratio="3-2-1", explain=True))

# Time series crack spread
print("\nTime series crack spread (last 5 days):")
np.random.seed(1)
n = 100
crude_ts  = pd.Series(np.cumsum(np.random.randn(n) * 0.5) + 80)
rbob_ts   = crude_ts * 42 * 0.030 + np.random.randn(n) * 2
ulsd_ts   = crude_ts * 42 * 0.034 + np.random.randn(n) * 2
crack_ts  = crack_spread(crude_ts, rbob_ts, ulsd_ts, ratio="3-2-1")
print(crack_ts.tail())

# ── spark_spread ──────────────────────────────────────────────────────────────
print("\n=== spark_spread ===")

power_price = 75.0   # $/MWh
gas_price   = 8.0    # $/MMBtu
heat_rate   = 7.0    # MMBtu/MWh (efficient CCGT)

spark = spark_spread(power_price, gas_price, heat_rate)
print(f"Power:       ${power_price:.2f}/MWh")
print(f"Gas:         ${gas_price:.2f}/MMBtu")
print(f"Heat rate:   {heat_rate} MMBtu/MWh")
print(f"Spark spread: ${spark:.2f}/MWh")
print("(Positive = generation is profitable)")

# Gas price in €/MWh (TTF) → convert to $/MMBtu equivalent first in practice
print(spark_spread(power_price, gas_price, heat_rate, explain=True))

# ── lng_arbitrage ─────────────────────────────────────────────────────────────
print("\n=== lng_arbitrage (Henry Hub → Asia) ===")

arb = lng_arbitrage(
    destination_price=14.0,   # JKM $/MMBtu
    source_price=3.5,          # Henry Hub $/MMBtu
    freight_cost=2.0,
    regas_cost=0.3,
    liquefaction_cost=2.5,
    boil_off_cost=0.2,
)
print(f"JKM (destination):     $14.00/MMBtu")
print(f"Henry Hub (source):    $3.50/MMBtu")
print(f"Total costs:           ${2.0+0.3+2.5+0.2:.2f}/MMBtu")
print(f"Net arbitrage:         ${arb:.2f}/MMBtu")
print("Open arb!" if arb > 0 else "Arb is closed.")
print(lng_arbitrage(14.0, 3.5, 2.0, 0.3, 2.5, 0.2, explain=True))

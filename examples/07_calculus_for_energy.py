"""
Example 7 — Calculus for Energy

Demonstrates: curve_slope (numerical derivative of a futures curve)
and the internal engine layer that powers it.
"""
from kolmo_stats import curve_slope
from kolmo_stats.engine.numerical import gradient, average_slope
import numpy as np

# ── curve_slope — Brent vs TTF ────────────────────────────────────────────────
print("=== curve_slope ===")

brent_backwardated = {"M1": 90, "M2": 88, "M3": 86, "M6": 82, "M12": 76}
brent_contango     = {"M1": 75, "M2": 77, "M3": 79, "M6": 83, "M12": 88}
ttf_steep_contango = {"Q1": 28, "Q2": 33, "Q3": 39, "Q4": 46, "Cal26": 55}

print(f"Brent (backwardated) slope: ${curve_slope(brent_backwardated):.2f}/tenor")
print(f"Brent (contango) slope:     ${curve_slope(brent_contango):.2f}/tenor")
print(f"TTF (steep contango) slope: ${curve_slope(ttf_steep_contango):.2f}/tenor")

# Comparison
for label, curve in [
    ("Flat Brent", [80, 80, 80, 80, 80]),
    ("Mild backwardation", [85, 84, 83.5, 83, 82]),
    ("Strong backwardation", [90, 85, 80, 73, 65]),
    ("Contango", [75, 78, 81, 85, 90]),
]:
    s = curve_slope(curve)
    shape = "flat" if abs(s) < 0.1 else ("backwardation" if s < 0 else "contango")
    print(f"  {label:<25} slope={s:+.2f}  → {shape}")

# ── internal engine layer ─────────────────────────────────────────────────────
print("\n=== engine.numerical (internal) ===")
prices = np.array([90.0, 88.0, 86.0, 82.0, 76.0])
dy = gradient(prices)
print(f"Prices:    {prices}")
print(f"Gradient:  {dy}")
print(f"Avg slope: {average_slope(prices):.2f}")
print()
print("curve_slope() calls engine.numerical.average_slope() internally.")
print("A future C++ backend can replace this without changing the public API.")

# ── explain mode ──────────────────────────────────────────────────────────────
print("\n=== curve_slope explain ===")
print(curve_slope(brent_backwardated, explain=True))

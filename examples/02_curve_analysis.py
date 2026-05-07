"""
Example 2 — Curve Analysis

Demonstrates: curve_shape, calendar_spread, butterfly_spread,
              roll_yield, curve_slope
"""
from kolmo_stats import curve_shape, calendar_spread, butterfly_spread, roll_yield, curve_slope

# Sample Brent forward curve ($/bbl)
brent_curve = {
    "M1": 84.50,
    "M2": 83.20,
    "M3": 82.10,
    "M6": 80.50,
    "M12": 78.00,
    "Cal26": 75.00,
}

print("=== curve_shape ===")
shape = curve_shape(brent_curve)
print(f"Brent curve shape: {shape}")
print(curve_shape(brent_curve, explain=True))

print("\n=== calendar_spread ===")
m1_m6 = calendar_spread(brent_curve, "M1", "M6")
print(f"Brent M1-M6 spread: ${m1_m6:.2f}/bbl")

m1_cal26 = calendar_spread(brent_curve, "M1", "Cal26")
print(f"Brent M1-Cal26 spread: ${m1_cal26:.2f}/bbl")

print("\n=== butterfly_spread ===")
fly = butterfly_spread(brent_curve, "M1", "M3", "M6")
print(f"M1-2*M3+M6 butterfly: ${fly:.2f}/bbl")
print(butterfly_spread(brent_curve, "M1", "M3", "M6", explain=True))

print("\n=== roll_yield ===")
ry = roll_yield(near_price=84.50, far_price=83.20, days_between=30)
print(f"Brent M1/M2 annualised roll yield: {ry:.1%}")

ry_raw = roll_yield(84.50, 83.20, days_between=30, annualize=False)
print(f"Raw (non-annualised) roll yield: {ry_raw:.4f}")

print("\n=== curve_slope ===")
slope = curve_slope(brent_curve)
print(f"Brent curve average slope: ${slope:.2f}/bbl per tenor")
print(f"(Negative = backwardation)")
print(curve_slope(brent_curve, explain=True))

# Contango curve for comparison
ttf_curve = {"Q1": 30.0, "Q2": 32.0, "Q3": 35.0, "Q4": 38.0}
print(f"\nTTF curve shape: {curve_shape(ttf_curve)}")
print(f"TTF curve slope: ${curve_slope(ttf_curve):.2f}/quarter")

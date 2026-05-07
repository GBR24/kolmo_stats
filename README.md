# kolmo

Energy market analytics for Python — statistics, curves, spreads, risk, and project economics.

```
pip install kolmo-stats
```

```python
from kolmo import crack_spread, curve_shape, historical_var, npv, breakeven_price
```

---

## What is kolmo?

kolmo provides simple, well-documented, mathematically sound tools for energy traders,
analysts, and risk teams — focused on oil, gas, LNG, power, and energy derivatives.

It works with data you already have: pandas Series, DataFrames, NumPy arrays, lists,
and dicts. No API keys. No data downloads. No dependencies beyond the standard
scientific Python stack.

---

## Installation

```bash
pip install kolmo-stats
```

Requires Python >= 3.10. Dependencies: numpy, pandas, scipy, networkx.

---

## Quickstart

```python
import numpy as np
from kolmo import (
    crack_spread, curve_shape, curve_slope,
    historical_var, npv, breakeven_price, lng_arbitrage,
)

# Brent forward curve
brent = {"M1": 84.5, "M2": 83.2, "M3": 82.1, "M6": 80.5, "M12": 78.0}
print(curve_shape(brent))        # 'backwardation'
print(curve_slope(brent))        # -1.52  (negative = backwardation)

# Refinery margin
crack = crack_spread(crude=80, gasoline=103, distillate=110, ratio="3-2-1")
print(f"3-2-1 crack: ${crack:.2f}/bbl")

# LNG arbitrage
arb = lng_arbitrage(14.0, 3.5, freight_cost=2.0, liquefaction_cost=2.5,
                    regas_cost=0.3, boil_off_cost=0.2)
print(f"LNG arb: ${arb:.2f}/MMBtu")    # positive = arb is open

# Historical VaR
returns = np.random.randn(500) * 2
print(f"VaR 95%: ${historical_var(returns):,.0f}")

# Project NPV
cashflows = [80, 120, 140, 130, 110, 90, 70, 50, 30]
print(f"NPV: ${npv(cashflows, discount_rate=0.12, initial_investment=400):.1f}M")

# Breakeven oil price
price = breakeven_price(
    capex=500_000_000,
    fixed_opex=[30_000_000] * 15,
    variable_opex_per_unit=12.0,
    production=[5_000_000] * 15,
    discount_rate=0.10,
)
print(f"Breakeven: ${price:.2f}/bbl")
```

---

## The 20 public functions

### Statistics

| Function | Description |
|---|---|
| `mean(values)` | Arithmetic mean with NaN handling |
| `weighted_mean(values, weights)` | Weighted average (VWAP, exposure-weighted) |
| `rolling_zscore(series, window)` | How extreme is the current value vs recent history |
| `seasonal_zscore(series, period)` | Z-score vs seasonal group (month, quarter, week) |
| `rolling_correlation(x, y, window)` | Dynamic correlation between two series |
| `lead_lag_correlation(x, y, max_lag)` | Which market moves first |

### Curves

| Function | Description |
|---|---|
| `curve_shape(curve)` | Classify as backwardation, contango, flat, or mixed |
| `calendar_spread(curve, near, far)` | Near minus far contract price |
| `butterfly_spread(curve, front, middle, back)` | Front - 2*middle + back |
| `roll_yield(near, far, days_between)` | Annualised yield from rolling a futures position |
| `curve_slope(curve)` | Average first derivative (steepness of the curve) |

### Spreads

| Function | Description |
|---|---|
| `crack_spread(crude, gasoline, distillate, ratio)` | Refinery margin: 3-2-1, 2-1-1, or simple |
| `spark_spread(power, gas, heat_rate)` | Gas-fired generation margin |
| `lng_arbitrage(destination, source, freight, ...)` | LNG netback arbitrage value |

### Risk

| Function | Description |
|---|---|
| `historical_var(returns, confidence)` | Value at Risk from historical distribution |
| `expected_shortfall(returns, confidence)` | Average loss beyond VaR (CVaR) |
| `scenario_pnl(positions, shocks)` | Portfolio P&L under price shocks |
| `hedge_ratio(asset_returns, hedge_returns)` | Minimum variance hedge ratio |

### Project Economics

| Function | Description |
|---|---|
| `npv(cashflows, discount_rate)` | Net Present Value |
| `breakeven_price(capex, opex, production, rate)` | Minimum price for NPV = 0 |

---

## explain=True

Every function accepts `explain=True` and returns a dict with the result, a
plain-English explanation, the formula, and the key inputs.

```python
from kolmo import crack_spread
print(crack_spread(80, 103, 110, ratio="3-2-1", explain=True))
# {
#   'result': 12.67,
#   'explanation': 'Refinery crack spread using the 3-2-1 ratio.',
#   'formula': '((2 * gasoline) + distillate - (3 * crude)) / 3',
#   'inputs': {'crude': 80.0, 'gasoline': 103.0, 'ratio': '3-2-1'}
# }
```

---

## Internal engine layer

kolmo uses an internal `kolmo.engine` layer for numerical routines:

```
kolmo.curve_slope(brent_curve)
    └── kolmo.engine.numerical.average_slope(prices)
            └── numpy.gradient(prices)    # default Python backend
            └── kolmo._ext.gradient(...)  # future C++ backend
```

This layer is not part of the public API. It exists so that future versions can
add high-performance backends for simulation-heavy models while keeping the same
public API.

> **Strategic note:** kolmo starts with pure Python for simplicity and transparency.
> The architecture includes an internal engine layer so that future versions can add
> high-performance C++ backends for simulation-heavy and optimisation-heavy energy
> models, while preserving the same simple Python API. See `cpp/DESIGN.md`.

---

## Running tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

107 tests, all green.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Four levels: market knowledge, formulas,
analytical models, and numerical engine improvements.

## License

MIT

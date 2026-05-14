# Conventions

kolmo-stats should feel simple to use, but the math must be explicit. This page
records the conventions used by public functions.

## Sign Conventions

- Calendar spread: `near - far`. Positive usually indicates backwardation.
- Prompt spread: `M1 - M2`.
- Brent-WTI: `Brent - WTI`.
- JKM-TTF: `JKM - TTF`.
- Location spread: `destination - origin`, before transport and quality adjustments.
- Shipping-adjusted spread: `destination - source - costs`.
- Scenario P&L: `position * price_shock`.
- Hedge ratio: positive means sell hedge units against a long asset exposure.

## Units

- Oil flat prices and oil spreads default to `$ / bbl`.
- RBOB and ULSD exchange quotes are often `$ / gal`; convert with
  `usd_per_gal_to_usd_per_bbl` before mixing with crude `$ / bbl`.
- Gas and LNG prices default to `$ / MMBtu`.
- Power prices and spark spreads use `$ / MWh`.
- Product tons/barrels conversions require a caller-provided `bbl_per_ton`
  because density varies by product and specification.

## Risk Measures

- `historical_var` and `expected_shortfall` expect returns or P&L changes where
  losses are negative.
- VaR is a historical lower-tail quantile, not a maximum possible loss.
- Expected Shortfall is the average historical loss inside the tail beyond VaR.
- Rolling risk functions use the same sign convention as their non-rolling
  equivalents.

## Curves

- Curve inputs are ordered from near to far.
- `curve_shape` classifies by relative price changes between adjacent tenors.
- `curve_slope` currently treats tenors as equally spaced positions.
- `butterfly_spread(front, middle, back)` assumes the three tenors are evenly
  spaced if interpreted as curve curvature.

## Regimes

- Markov functions are observable first-order Markov chains.
- They are not hidden Markov models.
- Rows of transition matrices are current states; columns are next states.

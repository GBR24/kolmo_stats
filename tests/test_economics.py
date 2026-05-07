import pytest
from kolmo_stats import npv, breakeven_price


# ── npv ───────────────────────────────────────────────────────────────────────

def test_npv_zero_discount():
    # At 0% discount rate, NPV = sum(cashflows) - investment
    result = npv([100, 100, 100], discount_rate=0.0, initial_investment=200)
    assert result == pytest.approx(100.0)

def test_npv_basic():
    # Single cashflow: 110 / 1.10 - 100 = 100 - 100 = 0
    result = npv([110], discount_rate=0.10, initial_investment=100)
    assert result == pytest.approx(0.0)

def test_npv_positive():
    result = npv([100, 100, 100], discount_rate=0.10, initial_investment=200)
    assert result > 0

def test_npv_negative_when_overpriced():
    result = npv([50], discount_rate=0.10, initial_investment=1000)
    assert result < 0

def test_npv_invalid_discount_rate():
    with pytest.raises(ValueError):
        npv([100], discount_rate=-1.5)

def test_npv_empty_cashflows():
    with pytest.raises(ValueError):
        npv([], discount_rate=0.10)

def test_npv_explain():
    r = npv([100, 100, 100], discount_rate=0.10, initial_investment=200, explain=True)
    assert isinstance(r, dict)
    assert "pv_cashflows" in r["inputs"]
    assert r["result"] > 0


# ── breakeven_price ───────────────────────────────────────────────────────────

def test_breakeven_npv_is_zero():
    """Verify that plugging the breakeven price back in yields NPV ≈ 0."""
    capex = 1_000_000
    fixed_opex = [50_000, 50_000, 50_000]
    variable_opex = 20.0
    production = [10_000, 12_000, 8_000]
    discount_rate = 0.10

    price = breakeven_price(capex, fixed_opex, variable_opex, production, discount_rate)

    # Reconstruct NPV at breakeven price
    from kolmo_stats import npv as compute_npv
    import numpy as np
    prod = np.array(production)
    fopex = np.array(fixed_opex)
    cashflows = price * prod - variable_opex * prod - fopex
    result = compute_npv(cashflows, discount_rate, initial_investment=capex)
    assert result == pytest.approx(0.0, abs=1e-4)

def test_breakeven_positive():
    price = breakeven_price(
        capex=500_000,
        fixed_opex=[30_000, 30_000],
        variable_opex_per_unit=15.0,
        production=[5_000, 5_000],
        discount_rate=0.08,
    )
    assert price > 0

def test_breakeven_length_mismatch():
    with pytest.raises(ValueError, match="same length"):
        breakeven_price(100_000, [10_000], 5.0, [1_000, 1_000], 0.10)

def test_breakeven_explain():
    r = breakeven_price(
        capex=1_000_000,
        fixed_opex=[50_000, 50_000, 50_000],
        variable_opex_per_unit=20.0,
        production=[10_000, 12_000, 8_000],
        discount_rate=0.10,
        explain=True,
    )
    assert "pv_production" in r["inputs"]
    assert r["result"] > 0

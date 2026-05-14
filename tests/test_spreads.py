import numpy as np
import pandas as pd
import pytest
from kolmo_stats import (
    crack_spread,
    spark_spread,
    lng_arbitrage,
    brent_wti_spread,
    quality_spread,
    location_spread,
    ttf_jkm_spread,
    henry_hub_ttf_arb,
    lng_netback,
    shipping_adjusted_spread,
)


# ── crack_spread ──────────────────────────────────────────────────────────────

def test_crack_321_scalar():
    # (2*100 + 95 - 3*80) / 3 = (200+95-240)/3 = 55/3 ≈ 18.33
    result = crack_spread(80, 100, 95, ratio="3-2-1")
    assert result == pytest.approx((2 * 100 + 95 - 3 * 80) / 3)

def test_crack_532_scalar():
    result = crack_spread(80, 100, 95, ratio="5-3-2")
    assert result == pytest.approx((3 * 100 + 2 * 95 - 5 * 80) / 5)

def test_crack_211_scalar():
    result = crack_spread(80, 100, 95, ratio="2-1-1")
    assert result == pytest.approx((100 + 95 - 2 * 80) / 2)

def test_crack_simple():
    assert crack_spread(80, 95, ratio="simple") == pytest.approx(15.0)

def test_crack_321_missing_distillate():
    with pytest.raises(ValueError, match="distillate"):
        crack_spread(80, 100, ratio="3-2-1")

def test_crack_invalid_ratio():
    with pytest.raises(ValueError, match="ratio"):
        crack_spread(80, 100, 95, ratio="1-1-1")

def test_crack_array_input():
    crude = np.array([80.0, 82.0])
    gas = np.array([100.0, 103.0])
    dist = np.array([95.0, 98.0])
    result = crack_spread(crude, gas, dist, ratio="3-2-1")
    assert result.shape == (2,)

def test_crack_series_input():
    crude = pd.Series([80.0, 82.0])
    gas = pd.Series([100.0, 103.0])
    dist = pd.Series([95.0, 98.0])
    result = crack_spread(crude, gas, dist, ratio="3-2-1")
    assert isinstance(result, pd.Series)

def test_crack_distillate_series_sets_series_output():
    crude = 80.0
    gas = 100.0
    dist = pd.Series([95.0, 98.0])
    result = crack_spread(crude, gas, dist, ratio="3-2-1")
    assert isinstance(result, pd.Series)

def test_crack_explain():
    r = crack_spread(80, 100, 95, ratio="3-2-1", explain=True)
    assert "formula" in r
    assert "3-2-1" in r["explanation"]


# ── spark_spread ──────────────────────────────────────────────────────────────

def test_spark_spread_basic():
    assert spark_spread(60, 5, heat_rate=7.0) == pytest.approx(25.0)

def test_spark_spread_negative_when_uneconomic():
    assert spark_spread(30, 5, heat_rate=7.0) == pytest.approx(-5.0)

def test_spark_spread_zero_heat_rate():
    with pytest.raises(ValueError):
        spark_spread(60, 5, heat_rate=0)

def test_spark_spread_series():
    power = pd.Series([60.0, 65.0])
    gas = pd.Series([5.0, 5.5])
    result = spark_spread(power, gas, heat_rate=7.0)
    assert isinstance(result, pd.Series)

def test_spark_spread_explain():
    r = spark_spread(60, 5, heat_rate=7.0, explain=True)
    assert r["result"] == pytest.approx(25.0)


# ── lng_arbitrage ─────────────────────────────────────────────────────────────

def test_lng_arb_open():
    # 12 - 3 - 2 - 0.3 - 2.5 - 0.2 = 4.0
    result = lng_arbitrage(12, 3, 2, regas_cost=0.3, liquefaction_cost=2.5, boil_off_cost=0.2)
    assert result == pytest.approx(4.0)

def test_lng_arb_closed():
    result = lng_arbitrage(10, 9, 3)
    assert result < 0

def test_lng_arb_zero_costs():
    assert lng_arbitrage(10, 3, 2) == pytest.approx(5.0)

def test_lng_arb_explain():
    r = lng_arbitrage(12, 3, 2, regas_cost=0.3, liquefaction_cost=2.5, boil_off_cost=0.2, explain=True)
    assert r["inputs"]["total_cost"] == pytest.approx(5.0)


# ── oil basis spreads ─────────────────────────────────────────────────────────

def test_brent_wti_spread():
    assert brent_wti_spread(84, 80) == pytest.approx(4.0)

def test_quality_spread_series():
    light = pd.Series([85.0, 86.0])
    heavy = pd.Series([78.0, 79.5])
    result = quality_spread(light, heavy)
    assert isinstance(result, pd.Series)
    assert result.iloc[0] == pytest.approx(7.0)

def test_location_spread_explain():
    r = location_spread(82, 79, explain=True)
    assert r["result"] == pytest.approx(3.0)
    assert "formula" in r


# ── gas / LNG spreads ─────────────────────────────────────────────────────────

def test_ttf_jkm_spread():
    assert ttf_jkm_spread(ttf_price=10, jkm_price=14) == pytest.approx(4.0)

def test_lng_netback():
    result = lng_netback(14, freight_cost=2, regas_cost=0.3, liquefaction_cost=2.5, boil_off_cost=0.2)
    assert result == pytest.approx(9.0)

def test_shipping_adjusted_spread():
    result = shipping_adjusted_spread(14, 3.5, freight_cost=2, regas_cost=0.3, liquefaction_cost=2.5, boil_off_cost=0.2)
    assert result == pytest.approx(5.5)

def test_henry_hub_ttf_arb():
    result = henry_hub_ttf_arb(3.5, 10.5, freight_cost=2, regas_cost=0.3, liquefaction_cost=2.5, boil_off_cost=0.2)
    assert result == pytest.approx(2.0)

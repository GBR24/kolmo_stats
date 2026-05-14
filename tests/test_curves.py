import pytest
import pandas as pd
from kolmo_stats import (
    curve_shape,
    calendar_spread,
    butterfly_spread,
    roll_yield,
    curve_slope,
    prompt_spread,
    m1_m3,
    m1_m12,
    time_spread_series,
    annualized_carry,
)


# ── curve_shape ───────────────────────────────────────────────────────────────

def test_curve_shape_backwardation():
    assert curve_shape({"M1": 90, "M2": 88, "M3": 86}) == "backwardation"

def test_curve_shape_contango():
    assert curve_shape({"M1": 80, "M2": 82, "M3": 85}) == "contango"

def test_curve_shape_flat():
    assert curve_shape({"M1": 80.0, "M2": 80.0, "M3": 80.0}) == "flat"

def test_curve_shape_mixed():
    assert curve_shape({"M1": 80, "M2": 85, "M3": 82}) == "mixed"

def test_curve_shape_list_input():
    assert curve_shape([90, 88, 86]) == "backwardation"

def test_curve_shape_too_short():
    with pytest.raises(ValueError):
        curve_shape([90])

def test_curve_shape_explain():
    r = curve_shape({"M1": 90, "M2": 88}, explain=True)
    assert r["result"] == "backwardation"
    assert "formula" in r


# ── calendar_spread ───────────────────────────────────────────────────────────

def test_calendar_spread_dict():
    assert calendar_spread({"M1": 84, "M6": 80}, "M1", "M6") == pytest.approx(4.0)

def test_calendar_spread_contango_negative():
    assert calendar_spread({"M1": 80, "M6": 84}, "M1", "M6") == pytest.approx(-4.0)

def test_calendar_spread_series():
    import pandas as pd
    curve = pd.Series({"M1": 84.0, "M6": 80.0})
    assert calendar_spread(curve, "M1", "M6") == pytest.approx(4.0)

def test_calendar_spread_missing_tenor():
    with pytest.raises(KeyError):
        calendar_spread({"M1": 84}, "M1", "M6")

def test_calendar_spread_wrong_type():
    with pytest.raises(TypeError):
        calendar_spread([84, 80], "M1", "M6")

def test_calendar_spread_explain():
    r = calendar_spread({"M1": 84, "M6": 80}, "M1", "M6", explain=True)
    assert r["result"] == pytest.approx(4.0)


# ── butterfly_spread ──────────────────────────────────────────────────────────

def test_butterfly_spread_basic():
    # M1=90, M2=85, M3=82 → 90 - 2*85 + 82 = 2
    assert butterfly_spread({"M1": 90, "M2": 85, "M3": 82}, "M1", "M2", "M3") == pytest.approx(2.0)

def test_butterfly_spread_zero():
    # Perfectly linear curve → butterfly = 0
    assert butterfly_spread({"M1": 90, "M2": 88, "M3": 86}, "M1", "M2", "M3") == pytest.approx(0.0)

def test_butterfly_spread_explain():
    r = butterfly_spread({"M1": 90, "M2": 85, "M3": 82}, "M1", "M2", "M3", explain=True)
    assert r["result"] == pytest.approx(2.0)


# ── roll_yield ────────────────────────────────────────────────────────────────

def test_roll_yield_backwardation_positive():
    # near > far → positive roll yield
    r = roll_yield(84, 80, days_between=30, annualize=False)
    assert r == pytest.approx(0.05)

def test_roll_yield_contango_negative():
    r = roll_yield(80, 84, days_between=30, annualize=False)
    assert r < 0

def test_roll_yield_annualised():
    r = roll_yield(84, 80, days_between=30, annualize=True)
    assert r == pytest.approx(0.05 * 365 / 30)

def test_roll_yield_zero_far_price():
    with pytest.raises(ValueError):
        roll_yield(84, 0)

def test_roll_yield_explain():
    r = roll_yield(84, 80, days_between=30, explain=True)
    assert "result" in r
    assert "raw_roll_yield" in r["inputs"]


# ── curve_slope ───────────────────────────────────────────────────────────────

def test_curve_slope_backwardation_negative():
    slope = curve_slope({"M1": 90, "M2": 88, "M3": 86})
    assert slope == pytest.approx(-2.0)

def test_curve_slope_contango_positive():
    slope = curve_slope([80, 82, 84])
    assert slope == pytest.approx(2.0)

def test_curve_slope_flat_zero():
    slope = curve_slope([80, 80, 80])
    assert slope == pytest.approx(0.0)

def test_curve_slope_too_short():
    with pytest.raises(ValueError):
        curve_slope([80])

def test_curve_slope_explain():
    r = curve_slope([90, 88, 86], explain=True)
    assert r["result"] < 0
    assert "backwardation" in r["inputs"]["interpretation"]

def test_curve_slope_invalid_method():
    with pytest.raises(ValueError):
        curve_slope([90, 88, 86], method="spline")


# ── carry / time-spread helpers ───────────────────────────────────────────────

def test_prompt_spread():
    curve = {"M1": 84.0, "M2": 82.0, "M3": 80.0, "M12": 75.0}
    assert prompt_spread(curve) == pytest.approx(2.0)

def test_m1_m3_and_m1_m12():
    curve = {"M1": 84.0, "M2": 82.0, "M3": 80.0, "M12": 75.0}
    assert m1_m3(curve) == pytest.approx(4.0)
    assert m1_m12(curve) == pytest.approx(9.0)

def test_time_spread_series():
    near = pd.Series([84.0, 83.0])
    far = pd.Series([80.0, 81.0])
    result = time_spread_series(near, far)
    assert isinstance(result, pd.Series)
    assert result.tolist() == pytest.approx([4.0, 2.0])

def test_annualized_carry_contango_positive():
    result = annualized_carry(80, 84, days_between=30)
    assert result == pytest.approx(0.05 * 365 / 30)

def test_annualized_carry_backwardation_negative():
    assert annualized_carry(84, 80, days_between=30) < 0

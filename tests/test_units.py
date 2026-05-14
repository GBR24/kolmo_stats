import pytest

from kolmo_stats import (
    usd_per_gal_to_usd_per_bbl,
    usd_per_bbl_to_usd_per_gal,
    product_tons_to_bbl,
    bbl_to_product_tons,
)
from kolmo_stats.units import bbl_to_metric_tons


def test_usd_per_gal_to_usd_per_bbl():
    assert usd_per_gal_to_usd_per_bbl(2.50) == pytest.approx(105.0)


def test_bbl_to_metric_tons_negative_factor():
    with pytest.raises(ValueError):
        bbl_to_metric_tons(100, bbl_per_ton=-1)


def test_usd_per_bbl_to_usd_per_gal():
    assert usd_per_bbl_to_usd_per_gal(105.0) == pytest.approx(2.50)


def test_product_tons_to_bbl():
    assert product_tons_to_bbl(100, bbl_per_ton=7.45) == pytest.approx(745.0)


def test_product_tons_to_bbl_negative_factor():
    with pytest.raises(ValueError):
        product_tons_to_bbl(100, bbl_per_ton=-1)


def test_bbl_to_product_tons():
    assert bbl_to_product_tons(745, bbl_per_ton=7.45) == pytest.approx(100.0)


def test_bbl_to_product_tons_zero_factor():
    with pytest.raises(ValueError):
        bbl_to_product_tons(100, bbl_per_ton=0)

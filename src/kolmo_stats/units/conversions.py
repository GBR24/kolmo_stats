"""
Common energy unit conversions.

These are utility functions used internally and available for users who need
to convert between energy measurement systems before passing data to the
public API functions.
"""
from __future__ import annotations

# Conversion constants
BBL_PER_METRIC_TON_CRUDE = 7.33     # approximate for average crude
GAL_PER_BBL = 42.0
MMBTU_PER_MWH = 3.41214            # 1 MWh = 3.41214 MMBtu
GJ_PER_MMBTU = 1.05506
KG_PER_MMBTU_LNG = 21.5            # approximate for LNG


def bbl_to_metric_tons(barrels: float, bbl_per_ton: float = BBL_PER_METRIC_TON_CRUDE) -> float:
    """Convert barrels to metric tons."""
    return barrels / bbl_per_ton


def metric_tons_to_bbl(tons: float, bbl_per_ton: float = BBL_PER_METRIC_TON_CRUDE) -> float:
    """Convert metric tons to barrels."""
    return tons * bbl_per_ton


def usd_per_bbl_to_usd_per_ton(price: float, bbl_per_ton: float = BBL_PER_METRIC_TON_CRUDE) -> float:
    """Convert $/bbl crude price to $/metric ton."""
    return price * bbl_per_ton


def gal_to_bbl(gallons: float) -> float:
    """Convert US gallons to barrels."""
    return gallons / GAL_PER_BBL


def bbl_to_gal(barrels: float) -> float:
    """Convert barrels to US gallons."""
    return barrels * GAL_PER_BBL


def mmbtu_to_mwh(mmbtu: float) -> float:
    """Convert MMBtu to MWh."""
    return mmbtu / MMBTU_PER_MWH


def mwh_to_mmbtu(mwh: float) -> float:
    """Convert MWh to MMBtu."""
    return mwh * MMBTU_PER_MWH


def gj_to_mmbtu(gj: float) -> float:
    """Convert GJ to MMBtu."""
    return gj / GJ_PER_MMBTU


def mmbtu_to_gj(mmbtu: float) -> float:
    """Convert MMBtu to GJ."""
    return mmbtu * GJ_PER_MMBTU


def usd_per_mmbtu_to_usd_per_mwh(price: float) -> float:
    """Convert $/MMBtu gas price to $/MWh equivalent."""
    return price * MMBTU_PER_MWH


def usd_per_mwh_to_usd_per_mmbtu(price: float) -> float:
    """Convert $/MWh to $/MMBtu."""
    return price / MMBTU_PER_MWH

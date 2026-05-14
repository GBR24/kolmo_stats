from kolmo_stats.spreads.crack import crack_spread
from kolmo_stats.spreads.spark import spark_spread
from kolmo_stats.spreads.lng import lng_arbitrage
from kolmo_stats.spreads.oil import brent_wti_spread, quality_spread, location_spread
from kolmo_stats.spreads.gas import (
    ttf_jkm_spread,
    henry_hub_ttf_arb,
    lng_netback,
    shipping_adjusted_spread,
)

__all__ = [
    "crack_spread",
    "spark_spread",
    "lng_arbitrage",
    "brent_wti_spread",
    "quality_spread",
    "location_spread",
    "ttf_jkm_spread",
    "henry_hub_ttf_arb",
    "lng_netback",
    "shipping_adjusted_spread",
]

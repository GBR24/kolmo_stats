"""
Portfolio inner loops with optional native dispatch.
"""
from __future__ import annotations

from importlib import import_module

import numpy as np


def scenario_matrix_values(
    positions: np.ndarray,
    shocks: np.ndarray,
) -> np.ndarray:
    """
    Compute scenario P&L values as ``shock * position``.

    If ``kolmo_stats._ext.portfolio_scenario_matrix`` exists, it may replace
    this inner loop. The public Python API shape stays unchanged.
    """
    native = _native_function("portfolio_scenario_matrix")
    if native is not None:
        return np.asarray(native(positions.tolist(), shocks.tolist()), dtype=float)
    return shocks * positions.reshape(1, -1)


def _native_function(name: str):
    try:
        ext = import_module("kolmo_stats._ext")
    except Exception:
        return None
    return getattr(ext, name, None)

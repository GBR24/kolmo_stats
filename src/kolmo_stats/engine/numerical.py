"""
Numerical differentiation helpers.

Uses numpy's gradient (central differences at interior points, one-sided
at boundaries) as the default engine. Future C++ backends can replace
`gradient` and `average_slope` without touching the public API.
"""
from __future__ import annotations

import numpy as np


def gradient(y: np.ndarray, x: np.ndarray | None = None) -> np.ndarray:
    """First derivative via numpy gradient (central differences)."""
    if x is not None:
        return np.gradient(y, x)
    return np.gradient(y)


def average_slope(y: np.ndarray, x: np.ndarray | None = None) -> float:
    """Mean value of the first derivative across all points."""
    return float(np.mean(gradient(y, x)))

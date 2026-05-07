"""
Array coercion and validation utilities.

Internal use only. Provides a single entry point for normalising inputs
so the rest of the library never has to handle list / tuple / Series /
ndarray divergence inline.
"""
from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd

ArrayLike = Union[list, tuple, np.ndarray, pd.Series]


def coerce_array(values: ArrayLike) -> np.ndarray:
    """Convert any array-like to a float64 ndarray."""
    if isinstance(values, pd.Series):
        return values.to_numpy(dtype=float)
    return np.asarray(values, dtype=float)


def validate_same_length(a, b, names: tuple[str, str] = ("a", "b")) -> None:
    if len(a) != len(b):
        raise ValueError(
            f"{names[0]} and {names[1]} must have the same length; "
            f"got {len(a)} and {len(b)}"
        )


def drop_nan_pairs(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Remove indices where either array contains NaN."""
    mask = ~(np.isnan(a) | np.isnan(b))
    return a[mask], b[mask]

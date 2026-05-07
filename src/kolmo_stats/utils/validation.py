"""
Input validation helpers used across the library.
"""
from __future__ import annotations

import pandas as pd


def require_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive; got {value}")


def require_in_range(value: float, low: float, high: float, name: str) -> None:
    if not (low <= value <= high):
        raise ValueError(f"{name} must be in [{low}, {high}]; got {value}")


def require_non_empty(arr, name: str = "input") -> None:
    if len(arr) == 0:
        raise ValueError(f"{name} must not be empty")


def require_datetime_index(series: pd.Series, name: str = "series") -> None:
    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError(
            f"{name} must have a DatetimeIndex. "
            "Convert with pd.to_datetime() and set as the index."
        )

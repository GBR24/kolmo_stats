"""
Helpers for building explain=True return dictionaries.
"""
from __future__ import annotations

from typing import Any


def make_explain(
    result: Any,
    explanation: str,
    formula: str,
    inputs: dict,
) -> dict:
    """Return the standard explain dictionary."""
    return {
        "result": result,
        "explanation": explanation,
        "formula": formula,
        "inputs": inputs,
    }

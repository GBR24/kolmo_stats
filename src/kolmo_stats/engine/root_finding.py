"""
Root-finding primitives wrapping scipy.optimize.

The public API functions (e.g. breakeven_price) call find_root so that a
future C++ brentq implementation can be swapped in here without any change
to the business logic above.
"""
from __future__ import annotations

from typing import Callable

from scipy.optimize import brentq


def find_root(
    f: Callable[[float], float],
    a: float,
    b: float,
    xtol: float = 1e-8,
    maxiter: int = 200,
) -> float:
    """Find a root of f in [a, b] using Brent's method."""
    return brentq(f, a, b, xtol=xtol, maxiter=maxiter)


def find_root_auto(
    f: Callable[[float], float],
    x0: float = 1.0,
    factor: float = 10.0,
    max_expand: int = 30,
) -> float:
    """
    Auto-bracket a root by expanding outward from x0, then apply Brent's method.

    Useful when the bracket bounds are not known in advance.
    """
    lo = max(x0 / factor, 1e-6)
    hi = x0 * factor
    for _ in range(max_expand):
        try:
            fa, fb = f(lo), f(hi)
            if fa * fb < 0:
                return brentq(f, lo, hi)
        except (ValueError, ZeroDivisionError):
            pass
        lo /= factor
        hi *= factor
    raise ValueError(
        f"Could not bracket root near x0={x0}. "
        "Check that a sign change exists in the function."
    )

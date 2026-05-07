"""
Scenario stress testing for energy portfolios.
"""
from __future__ import annotations

import pandas as pd

from kolmo_stats.utils.explain import make_explain


def scenario_pnl(
    positions: dict,
    shocks: dict,
    explain: bool = False,
) -> pd.DataFrame | dict:
    """
    Calculate portfolio P&L under a set of price shocks.

    Assets in positions but not in shocks receive a zero shock.
    Assets in shocks but not in positions are included with zero position.

    Parameters
    ----------
    positions : dict
        {asset_name: position_size}
        Position size is in natural units (e.g. barrels, MWh, lots).
    shocks : dict
        {asset_name: price_shock}
        Price shock in the same unit as the position P&L (e.g. $/bbl).
    explain : bool

    Returns
    -------
    pandas DataFrame with columns ["asset", "position", "shock", "pnl"].
    DataFrame.attrs["total_pnl"] contains the portfolio total.
    Returns dict if explain=True.

    Examples
    --------
    >>> positions = {"Brent": 10000, "TTF": -5000}
    >>> shocks = {"Brent": -5, "TTF": 10}
    >>> df = scenario_pnl(positions, shocks)
    >>> df.attrs["total_pnl"]
    -100000
    """
    all_assets = sorted(set(positions) | set(shocks))
    rows = []
    for asset in all_assets:
        pos = float(positions.get(asset, 0))
        shock = float(shocks.get(asset, 0))
        rows.append({"asset": asset, "position": pos, "shock": shock, "pnl": pos * shock})

    df = pd.DataFrame(rows)
    total = float(df["pnl"].sum())
    df.attrs["total_pnl"] = total

    if explain:
        return make_explain(
            result=df,
            explanation=(
                "Portfolio P&L under price shocks. "
                f"Total P&L: {total:,.2f}."
            ),
            formula="pnl = position * shock for each asset",
            inputs={"total_pnl": total, "n_assets": len(df)},
        )
    return df

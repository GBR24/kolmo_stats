"""
Scenario matrices for oil and gas portfolios.
"""
from __future__ import annotations

import pandas as pd

from kolmo_stats.utils.explain import make_explain


def stress_matrix(
    positions: dict,
    scenarios: dict[str, dict],
    explain: bool = False,
) -> pd.DataFrame | dict:
    """
    Compute portfolio P&L across multiple named stress scenarios.

    Parameters
    ----------
    positions : dict
        {asset_name: position_size}
    scenarios : dict
        {scenario_name: {asset_name: price_shock}}

    Returns
    -------
    pandas DataFrame indexed by scenario. Asset columns contain per-asset P&L
    and ``total_pnl`` contains the row total.
    """
    if not scenarios:
        raise ValueError("scenarios must not be empty")

    assets = sorted(set(positions) | set().union(*(set(s) for s in scenarios.values())))
    rows = []
    for scenario_name, shocks in scenarios.items():
        row = {"scenario": scenario_name}
        total = 0.0
        for asset in assets:
            pnl = float(positions.get(asset, 0.0)) * float(shocks.get(asset, 0.0))
            row[asset] = pnl
            total += pnl
        row["total_pnl"] = total
        rows.append(row)

    df = pd.DataFrame(rows).set_index("scenario")

    if explain:
        return make_explain(
            result=df,
            explanation=(
                "Stress matrix: per-asset and total P&L across named scenarios."
            ),
            formula="pnl[scenario, asset] = position[asset] * shock[scenario, asset]",
            inputs={
                "n_assets": len(assets),
                "n_scenarios": len(scenarios),
                "assets": assets,
            },
        )
    return df

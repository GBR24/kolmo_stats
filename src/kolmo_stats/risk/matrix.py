"""
Scenario matrices for oil and gas portfolios.
"""
from __future__ import annotations

import pandas as pd
import numpy as np

from kolmo_stats.engine.portfolio import scenario_matrix_values
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
    df = portfolio_scenario_matrix(positions, scenarios, explain=False)

    if explain:
        return make_explain(
            result=df,
            explanation=(
                "Stress matrix: per-asset and total P&L across named scenarios."
            ),
            formula="pnl[scenario, asset] = position[asset] * shock[scenario, asset]",
            inputs={
                "n_assets": len(df.columns) - 1,
                "n_scenarios": len(scenarios),
                "assets": [c for c in df.columns if c != "total_pnl"],
            },
        )
    return df


def portfolio_scenario_matrix(
    positions: dict,
    scenarios: dict[str, dict],
    explain: bool = False,
) -> pd.DataFrame | dict:
    """
    Compute a scenario-by-asset portfolio P&L matrix.

    This is the stable Python API for large portfolio scenario calculations.
    The inner matrix multiplication can be replaced by an optional native
    backend without changing the return shape.
    """
    if not positions:
        raise ValueError("positions must not be empty")
    if not scenarios:
        raise ValueError("scenarios must not be empty")

    assets = sorted(set(positions) | set().union(*(set(s) for s in scenarios.values())))
    scenario_names = list(scenarios)
    position_vector = np.asarray([float(positions.get(asset, 0.0)) for asset in assets])
    shock_matrix = np.asarray(
        [
            [float(scenarios[name].get(asset, 0.0)) for asset in assets]
            for name in scenario_names
        ],
        dtype=float,
    )

    pnl_matrix = scenario_matrix_values(position_vector, shock_matrix)
    df = pd.DataFrame(pnl_matrix, index=scenario_names, columns=assets)
    df.index.name = "scenario"
    df["total_pnl"] = df.sum(axis=1)

    if explain:
        return make_explain(
            result=df,
            explanation="Scenario-by-asset P&L matrix for a portfolio.",
            formula="pnl_matrix = shock_matrix * position_vector",
            inputs={
                "n_assets": len(assets),
                "n_scenarios": len(scenarios),
                "assets": assets,
            },
        )
    return df

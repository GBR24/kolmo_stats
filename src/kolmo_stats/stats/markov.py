"""
Observable Markov-chain helpers for oil and gas regimes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.utils.explain import make_explain


def transition_matrix(
    states,
    state_order: list | None = None,
    fill_absorbing: bool = True,
    explain: bool = False,
) -> pd.DataFrame | dict:
    """
    Estimate a first-order transition probability matrix from observed states.

    Rows are current states; columns are next states. By default, states with
    no observed outgoing transition are treated as absorbing so the result is
    usable for simulation.
    """
    observed = pd.Series(states, dtype="object").dropna().tolist()
    if len(observed) < 2:
        raise ValueError("states must contain at least two observations")

    order = list(state_order) if state_order is not None else list(dict.fromkeys(observed))
    missing = set(observed) - set(order)
    if missing:
        raise ValueError(f"state_order is missing observed states: {sorted(missing)}")

    counts = pd.DataFrame(0.0, index=order, columns=order)
    for current, nxt in zip(observed[:-1], observed[1:]):
        counts.loc[current, nxt] += 1.0

    row_sums = counts.sum(axis=1)
    probs = counts.div(row_sums.replace(0.0, np.nan), axis=0).fillna(0.0)
    if fill_absorbing:
        for state in probs.index[row_sums == 0.0]:
            probs.loc[state, state] = 1.0

    if explain:
        return make_explain(
            result=probs,
            explanation="First-order transition matrix estimated from observed regimes.",
            formula="P[i, j] = count(state_t=i, state_t+1=j) / count(state_t=i)",
            inputs={
                "n_observations": len(observed),
                "n_states": len(order),
                "states": order,
                "fill_absorbing": fill_absorbing,
            },
        )
    return probs


def simulate_markov_chain(
    matrix,
    start_state,
    n_steps: int,
    seed: int | None = None,
    explain: bool = False,
) -> pd.Series | dict:
    """
    Simulate states from a transition matrix.

    The returned Series includes the start state, so its length is
    ``n_steps + 1``.
    """
    if n_steps < 0:
        raise ValueError("n_steps must be non-negative")

    if isinstance(matrix, pd.DataFrame):
        states = list(matrix.index)
        if list(matrix.columns) != states:
            raise ValueError("matrix columns must match matrix index order")
        probs = matrix.to_numpy(dtype=float)
    else:
        probs = np.asarray(matrix, dtype=float)

    if probs.ndim != 2 or probs.shape[0] != probs.shape[1]:
        raise ValueError("matrix must be square")
    if not isinstance(matrix, pd.DataFrame):
        states = list(range(probs.shape[0]))
    if start_state not in states:
        raise ValueError("start_state must be present in matrix states")
    if np.any(probs < 0):
        raise ValueError("transition probabilities must be non-negative")

    row_sums = probs.sum(axis=1)
    if not np.allclose(row_sums, 1.0):
        raise ValueError("each transition matrix row must sum to 1")

    rng = np.random.default_rng(seed)
    current = start_state
    path = [current]
    for _ in range(n_steps):
        idx = states.index(current)
        current = rng.choice(states, p=probs[idx])
        path.append(current)

    result = pd.Series(path, name="state")
    if explain:
        return make_explain(
            result=result,
            explanation="Markov-chain simulation from a transition matrix.",
            formula="state_t+1 ~ P[state_t, :]",
            inputs={"start_state": start_state, "n_steps": n_steps, "seed": seed},
        )
    return result


def regime_probabilities(
    matrix,
    current_state,
    horizon: int,
    explain: bool = False,
) -> pd.Series | dict:
    """
    Probability distribution over regimes after a fixed horizon.
    """
    if horizon < 0:
        raise ValueError("horizon must be non-negative")

    if isinstance(matrix, pd.DataFrame):
        states = list(matrix.index)
        if list(matrix.columns) != states:
            raise ValueError("matrix columns must match matrix index order")
        probs = matrix.to_numpy(dtype=float)
    else:
        probs = np.asarray(matrix, dtype=float)

    if probs.ndim != 2 or probs.shape[0] != probs.shape[1]:
        raise ValueError("matrix must be square")
    if not isinstance(matrix, pd.DataFrame):
        states = list(range(probs.shape[0]))
    if current_state not in states:
        raise ValueError("current_state must be present in matrix states")
    if np.any(probs < 0):
        raise ValueError("transition probabilities must be non-negative")

    row_sums = probs.sum(axis=1)
    if not np.allclose(row_sums, 1.0):
        raise ValueError("each transition matrix row must sum to 1")

    initial = np.zeros(len(states))
    initial[states.index(current_state)] = 1.0
    result = initial @ np.linalg.matrix_power(probs, horizon)
    series = pd.Series(result, index=states, name="probability")

    if explain:
        return make_explain(
            result=series,
            explanation=f"Regime probabilities after {horizon} transitions.",
            formula="p_h = p_0 @ P^horizon",
            inputs={"current_state": current_state, "horizon": horizon},
        )
    return series

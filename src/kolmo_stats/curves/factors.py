"""
Curve factor analytics.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from kolmo_stats.utils.explain import make_explain


def curve_pca(
    curves,
    n_components: int = 3,
    explain: bool = False,
) -> dict:
    """
    Principal-component analysis of curve levels or curve changes.

    Rows are observations and columns are tenors. Components are ordered by
    explained variance and can be interpreted as level/slope/curvature factors
    when the input columns are ordered from prompt to deferred tenors.
    """
    frame = _as_frame(curves)
    if n_components < 1:
        raise ValueError("n_components must be at least 1")
    if frame.shape[0] < 2:
        raise ValueError("curves must contain at least 2 observations")
    if frame.shape[1] < 2:
        raise ValueError("curves must contain at least 2 tenors")

    n_components = min(n_components, frame.shape[0], frame.shape[1])
    mean_curve = frame.mean(axis=0)
    centered = frame - mean_curve
    u, singular, vt = np.linalg.svd(centered.to_numpy(dtype=float), full_matrices=False)

    components = pd.DataFrame(
        vt[:n_components],
        index=[f"PC{i + 1}" for i in range(n_components)],
        columns=frame.columns,
    )
    scores = pd.DataFrame(
        u[:, :n_components] * singular[:n_components],
        index=frame.index,
        columns=components.index,
    )
    explained_variance = (singular[:n_components] ** 2) / (len(frame) - 1)
    total_variance = float(((singular**2) / (len(frame) - 1)).sum())
    explained_ratio = explained_variance / total_variance if total_variance else explained_variance

    result = {
        "components": components,
        "scores": scores,
        "explained_variance": pd.Series(explained_variance, index=components.index),
        "explained_variance_ratio": pd.Series(explained_ratio, index=components.index),
        "mean_curve": mean_curve,
    }
    if explain:
        return make_explain(
            result=result,
            explanation="PCA factors for ordered futures-curve observations.",
            formula="center curves, then SVD: X = U*S*V.T",
            inputs={"n_observations": frame.shape[0], "n_tenors": frame.shape[1]},
        )
    return result


def curve_factor_exposures(
    curve_changes,
    components,
    explain: bool = False,
):
    """
    Project curve changes onto PCA component loadings.
    """
    changes = _as_frame(curve_changes)
    comps = components if isinstance(components, pd.DataFrame) else pd.DataFrame(components)
    missing = [col for col in comps.columns if col not in changes.columns]
    if missing:
        raise ValueError(f"curve_changes missing component tenors: {missing}")

    aligned = changes.loc[:, comps.columns]
    exposure_values = aligned.to_numpy(dtype=float) @ comps.to_numpy(dtype=float).T
    exposures = pd.DataFrame(exposure_values, index=changes.index, columns=comps.index)
    if len(exposures) == 1:
        result = exposures.iloc[0]
    else:
        result = exposures

    if explain:
        return make_explain(
            result=result,
            explanation="Projection of curve changes onto PCA factor loadings.",
            formula="factor_exposure = curve_change @ component.T",
            inputs={"n_observations": len(changes), "n_components": len(comps)},
        )
    return result


def _as_frame(values) -> pd.DataFrame:
    if isinstance(values, pd.DataFrame):
        frame = values.copy()
    elif isinstance(values, pd.Series):
        frame = values.to_frame().T
    else:
        arr = np.asarray(values, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        frame = pd.DataFrame(arr, columns=[f"tenor_{i}" for i in range(arr.shape[1])])
    frame = frame.dropna()
    if frame.empty:
        raise ValueError("curve data must contain valid numeric values")
    return frame

# Development Guide

kolmo-stats is open source, so the repo should reward small, careful
contributions. Prefer clear formulas, good naming, and focused tests over clever
abstractions.

## Adding Or Changing A Public Function

1. Put the function in the narrowest domain module under `src/kolmo_stats/`.
2. Export it from the domain `__init__.py` and from `src/kolmo_stats/__init__.py`.
3. Add a docstring with the convention, formula, units, and an example.
4. Support scalars, NumPy arrays, lists, and pandas Series where that makes sense.
5. Preserve pandas indexes when returning Series.
6. Add `explain=False` when the function is an analytics calculation.
7. Add tests for formula, pandas/list handling, invalid inputs, and `explain=True`.
8. Update `README.md` if the function is public.

## Validation

Be strict at the boundary:

- Reject unsupported method names instead of silently ignoring them.
- Reject impossible dimensions, bad probabilities, and invalid windows.
- Make unit assumptions explicit in names or docstrings.
- Avoid accepting inputs that produce mathematically plausible but market-wrong
  outputs without warning.

## Native Backend Rule

Heavy implementations may eventually live under `native/`, but users should
always call Python functions. Keep validation, pandas support, docs, and
`explain=True` in Python. Native code should accelerate inner loops only.

## Test Commands

```bash
python -m pytest
PYTHONPATH=src python -m compileall -q src tests
git diff --check
```

The CI/dev expectation is that these pass before opening a PR.

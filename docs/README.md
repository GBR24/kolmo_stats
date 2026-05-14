# Documentation

This folder is the map for users and contributors.

## Start Here

- [CONVENTIONS.md](CONVENTIONS.md) explains signs, units, and market conventions.
- [DEVELOPMENT.md](DEVELOPMENT.md) explains how to add or change analytics.
- [native/README.md](../native/README.md) explains the future compiled-backend strategy.
- [knowledge_graph/CONTRIBUTING.md](../knowledge_graph/CONTRIBUTING.md) explains market graph contributions.

## Repository Structure

| Path | Purpose |
|---|---|
| `src/kolmo_stats/` | Python package. Public functions are exported from `kolmo_stats.__init__`. |
| `tests/` | Unit and regression tests. Every public function should have formula and validation coverage. |
| `examples/` | Short runnable scripts that demonstrate realistic oil/gas workflows. |
| `docs/` | User and contributor documentation. |
| `knowledge_graph/` | Editable market relationship graph data and graph contribution guide. |
| `native/` | Optional future compiled backends. Users still call Python functions. |

## Local Workflow

```bash
pip install -e ".[dev]"
python -m pytest
```

The repo uses a `src/` layout. Pytest is configured to import from `src/` so
local tests exercise the working tree, not an installed package from site-packages.

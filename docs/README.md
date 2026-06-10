# Documentation

This folder is the map for users and contributors.

## Start Here

- [CONVENTIONS.md](CONVENTIONS.md) explains signs, units, and market conventions.
- [FUNCTION_CATALOG.md](FUNCTION_CATALOG.md) lists the public API by domain.
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
| `src/kolmo_stats/graph/market_graph.yml` | Packaged YAML market relationship graph data. |
| `knowledge_graph/` | Compatibility shim and graph contribution guide. |
| `native/` | Optional future compiled backends. Users still call Python functions. |

## Local Workflow

```bash
pip install -e ".[dev]"
python -m pytest
```

The repo uses a `src/` layout. Pytest is configured to import from `src/` so
local tests exercise the working tree, not an installed package from site-packages.

## Market Graph Viewer

```bash
pip install -e .
python examples/08_market_graph_viewer.py
```

Open `http://127.0.0.1:8000` to browse the packaged graph before suggesting
market knowledge or editing `src/kolmo_stats/graph/market_graph.yml`.

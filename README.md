# FlowForge v0.2.2

**FlowForge** is a **developer-first ETL (Extract, Transform, Load) and integration runtime** written in Python.

Key features:

- **Pipeline execution** with step-level lifecycle management and retry tracking
- **Reliability** — exact retry attempt tracking and failed step persistence
- **Step-level persistence** and injectable SQLite repository for data management
- **Hooks** — `before_step` and `after_step` callbacks for custom behavior around each step
- **CLI** — quick commands for running scripts, viewing run history, and inspecting execution details
- **Type safety** — built with strict type checking using mypy
- **Modern Python stack** — Python 3.11+, using structlog for structured logging, ruff for linting, pytest for testing

The project is currently at v0.2.2 and it is in active development, with recent improvements to packaging (proper `src/` layout, `pyproject.toml`), type checking configuration, execution models, and CLI/hooks support. It's designed to make it easy to build reliable data pipelines and integrations.

## What changed

- Proper `src/` Python package layout
- `pyproject.toml` packaging
- Structured logging support via `structlog`
- Strict type checking configuration
- Ruff configuration
- Cleaner VS Code configuration for Pylance
- Pipeline run and step execution models
  * Reliable step lifecycle and exact retry attempt tracking
- Step-level persistence
- Retry policy with attempt tracking
- Failed step persistence
- Injectable SQLite repository
- Tests for success, retry and failure paths

## Setup on Windows

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Open the **flowforge** folder itself in VS Code. Then select:

`Ctrl+Shift+P` → `Python: Select Interpreter` → `.venv\Scripts\python.exe`

For navigation, Pylance should be installed and enabled.

## Run example

```powershell
python examples\product_sync.py
```

## Tests

```powershell
pytest
```

## Static checks

```powershell
ruff check .
mypy src
```

## Important

Do not commit `.venv`, `flowforge.db`, `__pycache__`, or test caches. They are excluded by `.gitignore`.

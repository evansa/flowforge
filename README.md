# FlowForge v0.2.2

Developer-first ETL and integration runtime.

## What changed

- Proper `src/` Python package layout
- `pyproject.toml` packaging
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

# FlowForge v0.2.2

FlowForge is a Python ETL and integration runtime for building reliable pipeline-style workflows with retries, step tracking, and local SQLite persistence.

## Features

- Pipeline definitions with `extract()`, `transform()`, and `load()` steps
- Pipeline execution with step-level lifecycle management and retry tracking
- Reliability via exact retry-attempt tracking and failed-step persistence
- Step-level execution state tracking and persistence
- Pipeline run history with execution metadata
- Hook points for `before_step` and `after_step`
- Local SQLite-backed repository for run and step inspection
- CLI for running scripts, viewing history, and inspecting executions
- Strict Python 3.11+ typing and tooling support
- Modern Python tooling with `structlog`, `ruff`, `mypy`, and `pytest`

The project is currently at v0.2.2 and is in active development. Recent work includes packaging improvements, stricter typing, execution models, SQLite persistence, and CLI/hook support.

## What changed

- Proper `src/` Python package layout
- `pyproject.toml` packaging and console entry point
- Structured logging support via `structlog`
- Strict type checking configuration
- Ruff configuration
- Pipeline run and step execution models
- Step-level persistence
- Retry policy with attempt tracking
- Failed step persistence
- Injectable SQLite repository
- CLI support for script execution, history, and details
- Tests covering success, retry, and failure paths

## Installation

On Windows:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Then select the project interpreter in VS Code:

`Ctrl+Shift+P` → `Python: Select Interpreter` → `.venv\Scripts\python.exe`

## Quick start

```python
from flowforge import Pipeline

pipeline = Pipeline(
    name="product-sync",
    retries=3,
    retry_delay_seconds=0.1,
    database="flowforge.db",
)


@pipeline.extract()
def extract_products():
    return [{"product_id": "1001", "name": "Keyboard"}]


@pipeline.transform()
def transform_products(products):
    return [{**product, "released": True} for product in products]


@pipeline.load()
def load_products(products):
    for product in products:
        print(product)


result = pipeline.run()
print(result.execution_id)
print(result.status)
print(result.records_processed)
```

This executes each step in order while persisting the run and its step state to SQLite.

## Hooks

You can customize pipeline behavior by overriding methods on a `Pipeline` instance or assigning callables at runtime:

```python
class MyPipeline(Pipeline):
    def before_step(self, step_name: str, execution_id: str | None = None) -> None:
        print(f"Running {step_name} for {execution_id}")

    def after_step(
        self,
        step_name: str,
        execution_id: str | None = None,
        result: object | None = None,
        error: Exception | None = None,
    ) -> None:
        if error is not None:
            print(f"Step {step_name} failed: {error}")
```

Hook failures are logged and do not stop pipeline execution.

## CLI usage

The package exposes a `flowforge` command via the project entry point.

```powershell
flowforge run path\to\script.py
flowforge history
flowforge info <execution_id>
```

The CLI uses the local `flowforge.db` database by default unless a different database is specified in the pipeline configuration.

## Example script

```powershell
python examples\product_sync.py
```

This creates a sample pipeline run and prints the execution result.

## Tests

```powershell
pytest
```

## Static checks

```powershell
ruff check .
mypy src
```

## Notes

- The project uses a `src/` layout.
- The default database file is `flowforge.db`.
- Do not commit `.venv`, local SQLite databases, `__pycache__`, or pytest caches.
- The project uses `ruff` for linting and `mypy` for type checking.

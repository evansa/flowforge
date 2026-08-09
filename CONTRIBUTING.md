# Contributing to FlowForge

Thanks for wanting to contribute! This document covers development setup, coding style, testing and PR guidelines.

Development setup
- Python 3.11 is required.
- Create a virtual environment: python -m venv .venv
- Activate it and install dev deps: pip install -e .[dev]
- The package entry point lives under src/flowforge.

Code style
- ruff is the preferred linter; mypy for static typing.
- Follow PEP8 and keep lines <= 88 characters.
- Type hints are required for public functions and methods (mypy strict).

Testing
- Tests are run with pytest. Run: pytest -q
- Use pytest fixtures and tmp_path for filesystem tests.
- Cover hooks and CLI behaviour with unit tests.

Pull Request guidelines
- Branch from main or an appropriate feature branch.
- Provide a clear PR title and description describing the change.
- Include tests for new features or bug fixes.
- Ensure all tests pass and run ruff/mypy locally before opening the PR.
- Use conventional commits where possible.

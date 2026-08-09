"""Small CLI for FlowForge quick operations.

Provides three subcommands:
- run <script>: execute a local python script file (runpy.run_path)
- history: show recent pipeline runs
- info <execution_id>: show run and steps details

Uses the local flowforge.db by default.
"""
from __future__ import annotations

import argparse
import runpy
import sqlite3
from typing import Any

from flowforge.storage.database import DEFAULT_DATABASE
from flowforge.storage.repository import PipelineRepository


def _print_row(row: tuple[Any, ...]) -> None:
    print(" | ".join(str(c) for c in row))


def cmd_run(args: argparse.Namespace) -> int:
    script = args.script
    try:
        runpy.run_path(script, run_name="__main__")
        return 0
    except Exception as exc:  # pragma: no cover - simple runner
        print(f"Error running {script}: {exc}")
        return 2


def cmd_history(args: argparse.Namespace) -> int:
    db = DEFAULT_DATABASE
    con = sqlite3.connect(db)
    cur = con.execute(
        "SELECT execution_id, pipeline_name, status, started_at, finished_at, records_processed "
        "FROM pipeline_runs ORDER BY started_at DESC LIMIT 20"
    )
    rows = cur.fetchall()
    if not rows:
        print("No runs recorded yet.")
        return 0
    for r in rows:
        _print_row(r)
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    execution_id = args.execution_id
    repo = PipelineRepository(database=DEFAULT_DATABASE)
    run = repo.get_run(execution_id)
    if run is None:
        print(f"No run found for execution_id={execution_id}")
        return 1
    print("Run:")
    _print_row(run)
    print("Steps:")
    for s in repo.get_steps(execution_id):
        _print_row(s)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="flowforge")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("script", help="Path to a python script to execute")
    p_run.set_defaults(func=cmd_run)

    p_history = sub.add_parser("history")
    p_history.set_defaults(func=cmd_history)

    p_info = sub.add_parser("info")
    p_info.add_argument("execution_id")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

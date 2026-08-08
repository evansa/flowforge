"""SQLite database setup for local FlowForge development."""

import sqlite3
from pathlib import Path

DEFAULT_DATABASE = "flowforge.db"


def initialise_database(database: str = DEFAULT_DATABASE) -> None:
    """Create FlowForge tables if they do not already exist."""
    database_path = Path(database)
    if database_path.parent != Path("."):
        database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                execution_id TEXT PRIMARY KEY,
                pipeline_name TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                records_processed INTEGER NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                records_processed INTEGER NOT NULL,
                attempts INTEGER NOT NULL,
                error_message TEXT
            )
            """
        )

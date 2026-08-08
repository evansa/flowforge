"""Persistence repository for pipeline executions."""

import sqlite3

from flowforge.models.pipeline_run import PipelineRun
from flowforge.models.pipeline_step import PipelineStep
from flowforge.storage.database import DEFAULT_DATABASE, initialise_database


class PipelineRepository:
    """Persist pipeline runs and step executions."""

    def __init__(self, database: str = DEFAULT_DATABASE) -> None:
        self.database = database
        initialise_database(database)

    def save_run(self, run: PipelineRun) -> None:
        """Persist a pipeline run."""
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO pipeline_runs (
                    execution_id, pipeline_name, status, started_at,
                    finished_at, records_processed
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    run.execution_id,
                    run.pipeline_name,
                    run.status,
                    run.started_at.isoformat(),
                    run.finished_at.isoformat() if run.finished_at else None,
                    run.records_processed,
                ),
            )

    def save_step(self, step: PipelineStep) -> None:
        """Persist the current state of a pipeline step.

        A step has one persisted record per pipeline execution. Repeated saves
        update that record so retry lifecycle transitions do not create
        duplicate step rows.
        """
        with sqlite3.connect(self.database) as connection:
            existing = connection.execute(
                """
                SELECT id
                FROM pipeline_steps
                WHERE execution_id = ? AND name = ?
                ORDER BY id
                LIMIT 1
                """,
                (step.execution_id, step.name),
            ).fetchone()

            values = (
                step.status,
                step.started_at.isoformat() if step.started_at else None,
                step.finished_at.isoformat() if step.finished_at else None,
                step.records_processed,
                step.attempts,
                step.error_message,
            )

            if existing is None:
                connection.execute(
                    """
                    INSERT INTO pipeline_steps (
                        execution_id, name, status, started_at, finished_at,
                        records_processed, attempts, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (step.execution_id, step.name, *values),
                )
            else:
                connection.execute(
                    """
                    UPDATE pipeline_steps
                    SET status = ?,
                        started_at = ?,
                        finished_at = ?,
                        records_processed = ?,
                        attempts = ?,
                        error_message = ?
                    WHERE id = ?
                    """,
                    (*values, existing[0]),
                )

    def get_run(self, execution_id: str) -> tuple[object, ...] | None:
        """Return a persisted run by execution ID."""
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute(
                "SELECT * FROM pipeline_runs WHERE execution_id = ?",
                (execution_id,),
            )
            return cursor.fetchone()

    def get_steps(self, execution_id: str) -> list[tuple[object, ...]]:
        """Return persisted steps for a run."""
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute(
                """SELECT execution_id, name, status, started_at,
                    finished_at, records_processed, attempts, error_message
                FROM pipeline_steps
                WHERE execution_id = ?
                ORDER BY id
                """,
                (execution_id,),
            )
            return cursor.fetchall()

    def get_runs(self, pipeline_name: str) -> list[tuple[object, ...]]:
        """Return persisted runs for a pipeline."""
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute(
                "SELECT * FROM pipeline_runs "
                "WHERE pipeline_name = ? ORDER BY started_at",
                (pipeline_name,),
            )
            return cursor.fetchall()

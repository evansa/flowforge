"""Pipeline execution domain model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

PipelineRunStatus = Literal["RUNNING", "SUCCESS", "FAILED"]


@dataclass(slots=True)
class PipelineRun:
    """Represent one execution of a pipeline."""

    pipeline_name: str
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    status: PipelineRunStatus = "RUNNING"
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    records_processed: int = 0

    def complete(self, records_processed: int | None = None) -> None:
        """Mark the execution as successful."""
        self.status = "SUCCESS"
        if records_processed is not None:
            self.records_processed = records_processed
        self.finished_at = datetime.now(UTC)

    def fail(self) -> None:
        """Mark the execution as failed."""
        self.status = "FAILED"
        self.finished_at = datetime.now(UTC)

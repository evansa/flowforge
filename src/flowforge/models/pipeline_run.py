"""Pipeline execution domain model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(slots=True)
class PipelineRun:
    """Represent one execution of a pipeline."""

    pipeline_name: str
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "RUNNING"
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    records_processed: int = 0

    def complete(self) -> None:
        """Mark the execution as successful."""
        self.status = "SUCCESS"
        self.finished_at = datetime.now(UTC)

    def fail(self) -> None:
        """Mark the execution as failed."""
        self.status = "FAILED"
        self.finished_at = datetime.now(UTC)

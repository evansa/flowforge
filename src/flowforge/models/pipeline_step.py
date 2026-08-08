"""Pipeline step execution domain model."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class PipelineStep:
    """Represent the execution state of one pipeline step."""

    execution_id: str
    name: str
    status: str = "RUNNING"
    started_at: datetime | None = None
    finished_at: datetime | None = None
    records_processed: int = 0
    attempts: int = 0
    error_message: str | None = None

    def start(self) -> None:
        """Start the step."""
        self.status = "RUNNING"
        self.started_at = datetime.now(UTC)

    def complete(self) -> None:
        """Mark the step as successful."""
        self.status = "SUCCESS"
        self.finished_at = datetime.now(UTC)

    def fail(self, error: Exception, attempts: int) -> None:
        """Mark the step as failed."""
        self.status = "FAILED"
        self.finished_at = datetime.now(UTC)
        self.error_message = str(error)
        self.attempts = attempts

"""Pipeline step execution domain model."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

StepStatus = Literal["PENDING", "RUNNING", "RETRYING", "SUCCESS", "FAILED"]


@dataclass(slots=True)
class PipelineStep:
    """Represent the execution state of one pipeline step."""

    execution_id: str
    name: str
    status: StepStatus = "PENDING"
    started_at: datetime | None = None
    finished_at: datetime | None = None
    records_processed: int = 0
    attempts: int = 0
    error_message: str | None = None

    def start(self) -> None:
        """Mark the step as running."""
        self.status = "RUNNING"
        self.started_at = datetime.now(UTC)
        self.finished_at = None
        self.error_message = None

    def retry(self, attempts: int, error: Exception) -> None:
        """Mark the step as waiting for another attempt."""
        self.status = "RETRYING"
        self.attempts = attempts
        self.error_message = str(error)

    def complete(self, attempts: int, records_processed: int = 0) -> None:
        """Mark the step as successfully completed."""
        self.status = "SUCCESS"
        self.attempts = attempts
        self.records_processed = records_processed
        self.finished_at = datetime.now(UTC)
        self.error_message = None

    def fail(self, error: Exception, attempts: int) -> None:
        """Mark the step as failed after all retry attempts are exhausted."""
        self.status = "FAILED"
        self.finished_at = datetime.now(UTC)
        self.error_message = str(error)
        self.attempts = attempts

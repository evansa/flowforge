"""Public pipeline definition API."""

from collections.abc import Callable
from typing import Any

from flowforge.core.executor import PipelineExecutor
from flowforge.core.retry import RetryPolicy
from flowforge.models.pipeline_run import PipelineRun
from flowforge.storage.repository import PipelineRepository

StepFunction = Callable[..., Any]


class Pipeline:
    """Define an extract-transform-load pipeline."""

    def __init__(
        self,
        name: str,
        retries: int = 3,
        retry_delay_seconds: float = 1.0,
        database: str = "flowforge.db",
    ) -> None:
        self.name = name
        self.steps: list[tuple[str, StepFunction]] = []
        self.retry_policy = RetryPolicy(
            max_attempts=retries,
            delay_seconds=retry_delay_seconds,
        )
        self.repository = PipelineRepository(database)
        self.executor = PipelineExecutor(
            repository=self.repository,
            retry_policy=self.retry_policy,
        )

    def extract(self) -> Callable[[StepFunction], StepFunction]:
        """Register an extract step."""
        return self.register("EXTRACT")

    def transform(self) -> Callable[[StepFunction], StepFunction]:
        """Register a transform step."""
        return self.register("TRANSFORM")

    def load(self) -> Callable[[StepFunction], StepFunction]:
        """Register a load step."""
        return self.register("LOAD")

    def register(self, name: str) -> Callable[[StepFunction], StepFunction]:
        """Register a named pipeline step."""
        def decorator(function: StepFunction) -> StepFunction:
            self.steps.append((name, function))
            return function

        return decorator

    def run(self) -> PipelineRun:
        """Execute the pipeline."""
        return self.executor.execute(self)

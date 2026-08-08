"""Pipeline execution engine."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from flowforge.core.retry import RetryPolicy
from flowforge.models.pipeline_run import PipelineRun
from flowforge.models.pipeline_step import PipelineStep
from flowforge.observability.logger import get_logger
from flowforge.storage.repository import PipelineRepository

if TYPE_CHECKING:
    from flowforge.core.pipeline import Pipeline


class PipelineExecutor:
    """Execute registered pipeline steps and persist their state."""

    def __init__(
        self,
        repository: PipelineRepository,
        retry_policy: RetryPolicy,
    ) -> None:
        self.repository = repository
        self.retry_policy = retry_policy
        self.logger = get_logger()

    def execute(self, pipeline: "Pipeline") -> PipelineRun:
        """Execute a pipeline and return its completed run."""
        run = PipelineRun(pipeline_name=pipeline.name)
        data: object | None = None

        try:
            for step_name, function in pipeline.steps:
                step = PipelineStep(
                    execution_id=run.execution_id,
                    name=step_name,
                )
                step.start()
                self.logger.info(
                    "pipeline_step_started",
                    pipeline=pipeline.name,
                    execution_id=run.execution_id,
                    step=step_name,
                )

                try:
                    def execute_step(
                        current_step_name: str = step_name,
                        current_function: Callable[..., object] = function,
                        current_data: object | None = data,
                    ) -> object | None:
                        if current_step_name == "EXTRACT":
                            return current_function()
                        return current_function(current_data)

                    data, attempts = self.retry_policy.execute(execute_step)
                    step.attempts = attempts

                    if isinstance(data, list):
                        step.records_processed = len(data)
                        run.records_processed = len(data)

                    step.complete()
                    self.repository.save_step(step)
                    self.logger.info(
                        "pipeline_step_completed",
                        pipeline=pipeline.name,
                        execution_id=run.execution_id,
                        step=step_name,
                        attempts=attempts,
                    )
                except Exception as error:
                    attempts = getattr(step, "attempts", 0)
                    step.fail(
                        error,
                        attempts=max(attempts, self.retry_policy.max_attempts),
                    )
                    self.repository.save_step(step)
                    raise

            run.complete()
        except Exception as error:
            run.fail()
            self.logger.error(
                "pipeline_failed",
                pipeline=pipeline.name,
                execution_id=run.execution_id,
                error=str(error),
            )
            raise
        finally:
            self.repository.save_run(run)

        return run

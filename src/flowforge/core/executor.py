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
        data: object = None
        last_records_processed = 0

        try:
            self.repository.save_run(run)

            for step_name, function in pipeline.steps:
                step = PipelineStep(
                    execution_id=run.execution_id,
                    name=step_name,
                )
                # call pipeline hook before the step executes (no-op by default)
                try:
                    pipeline.before_step(step_name, run.execution_id)
                except Exception:
                    # Hooks should not stop pipeline execution; log and continue.
                    self.logger.warning(
                        "pipeline_before_step_hook_failed",
                        pipeline=pipeline.name,
                        execution_id=run.execution_id,
                        step=step_name,
                    )
                step.start()
                self.repository.save_step(step)

                attempts = 0

                def execute_step(
                    current_step_name: str = step_name,
                    current_function: Callable[..., object] = function,
                    current_data: object = data,
                ) -> object:
                    nonlocal attempts
                    attempts += 1
                    if current_step_name == "EXTRACT":
                        return current_function()
                    return current_function(current_data)

                def handle_retry(
                    attempt: int,
                    _delay: float,
                    error: Exception,
                    current_step: PipelineStep = step,
                    current_step_name: str = step_name,
                    current_pipeline_name: str = pipeline.name,
                    current_execution_id: str = run.execution_id,
                ) -> None:
                    current_step.retry(attempts=attempt, error=error)
                    self.repository.save_step(current_step)
                    self.logger.warning(
                        "pipeline_step_retrying",
                        pipeline=current_pipeline_name,
                        execution_id=current_execution_id,
                        step=current_step_name,
                        attempt=attempt,
                        next_attempt=attempt + 1,
                        error=str(error),
                    )

                try:
                    data, attempts = self.retry_policy.execute(
                        execute_step,
                        on_retry=handle_retry,
                    )
                except Exception as error:
                    step.fail(error, attempts=attempts)
                    self.repository.save_step(step)
                    self.logger.error(
                        "pipeline_step_failed",
                        pipeline=pipeline.name,
                        execution_id=run.execution_id,
                        step=step_name,
                        attempts=attempts,
                        error=str(error),
                    )
                    # notify hook that step failed
                    try:
                        pipeline.after_step(step_name, run.execution_id, result=None, error=error)
                    except Exception:
                        self.logger.warning(
                            "pipeline_after_step_hook_failed",
                            pipeline=pipeline.name,
                            execution_id=run.execution_id,
                            step=step_name,
                        )
                    raise

                records_processed = len(data) if isinstance(data, list) else 0
                if isinstance(data, list):
                    last_records_processed = records_processed

                step.complete(
                    attempts=attempts,
                    records_processed=records_processed,
                )
                self.repository.save_step(step)

                # call after_step hook with the step result
                try:
                    pipeline.after_step(step_name, run.execution_id, result=data, error=None)
                except Exception:
                    self.logger.warning(
                        "pipeline_after_step_hook_failed",
                        pipeline=pipeline.name,
                        execution_id=run.execution_id,
                        step=step_name,
                    )

                self.logger.info(
                    "pipeline_step_completed",
                    pipeline=pipeline.name,
                    execution_id=run.execution_id,
                    step=step_name,
                    attempts=attempts,
                    records_processed=records_processed,
                )

            run.complete(records_processed=last_records_processed)
            return run
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

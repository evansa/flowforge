"""Tests for the FlowForge pipeline API."""

from pathlib import Path
from typing import Any

import pytest

from flowforge import Pipeline
from flowforge.storage.repository import PipelineRepository


def test_pipeline_success(tmp_path: Path) -> None:
    pipeline = Pipeline(
        "test-pipeline",
        retry_delay_seconds=0,
        database=str(tmp_path / "test.db"),
    )

    @pipeline.extract()
    def extract() -> list[dict[str, int]]:
        return [{"id": 1}]

    @pipeline.transform()
    def transform(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{**item, "processed": True} for item in data]

    @pipeline.load()
    def load(data: list[dict[str, Any]]) -> None:
        assert data[0]["processed"] is True

    result = pipeline.run()

    assert result.status == "SUCCESS"
    assert result.records_processed == 1

    repository = PipelineRepository(str(tmp_path / "test.db"))
    assert repository.get_run(result.execution_id) is not None
    assert len(repository.get_steps(result.execution_id)) == 3


def test_pipeline_retries_and_succeeds(tmp_path: Path) -> None:
    attempts = 0
    pipeline = Pipeline(
        "retry-pipeline",
        retries=3,
        retry_delay_seconds=0,
        database=str(tmp_path / "retry.db"),
    )

    @pipeline.extract()
    def extract() -> list[int]:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("temporary failure")
        return [1]

    result = pipeline.run()

    assert result.status == "SUCCESS"
    assert attempts == 3


def test_pipeline_failure_is_persisted(tmp_path: Path) -> None:
    database = str(tmp_path / "failure.db")
    pipeline = Pipeline(
        "failure-pipeline",
        retries=2,
        retry_delay_seconds=0,
        database=database,
    )

    @pipeline.extract()
    def extract() -> list[int]:
        raise ValueError("bad data")

    with pytest.raises(ValueError, match="bad data"):
        pipeline.run()

    repository = PipelineRepository(database)
    runs = repository.get_runs("failure-pipeline")
    assert len(runs) == 1
    assert runs[0][2] == "FAILED"

    steps = repository.get_steps(runs[0][0])
    assert len(steps) == 1
    assert steps[0][2] == "FAILED"
    assert steps[0][7] == "bad data"

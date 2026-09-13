"""Typed result returned by pipeline steps."""

from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(slots=True)
class StepResult(Generic[T]):
    """Represent the result of executing a pipeline step."""

    data: T
    records_processed: int
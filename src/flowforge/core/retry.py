"""Retry policy implementation."""

from collections.abc import Callable
from time import sleep
from typing import TypeVar

T = TypeVar("T")
RetryCallback = Callable[[int, float, Exception], None]


class RetryPolicy:
    """Execute a callable with configurable retry behaviour."""

    def __init__(
        self,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        exponential_backoff: bool = True,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if delay_seconds < 0:
            raise ValueError("delay_seconds cannot be negative")

        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds
        self.exponential_backoff = exponential_backoff

    def execute(
        self,
        function: Callable[[], T],
        on_retry: RetryCallback | None = None,
    ) -> tuple[T, int]:
        """Execute a callable and return its result and attempts used."""
        for attempt in range(1, self.max_attempts + 1):
            try:
                return function(), attempt
            except Exception as error:
                if attempt == self.max_attempts:
                    raise

                delay = (
                    self.delay_seconds * attempt
                    if self.exponential_backoff
                    else self.delay_seconds
                )
                if on_retry is not None:
                    on_retry(attempt, delay, error)
                if delay:
                    sleep(delay)

        raise RuntimeError("Retry policy exited unexpectedly")

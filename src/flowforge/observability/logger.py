"""Structured logging configuration."""

import structlog


def configure_logging() -> None:
    """Configure structured logging for FlowForge."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )


def get_logger() -> structlog.stdlib.BoundLogger:
    """Return a FlowForge logger."""
    return structlog.get_logger()

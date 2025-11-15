"""Structured logging configuration using structlog.

This module sets up structured logging for the application, which makes logs
easier to parse, search, and analyze in production environments like CloudWatch.
"""

import logging
import sys

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application.

    This function should be called once at application startup.
    It configures both structlog and the standard library logging.

    The logging configuration varies based on the log_format setting:
    - "json": Machine-readable JSON format for production
    - "console": Human-readable console format for development
    """
    # Determine processors based on log format
    if settings.log_format == "json":
        # JSON format for production (CloudWatch, etc.)
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console format for development
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,  # type: ignore[arg-type]
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.log_level)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=logging.getLevelName(settings.log_level),
        stream=sys.stdout,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Optional logger name. If not provided, uses the root logger.

    Returns:
        structlog.BoundLogger: A configured logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_created", user_id="123", email="user@example.com")
    """
    return structlog.get_logger(name)


# Pre-configured logger for convenience
logger = get_logger()

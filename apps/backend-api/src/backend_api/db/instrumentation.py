"""Database query instrumentation for performance monitoring."""

import time
from typing import Any

from config.logging import get_logger
from sqlalchemy import Engine, event

logger = get_logger(__name__)


def setup_database_instrumentation(engine: Engine, slow_query_threshold_ms: float = 100.0) -> None:
    """Set up database query instrumentation on the given engine.

    Args:
        engine: SQLAlchemy engine to instrument
        slow_query_threshold_ms: Threshold for slow query warnings (default: 100ms)
    """

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        """Record query start time."""
        context._query_start_time = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        """Log query completion with timing and context."""
        if not hasattr(context, "_query_start_time"):
            return

        # Calculate duration
        duration_ms = (time.perf_counter() - context._query_start_time) * 1000

        # Prepare structured log data
        log_kwargs = {
            "statement": _clean_statement(statement),
            "duration_ms": round(duration_ms, 2),
            "row_count": cursor.rowcount if cursor.rowcount >= 0 else 0,
        }

        # Log at appropriate level with structured data
        if duration_ms >= slow_query_threshold_ms:
            logger.warning("Slow database query detected", slow_query=True, **log_kwargs)
        else:
            logger.debug("Database query executed", **log_kwargs)

    logger.info(
        "Database instrumentation enabled",
        slow_query_threshold_ms=slow_query_threshold_ms,
    )

    @event.listens_for(engine, "handle_error")
    def handle_error(exception_context: Any) -> None:
        """Log database execution errors at error level with context."""
        try:
            statement = exception_context.statement or ""
        except Exception:
            statement = ""

        error_kwargs = {
            "statement": _clean_statement(statement) if statement else "",
            "is_disconnect": getattr(exception_context, "is_disconnect", False),
            "error": str(getattr(exception_context, "original_exception", "")),
        }

        logger.error("Database query failed", **error_kwargs)


def _clean_statement(statement: str, max_length: int = 200) -> str:
    """Clean and truncate SQL statement for logging.

    Args:
        statement: Raw SQL statement
        max_length: Maximum length for truncation

    Returns:
        Cleaned and truncated statement
    """
    # Remove extra whitespace and normalize
    cleaned = " ".join(statement.strip().split())

    # Truncate if too long
    if len(cleaned) > max_length:
        cleaned = cleaned[: max_length - 3] + "..."

    return cleaned

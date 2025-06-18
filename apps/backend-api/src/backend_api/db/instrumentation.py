"""Database query instrumentation for performance monitoring."""

import time
from typing import Any

from sqlalchemy import Engine, event

from config.logging import get_logger
from backend_api.core.request_context import get_request_context_dict, increment_query_count

logger = get_logger(__name__)


def setup_database_instrumentation(engine: Engine, slow_query_threshold_ms: float = 100.0) -> None:
    """Set up database query instrumentation on the given engine.

    Args:
        engine: SQLAlchemy engine to instrument
        slow_query_threshold_ms: Threshold for slow query warnings (default: 100ms)
    """

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(
        conn: Any, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool
    ) -> None:
        """Record query start time."""
        context._query_start_time = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(
        conn: Any, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool
    ) -> None:
        """Log query completion with timing and context."""
        if not hasattr(context, "_query_start_time"):
            return

        ***REMOVED*** Calculate duration
        duration_ms = (time.perf_counter() - context._query_start_time) * 1000

        ***REMOVED*** Get request context
        request_context = get_request_context_dict()

        ***REMOVED*** Increment query count for this request
        query_count = increment_query_count()

        ***REMOVED*** Prepare structured log data
        log_kwargs = {
            "statement": _clean_statement(statement),
            "duration_ms": round(duration_ms, 2),
            "row_count": cursor.rowcount if cursor.rowcount >= 0 else 0,
            "query_count": query_count,
            **request_context,  ***REMOVED*** Include request_id, method, path, user_id
        }

        ***REMOVED*** Log at appropriate level with structured data
        if duration_ms >= slow_query_threshold_ms:
            logger.warning("Slow database query detected", slow_query=True, **log_kwargs)
        else:
            logger.info("Database query executed", **log_kwargs)

    logger.info("Database instrumentation enabled", slow_query_threshold_ms=slow_query_threshold_ms)


def _clean_statement(statement: str, max_length: int = 200) -> str:
    """Clean and truncate SQL statement for logging.

    Args:
        statement: Raw SQL statement
        max_length: Maximum length for truncation

    Returns:
        Cleaned and truncated statement
    """
    ***REMOVED*** Remove extra whitespace and normalize
    cleaned = " ".join(statement.strip().split())

    ***REMOVED*** Truncate if too long
    if len(cleaned) > max_length:
        cleaned = cleaned[: max_length - 3] + "..."

    return cleaned

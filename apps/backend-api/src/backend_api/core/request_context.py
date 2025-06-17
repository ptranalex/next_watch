"""Request context management for tracking database queries per request."""

import contextvars
import uuid
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class RequestContext:
    """Request context information."""

    request_id: str
    method: str
    path: str
    user_id: Optional[str] = None
    query_count: int = 0
    start_time: Optional[float] = None


***REMOVED*** Context variables for tracking request state
_request_context: contextvars.ContextVar[Optional[RequestContext]] = contextvars.ContextVar(
    "request_context", default=None
)


def set_request_context(
    method: str,
    path: str,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    start_time: Optional[float] = None,
) -> RequestContext:
    """Set the current request context.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        user_id: Optional user ID
        request_id: Optional request ID (generates one if not provided)
        start_time: Optional start time

    Returns:
        The created RequestContext
    """
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]  ***REMOVED*** Short UUID for readability

    context = RequestContext(
        request_id=request_id,
        method=method,
        path=path,
        user_id=user_id,
        query_count=0,
        start_time=start_time,
    )

    _request_context.set(context)
    return context


def get_request_context() -> Optional[RequestContext]:
    """Get the current request context.

    Returns:
        Current RequestContext or None if not set
    """
    return _request_context.get()


def increment_query_count() -> int:
    """Increment the query count for the current request.

    Returns:
        New query count
    """
    context = get_request_context()
    if context is not None:
        context.query_count += 1
        return context.query_count
    return 0


def get_request_context_dict() -> Dict[str, Any]:
    """Get request context as a dictionary for logging.

    Returns:
        Dictionary representation of current context
    """
    context = get_request_context()
    if context is not None:
        return asdict(context)
    return {}


def clear_request_context() -> None:
    """Clear the current request context."""
    _request_context.set(None)

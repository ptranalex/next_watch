"""Context-Aware Dependencies for Fast Core.

This module provides FastAPI dependencies that automatically access request context,
trace information, and provide utilities for trace propagation.
"""

from fastapi import Depends, Request

from fast_core.middleware.context import (
    RequestContext,
    get_request_context,
    get_request_id,
    get_trace_headers,
    inject_trace_context,
)


def get_current_request_context() -> RequestContext | None:
    """FastAPI dependency to get current request context.

    Returns:
        Current request context if available
    """
    return get_request_context()


def get_current_request_id() -> str | None:
    """FastAPI dependency to get current request ID.

    Returns:
        Current request ID if available
    """
    return get_request_id()


def get_current_trace_headers() -> dict[str, str]:
    """FastAPI dependency to get current trace headers.

    Returns:
        Dictionary of trace headers for propagation
    """
    return get_trace_headers()


def get_request_id_from_request(request: Request) -> str | None:
    """FastAPI dependency to get request ID from request state.

    Args:
        request: FastAPI request object

    Returns:
        Request ID from request state
    """
    return getattr(request.state, "request_id", None)


def get_context_from_request(request: Request) -> RequestContext | None:
    """FastAPI dependency to get request context from request state.

    Args:
        request: FastAPI request object

    Returns:
        Request context from request state
    """
    return getattr(request.state, "request_context", None)


def require_request_context() -> RequestContext:
    """FastAPI dependency that requires request context to be available.

    Returns:
        Current request context

    Raises:
        RuntimeError: If no request context is available
    """
    context = get_request_context()
    if context is None:
        raise RuntimeError(
            "No request context available. Ensure RequestContextMiddleware is installed."
        )
    return context


def require_request_id() -> str:
    """FastAPI dependency that requires request ID to be available.

    Returns:
        Current request ID

    Raises:
        RuntimeError: If no request ID is available
    """
    request_id = get_request_id()
    if request_id is None:
        raise RuntimeError("No request ID available. Ensure RequestContextMiddleware is installed.")
    return request_id


class TraceContextInjector:
    """Utility class for injecting trace context into headers."""

    def __init__(self, context: RequestContext | None = Depends(get_current_request_context)):
        """Initialize with current request context.

        Args:
            context: Request context from dependency injection
        """
        self.context = context

    def inject_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        """Inject trace context into headers.

        Args:
            headers: Existing headers

        Returns:
            Headers with trace context injected
        """
        return inject_trace_context(headers or {})

    def get_propagation_headers(self) -> dict[str, str]:
        """Get headers for downstream service calls.

        Returns:
            Headers for service-to-service communication
        """
        if self.context:
            return self.context.get_propagation_headers()
        return {}


def get_trace_context_injector() -> TraceContextInjector:
    """FastAPI dependency to get trace context injector.

    Returns:
        TraceContextInjector instance with current context
    """
    return TraceContextInjector()


***REMOVED*** Backwards compatibility aliases
get_request_id_dependency = get_current_request_id
get_trace_headers_dependency = get_current_trace_headers

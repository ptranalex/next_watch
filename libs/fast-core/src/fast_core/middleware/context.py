"""Request Context Middleware for Fast Core.

This module provides centralized request context management with automatic
trace header extraction, OpenTelemetry integration, and context propagation.
"""

import contextvars
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Optional

import structlog
from fastapi import Request
from opentelemetry import propagate, trace
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = structlog.get_logger(__name__)

***REMOVED*** Context variables for request-scoped data
_request_id_context: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
_trace_headers_context: contextvars.ContextVar[dict[str, str]] = contextvars.ContextVar(
    "trace_headers", default={}
)
_request_context: contextvars.ContextVar[Optional["RequestContext"]] = contextvars.ContextVar(
    "request_context", default=None
)


class RequestContext:
    """Request context containing tracing and correlation information."""

    def __init__(
        self,
        request_id: str,
        trace_id: str | None = None,
        span_id: str | None = None,
        parent_span_id: str | None = None,
        trace_headers: dict[str, str] | None = None,
        user_id: str | None = None,
        service_name: str | None = None,
    ):
        """Initialize request context.

        Args:
            request_id: Unique request identifier
            trace_id: OpenTelemetry trace ID
            span_id: OpenTelemetry span ID
            parent_span_id: Parent span ID if exists
            trace_headers: Raw trace headers for propagation
            user_id: Authenticated user ID if available
            service_name: Name of the current service
        """
        self.request_id = request_id
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.trace_headers = trace_headers or {}
        self.user_id = user_id
        self.service_name = service_name

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for logging."""
        return {
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "user_id": self.user_id,
            "service_name": self.service_name,
        }

    def get_propagation_headers(self) -> dict[str, str]:
        """Get headers for downstream service calls."""
        headers = {}

        ***REMOVED*** Always include request ID
        headers["X-Request-ID"] = self.request_id

        ***REMOVED*** Include original trace headers for propagation
        headers.update(self.trace_headers)

        ***REMOVED*** Include user context if available
        if self.user_id:
            headers["X-User-ID"] = self.user_id

        if self.service_name:
            headers["X-Source-Service"] = self.service_name

        return headers


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware for request context management and trace propagation.

    This middleware should be added FIRST (outermost) to ensure request context
    is available to all subsequent middleware and handlers.
    """

    def __init__(
        self,
        app: Any,
        service_name: str | None = None,
        auto_generate_request_id: bool = True,
        extract_user_id: bool = True,
        trace_propagation: bool = True,
        include_w3c_trace_context: bool = True,
        include_b3_headers: bool = True,
        include_jaeger_headers: bool = True,
    ):
        """Initialize request context middleware.

        Args:
            app: ASGI application
            service_name: Name of the current service
            auto_generate_request_id: Automatically generate request ID if not present
            extract_user_id: Extract user ID from headers
            trace_propagation: Enable trace context propagation
            include_w3c_trace_context: Include W3C Trace Context headers
            include_b3_headers: Include B3 (Zipkin) headers
            include_jaeger_headers: Include Jaeger headers
        """
        super().__init__(app)
        self.service_name = service_name or "unknown-service"
        self.auto_generate_request_id = auto_generate_request_id
        self.extract_user_id = extract_user_id
        self.trace_propagation = trace_propagation
        self.include_w3c_trace_context = include_w3c_trace_context
        self.include_b3_headers = include_b3_headers
        self.include_jaeger_headers = include_jaeger_headers

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and set up context.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with trace headers
        """
        ***REMOVED*** Extract or generate request ID
        request_id = self._extract_request_id(request)

        ***REMOVED*** Extract trace headers from incoming request (if trace propagation enabled)
        trace_headers = {}
        if self.trace_propagation:
            trace_headers = self._extract_trace_headers(request)

        ***REMOVED*** Set up OpenTelemetry context from headers (if trace propagation enabled)
        trace_id, span_id, parent_span_id = None, None, None
        if self.trace_propagation:
            carrier = dict(request.headers)
            ctx = propagate.extract(carrier)

            ***REMOVED*** Get trace information from OpenTelemetry context
            trace_id, span_id, parent_span_id = self._get_trace_info(ctx)

        ***REMOVED*** Extract user ID if available (if extraction enabled)
        user_id = None
        if self.extract_user_id:
            user_id = self._extract_user_id(request)

        ***REMOVED*** Create request context
        context = RequestContext(
            request_id=request_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            trace_headers=trace_headers,
            user_id=user_id,
            service_name=self.service_name,
        )

        ***REMOVED*** Set context variables for the request scope
        request_id_token = _request_id_context.set(request_id)
        trace_headers_token = _trace_headers_context.set(trace_headers)
        context_token = _request_context.set(context)

        ***REMOVED*** Store in request state for FastAPI compatibility
        request.state.request_id = request_id
        request.state.request_context = context

        ***REMOVED*** Add request context attributes to current OpenTelemetry span
        if self.trace_propagation:
            self._add_span_attributes(context)
            self._add_span_event(context, request)

        logger.debug(
            "Request context established",
            **context.to_dict(),
            method=request.method,
            path=request.url.path,
        )

        try:
            ***REMOVED*** Process request with OpenTelemetry context
            with trace.use_span(
                trace.get_current_span(ctx) if self.trace_propagation else trace.get_current_span(),
                end_on_exit=False,
            ):
                response = await call_next(request)

            ***REMOVED*** Add trace headers to response
            response.headers.update(self._get_response_headers(context))

            return response

        finally:
            ***REMOVED*** Clean up context variables
            _request_id_context.reset(request_id_token)
            _trace_headers_context.reset(trace_headers_token)
            _request_context.reset(context_token)

    def _extract_request_id(self, request: Request) -> str:
        """Extract or generate request ID.

        Args:
            request: Incoming request

        Returns:
            Request ID string
        """
        ***REMOVED*** Try multiple headers for request ID
        for header in ["X-Request-ID", "X-Correlation-ID", "X-Trace-ID"]:
            request_id = request.headers.get(header)
            if request_id:
                return request_id

        ***REMOVED*** Generate new UUID if no request ID found and auto-generation is enabled
        if self.auto_generate_request_id:
            return str(uuid.uuid4())

        ***REMOVED*** If auto-generation is disabled, return a default
        return "no-request-id"

    def _extract_trace_headers(self, request: Request) -> dict[str, str]:
        """Extract trace propagation headers from request.

        Args:
            request: Incoming request

        Returns:
            Dictionary of trace headers
        """
        trace_headers = {}

        ***REMOVED*** W3C Trace Context headers (primary standard)
        if self.include_w3c_trace_context:
            if "traceparent" in request.headers:
                trace_headers["traceparent"] = request.headers["traceparent"]
            if "tracestate" in request.headers:
                trace_headers["tracestate"] = request.headers["tracestate"]

        ***REMOVED*** B3 headers (Zipkin)
        if self.include_b3_headers:
            b3_headers = [
                "X-B3-TraceId",
                "X-B3-SpanId",
                "X-B3-ParentSpanId",
                "X-B3-Sampled",
                "X-B3-Flags",
                "b3",
            ]
            for header in b3_headers:
                if header in request.headers:
                    trace_headers[header] = request.headers[header]

        ***REMOVED*** Jaeger headers
        if self.include_jaeger_headers:
            jaeger_headers = ["uber-trace-id", "jaeger-debug-id", "jaeger-baggage"]
            for header in jaeger_headers:
                if header in request.headers:
                    trace_headers[header] = request.headers[header]

        ***REMOVED*** Custom request correlation headers (always include for request ID tracking)
        correlation_headers = ["X-Request-ID", "X-Correlation-ID"]
        for header in correlation_headers:
            if header in request.headers:
                trace_headers[header] = request.headers[header]

        return trace_headers

    def _extract_user_id(self, request: Request) -> str | None:
        """Extract user ID from request headers.

        Args:
            request: Incoming request

        Returns:
            User ID if available
        """
        ***REMOVED*** Try common user ID headers
        for header in ["X-User-ID", "X-User", "X-Subject"]:
            user_id = request.headers.get(header)
            if user_id:
                return user_id
        return None

    def _get_trace_info(self, ctx: Any | None = None) -> tuple[str | None, str | None, str | None]:
        """Get trace information from current OpenTelemetry context.

        Returns:
            Tuple of (trace_id, span_id, parent_span_id)
        """
        try:
            span = trace.get_current_span(ctx) if ctx is not None else trace.get_current_span()
            if span and span.is_recording():
                span_context = span.get_span_context()
                trace_id = format(span_context.trace_id, "032x")
                span_id = format(span_context.span_id, "016x")

                ***REMOVED*** Get parent span ID if this is a child span
                parent_span_id = None
                if hasattr(span, "parent") and span.parent:
                    parent_span_id = format(span.parent.span_id, "016x")

                return trace_id, span_id, parent_span_id
        except Exception as e:
            logger.debug("Failed to extract trace info", error=str(e), exc_info=True)

        return None, None, None

    def _add_span_attributes(self, context: RequestContext) -> None:
        """Add request context attributes to the current OpenTelemetry span."""
        try:
            span = trace.get_current_span()
            if span and span.is_recording():
                ***REMOVED*** Add request ID attributes (both formats for compatibility)
                span.set_attribute("request.id", context.request_id)
                span.set_attribute("http.request_id", context.request_id)  ***REMOVED*** Legacy compatibility

                ***REMOVED*** Add user and service context
                if context.user_id:
                    span.set_attribute("user.id", context.user_id)
                if context.service_name:
                    span.set_attribute("service.name", context.service_name)

                logger.debug(
                    "Request ID added to OpenTelemetry span", request_id=context.request_id
                )
        except Exception as e:
            logger.debug("Failed to add span attributes", error=str(e), exc_info=True)

    def _add_span_event(self, context: RequestContext, request: Request) -> None:
        """Add an event to the current OpenTelemetry span with request context."""
        try:
            span = trace.get_current_span()
            if span and span.is_recording():
                ***REMOVED*** Build event attributes, only including non-None values
                event_attributes = {
                    "request.id": context.request_id,
                    "http.method": request.method,
                    "http.url": str(request.url),
                }

                ***REMOVED*** Add optional attributes if available
                if context.trace_id:
                    event_attributes["trace.id"] = context.trace_id
                if context.span_id:
                    event_attributes["span.id"] = context.span_id
                if context.parent_span_id:
                    event_attributes["parent_span.id"] = context.parent_span_id
                if context.user_id:
                    event_attributes["user.id"] = context.user_id
                if context.service_name:
                    event_attributes["service.name"] = context.service_name

                ***REMOVED*** Add span event for better searchability
                span.add_event("request.started", event_attributes)

                logger.debug(
                    "Request started event added to OpenTelemetry span",
                    request_id=context.request_id,
                )
        except Exception as e:
            logger.debug("Failed to add span event", error=str(e), exc_info=True)

    def _get_response_headers(self, context: RequestContext) -> dict[str, str]:
        """Get headers to add to response.

        Args:
            context: Request context

        Returns:
            Dictionary of response headers
        """
        headers = {
            "X-Request-ID": context.request_id,
        }

        if context.trace_id:
            headers["X-Trace-ID"] = context.trace_id

        if context.service_name:
            headers["X-Service"] = context.service_name

        return headers


***REMOVED*** Context accessor functions
def get_request_id() -> str | None:
    """Get request ID from current context.

    Returns:
        Request ID if available
    """
    return _request_id_context.get()


def get_trace_headers() -> dict[str, str]:
    """Get trace headers from current context.

    Returns:
        Dictionary of trace headers for propagation
    """
    return _trace_headers_context.get() or {}


def get_request_context() -> RequestContext | None:
    """Get full request context.

    Returns:
        Request context if available
    """
    return _request_context.get()


def inject_trace_context(headers: dict[str, str]) -> dict[str, str]:
    """Inject trace context into outgoing headers.

    Args:
        headers: Existing headers dictionary

    Returns:
        Headers with trace context injected
    """
    context = get_request_context()
    if context:
        ***REMOVED*** Start with existing headers
        result = dict(headers)
        ***REMOVED*** Add propagation headers
        result.update(context.get_propagation_headers())
        return result
    return headers


def create_child_span_context(name: str, **attributes: Any) -> Any:
    """Create a child span with request context attributes.

    Args:
        name: Span name
        **attributes: Additional span attributes

    Returns:
        Span context manager
    """
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(name)

    ***REMOVED*** Add request context attributes
    context = get_request_context()
    if context and span.is_recording():
        span.set_attribute("request.id", context.request_id)
        if context.user_id:
            span.set_attribute("user.id", context.user_id)
        if context.service_name:
            span.set_attribute("service.name", context.service_name)

        ***REMOVED*** Add custom attributes
        for key, value in attributes.items():
            span.set_attribute(key, value)

    return span

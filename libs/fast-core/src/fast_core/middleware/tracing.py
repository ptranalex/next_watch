"""Tracing middleware for FastAPI applications.

This module provides distributed tracing middleware for FastAPI applications
with OpenTelemetry integration and Tempo backend support.
"""

import os
from typing import Any, Awaitable, Callable, Optional

import structlog
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

***REMOVED*** SQLAlchemy and Redis instrumentors are imported conditionally when needed
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.jaeger import JaegerPropagator

***REMOVED*** TraceContextPropagator not available in this OpenTelemetry version
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = structlog.get_logger(__name__)


class RequestIDTracingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request_id to OpenTelemetry spans.

    This middleware runs first (outermost) and ensures request_id is available
    for all subsequent middleware and handlers. It generates a UUID if none exists
    and adds it to both the OpenTelemetry span and response headers.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        ***REMOVED*** Get existing request_id or generate one if not present
        request_id = getattr(request.state, "request_id", None)
        if not request_id:
            import uuid

            request_id = str(uuid.uuid4())
            request.state.request_id = request_id

        ***REMOVED*** Get current span and add request_id as attribute
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            current_span.set_attribute("request.id", request_id)
            current_span.set_attribute("http.request_id", request_id)

            ***REMOVED*** Also add to span events for better searchability
            current_span.add_event(
                "request.started",
                {
                    "request.id": request_id,
                    "http.method": request.method,
                    "http.url": str(request.url),
                },
            )
            logger.info("Request ID added to OpenTelemetry span", request_id=request_id)

        response = await call_next(request)

        ***REMOVED*** Ensure request_id is in response header
        response.headers["X-Request-ID"] = request_id

        return response


def setup_tracing(app: FastAPI, settings: Any) -> None:
    """Set up OpenTelemetry tracing middleware for FastAPI application.

    Args:
        app: FastAPI application instance
        settings: Application settings containing tracing configuration
    """
    try:
        ***REMOVED*** Get tracing configuration - check if settings itself has tracing config
        ***REMOVED*** or if it has a separate monitoring object
        if hasattr(settings, "enable_tracing"):
            ***REMOVED*** Settings object itself has tracing configuration (e.g., FastAPIConfig with MonitoringConfigMixin)
            monitoring = settings
        else:
            ***REMOVED*** Look for separate monitoring configuration object
            monitoring = getattr(settings, "monitoring", None)

        if not monitoring:
            logger.info("No monitoring configuration, skipping tracing setup")
            return

        if not getattr(monitoring, "enable_tracing", False):
            logger.info("Tracing disabled via configuration")
            return

        service_name = getattr(settings, "service_name", "unknown-service")
        tracing_endpoint = getattr(monitoring, "tracing_endpoint", None)
        sample_rate = getattr(monitoring, "tracing_sample_rate", 0.1)

        logger.info(
            "Setting up OpenTelemetry tracing",
            service_name=service_name,
            endpoint=tracing_endpoint,
            sample_rate=sample_rate,
        )

        ***REMOVED*** Create resource with service information
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": getattr(settings, "version", "1.0.0"),
                "service.namespace": "nextwatch",
                "service.instance.id": f"{service_name}-{os.getpid()}",
                "deployment.environment": getattr(settings, "environment", "development"),
            }
        )

        ***REMOVED*** Set up tracer provider
        tracer_provider = TracerProvider(resource=resource, sampler=_create_sampler(sample_rate))
        trace.set_tracer_provider(tracer_provider)

        ***REMOVED*** Set up span processors
        if tracing_endpoint:
            ***REMOVED*** Production: Export to Tempo via OTLP
            otlp_exporter = OTLPSpanExporter(
                endpoint=tracing_endpoint,
                insecure=True,  ***REMOVED*** Use insecure for internal Docker network
                timeout=10,
            )
            span_processor = BatchSpanProcessor(
                otlp_exporter,
                max_queue_size=2048,
                max_export_batch_size=512,
                export_timeout_millis=30000,
                schedule_delay_millis=5000,
            )
            tracer_provider.add_span_processor(span_processor)
            logger.info("OTLP span exporter configured", endpoint=tracing_endpoint)
        else:
            ***REMOVED*** Development: Console output
            console_exporter = ConsoleSpanExporter()
            span_processor = BatchSpanProcessor(console_exporter)
            tracer_provider.add_span_processor(span_processor)
            logger.info("Console span exporter configured")

        ***REMOVED*** Set up propagators for cross-service tracing
        composite_propagator = CompositePropagator(
            [
                B3MultiFormat(),
                JaegerPropagator(),
            ]
        )
        set_global_textmap(composite_propagator)

        ***REMOVED*** Instrument FastAPI application
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            excluded_urls="/health,/metrics,/ready,/live",
            meter_provider=None,  ***REMOVED*** We handle metrics separately
        )

        ***REMOVED*** Instrument logging for trace correlation
        LoggingInstrumentor().instrument(set_logging_format=True, log_hook=_log_hook)

        ***REMOVED*** Instrument HTTP clients
        HTTPXClientInstrumentor().instrument()

        ***REMOVED*** Instrument database connections if available
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

            SQLAlchemyInstrumentor().instrument()
            logger.info("SQLAlchemy instrumentation enabled")
        except ImportError:
            logger.debug("SQLAlchemy instrumentation not available (sqlalchemy not installed)")
        except Exception as e:
            logger.debug("SQLAlchemy instrumentation not available", error=str(e))

        ***REMOVED*** Instrument Redis if available
        try:
            from opentelemetry.instrumentation.redis import RedisInstrumentor

            RedisInstrumentor().instrument()
            logger.info("Redis instrumentation enabled")
        except ImportError:
            logger.debug("Redis instrumentation not available (redis not installed)")
        except Exception as e:
            logger.debug("Redis instrumentation not available", error=str(e))

        ***REMOVED*** Add request ID tracing middleware
        app.add_middleware(RequestIDTracingMiddleware)
        logger.info("Request ID tracing middleware added")

        logger.info("OpenTelemetry tracing successfully configured")

    except Exception as e:
        logger.error("Failed to setup tracing", error=str(e), exc_info=True)
        ***REMOVED*** Don't fail the application if tracing setup fails
        pass


def _create_sampler(sample_rate: float) -> Any:
    """Create a sampler based on the sample rate.

    Args:
        sample_rate: Sampling rate between 0.0 and 1.0

    Returns:
        Sampler instance
    """
    from opentelemetry.sdk.trace.sampling import (
        ParentBased,
        TraceIdRatioBased,
        ALWAYS_OFF,
        ALWAYS_ON,
    )

    if sample_rate <= 0:
        return ALWAYS_OFF
    elif sample_rate >= 1.0:
        return ALWAYS_ON
    else:
        return ParentBased(root=TraceIdRatioBased(sample_rate))


def _log_hook(span: Any, record: Any) -> None:
    """Custom log hook to add additional trace context to logs.

    Args:
        span: Current span
        record: Log record
    """
    if span and span.is_recording():
        ***REMOVED*** Add service information to log record
        record.service_name = span.resource.attributes.get("service.name", "unknown")
        record.service_version = span.resource.attributes.get("service.version", "unknown")


def get_current_trace_id() -> Optional[str]:
    """Get the current trace ID as a hex string.

    Returns:
        Trace ID as hex string or None if no active trace
    """
    try:
        span = trace.get_current_span()
        if span.is_recording():
            trace_id = span.get_span_context().trace_id
            return format(trace_id, "032x")
    except Exception:
        pass
    return None


def get_current_span_id() -> Optional[str]:
    """Get the current span ID as a hex string.

    Returns:
        Span ID as hex string or None if no active span
    """
    try:
        span = trace.get_current_span()
        if span.is_recording():
            span_id = span.get_span_context().span_id
            return format(span_id, "016x")
    except Exception:
        pass
    return None


def add_span_attributes(**attributes: Any) -> None:
    """Add attributes to the current span.

    Args:
        **attributes: Key-value pairs to add as span attributes
    """
    try:
        span = trace.get_current_span()
        if span.is_recording():
            for key, value in attributes.items():
                span.set_attribute(key, value)
    except Exception as e:
        logger.debug("Failed to add span attributes", error=str(e))


def create_child_span(name: str, **attributes: Any) -> Any:
    """Create a child span context manager.

    Args:
        name: Name of the span
        **attributes: Attributes to add to the span

    Returns:
        Span context manager
    """
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(name)

    ***REMOVED*** Add attributes if provided
    if attributes and span.is_recording():
        for key, value in attributes.items():
            span.set_attribute(key, value)

    return span

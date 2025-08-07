"""Prometheus metrics collection for FastAPI applications.

This module provides comprehensive metrics collection using Prometheus,
including HTTP request metrics, custom business metrics, and health monitoring.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Union, Sequence, Awaitable

import structlog
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class MetricsRegistry:
    """Central registry for Prometheus metrics."""

    def __init__(self, service_name: str, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics registry.

        Args:
            service_name: Name of the service (e.g., 'bff-api', 'backend-api')
            registry: Custom registry (defaults to prometheus default)
        """
        self.service_name = service_name
        self.registry = registry or REGISTRY
        self._metrics: Dict[str, Any] = {}

        ***REMOVED*** Standard HTTP metrics
        self._setup_http_metrics()

        ***REMOVED*** Service info metric
        self._setup_service_info()

        ***REMOVED*** Health status metrics
        self._setup_health_metrics()

        logger.info(f"Metrics registry initialized for service: {service_name}")

    def _setup_http_metrics(self) -> None:
        """Set up standard HTTP request metrics."""
        ***REMOVED*** HTTP request duration histogram
        self.http_request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint", "status_code", "service"],
            registry=self.registry,
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        )

        ***REMOVED*** HTTP request count
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code", "service"],
            registry=self.registry,
        )

        ***REMOVED*** HTTP requests in progress
        self.http_requests_in_progress = Gauge(
            "http_requests_in_progress",
            "HTTP requests currently being processed",
            ["service"],
            registry=self.registry,
        )

        ***REMOVED*** HTTP request size
        self.http_request_size_bytes = Histogram(
            "http_request_size_bytes",
            "HTTP request size in bytes",
            ["service"],
            registry=self.registry,
        )

        ***REMOVED*** HTTP response size
        self.http_response_size_bytes = Histogram(
            "http_response_size_bytes",
            "HTTP response size in bytes",
            ["service"],
            registry=self.registry,
        )

    def _setup_service_info(self) -> None:
        """Set up service information metric."""
        self.service_info = Info("service_info", "Service information", registry=self.registry)

        ***REMOVED*** Set basic service info
        self.service_info.info(
            {
                "service_name": self.service_name,
                "version": "1.0.0",  ***REMOVED*** This should come from settings
            }
        )

    def _setup_health_metrics(self) -> None:
        """Set up health status metrics.

        Creates standard health metrics following industry best practices
        used by Spring Boot, Kubernetes, and other platforms.
        """
        ***REMOVED*** Overall service health status gauge
        ***REMOVED*** Values: 3=healthy, 2=degraded, 1=unhealthy, 0=unknown
        self.service_health_status = Gauge(
            "service_health_status",
            "Overall service health status (3=healthy, 2=degraded, 1=unhealthy, 0=unknown)",
            ["service"],
            registry=self.registry,
        )

        ***REMOVED*** Individual health check statuses
        self.health_check_status = Gauge(
            "health_check_status",
            "Individual health check status (1=healthy, 0=unhealthy)",
            ["service", "check_name", "check_category"],
            registry=self.registry,
        )

        ***REMOVED*** Health check response times
        self.health_check_duration = Histogram(
            "health_check_duration_seconds",
            "Health check execution duration",
            ["service", "check_name", "check_category"],
            registry=self.registry,
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        ***REMOVED*** Health check execution counts
        self.health_check_total = Counter(
            "health_check_executions_total",
            "Total health check executions",
            ["service", "check_name", "check_category", "status"],
            registry=self.registry,
        )

        ***REMOVED*** Initialize overall service health to unknown
        self.service_health_status.labels(service=self.service_name).set(0)

        logger.info("Health status metrics initialized")

    def update_service_health_status(self, status: str) -> None:
        """Update the overall service health status metric.

        Args:
            status: Health status ("healthy", "degraded", "unhealthy", "unknown")
        """
        status_values = {"healthy": 3, "degraded": 2, "unhealthy": 1, "unknown": 0}

        value = status_values.get(status.lower(), 0)
        self.service_health_status.labels(service=self.service_name).set(value)

        logger.debug(f"Updated service health status: {status} (value={value})")

    def update_health_check_status(
        self,
        check_name: str,
        check_category: str,
        is_healthy: bool,
        duration_seconds: Optional[float] = None,
    ) -> None:
        """Update individual health check metrics.

        Args:
            check_name: Name of the health check
            check_category: Category of the health check (critical, important, informational)
            is_healthy: Whether the check passed
            duration_seconds: Check execution duration in seconds
        """
        labels = {
            "service": self.service_name,
            "check_name": check_name,
            "check_category": check_category.lower(),
        }

        ***REMOVED*** Update status gauge
        self.health_check_status.labels(**labels).set(1 if is_healthy else 0)

        ***REMOVED*** Update duration histogram if provided
        if duration_seconds is not None:
            self.health_check_duration.labels(**labels).observe(duration_seconds)

        ***REMOVED*** Update execution counter
        status = "healthy" if is_healthy else "unhealthy"
        count_labels = {**labels, "status": status}
        self.health_check_total.labels(**count_labels).inc()

        logger.debug(f"Updated health check metrics: {check_name} = {status}")

    def create_counter(
        self,
        name: str,
        description: str,
        labels: Optional[List[str]] = None,
    ) -> Counter:
        """Create a counter metric.

        Args:
            name: Metric name
            description: Metric description
            labels: Label names

        Returns:
            Counter metric
        """
        labels = labels or []
        if "service" not in labels:
            labels.append("service")

        counter = Counter(name, description, labels, registry=self.registry)
        self._metrics[name] = counter
        return counter

    def create_gauge(
        self,
        name: str,
        description: str,
        labels: Optional[List[str]] = None,
    ) -> Gauge:
        """Create a gauge metric.

        Args:
            name: Metric name
            description: Metric description
            labels: Label names

        Returns:
            Gauge metric
        """
        labels = labels or []
        if "service" not in labels:
            labels.append("service")

        gauge = Gauge(name, description, labels, registry=self.registry)
        self._metrics[name] = gauge
        return gauge

    def create_histogram(
        self,
        name: str,
        description: str,
        labels: Optional[List[str]] = None,
        buckets: Optional[Sequence[float]] = None,
    ) -> Histogram:
        """Create a histogram metric.

        Args:
            name: Metric name
            description: Metric description
            labels: Label names
            buckets: Histogram buckets

        Returns:
            Histogram metric
        """
        labels = labels or []
        if "service" not in labels:
            labels.append("service")

        ***REMOVED*** Handle buckets parameter properly
        if buckets is not None:
            histogram = Histogram(
                name, description, labels, registry=self.registry, buckets=buckets
            )
        else:
            histogram = Histogram(name, description, labels, registry=self.registry)
        self._metrics[name] = histogram
        return histogram

    def get_metric(self, name: str) -> Optional[Any]:
        """Get a metric by name.

        Args:
            name: Metric name

        Returns:
            Metric instance or None
        """
        return self._metrics.get(name)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics."""

    def __init__(
        self,
        app: Any,
        metrics_registry: MetricsRegistry,
        exclude_paths: Optional[Set[str]] = None,
        exclude_methods: Optional[Set[str]] = None,
    ):
        """Initialize Prometheus middleware.

        Args:
            app: FastAPI application
            metrics_registry: Metrics registry instance
            exclude_paths: Paths to exclude from metrics
            exclude_methods: HTTP methods to exclude from metrics
        """
        super().__init__(app)
        self.metrics = metrics_registry
        self.exclude_paths = exclude_paths or {"/metrics", "/health", "/docs", "/openapi.json"}
        self.exclude_methods = exclude_methods or {"OPTIONS"}

        logger.info("Prometheus middleware initialized")

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and collect metrics."""
        ***REMOVED*** Skip excluded paths and methods
        if request.url.path in self.exclude_paths or request.method in self.exclude_methods:
            return await call_next(request)

        ***REMOVED*** Track request in progress
        self.metrics.http_requests_in_progress.labels(service=self.metrics.service_name).inc()

        start_time = time.time()

        try:
            ***REMOVED*** Process request
            response = await call_next(request)

            ***REMOVED*** Calculate duration
            duration = time.time() - start_time

            ***REMOVED*** Get route pattern for consistent labeling
            endpoint = self._get_route_pattern(request)

            ***REMOVED*** Record metrics
            labels = {
                "method": request.method,
                "endpoint": endpoint,
                "status_code": str(response.status_code),
                "service": self.metrics.service_name,
            }

            self.metrics.http_request_duration.labels(**labels).observe(duration)
            self.metrics.http_requests_total.labels(**labels).inc()

            ***REMOVED*** Record request/response sizes if available
            try:
                ***REMOVED*** Get request size from headers
                content_length = request.headers.get("content-length")
                if content_length:
                    self.metrics.http_request_size_bytes.labels(
                        service=self.metrics.service_name
                    ).observe(int(content_length))
            except (ValueError, TypeError):
                pass

            try:
                ***REMOVED*** Get response size from headers or body
                response_size = None
                if hasattr(response, "headers") and "content-length" in response.headers:
                    response_size = int(response.headers["content-length"])
                elif hasattr(response, "body") and response.body:
                    response_size = len(response.body)

                if response_size:
                    self.metrics.http_response_size_bytes.labels(
                        service=self.metrics.service_name
                    ).observe(response_size)
            except (ValueError, TypeError, AttributeError):
                pass

            return response

        except Exception as e:
            ***REMOVED*** Record error metrics
            duration = time.time() - start_time
            endpoint = self._get_route_pattern(request)

            labels = {
                "method": request.method,
                "endpoint": endpoint,
                "status_code": "500",
                "service": self.metrics.service_name,
            }

            self.metrics.http_request_duration.labels(**labels).observe(duration)
            self.metrics.http_requests_total.labels(**labels).inc()

            raise

        finally:
            ***REMOVED*** Decrement in-progress counter
            self.metrics.http_requests_in_progress.labels(service=self.metrics.service_name).dec()

    def _get_route_pattern(self, request: Request) -> str:
        """Extract route pattern from request.

        Args:
            request: Starlette request

        Returns:
            Route pattern or path
        """
        ***REMOVED*** Try to get the route pattern from FastAPI
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope["route"]
            if hasattr(route, "path"):
                return str(route.path)

        ***REMOVED*** Fallback to URL path
        return request.url.path


def track_operation(
    metrics_registry: MetricsRegistry,
    operation_name: str,
    labels: Optional[Dict[str, str]] = None,
) -> Callable[[F], F]:
    """Decorator to track custom operation metrics.

    Args:
        metrics_registry: Metrics registry
        operation_name: Name of the operation
        labels: Additional labels

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        ***REMOVED*** Create operation metrics if they don't exist
        duration_metric_name = f"{operation_name}_duration_seconds"
        count_metric_name = f"{operation_name}_total"
        error_metric_name = f"{operation_name}_errors_total"

        if not metrics_registry.get_metric(duration_metric_name):
            metrics_registry.create_histogram(
                duration_metric_name,
                f"Duration of {operation_name} operations",
                ["status", "service"],
            )

        if not metrics_registry.get_metric(count_metric_name):
            metrics_registry.create_counter(
                count_metric_name,
                f"Total {operation_name} operations",
                ["status", "service"],
            )

        if not metrics_registry.get_metric(error_metric_name):
            metrics_registry.create_counter(
                error_metric_name,
                f"Total {operation_name} errors",
                ["error_type", "service"],
            )

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            operation_labels = {"service": metrics_registry.service_name}
            if labels:
                operation_labels.update(labels)

            try:
                result = await func(*args, **kwargs)

                ***REMOVED*** Record success metrics
                duration = time.time() - start_time
                success_labels = {**operation_labels, "status": "success"}

                ***REMOVED*** Safely access metrics with null checks
                duration_metric = metrics_registry.get_metric(duration_metric_name)
                count_metric = metrics_registry.get_metric(count_metric_name)

                if duration_metric:
                    duration_metric.labels(**success_labels).observe(duration)
                if count_metric:
                    count_metric.labels(**success_labels).inc()

                return result

            except Exception as e:
                ***REMOVED*** Record error metrics
                duration = time.time() - start_time
                error_labels = {**operation_labels, "status": "error"}
                error_type_labels = {**operation_labels, "error_type": type(e).__name__}

                ***REMOVED*** Safely access metrics with null checks
                duration_metric = metrics_registry.get_metric(duration_metric_name)
                count_metric = metrics_registry.get_metric(count_metric_name)
                error_metric = metrics_registry.get_metric(error_metric_name)

                if duration_metric:
                    duration_metric.labels(**error_labels).observe(duration)
                if count_metric:
                    count_metric.labels(**error_labels).inc()
                if error_metric:
                    error_metric.labels(**error_type_labels).inc()

                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            operation_labels = {"service": metrics_registry.service_name}
            if labels:
                operation_labels.update(labels)

            try:
                result = func(*args, **kwargs)

                ***REMOVED*** Record success metrics
                duration = time.time() - start_time
                success_labels = {**operation_labels, "status": "success"}

                ***REMOVED*** Safely access metrics with null checks
                duration_metric = metrics_registry.get_metric(duration_metric_name)
                count_metric = metrics_registry.get_metric(count_metric_name)

                if duration_metric:
                    duration_metric.labels(**success_labels).observe(duration)
                if count_metric:
                    count_metric.labels(**success_labels).inc()

                return result

            except Exception as e:
                ***REMOVED*** Record error metrics
                duration = time.time() - start_time
                error_labels = {**operation_labels, "status": "error"}
                error_type_labels = {**operation_labels, "error_type": type(e).__name__}

                ***REMOVED*** Safely access metrics with null checks
                duration_metric = metrics_registry.get_metric(duration_metric_name)
                count_metric = metrics_registry.get_metric(count_metric_name)
                error_metric = metrics_registry.get_metric(error_metric_name)

                if duration_metric:
                    duration_metric.labels(**error_labels).observe(duration)
                if count_metric:
                    count_metric.labels(**error_labels).inc()
                if error_metric:
                    error_metric.labels(**error_type_labels).inc()

                raise

        ***REMOVED*** Return appropriate wrapper based on function type
        if hasattr(func, "__code__") and "async" in func.__code__.co_flags.__class__.__name__:
            return async_wrapper  ***REMOVED*** type: ignore
        else:
            return sync_wrapper  ***REMOVED*** type: ignore

    return decorator


def setup_metrics_endpoint(
    app: FastAPI, metrics_registry: MetricsRegistry, path: str = "/metrics"
) -> None:
    """Add Prometheus metrics endpoint to FastAPI app.

    Args:
        app: FastAPI application
        metrics_registry: Metrics registry
        path: Metrics endpoint path
    """

    @app.get(
        path,
        tags=["Monitoring"],
        summary="Prometheus metrics",
        description="Prometheus metrics endpoint for monitoring",
        include_in_schema=False,  ***REMOVED*** Don't include in OpenAPI docs
    )
    async def metrics_endpoint() -> Response:
        """Prometheus metrics endpoint."""
        return Response(
            generate_latest(metrics_registry.registry),
            media_type=CONTENT_TYPE_LATEST,
        )

    logger.info(f"Metrics endpoint registered at: {path}")


***REMOVED*** Global metrics registry instance - will be initialized by applications
_metrics_registry: Optional[MetricsRegistry] = None


def get_metrics_registry() -> Optional[MetricsRegistry]:
    """Get the global metrics registry."""
    return _metrics_registry


def initialize_metrics(service_name: str) -> MetricsRegistry:
    """Initialize global metrics registry.

    This function implements a singleton pattern to ensure only one
    metrics registry exists per process. If called multiple times,
    it returns the existing registry.

    Args:
        service_name: Name of the service

    Returns:
        Metrics registry instance

    Raises:
        ValueError: If service_name is empty or invalid
    """
    global _metrics_registry

    ***REMOVED*** Validate input
    if not service_name or not isinstance(service_name, str):
        raise ValueError("service_name must be a non-empty string")

    ***REMOVED*** If registry already exists, return it
    if _metrics_registry is not None:
        logger.debug(
            f"Metrics registry already initialized for service: {_metrics_registry.service_name}"
        )
        return _metrics_registry

    ***REMOVED*** Create new registry only if one doesn't exist
    try:
        _metrics_registry = MetricsRegistry(service_name)
        logger.info(f"Initialized new metrics registry for service: {service_name}")
        return _metrics_registry
    except Exception as e:
        logger.error(f"Failed to initialize metrics registry for service {service_name}: {e}")
        raise

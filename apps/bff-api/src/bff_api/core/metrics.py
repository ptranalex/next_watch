"""BFF-specific metrics and monitoring.

This module provides custom metrics for the BFF API service,
including business logic metrics and service health tracking.
"""

import re
from typing import Dict, Optional, Any, Callable, TypeVar

from fast_core.monitoring.metrics import MetricsRegistry, get_metrics_registry, track_operation
from config.logging import get_logger

***REMOVED*** Type variable for function decorators
F = TypeVar("F", bound=Callable[..., Any])

logger = get_logger(__name__)


def normalize_endpoint_for_metrics(endpoint: str) -> str:
    """Simple endpoint normalization for client-side service calls.

    This is the industry-standard approach: replace numeric IDs with generic placeholders
    to prevent cardinality explosion while keeping the solution maintainable.

    Only used when we don't have access to FastAPI's route patterns.

    Args:
        endpoint: Raw endpoint path (e.g., "/api/v1/movies/123", "/api/v1/genres/12")

    Returns:
        Normalized endpoint path (e.g., "/api/v1/movies/{id}", "/api/v1/genres/{id}")
    """
    if not endpoint:
        return endpoint

    ***REMOVED*** Remove query parameters (they cause cardinality explosion)
    endpoint = endpoint.split("?")[0]

    ***REMOVED*** Split into parts and replace numeric IDs with generic placeholder
    parts = endpoint.split("/")
    normalized_parts = []

    for part in parts:
        if part.isdigit():
            ***REMOVED*** Replace numeric IDs with generic placeholder
            normalized_parts.append("{id}")
        else:
            ***REMOVED*** Keep non-numeric parts as-is
            normalized_parts.append(part)

    return "/".join(normalized_parts)


class BFFMetrics:
    """BFF-specific metrics collection."""

    def __init__(self, metrics_registry: Optional[MetricsRegistry] = None):
        """Initialize BFF metrics.

        Args:
            metrics_registry: Metrics registry (uses global if None)
        """
        self.registry = metrics_registry or get_metrics_registry()
        if not self.registry:
            logger.warning("No metrics registry available, metrics will be disabled")
            return

        self._setup_custom_metrics()
        logger.info("BFF metrics initialized")

    def _setup_custom_metrics(self) -> None:
        """Set up BFF-specific custom metrics."""
        if not self.registry:
            return

        ***REMOVED*** Service aggregation metrics
        self.service_calls = self.registry.create_counter(
            "bff_service_calls_total",
            "Total calls to backend services",
            ["service_name", "endpoint", "status", "service"],
        )

        self.service_response_time = self.registry.create_histogram(
            "bff_service_response_time_seconds",
            "Response time for backend service calls",
            ["service_name", "endpoint", "service"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        )

        ***REMOVED*** Cache metrics
        self.cache_operations = self.registry.create_counter(
            "bff_cache_operations_total",
            "Total cache operations",
            ["operation", "cache_name", "status", "service"],
        )

        self.cache_hit_rate = self.registry.create_gauge(
            "bff_cache_hit_rate", "Cache hit rate percentage", ["cache_name", "service"]
        )

        ***REMOVED*** Business logic metrics
        self.movie_requests = self.registry.create_counter(
            "bff_movie_requests_total",
            "Total movie-related requests",
            ["operation", "status", "service"],
        )

        self.search_requests = self.registry.create_counter(
            "bff_search_requests_total",
            "Total search requests",
            ["search_type", "status", "service"],
        )

        self.aggregation_operations = self.registry.create_histogram(
            "bff_aggregation_duration_seconds",
            "Time spent aggregating data from multiple services",
            ["operation", "service_count", "service"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
        )

        ***REMOVED*** User engagement metrics
        self.user_actions = self.registry.create_counter(
            "bff_user_actions_total", "Total user actions", ["action_type", "service"]
        )

        ***REMOVED*** Error tracking metrics
        self.service_errors = self.registry.create_counter(
            "bff_service_errors_total",
            "Total service errors encountered",
            ["service_name", "error_type", "service"],
        )

    def record_service_call(
        self, service_name: str, endpoint: str, status: str, response_time: float
    ) -> None:
        """Record a backend service call.

        Args:
            service_name: Name of the backend service
            endpoint: Service endpoint called
            status: Call status (success, error, timeout)
            response_time: Response time in seconds
        """
        if not self.registry:
            return

        ***REMOVED*** Normalize endpoint to prevent cardinality explosion
        normalized_endpoint = normalize_endpoint_for_metrics(endpoint)

        service_labels = {
            "service_name": service_name,
            "endpoint": normalized_endpoint,
            "status": status,
            "service": self.registry.service_name,
        }

        self.service_calls.labels(**service_labels).inc()

        time_labels = {
            "service_name": service_name,
            "endpoint": normalized_endpoint,
            "service": self.registry.service_name,
        }
        self.service_response_time.labels(**time_labels).observe(response_time)

    def record_cache_operation(self, operation: str, cache_name: str, status: str) -> None:
        """Record a cache operation.

        Args:
            operation: Cache operation (get, set, delete, clear)
            cache_name: Name of the cache
            status: Operation status (hit, miss, error)
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "cache_name": cache_name,
            "status": status,
            "service": self.registry.service_name,
        }
        self.cache_operations.labels(**labels).inc()

    def update_cache_hit_rate(self, cache_name: str, hit_rate: float) -> None:
        """Update cache hit rate.

        Args:
            cache_name: Name of the cache
            hit_rate: Hit rate as percentage (0-100)
        """
        if not self.registry:
            return

        labels = {"cache_name": cache_name, "service": self.registry.service_name}
        self.cache_hit_rate.labels(**labels).set(hit_rate)

    def record_movie_request(self, operation: str, status: str) -> None:
        """Record a movie-related request.

        Args:
            operation: Movie operation (list, detail, recommendations, etc.)
            status: Request status (success, error)
        """
        if not self.registry:
            return

        labels = {"operation": operation, "status": status, "service": self.registry.service_name}
        self.movie_requests.labels(**labels).inc()

    def record_search_request(self, search_type: str, status: str) -> None:
        """Record a search request.

        Args:
            search_type: Type of search (movie, actor, genre, etc.)
            status: Request status (success, error)
        """
        if not self.registry:
            return

        labels = {
            "search_type": search_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.search_requests.labels(**labels).inc()

    def record_aggregation_operation(
        self, operation: str, service_count: int, duration: float
    ) -> None:
        """Record a data aggregation operation.

        Args:
            operation: Aggregation operation name
            service_count: Number of services involved
            duration: Operation duration in seconds
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "service_count": str(service_count),
            "service": self.registry.service_name,
        }
        self.aggregation_operations.labels(**labels).observe(duration)

    def record_user_action(self, action_type: str) -> None:
        """Record a user action.

        Args:
            action_type: Type of user action (view, like, rate, etc.)
        """
        if not self.registry:
            return

        labels = {"action_type": action_type, "service": self.registry.service_name}
        self.user_actions.labels(**labels).inc()

    def record_service_error(self, service_name: str, error_type: str) -> None:
        """Record a service error.

        Args:
            service_name: Name of the service with error
            error_type: Type of error (timeout, connection, http_error, etc.)
        """
        if not self.registry:
            return

        labels = {
            "service_name": service_name,
            "error_type": error_type,
            "service": self.registry.service_name,
        }
        self.service_errors.labels(**labels).inc()


***REMOVED*** Global BFF metrics instance
_bff_metrics: Optional[BFFMetrics] = None


def get_bff_metrics() -> Optional[BFFMetrics]:
    """Get the global BFF metrics instance."""
    return _bff_metrics


def initialize_bff_metrics() -> Optional[BFFMetrics]:
    """Initialize global BFF metrics instance.

    This function implements a singleton pattern to ensure only one
    BFF metrics instance exists per process. If called multiple times,
    it returns the existing instance.

    Returns:
        BFFMetrics instance if successful, None if metrics registry unavailable
    """
    global _bff_metrics

    ***REMOVED*** If BFF metrics already exists, return it
    if _bff_metrics is not None:
        logger.debug("BFF metrics already initialized")
        return _bff_metrics

    ***REMOVED*** Create new BFF metrics instance
    try:
        _bff_metrics = BFFMetrics()

        ***REMOVED*** Return None if the metrics instance couldn't initialize properly
        if _bff_metrics and not _bff_metrics.registry:
            _bff_metrics = None
            logger.warning("Failed to initialize BFF metrics - no metrics registry available")
        else:
            logger.info("BFF metrics initialized successfully")

        return _bff_metrics
    except Exception as e:
        logger.error(f"Failed to initialize BFF metrics: {e}")
        _bff_metrics = None
        return None


***REMOVED*** Decorator for tracking BFF operations
def track_bff_operation(
    operation_name: str, labels: Optional[Dict[str, str]] = None
) -> Callable[[F], F]:
    """Decorator to track BFF-specific operations.

    Args:
        operation_name: Name of the operation
        labels: Additional labels for the operation

    Returns:
        Decorator function
    """
    registry = get_metrics_registry()
    if not registry:

        def noop_decorator(func: F) -> F:
            return func

        return noop_decorator

    return track_operation(registry, f"bff_{operation_name}", labels)


***REMOVED*** Example usage decorators for common BFF operations
def track_movie_operation(func: F) -> F:
    """Track movie-related operations."""
    return track_bff_operation("movie_operation")(func)


def track_search_operation(func: F) -> F:
    """Track search operations."""
    return track_bff_operation("search_operation")(func)


def track_aggregation_operation(func: F) -> F:
    """Track data aggregation operations."""
    return track_bff_operation("aggregation_operation")(func)


def track_cache_operation(func: F) -> F:
    """Track cache operations."""
    return track_bff_operation("cache_operation")(func)

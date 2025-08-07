"""Recommendation-specific metrics and monitoring.

This module provides custom metrics for the Recommendation API service,
including recommendation generation, vector similarity searches, caching performance,
ML API integration, and personalization algorithms.
"""

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
        endpoint: Raw endpoint path (e.g., "/api/v1/recommendations/123", "/api/v1/similar/456")

    Returns:
        Normalized endpoint path (e.g., "/api/v1/recommendations/{id}", "/api/v1/similar/{id}")
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


class RecommendationMetrics:
    """Recommendation-specific metrics collection."""

    def __init__(self, metrics_registry: Optional[MetricsRegistry] = None):
        """Initialize Recommendation metrics."""
        self.registry = metrics_registry or get_metrics_registry()
        if not self.registry:
            logger.warning("No metrics registry available, metrics will be disabled")
            return

        self._setup_custom_metrics()
        logger.info("Recommendation metrics initialized")

    def _setup_custom_metrics(self) -> None:
        """Set up Recommendation-specific custom metrics."""
        if not self.registry:
            return

        ***REMOVED*** Recommendation operation metrics
        self.recommendation_requests = self.registry.create_counter(
            "recommendation_requests_total",
            "Total recommendation requests by type and status",
            ["recommendation_type", "status", "service"],
        )

        self.recommendation_duration = self.registry.create_histogram(
            "recommendation_duration_seconds",
            "Duration of recommendation operations",
            ["recommendation_type", "status", "service"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
        )

        self.recommendation_results_count = self.registry.create_histogram(
            "recommendation_results_count",
            "Number of recommendations returned",
            ["recommendation_type", "service"],
            buckets=(0, 5, 10, 20, 50, 100, 200),
        )

        ***REMOVED*** Vector similarity metrics
        self.vector_operations = self.registry.create_counter(
            "recommendation_vector_operations_total",
            "Vector database operations",
            ["operation", "status", "service"],
        )

        self.vector_search_duration = self.registry.create_histogram(
            "recommendation_vector_search_duration_seconds",
            "Duration of vector similarity searches",
            ["search_type", "service"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
        )

        ***REMOVED*** Cache performance metrics
        self.cache_operations = self.registry.create_counter(
            "recommendation_cache_operations_total",
            "Cache operations by type and result",
            ["cache_type", "operation", "result", "service"],
        )

        self.cache_hit_ratio = self.registry.create_gauge(
            "recommendation_cache_hit_ratio",
            "Cache hit ratio by recommendation type",
            ["recommendation_type", "service"],
        )

        ***REMOVED*** ML API integration metrics
        self.ml_api_requests = self.registry.create_counter(
            "recommendation_ml_api_requests_total",
            "ML API requests by operation and status",
            ["operation", "status", "service"],
        )

        self.ml_api_duration = self.registry.create_histogram(
            "recommendation_ml_api_duration_seconds",
            "Duration of ML API calls",
            ["operation", "service"],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
        )

        ***REMOVED*** Backend API integration metrics
        self.backend_api_requests = self.registry.create_counter(
            "recommendation_backend_api_requests_total",
            "Backend API requests by operation and status",
            ["operation", "status", "service"],
        )

        self.backend_api_duration = self.registry.create_histogram(
            "recommendation_backend_api_duration_seconds",
            "Duration of backend API calls",
            ["operation", "service"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
        )

        ***REMOVED*** Filter usage metrics
        self.recommendation_filters_usage = self.registry.create_counter(
            "recommendation_filters_usage_total",
            "Usage of recommendation filters",
            ["filter_type", "filter_value", "service"],
        )

    def record_recommendation_request(
        self, recommendation_type: str, status: str, duration: float, results_count: int
    ) -> None:
        """Record a recommendation request."""
        if not self.registry:
            return

        request_labels = {
            "recommendation_type": recommendation_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.recommendation_requests.labels(**request_labels).inc()

        duration_labels = {
            "recommendation_type": recommendation_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.recommendation_duration.labels(**duration_labels).observe(duration)

        if status == "success":
            results_labels = {
                "recommendation_type": recommendation_type,
                "service": self.registry.service_name,
            }
            self.recommendation_results_count.labels(**results_labels).observe(results_count)

    def record_vector_operation(self, operation: str, status: str, duration: float = 0.0) -> None:
        """Record a vector database operation."""
        if not self.registry:
            return

        operation_labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.vector_operations.labels(**operation_labels).inc()

        if operation.startswith("search") and duration > 0:
            search_type = operation.replace("search_", "")
            duration_labels = {
                "search_type": search_type,
                "service": self.registry.service_name,
            }
            self.vector_search_duration.labels(**duration_labels).observe(duration)

    def record_cache_operation(self, cache_type: str, operation: str, result: str) -> None:
        """Record a cache operation."""
        if not self.registry:
            return

        labels = {
            "cache_type": cache_type,
            "operation": operation,
            "result": result,
            "service": self.registry.service_name,
        }
        self.cache_operations.labels(**labels).inc()

    def record_ml_api_request(self, operation: str, status: str, duration: float) -> None:
        """Record an ML API request."""
        if not self.registry:
            return

        request_labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.ml_api_requests.labels(**request_labels).inc()

        duration_labels = {
            "operation": operation,
            "service": self.registry.service_name,
        }
        self.ml_api_duration.labels(**duration_labels).observe(duration)

    def record_backend_api_request(self, operation: str, status: str, duration: float) -> None:
        """Record a backend API request."""
        if not self.registry:
            return

        request_labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.backend_api_requests.labels(**request_labels).inc()

        duration_labels = {
            "operation": operation,
            "service": self.registry.service_name,
        }
        self.backend_api_duration.labels(**duration_labels).observe(duration)

    def record_recommendation_filter_usage(self, filter_type: str, filter_value: str) -> None:
        """Record usage of recommendation filters."""
        if not self.registry:
            return

        labels = {
            "filter_type": filter_type,
            "filter_value": filter_value,
            "service": self.registry.service_name,
        }
        self.recommendation_filters_usage.labels(**labels).inc()

    def record_cache_hit_ratio(self, recommendation_type: str, hit_ratio: float) -> None:
        """Record cache hit ratio for a recommendation type."""
        if not self.registry:
            return

        labels = {
            "recommendation_type": recommendation_type,
            "service": self.registry.service_name,
        }
        self.cache_hit_ratio.labels(**labels).set(hit_ratio)


***REMOVED*** Global Recommendation metrics instance
_recommendation_metrics: Optional[RecommendationMetrics] = None


def get_recommendation_metrics() -> Optional[RecommendationMetrics]:
    """Get the global Recommendation metrics instance."""
    return _recommendation_metrics


def initialize_recommendation_metrics() -> Optional[RecommendationMetrics]:
    """Initialize global Recommendation metrics instance."""
    global _recommendation_metrics
    _recommendation_metrics = RecommendationMetrics()
    if _recommendation_metrics and not _recommendation_metrics.registry:
        _recommendation_metrics = None
    return _recommendation_metrics


***REMOVED*** Decorators for tracking Recommendation operations
def track_recommendation_operation(
    operation_name: str, labels: Optional[Dict[str, str]] = None
) -> Callable[[F], F]:
    """Decorator to track Recommendation-specific operations."""
    registry = get_metrics_registry()
    if not registry:

        def noop_decorator(func: F) -> F:
            return func

        return noop_decorator

    return track_operation(registry, f"recommendation_{operation_name}", labels)


def track_personalized_recommendation(func: F) -> F:
    """Track personalized recommendation operations."""
    return track_recommendation_operation("personalized")(func)


def track_similar_recommendation(func: F) -> F:
    """Track similar movie recommendation operations."""
    return track_recommendation_operation("similar")(func)


def track_popular_recommendation(func: F) -> F:
    """Track popular recommendation operations."""
    return track_recommendation_operation("popular")(func)


def track_trending_recommendation(func: F) -> F:
    """Track trending recommendation operations.."""
    return track_recommendation_operation("trending")(func)

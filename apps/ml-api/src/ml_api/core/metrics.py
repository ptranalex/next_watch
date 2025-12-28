"""ML API metrics collection using Prometheus.

This module provides ML-specific metrics for monitoring embedding service performance.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

try:
    import prometheus_client
except ImportError:
    prometheus_client = None  ***REMOVED*** type: ignore[assignment]
    PROMETHEUS_AVAILABLE = False
else:
    PROMETHEUS_AVAILABLE = True

from config.logging import get_logger

logger = get_logger(__name__)

BATCH_SIZE_SMALL_MAX = 10
BATCH_SIZE_MEDIUM_MAX = 50


def normalize_endpoint_for_metrics(endpoint: str) -> str:
    """Simple endpoint normalization for client-side service calls.

    This is the industry-standard approach: replace numeric IDs with generic placeholders
    to prevent cardinality explosion while keeping the solution maintainable.

    Only used when we don't have access to FastAPI's route patterns.

    Args:
        endpoint: Raw endpoint path (e.g., "/embeddings/123", "/models/456")

    Returns:
        Normalized endpoint path (e.g., "/embeddings/{id}", "/models/{id}")
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


class MLMetrics:
    """ML API metrics collector."""

    def __init__(self, registry: Any | None = None) -> None:
        """Initialize ML metrics.

        Args:
            registry: Prometheus registry (optional)
        """
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus client not available, metrics disabled")
            self.registry = registry
            return

        ***REMOVED*** At this point, prometheus_client is installed and the symbols are available.
        assert prometheus_client is not None
        self.registry = registry or prometheus_client.CollectorRegistry()

        ***REMOVED*** Embedding-specific metrics
        self.embedding_requests = prometheus_client.Counter(
            "ml_embedding_requests_total",
            "Total number of embedding requests",
            ["model", "batch_size_range"],
            registry=self.registry,
        )

        self.embedding_duration = prometheus_client.Histogram(
            "ml_embedding_duration_seconds",
            "Time spent generating embeddings",
            ["model"],
            registry=self.registry,
        )

        self.embedding_batch_size = prometheus_client.Histogram(
            "ml_embedding_batch_size",
            "Size of embedding batches processed",
            ["model"],
            buckets=(1, 5, 10, 20, 50, 100, 200, 500),
            registry=self.registry,
        )

        ***REMOVED*** Model metrics
        self.model_load_duration = prometheus_client.Histogram(
            "ml_model_load_duration_seconds",
            "Time spent loading ML models",
            ["model"],
            registry=self.registry,
        )

        self.model_memory_usage = prometheus_client.Gauge(
            "ml_model_memory_usage_bytes",
            "Memory usage of loaded models",
            ["model"],
            registry=self.registry,
        )

        ***REMOVED*** Error metrics
        self.embedding_errors = prometheus_client.Counter(
            "ml_embedding_errors_total",
            "Total number of embedding errors",
            ["model", "error_type"],
            registry=self.registry,
        )

        logger.info("ML metrics initialized with Prometheus")

    def record_embedding_request(self, model: str, batch_size: int) -> None:
        """Record an embedding request."""
        if not PROMETHEUS_AVAILABLE:
            return

        ***REMOVED*** Categorize batch size
        if batch_size == 1:
            batch_range = "single"
        elif batch_size <= BATCH_SIZE_SMALL_MAX:
            batch_range = "small"
        elif batch_size <= BATCH_SIZE_MEDIUM_MAX:
            batch_range = "medium"
        else:
            batch_range = "large"

        self.embedding_requests.labels(model=model, batch_size_range=batch_range).inc()

    def record_embedding_duration(self, model: str, duration: float) -> None:
        """Record embedding processing duration."""
        if PROMETHEUS_AVAILABLE:
            self.embedding_duration.labels(model=model).observe(duration)

    def record_embedding_batch_size(self, model: str, batch_size: int) -> None:
        """Record embedding batch size."""
        if PROMETHEUS_AVAILABLE:
            self.embedding_batch_size.labels(model=model).observe(batch_size)

    def record_model_load_duration(self, model: str, duration: float) -> None:
        """Record model loading duration."""
        if PROMETHEUS_AVAILABLE:
            self.model_load_duration.labels(model=model).observe(duration)

    def set_model_memory_usage(self, model: str, memory_bytes: float) -> None:
        """Set model memory usage."""
        if PROMETHEUS_AVAILABLE:
            self.model_memory_usage.labels(model=model).set(memory_bytes)

    def record_embedding_error(self, model: str, error_type: str) -> None:
        """Record an embedding error."""
        if PROMETHEUS_AVAILABLE:
            self.embedding_errors.labels(model=model, error_type=error_type).inc()


def initialize_ml_metrics(registry: Any | None = None) -> MLMetrics | None:
    """Initialize ML metrics.

    Args:
        registry: Prometheus registry (optional)

    Returns:
        ML metrics instance or None if metrics not available
    """
    if not PROMETHEUS_AVAILABLE:
        logger.warning("Prometheus client not available, ML metrics disabled")
        return None

    if registry is not None:
        return MLMetrics(registry=registry)
    return _get_cached_ml_metrics()


def get_ml_metrics() -> MLMetrics | None:
    """Get the global ML metrics instance.

    Returns:
        ML metrics instance or None if not initialized
    """
    return initialize_ml_metrics()


@lru_cache(maxsize=1)
def _get_cached_ml_metrics() -> MLMetrics:
    metrics = MLMetrics()
    logger.info("ML metrics initialized")
    return metrics

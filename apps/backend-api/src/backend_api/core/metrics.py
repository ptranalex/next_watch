"""Backend-specific metrics and monitoring.

This module provides custom metrics for the Backend API service,
including database operations, movie CRUD operations, and data integrity tracking.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from config.logging import get_logger
from fast_core.monitoring.metrics import (
    MetricsRegistry,
    get_metrics_registry,
    track_operation,
)

# Type variable for function decorators
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

    # Remove query parameters (they cause cardinality explosion)
    endpoint = endpoint.split("?")[0]

    # Split into parts and replace numeric IDs with generic placeholder
    parts = endpoint.split("/")
    normalized_parts: list[str] = []

    for part in parts:
        if part.isdigit():
            # Replace numeric IDs with generic placeholder
            normalized_parts.append("{id}")
        else:
            # Keep non-numeric parts as-is
            normalized_parts.append(part)

    return "/".join(normalized_parts)


class BackendMetrics:
    """Backend-specific metrics collection."""

    def __init__(self, metrics_registry: MetricsRegistry | None = None):
        """Initialize Backend metrics.

        Args:
            metrics_registry: Metrics registry (uses global if None)
        """
        self.registry = metrics_registry or get_metrics_registry()
        if not self.registry:
            logger.warning("No metrics registry available, metrics will be disabled")
            return

        self._setup_custom_metrics()
        logger.info("Backend metrics initialized")

    def _setup_custom_metrics(self) -> None:
        """Set up Backend-specific custom metrics."""
        if not self.registry:
            return

        # Database operation metrics
        self.database_operations = self.registry.create_counter(
            "backend_database_operations_total",
            "Total database operations",
            ["operation", "table", "status", "service"],
        )

        self.database_query_duration = self.registry.create_histogram(
            "backend_database_query_duration_seconds",
            "Duration of database queries",
            ["operation", "table", "service"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        self.database_connection_pool = self.registry.create_gauge(
            "backend_database_connections_active",
            "Active database connections",
            ["service"],
        )

        # Movie operation metrics
        self.movie_operations = self.registry.create_counter(
            "backend_movie_operations_total",
            "Total movie-related operations",
            ["operation", "status", "service"],
        )

        self.movie_search_operations = self.registry.create_histogram(
            "backend_movie_search_duration_seconds",
            "Duration of movie search operations",
            ["search_type", "filters_count", "service"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
        )

        self.movie_bulk_operations = self.registry.create_histogram(
            "backend_movie_bulk_operation_duration_seconds",
            "Duration of bulk movie operations",
            ["operation", "batch_size_range", "service"],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0),
        )

        # Actor and cast operation metrics
        self.actor_operations = self.registry.create_counter(
            "backend_actor_operations_total",
            "Total actor-related operations",
            ["operation", "status", "service"],
        )

        self.cast_retrieval_operations = self.registry.create_histogram(
            "backend_cast_retrieval_duration_seconds",
            "Duration of cast retrieval operations",
            ["movie_type", "cast_size_range", "service"],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
        )

        # User collection operations
        self.user_collection_operations = self.registry.create_counter(
            "backend_user_collection_operations_total",
            "Total user collection operations",
            ["operation", "collection_type", "status", "service"],
        )

        self.user_collection_size = self.registry.create_histogram(
            "backend_user_collection_size",
            "Size of user collections",
            ["collection_type", "service"],
            buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500),
        )

        # Data integrity metrics
        self.data_validation_errors = self.registry.create_counter(
            "backend_data_validation_errors_total",
            "Total data validation errors",
            ["validation_type", "entity_type", "service"],
        )

        self.data_consistency_checks = self.registry.create_counter(
            "backend_data_consistency_checks_total",
            "Total data consistency checks performed",
            ["check_type", "status", "service"],
        )

        # Genre and metadata operations
        self.genre_operations = self.registry.create_counter(
            "backend_genre_operations_total",
            "Total genre-related operations",
            ["operation", "status", "service"],
        )

        self.metadata_operations = self.registry.create_counter(
            "backend_metadata_operations_total",
            "Total metadata operations",
            ["metadata_type", "operation", "status", "service"],
        )

        # Performance optimization metrics
        self.query_optimization = self.registry.create_histogram(
            "backend_query_optimization_impact_seconds",
            "Time saved through query optimization",
            ["optimization_type", "service"],
            buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

        self.pagination_performance = self.registry.create_histogram(
            "backend_pagination_performance_seconds",
            "Performance of paginated queries",
            ["page_size_range", "total_count_range", "service"],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
        )

    def record_database_operation(
        self, operation: str, table: str, status: str, duration: float
    ) -> None:
        """Record a database operation.

        Args:
            operation: Database operation (select, insert, update, delete)
            table: Database table name
            status: Operation status (success, error, timeout)
            duration: Operation duration in seconds
        """
        if not self.registry:
            return

        operation_labels = {
            "operation": operation,
            "table": table,
            "status": status,
            "service": self.registry.service_name,
        }
        self.database_operations.labels(**operation_labels).inc()

        duration_labels = {
            "operation": operation,
            "table": table,
            "service": self.registry.service_name,
        }
        self.database_query_duration.labels(**duration_labels).observe(duration)

    def record_movie_operation(self, operation: str, status: str) -> None:
        """Record a movie-related operation.

        Args:
            operation: Movie operation (list, detail, search, bulk, create, update)
            status: Operation status (success, error)
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.movie_operations.labels(**labels).inc()

    def record_movie_search(self, search_type: str, filters_count: int, duration: float) -> None:
        """Record a movie search operation.

        Args:
            search_type: Type of search (title, advanced, filter_only)
            filters_count: Number of filters applied
            duration: Search duration in seconds
        """
        if not self.registry:
            return

        # Categorize filter count for better grouping
        if filters_count == 0:
            filters_category = "none"
        elif filters_count <= 2:
            filters_category = "1-2"
        elif filters_count <= 5:
            filters_category = "3-5"
        else:
            filters_category = "6+"

        labels = {
            "search_type": search_type,
            "filters_count": filters_category,
            "service": self.registry.service_name,
        }
        self.movie_search_operations.labels(**labels).observe(duration)

    def record_bulk_operation(self, operation: str, batch_size: int, duration: float) -> None:
        """Record a bulk operation.

        Args:
            operation: Bulk operation type (bulk_get, bulk_update)
            batch_size: Number of items in the batch
            duration: Operation duration in seconds
        """
        if not self.registry:
            return

        # Categorize batch size for better metrics grouping
        if batch_size <= 10:
            size_range = "1-10"
        elif batch_size <= 50:
            size_range = "11-50"
        elif batch_size <= 100:
            size_range = "51-100"
        elif batch_size <= 500:
            size_range = "101-500"
        else:
            size_range = "500+"

        labels = {
            "operation": operation,
            "batch_size_range": size_range,
            "service": self.registry.service_name,
        }
        self.movie_bulk_operations.labels(**labels).observe(duration)

    def record_actor_operation(self, operation: str, status: str) -> None:
        """Record an actor-related operation.

        Args:
            operation: Actor operation (list, detail, search, movies)
            status: Operation status (success, error)
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.actor_operations.labels(**labels).inc()

    def record_cast_retrieval(self, movie_type: str, cast_size: int, duration: float) -> None:
        """Record cast retrieval operation.

        Args:
            movie_type: Type of movie (feature, tv, documentary)
            cast_size: Number of cast members retrieved
            duration: Retrieval duration in seconds
        """
        if not self.registry:
            return

        # Categorize cast size
        if cast_size <= 5:
            size_range = "1-5"
        elif cast_size <= 15:
            size_range = "6-15"
        elif cast_size <= 30:
            size_range = "16-30"
        else:
            size_range = "30+"

        labels = {
            "movie_type": movie_type,
            "cast_size_range": size_range,
            "service": self.registry.service_name,
        }
        self.cast_retrieval_operations.labels(**labels).observe(duration)

    def record_user_collection_operation(
        self,
        operation: str,
        collection_type: str,
        status: str,
        collection_size: int | None = None,
    ) -> None:
        """Record user collection operation.

        Args:
            operation: Collection operation (create, read, update, delete, add_item, remove_item)
            collection_type: Type of collection (watchlist, favorites, custom)
            status: Operation status (success, error)
            collection_size: Current size of the collection (optional)
        """
        if not self.registry:
            return

        operation_labels = {
            "operation": operation,
            "collection_type": collection_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.user_collection_operations.labels(**operation_labels).inc()

        # Record collection size if provided
        if collection_size is not None:
            size_labels = {
                "collection_type": collection_type,
                "service": self.registry.service_name,
            }
            self.user_collection_size.labels(**size_labels).observe(collection_size)

    def record_data_validation_error(self, validation_type: str, entity_type: str) -> None:
        """Record a data validation error.

        Args:
            validation_type: Type of validation (schema, business_rule, foreign_key)
            entity_type: Type of entity (movie, actor, user, collection)
        """
        if not self.registry:
            return

        labels = {
            "validation_type": validation_type,
            "entity_type": entity_type,
            "service": self.registry.service_name,
        }
        self.data_validation_errors.labels(**labels).inc()

    def record_data_consistency_check(self, check_type: str, status: str) -> None:
        """Record a data consistency check.

        Args:
            check_type: Type of consistency check (referential_integrity, duplicate_detection)
            status: Check status (passed, failed, error)
        """
        if not self.registry:
            return

        labels = {
            "check_type": check_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.data_consistency_checks.labels(**labels).inc()

    def record_genre_operation(self, operation: str, status: str) -> None:
        """Record a genre-related operation.

        Args:
            operation: Genre operation (list, movies_by_genre)
            status: Operation status (success, error)
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.genre_operations.labels(**labels).inc()

    def record_metadata_operation(self, metadata_type: str, operation: str, status: str) -> None:
        """Record a metadata operation.

        Args:
            metadata_type: Type of metadata (trailers, ratings, reviews)
            operation: Metadata operation (retrieve, update, validate)
            status: Operation status (success, error, not_found)
        """
        if not self.registry:
            return

        labels = {
            "metadata_type": metadata_type,
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.metadata_operations.labels(**labels).inc()

    def record_pagination_performance(
        self, page_size: int, total_count: int, duration: float
    ) -> None:
        """Record pagination performance.

        Args:
            page_size: Size of the page
            total_count: Total number of items
            duration: Query duration in seconds
        """
        if not self.registry:
            return

        # Categorize page size
        if page_size <= 20:
            page_size_range = "1-20"
        elif page_size <= 50:
            page_size_range = "21-50"
        elif page_size <= 100:
            page_size_range = "51-100"
        else:
            page_size_range = "100+"

        # Categorize total count
        if total_count <= 100:
            total_count_range = "1-100"
        elif total_count <= 1000:
            total_count_range = "101-1000"
        elif total_count <= 10000:
            total_count_range = "1001-10000"
        else:
            total_count_range = "10000+"

        labels = {
            "page_size_range": page_size_range,
            "total_count_range": total_count_range,
            "service": self.registry.service_name,
        }
        self.pagination_performance.labels(**labels).observe(duration)

    def update_database_connection_pool(self, active_connections: int) -> None:
        """Update database connection pool metric.

        Args:
            active_connections: Number of active database connections
        """
        if not self.registry:
            return

        labels = {"service": self.registry.service_name}
        self.database_connection_pool.labels(**labels).set(active_connections)


# Global Backend metrics instance
_backend_metrics: BackendMetrics | None = None


def get_backend_metrics() -> BackendMetrics | None:
    """Get the global Backend metrics instance."""
    return _backend_metrics


def initialize_backend_metrics() -> BackendMetrics | None:
    """Initialize global Backend metrics instance.

    Returns:
        BackendMetrics instance if successful, None if metrics registry unavailable
    """
    global _backend_metrics
    _backend_metrics = BackendMetrics()
    # Return None if the metrics instance couldn't initialize properly
    if _backend_metrics and not _backend_metrics.registry:
        _backend_metrics = None
    return _backend_metrics


# Decorator for tracking Backend operations
def track_backend_operation(
    operation_name: str, labels: dict[str, str] | None = None
) -> Callable[[F], F]:
    """Decorator to track Backend-specific operations.

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

    return track_operation(registry, f"backend_{operation_name}", labels)


# Example usage decorators for common Backend operations
def track_movie_operation[T: Callable[..., Any]](func: T) -> T:
    """Track movie-related operations."""
    return track_backend_operation("movie_operation")(func)


def track_database_operation[T: Callable[..., Any]](func: T) -> T:
    """Track database operations."""
    return track_backend_operation("database_operation")(func)


def track_search_operation[T: Callable[..., Any]](func: T) -> T:
    """Track search operations."""
    return track_backend_operation("search_operation")(func)


def track_user_collection_operation[T: Callable[..., Any]](func: T) -> T:
    """Track user collection operations."""
    return track_backend_operation("user_collection_operation")(func)


def track_actor_operation[T: Callable[..., Any]](func: T) -> T:
    """Track actor-related operations."""
    return track_backend_operation("actor_operation")(func)


def track_bulk_operation[T: Callable[..., Any]](func: T) -> T:
    """Track bulk operations."""
    return track_backend_operation("bulk_operation")(func)

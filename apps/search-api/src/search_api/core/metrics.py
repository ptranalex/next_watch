"""Search-specific metrics and monitoring.

This module provides custom metrics for the Search API service,
including Redis operations, search performance, suggestion analytics, and user behavior tracking.
"""

from typing import Dict, Optional, Any, Callable, TypeVar
from fast_core.monitoring.metrics import MetricsRegistry, get_metrics_registry, track_operation
from config.logging import get_logger

***REMOVED*** Type variable for function decorators
F = TypeVar("F", bound=Callable[..., Any])

logger = get_logger(__name__)


class SearchMetrics:
    """Search-specific metrics collection."""

    def __init__(self, metrics_registry: Optional[MetricsRegistry] = None):
        """Initialize Search metrics.

        Args:
            metrics_registry: Metrics registry (uses global if None)
        """
        self.registry = metrics_registry or get_metrics_registry()
        if not self.registry:
            logger.warning("No metrics registry available, metrics will be disabled")
            return

        self._setup_custom_metrics()
        logger.info("Search metrics initialized")

    def _setup_custom_metrics(self) -> None:
        """Set up Search-specific custom metrics."""
        if not self.registry:
            return

        ***REMOVED*** Redis operation metrics
        self.redis_operations = self.registry.create_counter(
            "search_redis_operations_total",
            "Total Redis operations",
            ["operation", "key_type", "status", "service"],
        )

        self.redis_query_duration = self.registry.create_histogram(
            "search_redis_query_duration_seconds",
            "Duration of Redis queries",
            ["operation", "key_type", "service"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
        )

        self.redis_connection_pool = self.registry.create_gauge(
            "search_redis_connections_active",
            "Active Redis connections",
            ["service"],
        )

        self.redis_key_count = self.registry.create_gauge(
            "search_redis_keys_total",
            "Total number of Redis keys by type",
            ["key_type", "service"],
        )

        ***REMOVED*** Search operation metrics
        self.search_requests = self.registry.create_counter(
            "search_requests_total",
            "Total search requests by type and status",
            ["search_type", "status", "service"],
        )

        self.search_duration = self.registry.create_histogram(
            "search_duration_seconds",
            "Duration of search operations",
            ["search_type", "result_count_range", "service"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
        )

        self.search_results_count = self.registry.create_histogram(
            "search_results_count",
            "Number of results returned by search operations",
            ["search_type", "service"],
            buckets=(0, 1, 5, 10, 25, 50, 100, 250, 500, 1000),
        )

        ***REMOVED*** Suggestion engine metrics
        self.suggestion_requests = self.registry.create_counter(
            "search_suggestion_requests_total",
            "Total suggestion requests by type and status",
            ["suggestion_type", "status", "service"],
        )

        self.suggestion_duration = self.registry.create_histogram(
            "search_suggestion_duration_seconds",
            "Duration of suggestion operations",
            ["suggestion_type", "query_length_range", "service"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
        )

        self.suggestion_cache_hits = self.registry.create_counter(
            "search_suggestion_cache_hits_total",
            "Suggestion cache hit/miss counts",
            ["cache_type", "status", "service"],
        )

        ***REMOVED*** Query analytics metrics
        self.query_patterns = self.registry.create_counter(
            "search_query_patterns_total",
            "Query pattern analysis",
            ["pattern_type", "query_length_range", "service"],
        )

        self.popular_queries = self.registry.create_counter(
            "search_popular_queries_total",
            "Popular search queries (anonymized)",
            ["query_category", "service"],
        )

        self.search_filters_usage = self.registry.create_counter(
            "search_filters_usage_total",
            "Usage of search filters",
            ["filter_type", "filter_value_range", "service"],
        )

        ***REMOVED*** Performance optimization metrics
        self.fuzzy_search_fallbacks = self.registry.create_counter(
            "search_fuzzy_fallbacks_total",
            "Number of times fuzzy search was used as fallback",
            ["search_type", "original_results_range", "service"],
        )

        self.pagination_patterns = self.registry.create_counter(
            "search_pagination_patterns_total",
            "Pagination usage patterns",
            ["page_range", "limit_range", "service"],
        )

        self.index_optimization_impact = self.registry.create_histogram(
            "search_index_optimization_seconds",
            "Time saved through index optimization",
            ["optimization_type", "service"],
            buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

        ***REMOVED*** Entity-specific metrics
        self.entity_search_performance = self.registry.create_histogram(
            "search_entity_performance_seconds",
            "Performance by entity type",
            ["entity_type", "complexity", "service"],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
        )

        self.entity_popularity = self.registry.create_counter(
            "search_entity_popularity_total",
            "Popularity of different entity types in searches",
            ["entity_type", "service"],
        )

        ***REMOVED*** User behavior metrics
        self.search_session_patterns = self.registry.create_counter(
            "search_session_patterns_total",
            "Search session behavior patterns",
            ["pattern_type", "session_length_range", "service"],
        )

        self.suggestion_conversion_rate = self.registry.create_counter(
            "search_suggestion_conversions_total",
            "How often suggestions lead to actual searches",
            ["suggestion_type", "conversion_status", "service"],
        )

        ***REMOVED*** Error and quality metrics
        self.search_quality_metrics = self.registry.create_counter(
            "search_quality_metrics_total",
            "Search quality indicators",
            ["quality_metric", "quality_range", "service"],
        )

        self.search_errors = self.registry.create_counter(
            "search_errors_total",
            "Search operation errors by type",
            ["error_type", "search_type", "service"],
        )

    def record_redis_operation(
        self, operation: str, key_type: str, status: str, duration: float
    ) -> None:
        """Record a Redis operation.

        Args:
            operation: Redis operation (get, set, delete, scan, zrange)
            key_type: Type of Redis key (suggestion, entity, search_result)
            status: Operation status (success, error, timeout)
            duration: Operation duration in seconds
        """
        if not self.registry:
            return

        operation_labels = {
            "operation": operation,
            "key_type": key_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.redis_operations.labels(**operation_labels).inc()

        duration_labels = {
            "operation": operation,
            "key_type": key_type,
            "service": self.registry.service_name,
        }
        self.redis_query_duration.labels(**duration_labels).observe(duration)

    def record_search_request(
        self, search_type: str, status: str, duration: float, result_count: int
    ) -> None:
        """Record a search request.

        Args:
            search_type: Type of search (movie, all_entities, suggestion)
            status: Request status (success, error, timeout)
            duration: Search duration in seconds
            result_count: Number of results returned
        """
        if not self.registry:
            return

        ***REMOVED*** Record search request
        request_labels = {
            "search_type": search_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.search_requests.labels(**request_labels).inc()

        ***REMOVED*** Categorize result count for better grouping
        if result_count == 0:
            result_range = "0"
        elif result_count <= 10:
            result_range = "1-10"
        elif result_count <= 50:
            result_range = "11-50"
        elif result_count <= 100:
            result_range = "51-100"
        else:
            result_range = "100+"

        ***REMOVED*** Record search duration
        duration_labels = {
            "search_type": search_type,
            "result_count_range": result_range,
            "service": self.registry.service_name,
        }
        self.search_duration.labels(**duration_labels).observe(duration)

        ***REMOVED*** Record result count
        result_labels = {
            "search_type": search_type,
            "service": self.registry.service_name,
        }
        self.search_results_count.labels(**result_labels).observe(result_count)

    def record_suggestion_request(
        self, suggestion_type: str, status: str, duration: float, query_length: int
    ) -> None:
        """Record a suggestion request.

        Args:
            suggestion_type: Type of suggestion (basic, text, ranked)
            status: Request status (success, error, timeout)
            duration: Suggestion duration in seconds
            query_length: Length of the search query
        """
        if not self.registry:
            return

        ***REMOVED*** Record suggestion request
        request_labels = {
            "suggestion_type": suggestion_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.suggestion_requests.labels(**request_labels).inc()

        ***REMOVED*** Categorize query length
        if query_length <= 2:
            length_range = "1-2"
        elif query_length <= 5:
            length_range = "3-5"
        elif query_length <= 10:
            length_range = "6-10"
        else:
            length_range = "10+"

        ***REMOVED*** Record suggestion duration
        duration_labels = {
            "suggestion_type": suggestion_type,
            "query_length_range": length_range,
            "service": self.registry.service_name,
        }
        self.suggestion_duration.labels(**duration_labels).observe(duration)

    def record_cache_operation(self, cache_type: str, status: str) -> None:
        """Record a cache operation.

        Args:
            cache_type: Type of cache (suggestion, ranking, entity)
            status: Cache status (hit, miss, error)
        """
        if not self.registry:
            return

        labels = {
            "cache_type": cache_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.suggestion_cache_hits.labels(**labels).inc()

    def record_query_pattern(self, pattern_type: str, query_length: int) -> None:
        """Record query pattern analysis.

        Args:
            pattern_type: Pattern type (exact_match, partial_match, fuzzy_match)
            query_length: Length of the query
        """
        if not self.registry:
            return

        ***REMOVED*** Categorize query length
        if query_length <= 3:
            length_range = "1-3"
        elif query_length <= 7:
            length_range = "4-7"
        elif query_length <= 15:
            length_range = "8-15"
        else:
            length_range = "15+"

        labels = {
            "pattern_type": pattern_type,
            "query_length_range": length_range,
            "service": self.registry.service_name,
        }
        self.query_patterns.labels(**labels).inc()

    def record_popular_query(self, query_category: str) -> None:
        """Record popular query categories (anonymized).

        Args:
            query_category: Category of query (movie_title, actor_name, genre, etc.)
        """
        if not self.registry:
            return

        labels = {
            "query_category": query_category,
            "service": self.registry.service_name,
        }
        self.popular_queries.labels(**labels).inc()

    def record_filter_usage(self, filter_type: str, filter_value: Any) -> None:
        """Record search filter usage.

        Args:
            filter_type: Type of filter (genre, year, rating, actor)
            filter_value: Value of the filter (categorized for privacy)
        """
        if not self.registry:
            return

        ***REMOVED*** Categorize filter values to avoid high cardinality
        if filter_type == "year":
            if filter_value and isinstance(filter_value, int):
                if filter_value >= 2020:
                    value_range = "2020+"
                elif filter_value >= 2010:
                    value_range = "2010-2019"
                elif filter_value >= 2000:
                    value_range = "2000-2009"
                else:
                    value_range = "pre-2000"
            else:
                value_range = "none"
        elif filter_type == "rating":
            if filter_value and isinstance(filter_value, (int, float)):
                if filter_value >= 8.0:
                    value_range = "8.0+"
                elif filter_value >= 6.0:
                    value_range = "6.0-7.9"
                else:
                    value_range = "below-6.0"
            else:
                value_range = "none"
        else:
            value_range = "applied" if filter_value else "none"

        labels = {
            "filter_type": filter_type,
            "filter_value_range": value_range,
            "service": self.registry.service_name,
        }
        self.search_filters_usage.labels(**labels).inc()

    def record_fuzzy_fallback(self, search_type: str, original_results: int) -> None:
        """Record when fuzzy search was used as fallback.

        Args:
            search_type: Type of search operation
            original_results: Number of results from exact search
        """
        if not self.registry:
            return

        ***REMOVED*** Categorize original results
        if original_results == 0:
            results_range = "0"
        elif original_results <= 5:
            results_range = "1-5"
        else:
            results_range = "5+"

        labels = {
            "search_type": search_type,
            "original_results_range": results_range,
            "service": self.registry.service_name,
        }
        self.fuzzy_search_fallbacks.labels(**labels).inc()

    def record_pagination_usage(self, page: int, limit: int) -> None:
        """Record pagination patterns.

        Args:
            page: Page number requested
            limit: Results per page
        """
        if not self.registry:
            return

        ***REMOVED*** Categorize page ranges
        if page == 1:
            page_range = "1"
        elif page <= 5:
            page_range = "2-5"
        elif page <= 10:
            page_range = "6-10"
        else:
            page_range = "10+"

        ***REMOVED*** Categorize limit ranges
        if limit <= 10:
            limit_range = "1-10"
        elif limit <= 25:
            limit_range = "11-25"
        elif limit <= 50:
            limit_range = "26-50"
        else:
            limit_range = "50+"

        labels = {
            "page_range": page_range,
            "limit_range": limit_range,
            "service": self.registry.service_name,
        }
        self.pagination_patterns.labels(**labels).inc()

    def record_entity_search(self, entity_type: str, complexity: str, duration: float) -> None:
        """Record entity-specific search performance.

        Args:
            entity_type: Type of entity (movie, actor, genre)
            complexity: Search complexity (simple, moderate, complex)
            duration: Search duration in seconds
        """
        if not self.registry:
            return

        labels = {
            "entity_type": entity_type,
            "complexity": complexity,
            "service": self.registry.service_name,
        }
        self.entity_search_performance.labels(**labels).observe(duration)

        ***REMOVED*** Also record entity popularity
        popularity_labels = {
            "entity_type": entity_type,
            "service": self.registry.service_name,
        }
        self.entity_popularity.labels(**popularity_labels).inc()

    def record_suggestion_conversion(self, suggestion_type: str, converted: bool) -> None:
        """Record whether a suggestion led to an actual search.

        Args:
            suggestion_type: Type of suggestion shown
            converted: Whether user clicked/used the suggestion
        """
        if not self.registry:
            return

        labels = {
            "suggestion_type": suggestion_type,
            "conversion_status": "converted" if converted else "not_converted",
            "service": self.registry.service_name,
        }
        self.suggestion_conversion_rate.labels(**labels).inc()

    def record_search_quality(self, quality_metric: str, value: float) -> None:
        """Record search quality metrics.

        Args:
            quality_metric: Type of quality metric (relevance_score, user_satisfaction)
            value: Metric value (0.0 to 1.0)
        """
        if not self.registry:
            return

        ***REMOVED*** Categorize quality ranges
        if value >= 0.9:
            quality_range = "excellent"
        elif value >= 0.7:
            quality_range = "good"
        elif value >= 0.5:
            quality_range = "average"
        else:
            quality_range = "poor"

        labels = {
            "quality_metric": quality_metric,
            "quality_range": quality_range,
            "service": self.registry.service_name,
        }
        self.search_quality_metrics.labels(**labels).inc()

    def record_search_error(self, error_type: str, search_type: str) -> None:
        """Record search errors.

        Args:
            error_type: Type of error (timeout, redis_error, validation_error)
            search_type: Type of search that failed
        """
        if not self.registry:
            return

        labels = {
            "error_type": error_type,
            "search_type": search_type,
            "service": self.registry.service_name,
        }
        self.search_errors.labels(**labels).inc()

    def update_redis_connection_pool(self, active_connections: int) -> None:
        """Update Redis connection pool metric.

        Args:
            active_connections: Number of active Redis connections
        """
        if not self.registry:
            return

        labels = {"service": self.registry.service_name}
        self.redis_connection_pool.labels(**labels).set(active_connections)

    def update_redis_key_count(self, key_type: str, count: int) -> None:
        """Update Redis key count metric.

        Args:
            key_type: Type of Redis keys (suggestion, entity, search_result)
            count: Number of keys of this type
        """
        if not self.registry:
            return

        labels = {
            "key_type": key_type,
            "service": self.registry.service_name,
        }
        self.redis_key_count.labels(**labels).set(count)


***REMOVED*** Global Search metrics instance
_search_metrics: Optional[SearchMetrics] = None


def get_search_metrics() -> Optional[SearchMetrics]:
    """Get the global Search metrics instance."""
    return _search_metrics


def initialize_search_metrics() -> Optional[SearchMetrics]:
    """Initialize global Search metrics instance.

    Returns:
        SearchMetrics instance if successful, None if metrics registry unavailable
    """
    global _search_metrics

    ***REMOVED*** Return existing instance if already initialized
    if _search_metrics is not None:
        return _search_metrics

    _search_metrics = SearchMetrics()
    ***REMOVED*** Return None if the metrics instance couldn't initialize properly
    if _search_metrics and not _search_metrics.registry:
        _search_metrics = None
    return _search_metrics


***REMOVED*** Decorator for tracking Search operations
def track_search_operation(
    operation_name: str, labels: Optional[Dict[str, str]] = None
) -> Callable[[F], F]:
    """Decorator to track Search-specific operations.

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

    return track_operation(registry, f"search_{operation_name}", labels)


***REMOVED*** Example usage decorators for common Search operations
def track_movie_search(func: F) -> F:
    """Track movie search operations."""
    return track_search_operation("movie_search")(func)


def track_suggestion_operation(func: F) -> F:
    """Track suggestion operations."""
    return track_search_operation("suggestion_operation")(func)


def track_redis_operation(func: F) -> F:
    """Track Redis operations."""
    return track_search_operation("redis_operation")(func)


def track_entity_search(func: F) -> F:
    """Track entity search operations."""
    return track_search_operation("entity_search")(func)


def track_analytics_operation(func: F) -> F:
    """Track search analytics operations."""
    return track_search_operation("analytics_operation")(func)

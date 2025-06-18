"""Metrics collector for cache performance tracking."""

import time
from typing import Any, Callable, Dict, Optional

from .storage import get_global_storage


class MetricsCollector:
    """Collector for cache performance metrics."""

    def __init__(self, enabled: bool = True):
        """Initialize metrics collector.

        Args:
            enabled: Whether to collect metrics
        """
        self.enabled = enabled
        self._storage = get_global_storage() if enabled else None

    def record_cache_hit(self, function_name: str, response_time_ms: float) -> None:
        """Record a cache hit.

        Args:
            function_name: Name of the cached function
            response_time_ms: Response time in milliseconds
        """
        if self.enabled and self._storage:
            self._storage.record_hit(function_name, response_time_ms)

    def record_cache_miss(self, function_name: str, response_time_ms: float) -> None:
        """Record a cache miss.

        Args:
            function_name: Name of the cached function
            response_time_ms: Response time in milliseconds
        """
        if self.enabled and self._storage:
            self._storage.record_miss(function_name, response_time_ms)

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current metrics.

        Returns:
            Metrics dictionary or None if disabled
        """
        if self.enabled and self._storage:
            return self._storage.get_metrics().to_dict()
        return None

    def get_function_metrics(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific function.

        Args:
            function_name: Name of the function

        Returns:
            Function metrics or None if not found/disabled
        """
        if self.enabled and self._storage:
            return self._storage.get_function_metrics(function_name)
        return None

    def get_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary metrics.

        Returns:
            Summary metrics or None if disabled
        """
        if self.enabled and self._storage:
            return self._storage.get_summary()
        return None


***REMOVED*** Global metrics collector instance
_global_collector: Optional[MetricsCollector] = None


def get_global_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _global_collector

    if _global_collector is None:
        _global_collector = MetricsCollector(enabled=True)

    return _global_collector


def set_metrics_enabled(enabled: bool) -> None:
    """Enable or disable metrics collection globally."""
    global _global_collector

    if _global_collector is None:
        _global_collector = MetricsCollector(enabled=enabled)
    else:
        _global_collector.enabled = enabled


class TimingContext:
    """Context manager for timing operations."""

    def __init__(self, collector: MetricsCollector, function_name: str, is_cache_hit: bool):
        """Initialize timing context.

        Args:
            collector: Metrics collector instance
            function_name: Name of the function being timed
            is_cache_hit: Whether this is a cache hit or miss
        """
        self.collector = collector
        self.function_name = function_name
        self.is_cache_hit = is_cache_hit
        self.start_time = 0.0

    def __enter__(self) -> "TimingContext":
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """End timing and record metrics."""
        end_time = time.perf_counter()
        duration_ms = (end_time - self.start_time) * 1000  ***REMOVED*** Convert to milliseconds

        if self.is_cache_hit:
            self.collector.record_cache_hit(self.function_name, duration_ms)
        else:
            self.collector.record_cache_miss(self.function_name, duration_ms)

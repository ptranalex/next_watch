"""Metrics storage for cache performance data."""

import json
import threading
from typing import Any, Dict, Optional

from .types import CacheMetrics


class MetricsStorage:
    """Thread-safe storage for cache metrics."""

    def __init__(self) -> None:
        """Initialize metrics storage."""
        self._metrics = CacheMetrics()
        self._lock = threading.RLock()

    def record_hit(self, function_name: str, response_time_ms: float) -> None:
        """Record a cache hit with thread safety."""
        with self._lock:
            self._metrics.record_hit(function_name, response_time_ms)

    def record_miss(self, function_name: str, response_time_ms: float) -> None:
        """Record a cache miss with thread safety."""
        with self._lock:
            self._metrics.record_miss(function_name, response_time_ms)

    def get_metrics(self) -> CacheMetrics:
        """Get current metrics snapshot."""
        with self._lock:
            ***REMOVED*** Return a copy to avoid external modification
            return CacheMetrics(
                total_hits=self._metrics.total_hits,
                total_misses=self._metrics.total_misses,
                total_calls=self._metrics.total_calls,
                functions=self._metrics.functions.copy(),
                started_at=self._metrics.started_at,
            )

    def get_function_metrics(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific function."""
        with self._lock:
            if function_name in self._metrics.functions:
                func_metrics = self._metrics.functions[function_name]
                return {
                    "function_name": func_metrics.function_name,
                    "hits": func_metrics.hits,
                    "misses": func_metrics.misses,
                    "total_calls": func_metrics.total_calls,
                    "hit_ratio": round(func_metrics.hit_ratio, 2),
                    "miss_ratio": round(func_metrics.miss_ratio, 2),
                    "avg_cache_time_ms": round(func_metrics.avg_cache_time_ms, 2),
                    "avg_uncached_time_ms": round(func_metrics.avg_uncached_time_ms, 2),
                    "performance_improvement": round(func_metrics.performance_improvement, 2),
                    "last_hit": (
                        func_metrics.last_hit.isoformat() if func_metrics.last_hit else None
                    ),
                    "last_miss": (
                        func_metrics.last_miss.isoformat() if func_metrics.last_miss else None
                    ),
                    "created_at": func_metrics.created_at.isoformat(),
                }
            return None

    def get_summary(self) -> Dict[str, Any]:
        """Get summary metrics."""
        with self._lock:
            return {
                "total_hits": self._metrics.total_hits,
                "total_misses": self._metrics.total_misses,
                "total_calls": self._metrics.total_calls,
                "overall_hit_ratio": round(self._metrics.overall_hit_ratio, 2),
                "overall_miss_ratio": round(self._metrics.overall_miss_ratio, 2),
                "function_count": len(self._metrics.functions),
                "started_at": self._metrics.started_at.isoformat(),
            }

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics = CacheMetrics()

    def to_json(self) -> str:
        """Export metrics as JSON string."""
        with self._lock:
            return json.dumps(self._metrics.to_dict(), indent=2)


***REMOVED*** Global metrics storage instance
_global_storage: Optional[MetricsStorage] = None
_storage_lock = threading.Lock()


def get_global_storage() -> MetricsStorage:
    """Get or create global metrics storage instance."""
    global _global_storage

    if _global_storage is None:
        with _storage_lock:
            if _global_storage is None:
                _global_storage = MetricsStorage()

    return _global_storage


def reset_global_storage() -> None:
    """Reset global metrics storage."""
    global _global_storage

    with _storage_lock:
        _global_storage = None

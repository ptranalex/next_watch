"""Types for cache metrics tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class FunctionMetrics:
    """Metrics for a specific cached function."""

    function_name: str
    hits: int = 0
    misses: int = 0
    total_calls: int = 0
    total_cache_time_ms: float = 0.0
    total_uncached_time_ms: float = 0.0
    last_hit: datetime | None = None
    last_miss: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def hit_ratio(self) -> float:
        """Calculate hit ratio as percentage."""
        if self.total_calls == 0:
            return 0.0
        return (self.hits / self.total_calls) * 100

    @property
    def miss_ratio(self) -> float:
        """Calculate miss ratio as percentage."""
        return 100.0 - self.hit_ratio

    @property
    def avg_cache_time_ms(self) -> float:
        """Average response time for cache hits."""
        if self.hits == 0:
            return 0.0
        return self.total_cache_time_ms / self.hits

    @property
    def avg_uncached_time_ms(self) -> float:
        """Average response time for cache misses."""
        if self.misses == 0:
            return 0.0
        return self.total_uncached_time_ms / self.misses

    @property
    def performance_improvement(self) -> float:
        """Performance improvement ratio (uncached/cached)."""
        if self.avg_cache_time_ms == 0:
            return 0.0
        return self.avg_uncached_time_ms / self.avg_cache_time_ms


@dataclass
class CacheMetrics:
    """Overall cache system metrics."""

    total_hits: int = 0
    total_misses: int = 0
    total_calls: int = 0
    functions: dict[str, FunctionMetrics] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)

    @property
    def overall_hit_ratio(self) -> float:
        """Overall hit ratio across all functions."""
        if self.total_calls == 0:
            return 0.0
        return (self.total_hits / self.total_calls) * 100

    @property
    def overall_miss_ratio(self) -> float:
        """Overall miss ratio across all functions."""
        return 100.0 - self.overall_hit_ratio

    def get_function_metrics(self, function_name: str) -> FunctionMetrics:
        """Get or create metrics for a function."""
        if function_name not in self.functions:
            self.functions[function_name] = FunctionMetrics(function_name=function_name)
        return self.functions[function_name]

    def record_hit(self, function_name: str, response_time_ms: float) -> None:
        """Record a cache hit."""
        self.total_hits += 1
        self.total_calls += 1

        func_metrics = self.get_function_metrics(function_name)
        func_metrics.hits += 1
        func_metrics.total_calls += 1
        func_metrics.total_cache_time_ms += response_time_ms
        func_metrics.last_hit = datetime.now()

    def record_miss(self, function_name: str, response_time_ms: float) -> None:
        """Record a cache miss."""
        self.total_misses += 1
        self.total_calls += 1

        func_metrics = self.get_function_metrics(function_name)
        func_metrics.misses += 1
        func_metrics.total_calls += 1
        func_metrics.total_uncached_time_ms += response_time_ms
        func_metrics.last_miss = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            "overall": {
                "total_hits": self.total_hits,
                "total_misses": self.total_misses,
                "total_calls": self.total_calls,
                "hit_ratio": round(self.overall_hit_ratio, 2),
                "miss_ratio": round(self.overall_miss_ratio, 2),
                "started_at": self.started_at.isoformat(),
            },
            "functions": {
                name: {
                    "hits": metrics.hits,
                    "misses": metrics.misses,
                    "total_calls": metrics.total_calls,
                    "hit_ratio": round(metrics.hit_ratio, 2),
                    "miss_ratio": round(metrics.miss_ratio, 2),
                    "avg_cache_time_ms": round(metrics.avg_cache_time_ms, 2),
                    "avg_uncached_time_ms": round(metrics.avg_uncached_time_ms, 2),
                    "performance_improvement": round(metrics.performance_improvement, 2),
                    "last_hit": metrics.last_hit.isoformat() if metrics.last_hit else None,
                    "last_miss": metrics.last_miss.isoformat() if metrics.last_miss else None,
                    "created_at": metrics.created_at.isoformat(),
                }
                for name, metrics in self.functions.items()
            },
        }

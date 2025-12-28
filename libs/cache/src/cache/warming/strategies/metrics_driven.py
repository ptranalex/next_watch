"""Metrics-driven warming strategy."""

from typing import Any

import structlog

from cache.metrics import MetricsCollector
from cache.warming.types import WarmingConfig, WarmingStrategy, WarmingTarget

from .base import BaseWarmingStrategy

logger = structlog.get_logger(__name__)


class MetricsDrivenStrategy(BaseWarmingStrategy):
    """Warming strategy based on cache performance metrics."""

    def __init__(
        self,
        config: WarmingConfig,
        metrics_collector: MetricsCollector | None = None,
    ):
        """Initialize metrics-driven strategy.

        Args:
            config: Warming configuration
            metrics_collector: Metrics collector for performance data
        """
        super().__init__(config)
        self.strategy_type = WarmingStrategy.METRICS_DRIVEN
        self.metrics_collector = metrics_collector

    async def identify_targets(
        self, limit: int | None = None, context: dict[str, Any] | None = None
    ) -> list[WarmingTarget]:
        """Identify warming targets based on metrics data.

        Args:
            limit: Maximum number of targets to return
            context: Additional context (unused for metrics strategy)

        Returns:
            List of warming targets prioritized by performance impact
        """
        if not self.metrics_collector:
            logger.warning("No metrics collector available for metrics-driven warming")
            return []

        ***REMOVED*** Get all function metrics
        metrics_data = self.metrics_collector.get_metrics()
        if not metrics_data or "functions" not in metrics_data:
            logger.info("No metrics data available for warming")
            return []

        all_functions = metrics_data["functions"]
        if not all_functions:
            logger.info("No function metrics available for warming")
            return []

        ***REMOVED*** Identify warming targets
        targets = []
        for func_name, metrics_dict in all_functions.items():
            if self.should_warm_target(metrics_dict):
                priority = self.calculate_priority(metrics_dict)
                benefit = self._calculate_benefit(metrics_dict)

                target = self.create_warming_target(
                    function_name=func_name,
                    parameters={},  ***REMOVED*** Metrics strategy doesn't specify parameters
                    priority=priority,
                    estimated_benefit=benefit,
                )
                targets.append(target)

        ***REMOVED*** Sort by priority and apply limit
        targets.sort(key=lambda t: t.priority, reverse=True)
        if limit:
            targets = targets[:limit]

        logger.info(f"Identified {len(targets)} targets for metrics-driven warming")
        return targets

    def calculate_priority(self, target_data: dict[str, Any]) -> float:
        """Calculate priority based on miss rate, timing, and usage.

        Args:
            target_data: Function metrics data

        Returns:
            Priority score
        """
        miss_rate = target_data.get("miss_ratio", 0.0) / 100.0  ***REMOVED*** Convert percentage
        avg_miss_time = target_data.get("avg_uncached_time_ms", 0.0)
        total_calls = target_data.get("total_calls", 0)

        ***REMOVED*** Priority based on miss rate, miss time, and usage
        miss_rate_factor = miss_rate
        time_factor = min(avg_miss_time / 1000.0, 5.0)  ***REMOVED*** Cap at 5 seconds
        usage_factor = min(total_calls / 100.0, 10.0)  ***REMOVED*** Cap at 10x

        return miss_rate_factor * time_factor * usage_factor * self.config.metrics_driven_weight

    def should_warm_target(self, target_data: dict[str, Any]) -> bool:
        """Check if function should be warmed based on metrics thresholds.

        Args:
            target_data: Function metrics data

        Returns:
            True if function meets warming criteria
        """
        total_calls = target_data.get("total_calls", 0)
        miss_rate = target_data.get("miss_ratio", 0.0) / 100.0
        avg_miss_time = target_data.get("avg_uncached_time_ms", 0.0)

        ***REMOVED*** Apply thresholds from configuration
        if total_calls < self.config.min_total_calls:
            return False

        if miss_rate < self.config.min_miss_rate_threshold:
            return False

        if avg_miss_time < self.config.min_avg_miss_time_ms:
            return False

        return True

    def _calculate_benefit(self, metrics_dict: dict[str, Any]) -> float:
        """Calculate estimated benefit of warming.

        Args:
            metrics_dict: Function metrics data

        Returns:
            Estimated benefit score
        """
        avg_miss_time = metrics_dict.get("avg_uncached_time_ms", 0.0)
        avg_hit_time = metrics_dict.get("avg_cache_time_ms", 0.0)
        miss_count = metrics_dict.get("misses", 0)

        time_saved_per_miss = avg_miss_time - avg_hit_time
        return time_saved_per_miss * miss_count

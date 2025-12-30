"""Core cache warming engine."""

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

import structlog

from cache.manager import CacheManager
from cache.metrics import MetricsCollector
from cache.warming.strategies import (
    BaseWarmingStrategy,
    MetricsDrivenStrategy,
    PopularContentStrategy,
    ScheduledStrategy,
    UserSpecificStrategy,
)
from cache.warming.types import (
    WarmingConfig,
    WarmingResult,
    WarmingStats,
    WarmingStatus,
    WarmingStrategy,
    WarmingTarget,
)

logger = structlog.get_logger(__name__)


class WarmingEngine:
    """Core engine for cache warming operations."""

    def __init__(
        self,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector | None = None,
        config: WarmingConfig | None = None,
    ):
        """Initialize warming engine.

        Args:
            cache_manager: Cache manager for warming operations
            metrics_collector: Optional metrics collector for data-driven warming
            config: Optional warming configuration
        """
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.config = config or WarmingConfig()

        # Registry for warming functions
        self._warming_functions: dict[str, Callable[..., Awaitable[Any]]] = {}

        # Statistics tracking
        self._warming_history: list[WarmingResult] = []

        # Initialize warming strategies
        self._strategies: dict[WarmingStrategy, BaseWarmingStrategy] = {}
        self._initialize_strategies()

    def register_warming_function(
        self, function_name: str, func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Register a function that can be warmed.

        Args:
            function_name: Name of the function
            func: The actual function to call for warming
        """
        self._warming_functions[function_name] = func
        logger.debug(f"Registered warming function: {function_name}")

    def _initialize_strategies(self) -> None:
        """Initialize warming strategies based on configuration."""
        if self.config.enable_metrics_driven:
            self._strategies[WarmingStrategy.METRICS_DRIVEN] = MetricsDrivenStrategy(
                config=self.config, metrics_collector=self.metrics_collector
            )

        if self.config.enable_popular_content:
            self._strategies[WarmingStrategy.POPULAR_CONTENT] = PopularContentStrategy(
                config=self.config,
                popularity_provider=None,  # Can be set later via set_popularity_provider
            )

        if self.config.enable_user_specific:
            self._strategies[WarmingStrategy.USER_SPECIFIC] = UserSpecificStrategy(
                config=self.config,
                user_data_provider=None,  # Can be set later
                recommendation_provider=None,  # Can be set later
            )

        if self.config.enable_scheduled:
            self._strategies[WarmingStrategy.SCHEDULED] = ScheduledStrategy(config=self.config)

        logger.info(f"Initialized {len(self._strategies)} warming strategies")

    def set_popularity_provider(self, provider: Callable[[], Awaitable[dict[str, Any]]]) -> None:
        """Set popularity data provider for popular content strategy.

        Args:
            provider: Function that returns popularity data
        """
        if WarmingStrategy.POPULAR_CONTENT in self._strategies:
            strategy = self._strategies[WarmingStrategy.POPULAR_CONTENT]
            if isinstance(strategy, PopularContentStrategy):
                strategy.popularity_provider = provider

    def set_user_data_provider(self, provider: Callable[[int], Awaitable[dict[str, Any]]]) -> None:
        """Set user data provider for user-specific strategy.

        Args:
            provider: Function that returns user profile data
        """
        if WarmingStrategy.USER_SPECIFIC in self._strategies:
            strategy = self._strategies[WarmingStrategy.USER_SPECIFIC]
            if isinstance(strategy, UserSpecificStrategy):
                strategy.user_data_provider = provider

    def set_recommendation_provider(
        self, provider: Callable[[int], Awaitable[list[dict[str, Any]]]]
    ) -> None:
        """Set recommendation provider for user-specific strategy.

        Args:
            provider: Function that returns user recommendations
        """
        if WarmingStrategy.USER_SPECIFIC in self._strategies:
            strategy = self._strategies[WarmingStrategy.USER_SPECIFIC]
            if isinstance(strategy, UserSpecificStrategy):
                strategy.recommendation_provider = provider

    async def warm_targets(
        self,
        targets: list[WarmingTarget],
        max_concurrent: int | None = None,
        dry_run: bool = False,
    ) -> WarmingStats:
        """Warm specific cache targets.

        Args:
            targets: List of warming targets
            max_concurrent: Maximum concurrent operations
            dry_run: If True, only simulate warming without executing

        Returns:
            Warming statistics
        """
        if not targets:
            logger.info("No targets provided for warming")
            return WarmingStats()

        max_concurrent = max_concurrent or self.config.max_concurrent_operations

        logger.info(
            f"Starting warming of {len(targets)} targets",
            extra={
                "target_count": len(targets),
                "max_concurrent": max_concurrent,
                "dry_run": dry_run,
            },
        )

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        # Execute warming tasks
        tasks = [self._warm_single_target(target, semaphore, dry_run) for target in targets]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and calculate statistics
        stats = self._calculate_warming_stats(results)

        # Store results in history
        for result in results:
            if isinstance(result, WarmingResult):
                self._warming_history.append(result)

        logger.info(
            "Warming completed",
            extra={
                "total_targets": stats.total_targets,
                "successful": stats.successful_targets,
                "failed": stats.failed_targets,
                "success_rate": stats.success_rate,
                "total_time_ms": stats.total_execution_time_ms,
            },
        )

        return stats

    async def warm_by_strategy(
        self,
        strategy: WarmingStrategy,
        limit: int | None = None,
        dry_run: bool = False,
        context: dict[str, Any] | None = None,
    ) -> WarmingStats:
        """Warm cache using a specific strategy.

        Args:
            strategy: Warming strategy to use
            limit: Maximum number of targets to warm
            dry_run: If True, only simulate warming
            context: Additional context for strategy execution

        Returns:
            Warming statistics
        """
        if strategy not in self._strategies:
            logger.warning(f"Strategy {strategy} not available or not enabled")
            return WarmingStats()

        strategy_instance = self._strategies[strategy]

        try:
            # Get targets from strategy
            targets = await strategy_instance.identify_targets(limit=limit, context=context)

            if not targets:
                logger.info(f"No targets identified by {strategy} strategy")
                return WarmingStats()

            # Warm the identified targets
            return await self.warm_targets(targets, dry_run=dry_run)

        except Exception as e:
            logger.error(f"Error executing {strategy} strategy: {e}")
            return WarmingStats()

    async def warm_all_strategies(
        self,
        limit_per_strategy: int | None = None,
        dry_run: bool = False,
        context: dict[str, Any] | None = None,
    ) -> dict[WarmingStrategy, WarmingStats]:
        """Warm cache using all enabled strategies.

        Args:
            limit_per_strategy: Maximum targets per strategy
            dry_run: If True, only simulate warming
            context: Additional context for strategy execution

        Returns:
            Dictionary mapping strategies to their warming statistics
        """
        results = {}

        for strategy in self._strategies.keys():
            try:
                logger.info(f"Executing {strategy} warming strategy")
                stats = await self.warm_by_strategy(
                    strategy=strategy,
                    limit=limit_per_strategy,
                    dry_run=dry_run,
                    context=context,
                )
                results[strategy] = stats

            except Exception as e:
                logger.error(f"Error in {strategy} strategy: {e}")
                results[strategy] = WarmingStats()

        # Log summary
        total_targets = sum(stats.total_targets for stats in results.values())
        total_successful = sum(stats.successful_targets for stats in results.values())

        logger.info(
            f"All strategies completed: {total_successful}/{total_targets} targets warmed successfully"
        )

        return results

    def get_available_strategies(self) -> list[WarmingStrategy]:
        """Get list of available warming strategies.

        Returns:
            List of available strategies
        """
        return list(self._strategies.keys())

    def get_strategy_info(self, strategy: WarmingStrategy) -> dict[str, Any] | None:
        """Get information about a specific strategy.

        Args:
            strategy: Strategy to get info for

        Returns:
            Strategy information or None if not available
        """
        if strategy in self._strategies:
            return self._strategies[strategy].get_strategy_info()
        return None

    async def _warm_metrics_driven(
        self, limit: int | None = None, dry_run: bool = False
    ) -> WarmingStats:
        """Warm cache based on metrics data.

        Args:
            limit: Maximum number of targets to warm
            dry_run: If True, only simulate warming

        Returns:
            Warming statistics
        """
        if not self.metrics_collector:
            logger.warning("No metrics collector available for metrics-driven warming")
            return WarmingStats()

        # Get all function metrics
        metrics_data = self.metrics_collector.get_metrics()
        if not metrics_data or "functions" not in metrics_data:
            logger.info("No metrics data available for warming")
            return WarmingStats()

        all_functions = metrics_data["functions"]
        if not all_functions:
            logger.info("No function metrics available for warming")
            return WarmingStats()

        # Identify warming targets
        targets = []
        for func_name, metrics_dict in all_functions.items():
            # Convert dict to object-like access for compatibility
            class MetricsObj:
                def __init__(self, data: dict[str, Any]):
                    self.total_calls: int = data.get("total_calls", 0)
                    self.miss_ratio: float = (
                        data.get("miss_ratio", 0.0) / 100.0
                    )  # Convert percentage to ratio
                    self.avg_uncached_time_ms: float = data.get("avg_uncached_time_ms", 0.0)
                    self.avg_cache_time_ms: float = data.get("avg_cache_time_ms", 0.0)
                    self.misses: int = data.get("misses", 0)

                @property
                def miss_rate(self) -> float:
                    return self.miss_ratio

                @property
                def avg_cache_miss_time(self) -> float:
                    return self.avg_uncached_time_ms

                @property
                def avg_cache_hit_time(self) -> float:
                    return self.avg_cache_time_ms

                @property
                def miss_count(self) -> int:
                    return self.misses

            metrics = MetricsObj(metrics_dict)
            if self._should_warm_function(func_name, metrics):
                target = WarmingTarget(
                    function_name=func_name,
                    priority=self._calculate_priority(metrics),
                    estimated_benefit=self._calculate_benefit(metrics),
                    strategy=WarmingStrategy.METRICS_DRIVEN,
                )
                targets.append(target)

        # Sort by priority and apply limit
        targets.sort(key=lambda t: t.priority, reverse=True)
        if limit:
            targets = targets[:limit]

        logger.info(f"Identified {len(targets)} targets for metrics-driven warming")

        return await self.warm_targets(targets, dry_run=dry_run)

    async def _warm_single_target(
        self, target: WarmingTarget, semaphore: asyncio.Semaphore, dry_run: bool = False
    ) -> WarmingResult:
        """Warm a single cache target.

        Args:
            target: Target to warm
            semaphore: Concurrency control semaphore
            dry_run: If True, only simulate warming

        Returns:
            Warming result
        """
        async with semaphore:
            start_time = datetime.now()
            result = WarmingResult(
                target=target, status=WarmingStatus.RUNNING, start_time=start_time
            )

            try:
                if dry_run:
                    # Simulate warming
                    await asyncio.sleep(0.1)  # Simulate work
                    result.status = WarmingStatus.COMPLETED
                    result.cache_key = f"simulated:{target.function_name}"
                else:
                    # Actual warming
                    await self._execute_warming(target, result)

                result.end_time = datetime.now()
                result.execution_time_ms = result.duration_ms

                if result.status != WarmingStatus.COMPLETED:
                    result.status = WarmingStatus.COMPLETED

            except Exception as e:
                result.status = WarmingStatus.FAILED
                result.error = str(e)
                result.end_time = datetime.now()
                logger.error(f"Failed to warm target {target.function_name}: {e}", exc_info=True)

            return result

    async def _execute_warming(self, target: WarmingTarget, result: WarmingResult) -> None:
        """Execute the actual warming operation.

        Args:
            target: Target to warm
            result: Result object to update
        """
        func_name = target.function_name

        # Check if we have a registered warming function
        if func_name in self._warming_functions:
            warming_func = self._warming_functions[func_name]
            try:
                # Call the warming function with parameters
                await warming_func(**target.parameters)
                result.cache_key = f"warmed:{func_name}"
            except Exception as e:
                raise Exception(f"Warming function failed: {e}")
        else:
            # For now, just log that we would warm this function
            logger.info(f"Would warm function {func_name} with params {target.parameters}")
            result.cache_key = f"placeholder:{func_name}"

    def _should_warm_function(self, func_name: str, metrics: Any) -> bool:
        """Check if a function should be warmed based on metrics.

        Args:
            func_name: Function name
            metrics: Function metrics

        Returns:
            True if function should be warmed
        """
        # Apply thresholds from configuration
        if metrics.total_calls < self.config.min_total_calls:
            return False

        if metrics.miss_rate < self.config.min_miss_rate_threshold:
            return False

        if metrics.avg_cache_miss_time < self.config.min_avg_miss_time_ms:
            return False

        return True

    def _calculate_priority(self, metrics: Any) -> float:
        """Calculate warming priority based on metrics.

        Args:
            metrics: Function metrics

        Returns:
            Priority score
        """
        # Priority based on miss rate, miss time, and usage
        miss_rate_factor = float(metrics.miss_rate)
        time_factor = min(float(metrics.avg_cache_miss_time) / 1000.0, 5.0)
        usage_factor = min(float(metrics.total_calls) / 100.0, 10.0)

        return miss_rate_factor * time_factor * usage_factor

    def _calculate_benefit(self, metrics: Any) -> float:
        """Calculate estimated benefit of warming.

        Args:
            metrics: Function metrics

        Returns:
            Estimated benefit score
        """
        time_saved_per_miss = float(metrics.avg_cache_miss_time) - float(metrics.avg_cache_hit_time)
        return time_saved_per_miss * float(metrics.miss_count)

    def _calculate_warming_stats(self, results: list[Any]) -> WarmingStats:
        """Calculate statistics from warming results.

        Args:
            results: List of warming results (may include exceptions)

        Returns:
            Warming statistics
        """
        stats = WarmingStats()

        for result in results:
            if isinstance(result, WarmingResult):
                stats.total_targets += 1

                if result.success:
                    stats.successful_targets += 1
                else:
                    stats.failed_targets += 1

                if result.execution_time_ms:
                    stats.total_execution_time_ms += result.execution_time_ms
            else:
                # Exception occurred
                stats.total_targets += 1
                stats.failed_targets += 1

        # Calculate average execution time
        if stats.successful_targets > 0:
            stats.average_execution_time_ms = (
                stats.total_execution_time_ms / stats.successful_targets
            )

        return stats

    def get_warming_history(self, limit: int | None = None) -> list[WarmingResult]:
        """Get warming operation history.

        Args:
            limit: Optional limit on number of results

        Returns:
            List of warming results
        """
        history = self._warming_history.copy()
        if limit:
            history = history[-limit:]
        return history

    def clear_warming_history(self) -> None:
        """Clear warming operation history."""
        self._warming_history.clear()
        logger.info("Warming history cleared")

"""Background warming service for the Recommendation API.

This module provides a background task that periodically warms the cache
using different warming strategies.
"""

import asyncio
from contextlib import suppress
from datetime import datetime
from typing import Any

from cache import WarmingStrategy
from config.logging import get_logger

from recommendation_api.config import settings
from recommendation_api.services.cache_service.warming import get_recommendation_warming_service

logger = get_logger(__name__)

***REMOVED*** Global background task
_background_task: asyncio.Task | None = None
_is_running = False


class BackgroundWarmingService:
    """Background service for periodic cache warming."""

    def __init__(self) -> None:
        """Initialize the background warming service."""
        self.warming_service = get_recommendation_warming_service()
        self.interval_seconds = getattr(
            settings, "warming_interval_seconds", 3600
        )  ***REMOVED*** Default: 1 hour
        self.is_running = False
        self.last_run: datetime | None = None
        self.stats: dict[str, Any] = {}

    async def start(self) -> None:
        """Start the background warming service."""
        if self.is_running:
            logger.warning(
                "Background warming service is already running",
                service="recommendation-api",
                component="cache_warming",
            )
            return

        self.is_running = True
        logger.info(
            "Starting background warming service",
            service="recommendation-api",
            component="cache_warming",
            interval_seconds=self.interval_seconds,
        )

        while self.is_running:
            try:
                await self._run_warming_cycle()
                self.last_run = datetime.now()
            except Exception as e:
                logger.error(
                    "Error in background warming cycle",
                    service="recommendation-api",
                    component="cache_warming",
                    error=str(e),
                    exc_info=True,
                )

            ***REMOVED*** Sleep until next cycle
            await asyncio.sleep(self.interval_seconds)

    async def stop(self) -> None:
        """Stop the background warming service."""
        self.is_running = False
        logger.info(
            "Background warming service stopped",
            service="recommendation-api",
            component="cache_warming",
        )

    async def _run_warming_cycle(self) -> None:
        """Run a complete warming cycle with all strategies."""
        logger.info(
            "Starting warming cycle", service="recommendation-api", component="cache_warming"
        )
        start_time = datetime.now()

        ***REMOVED*** Run popular content strategy
        popular_stats = await self._run_strategy(WarmingStrategy.POPULAR_CONTENT)

        ***REMOVED*** Run metrics-driven strategy
        metrics_stats = await self._run_strategy(WarmingStrategy.METRICS_DRIVEN)

        ***REMOVED*** Run scheduled strategy
        scheduled_stats = await self._run_strategy(WarmingStrategy.SCHEDULED)

        ***REMOVED*** Update stats
        end_time = datetime.now()
        duration_seconds = (end_time - start_time).total_seconds()

        self.stats = {
            "last_run": end_time.isoformat(),
            "duration_seconds": duration_seconds,
            "strategies": {
                "popular_content": popular_stats,
                "metrics_driven": metrics_stats,
                "scheduled": scheduled_stats,
            },
        }

        logger.info(
            "Completed warming cycle",
            service="recommendation-api",
            component="cache_warming",
            duration_seconds=round(duration_seconds, 2),
            popular_targets=popular_stats.get("targets_warmed", 0),
            metrics_targets=metrics_stats.get("targets_warmed", 0),
            scheduled_targets=scheduled_stats.get("targets_warmed", 0),
        )

    async def _run_strategy(self, strategy: WarmingStrategy) -> dict[str, Any]:
        """Run a specific warming strategy.

        Args:
            strategy: Warming strategy to run

        Returns:
            Dictionary with strategy statistics
        """
        try:
            logger.info(
                "Running warming strategy",
                service="recommendation-api",
                component="cache_warming",
                strategy=strategy.name,
            )
            result = await self.warming_service.warm_by_strategy(strategy)
            logger.info(
                "Completed warming strategy",
                service="recommendation-api",
                component="cache_warming",
                strategy=strategy.name,
                targets_warmed=result.get("targets_warmed", 0),
                success_count=result.get("success_count", 0),
                error_count=result.get("error_count", 0),
            )
            return result
        except Exception as e:
            logger.error(
                "Error running warming strategy",
                service="recommendation-api",
                component="cache_warming",
                strategy=strategy.name,
                error=str(e),
                exc_info=True,
            )
            return {
                "strategy": strategy.name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the background warming service.

        Returns:
            Dictionary with service statistics
        """
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "interval_seconds": self.interval_seconds,
            "stats": self.stats,
        }


***REMOVED*** Global background warming service instance
_background_warming_service: BackgroundWarmingService | None = None


def get_background_warming_service() -> BackgroundWarmingService:
    """Get the global background warming service instance.

    Returns:
        Global background warming service instance
    """
    global _background_warming_service
    if _background_warming_service is None:
        _background_warming_service = BackgroundWarmingService()
    return _background_warming_service


async def start_background_warming() -> None:
    """Start the background warming service in a separate task."""
    global _background_task, _is_running

    if _is_running:
        logger.warning(
            "Background warming is already running",
            service="recommendation-api",
            component="cache_warming",
        )
        return

    try:
        service = get_background_warming_service()
        _background_task = asyncio.create_task(service.start())
        _is_running = True
        logger.info(
            "Background warming started", service="recommendation-api", component="cache_warming"
        )
    except Exception as e:
        logger.error(
            "Failed to start background warming",
            service="recommendation-api",
            component="cache_warming",
            error=str(e),
            exc_info=True,
        )


async def stop_background_warming() -> None:
    """Stop the background warming service."""
    global _background_task, _is_running

    if not _is_running:
        logger.warning(
            "Background warming is not running",
            service="recommendation-api",
            component="cache_warming",
        )
        return

    try:
        service = get_background_warming_service()
        await service.stop()

        if _background_task:
            _background_task.cancel()
            with suppress(asyncio.CancelledError):
                await _background_task
            _background_task = None

        _is_running = False
        logger.info(
            "Background warming stopped", service="recommendation-api", component="cache_warming"
        )
    except Exception as e:
        logger.error(
            "Error stopping background warming",
            service="recommendation-api",
            component="cache_warming",
            error=str(e),
            exc_info=True,
        )

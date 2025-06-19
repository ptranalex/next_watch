"""Background warming service for automatic cache warming.

This service runs warming tasks automatically in the background using asyncio tasks.
It integrates with the FastAPI application lifecycle to start and stop warming tasks.
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Any, Dict, Optional, Set

from config.logging import get_logger

from bff_api.config.app import get_settings
from bff_api.services.cache_service.warming import get_bff_warming_service

logger = get_logger(__name__)


class BackgroundWarmingService:
    """Service for running cache warming tasks in the background."""

    def __init__(self) -> None:
        """Initialize the background warming service."""
        self.settings = get_settings()
        self.warming_service = get_bff_warming_service()
        self._running_tasks: Set[asyncio.Task[Any]] = set()
        self._should_stop = False

        ***REMOVED*** Warming schedule configuration
        self._schedule_config = {
            "morning_warmup": {
                "time": time(7, 0),  ***REMOVED*** 7 AM
                "strategy": "popular_content",
                "limit": 100,
                "enabled": True,
            },
            "evening_warmup": {
                "time": time(17, 0),  ***REMOVED*** 5 PM
                "strategy": "metrics_driven",
                "limit": 50,
                "enabled": True,
            },
            "night_optimization": {
                "time": time(1, 0),  ***REMOVED*** 1 AM
                "strategy": "scheduled",
                "limit": 30,
                "enabled": True,
            },
            ***REMOVED*** Continuous metrics-driven warming every 10 minutes
            "continuous_metrics": {
                "interval_minutes": 10,
                "strategy": "metrics_driven",
                "limit": 10,
                "enabled": True,
            },
        }

    async def start(self) -> None:
        """Start background warming tasks."""
        logger.info(
            "Starting background warming service", service="bff", component="background_warming"
        )

        self._should_stop = False

        ***REMOVED*** Start scheduled warming tasks
        for schedule_name, config in self._schedule_config.items():
            if not config.get("enabled", True):
                continue

            if schedule_name == "continuous_metrics":
                ***REMOVED*** Start continuous task
                task = asyncio.create_task(
                    self._run_continuous_warming(config), name=f"warming_{schedule_name}"
                )
            else:
                ***REMOVED*** Start scheduled task
                task = asyncio.create_task(
                    self._run_scheduled_warming(schedule_name, config),
                    name=f"warming_{schedule_name}",
                )

            self._running_tasks.add(task)
            logger.info(
                "Started warming task",
                task_name=schedule_name,
                strategy=config.get("strategy"),
                service="bff",
                component="background_warming",
            )

        logger.info(
            "Background warming service started",
            active_tasks=len(self._running_tasks),
            service="bff",
            component="background_warming",
        )

    async def stop(self) -> None:
        """Stop all background warming tasks."""
        logger.info(
            "Stopping background warming service", service="bff", component="background_warming"
        )

        self._should_stop = True

        ***REMOVED*** Cancel all running tasks
        for task in self._running_tasks:
            if not task.done():
                task.cancel()

        ***REMOVED*** Wait for all tasks to complete
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks, return_exceptions=True)

        self._running_tasks.clear()

        logger.info(
            "Background warming service stopped", service="bff", component="background_warming"
        )

    async def _run_scheduled_warming(self, schedule_name: str, config: Dict[str, Any]) -> None:
        """Run a scheduled warming task that triggers at specific times."""
        target_time = config["time"]
        strategy = config["strategy"]
        limit = config.get("limit", 50)

        logger.info(
            "Scheduled warming task started",
            schedule_name=schedule_name,
            target_time=str(target_time),
            strategy=strategy,
            service="bff",
            component="background_warming",
        )

        try:
            while not self._should_stop:
                now = datetime.now()
                current_time = now.time()

                ***REMOVED*** Check if we should run now (within 1 minute of target time)
                if self._is_time_to_run(current_time, target_time):
                    logger.info(
                        "Executing scheduled warming",
                        schedule_name=schedule_name,
                        strategy=strategy,
                        limit=limit,
                        service="bff",
                        component="background_warming",
                    )

                    try:
                        from cache.warming import WarmingStrategy

                        ***REMOVED*** Map string to enum
                        strategy_map = {
                            "metrics_driven": WarmingStrategy.METRICS_DRIVEN,
                            "popular_content": WarmingStrategy.POPULAR_CONTENT,
                            "user_specific": WarmingStrategy.USER_SPECIFIC,
                            "scheduled": WarmingStrategy.SCHEDULED,
                        }

                        warming_strategy = strategy_map.get(strategy)
                        if warming_strategy:
                            stats = await self.warming_service.engine.warm_by_strategy(
                                strategy=warming_strategy, limit=limit, dry_run=False
                            )

                            logger.info(
                                "Scheduled warming completed",
                                schedule_name=schedule_name,
                                strategy=strategy,
                                total_targets=stats.total_targets,
                                successful=stats.successful_targets,
                                service="bff",
                                component="background_warming",
                            )
                        else:
                            logger.warning(
                                "Unknown warming strategy",
                                strategy=strategy,
                                service="bff",
                                component="background_warming",
                            )

                    except Exception as e:
                        logger.error(
                            "Error in scheduled warming",
                            schedule_name=schedule_name,
                            error=str(e),
                            service="bff",
                            component="background_warming",
                        )

                    ***REMOVED*** Wait until next day to avoid running multiple times
                    await asyncio.sleep(60 * 60)  ***REMOVED*** Sleep 1 hour
                else:
                    ***REMOVED*** Check again in 1 minute
                    await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info(
                "Scheduled warming task cancelled",
                schedule_name=schedule_name,
                service="bff",
                component="background_warming",
            )
        except Exception as e:
            logger.error(
                "Scheduled warming task failed",
                schedule_name=schedule_name,
                error=str(e),
                service="bff",
                component="background_warming",
            )

    async def _run_continuous_warming(self, config: Dict[str, Any]) -> None:
        """Run continuous warming that triggers at regular intervals."""
        interval_minutes = config.get("interval_minutes", 10)
        strategy = config["strategy"]
        limit = config.get("limit", 10)

        logger.info(
            "Continuous warming task started",
            interval_minutes=interval_minutes,
            strategy=strategy,
            service="bff",
            component="background_warming",
        )

        try:
            while not self._should_stop:
                try:
                    from cache.warming import WarmingStrategy

                    ***REMOVED*** Map string to enum
                    strategy_map = {
                        "metrics_driven": WarmingStrategy.METRICS_DRIVEN,
                        "popular_content": WarmingStrategy.POPULAR_CONTENT,
                        "user_specific": WarmingStrategy.USER_SPECIFIC,
                        "scheduled": WarmingStrategy.SCHEDULED,
                    }

                    warming_strategy = strategy_map.get(strategy)
                    if warming_strategy:
                        logger.debug(
                            "Running continuous warming",
                            strategy=strategy,
                            limit=limit,
                            service="bff",
                            component="background_warming",
                        )

                        stats = await self.warming_service.engine.warm_by_strategy(
                            strategy=warming_strategy, limit=limit, dry_run=False
                        )

                        logger.debug(
                            "Continuous warming completed",
                            strategy=strategy,
                            total_targets=stats.total_targets,
                            successful=stats.successful_targets,
                            service="bff",
                            component="background_warming",
                        )
                    else:
                        logger.warning(
                            "Unknown warming strategy",
                            strategy=strategy,
                            service="bff",
                            component="background_warming",
                        )

                except Exception as e:
                    logger.error(
                        "Error in continuous warming",
                        error=str(e),
                        service="bff",
                        component="background_warming",
                    )

                ***REMOVED*** Wait for next interval
                await asyncio.sleep(interval_minutes * 60)

        except asyncio.CancelledError:
            logger.info(
                "Continuous warming task cancelled", service="bff", component="background_warming"
            )
        except Exception as e:
            logger.error(
                "Continuous warming task failed",
                error=str(e),
                service="bff",
                component="background_warming",
            )

    def _is_time_to_run(self, current_time: time, target_time: time) -> bool:
        """Check if current time is within 1 minute of target time."""
        current_minutes = current_time.hour * 60 + current_time.minute
        target_minutes = target_time.hour * 60 + target_time.minute

        ***REMOVED*** Allow 1 minute window
        return abs(current_minutes - target_minutes) <= 1

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of background warming service."""
        return {
            "service": "background_warming",
            "running": not self._should_stop,
            "active_tasks": len([t for t in self._running_tasks if not t.done()]),
            "total_tasks": len(self._running_tasks),
            "schedule_config": {
                name: {
                    "enabled": config.get("enabled", True),
                    "strategy": config.get("strategy"),
                    "limit": config.get("limit"),
                }
                for name, config in self._schedule_config.items()
            },
        }

    def get_status(self) -> Dict[str, Any]:
        """Get detailed status of the background warming service."""
        task_statuses = {}
        for task in self._running_tasks:
            task_statuses[task.get_name() or "unnamed"] = {
                "done": task.done(),
                "cancelled": task.cancelled(),
                "exception": str(task.exception()) if task.done() and task.exception() else None,
            }

        return {
            "running": not self._should_stop,
            "total_tasks": len(self._running_tasks),
            "active_tasks": len([t for t in self._running_tasks if not t.done()]),
            "task_statuses": task_statuses,
            "schedule_config": self._schedule_config,
        }


***REMOVED*** Global instance
_background_warming_service: Optional[BackgroundWarmingService] = None


def get_background_warming_service() -> BackgroundWarmingService:
    """Get the global background warming service instance."""
    global _background_warming_service
    if _background_warming_service is None:
        _background_warming_service = BackgroundWarmingService()
    return _background_warming_service


async def start_background_warming() -> None:
    """Start the background warming service."""
    service = get_background_warming_service()
    await service.start()


async def stop_background_warming() -> None:
    """Stop the background warming service."""
    global _background_warming_service
    if _background_warming_service is not None:
        await _background_warming_service.stop()
        _background_warming_service = None

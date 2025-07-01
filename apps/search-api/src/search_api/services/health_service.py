"""Health check service for the Search API.

This service provides comprehensive health checks for all dependencies:
- Backend API service
- Redis for search suggestions and caching
"""

import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from config.logging import get_logger
from cache.manager import CacheManager
from fast_core.dependencies.client_factory import get_service_client

logger = get_logger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    is_healthy: bool
    status: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthService:
    """Service for performing health checks on all dependencies."""

    def __init__(self, cache_manager: Optional[CacheManager] = None) -> None:
        """Initialize the health service.

        Args:
            cache_manager: Optional cache manager for Redis health checks
        """
        self.cache_manager = cache_manager

    async def check_all(self) -> Dict[str, HealthCheckResult]:
        """Check health of all services.

        Returns:
            Dictionary mapping service names to health check results
        """
        ***REMOVED*** Run all health checks concurrently
        backend_task = asyncio.create_task(self.check_backend_api())
        redis_task = asyncio.create_task(self.check_redis())

        ***REMOVED*** Wait for all checks to complete
        gather_results = await asyncio.gather(backend_task, redis_task, return_exceptions=True)

        ***REMOVED*** Handle any exceptions and build results
        results: Dict[str, HealthCheckResult] = {}

        backend_result, redis_result = gather_results

        ***REMOVED*** Process backend result
        if isinstance(backend_result, Exception):
            results["backend_api"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(backend_result)
            )
        elif isinstance(backend_result, HealthCheckResult):
            results["backend_api"] = backend_result
        else:
            results["backend_api"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        ***REMOVED*** Process redis result
        if isinstance(redis_result, Exception):
            results["redis"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(redis_result)
            )
        elif isinstance(redis_result, HealthCheckResult):
            results["redis"] = redis_result
        else:
            results["redis"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        return results

    async def check_backend_api(self) -> HealthCheckResult:
        """Check Backend API health using Service Client Factory.

        Returns:
            Health check result for Backend API
        """
        start_time = time.time()

        try:
            backend_client_dep = get_service_client("backend")
            backend_client = await backend_client_dep()

            ***REMOVED*** Simple health check to backend
            response = await backend_client.get("/health/basic")
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                response_data = response.json()
                return HealthCheckResult(
                    is_healthy=True,
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    details={
                        "backend_status": response_data.get("status", "unknown"),
                        "backend_version": response_data.get("version", "unknown"),
                        "url": str(backend_client.base_url),
                    },
                )
            else:
                return HealthCheckResult(
                    is_healthy=False,
                    status="unhealthy",
                    response_time_ms=round(response_time, 2),
                    error=f"Backend API returned status {response.status_code}",
                    details={"url": str(backend_client.base_url)},
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Backend API health check failed: {e}")

            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    async def check_redis(self) -> HealthCheckResult:
        """Check Redis health.

        Returns:
            Health check result for Redis
        """
        start_time = time.time()

        try:
            if self.cache_manager:
                ***REMOVED*** Test Redis connection using cache manager
                test_key = "health_check:search_api"
                test_value = "ping"

                ***REMOVED*** Try to set and get a test value
                await self.cache_manager.set_json(test_key, test_value, ttl=10)
                retrieved_value = await self.cache_manager.get_json(test_key)

                response_time = (time.time() - start_time) * 1000

                if retrieved_value == test_value:
                    return HealthCheckResult(
                        is_healthy=True,
                        status="healthy",
                        response_time_ms=round(response_time, 2),
                        details={
                            "provider": "redis",
                            "cache_key_prefix": self.cache_manager.settings.cache_key_prefix,
                        },
                    )
                else:
                    return HealthCheckResult(
                        is_healthy=False,
                        status="unhealthy",
                        response_time_ms=round(response_time, 2),
                        error="Redis test value mismatch",
                    )
            else:
                ***REMOVED*** No cache manager available - try basic connection check
                try:
                    from search_api.config.app import settings
                    import redis.asyncio as redis

                    redis_client = redis.from_url(settings.redis_url)
                    await redis_client.ping()
                    await redis_client.close()

                    response_time = (time.time() - start_time) * 1000

                    return HealthCheckResult(
                        is_healthy=True,
                        status="healthy",
                        response_time_ms=round(response_time, 2),
                        details={
                            "provider": "redis",
                            "connection_method": "direct",
                        },
                    )
                except Exception as direct_error:
                    response_time = (time.time() - start_time) * 1000
                    return HealthCheckResult(
                        is_healthy=False,
                        status="unhealthy",
                        response_time_ms=round(response_time, 2),
                        error=f"Direct Redis connection failed: {str(direct_error)}",
                    )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Redis health check failed: {e}")

            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    def close(self) -> None:
        """Close all client connections."""
        if self.cache_manager:
            ***REMOVED*** Cache manager handles its own cleanup
            pass


***REMOVED*** Global health service instance
_health_service: Optional[HealthService] = None


def get_health_service(cache_manager: Optional[CacheManager] = None) -> HealthService:
    """Get the global health service instance.

    Args:
        cache_manager: Optional cache manager for Redis health checks

    Returns:
        HealthService instance
    """
    global _health_service

    if _health_service is None:
        _health_service = HealthService(cache_manager=cache_manager)

    return _health_service


def close_health_service() -> None:
    """Close the global health service instance."""
    global _health_service

    if _health_service is not None:
        _health_service.close()
        _health_service = None

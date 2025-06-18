"""Health check service for the Backend API.

This service provides comprehensive health checks for all dependencies:
- PostgreSQL database
- Redis cache
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import redis
from redis.exceptions import RedisError
from sqlmodel import Session, text

from backend_api.config.app import settings
from config.logging import get_logger
from backend_api.db.database import get_db

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

    def __init__(self) -> None:
        """Initialize the health service."""
        self._redis_client: Optional[redis.Redis[str]] = None

    async def check_all(self) -> Dict[str, HealthCheckResult]:
        """Check health of all services.

        Returns:
            Dictionary mapping service names to health check results
        """
        ***REMOVED*** Run all health checks concurrently
        postgres_task = asyncio.create_task(self.check_postgres())
        redis_task = asyncio.create_task(self.check_redis())

        ***REMOVED*** Wait for all checks to complete
        postgres_result, redis_result = await asyncio.gather(
            postgres_task, redis_task, return_exceptions=True
        )

        ***REMOVED*** Handle any exceptions and build results
        results: Dict[str, HealthCheckResult] = {}

        if isinstance(postgres_result, Exception):
            results["postgres"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(postgres_result)
            )
        elif isinstance(postgres_result, HealthCheckResult):
            results["postgres"] = postgres_result
        else:
            ***REMOVED*** This shouldn't happen, but handle it
            results["postgres"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        if isinstance(redis_result, Exception):
            results["redis"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(redis_result)
            )
        elif isinstance(redis_result, HealthCheckResult):
            results["redis"] = redis_result
        else:
            ***REMOVED*** This shouldn't happen, but handle it
            results["redis"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        return results

    async def check_postgres(self) -> HealthCheckResult:
        """Check PostgreSQL database health.

        Returns:
            Health check result for PostgreSQL
        """
        ***REMOVED*** Use the sync version since we don't have asyncpg dependency
        return self.check_postgres_sync()

    async def check_redis(self) -> HealthCheckResult:
        """Check Redis cache health.

        Returns:
            Health check result for Redis
        """
        start_time = time.time()

        try:
            ***REMOVED*** Create Redis client if not exists
            if self._redis_client is None:
                self._redis_client = redis.Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=settings.redis_socket_connect_timeout,
                    socket_timeout=settings.redis_socket_timeout,
                    retry_on_timeout=settings.redis_retry_on_timeout,
                    max_connections=settings.redis_max_connections,
                )

            ***REMOVED*** Ping Redis
            ping_result = self._redis_client.ping()

            if ping_result:
                ***REMOVED*** Get Redis info
                info = self._redis_client.info()
                response_time = (time.time() - start_time) * 1000

                return HealthCheckResult(
                    is_healthy=True,
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    details={
                        "version": info.get("redis_version", "Unknown"),
                        "mode": info.get("redis_mode", "Unknown"),
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory_human": info.get("used_memory_human", "Unknown"),
                        "uptime_in_days": info.get("uptime_in_days", 0),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0),
                        "total_commands_processed": info.get("total_commands_processed", 0),
                    },
                )
            else:
                response_time = (time.time() - start_time) * 1000
                return HealthCheckResult(
                    is_healthy=False,
                    status="unhealthy",
                    response_time_ms=round(response_time, 2),
                    error="Redis ping returned False",
                )

        except RedisError as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Redis health check failed: {e}")

            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=f"Redis error: {str(e)}",
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

    def check_postgres_sync(self) -> HealthCheckResult:
        """Synchronous PostgreSQL health check using existing database session.

        Returns:
            Health check result for PostgreSQL
        """
        start_time = time.time()

        try:
            ***REMOVED*** Use the existing database session
            with next(get_db()) as db:
                ***REMOVED*** Try a simple query
                result = db.execute(text("SELECT 1")).scalar()

                ***REMOVED*** Get version
                version_result = db.execute(text("SELECT version()")).scalar()
                version = version_result if version_result else "Unknown"

                ***REMOVED*** Get database size
                db_size_result = db.execute(
                    text("SELECT pg_size_pretty(pg_database_size(current_database())) as size")
                ).scalar()
                db_size = db_size_result if db_size_result else "Unknown"

                response_time = (time.time() - start_time) * 1000

                return HealthCheckResult(
                    is_healthy=True,
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    details={
                        "version": version,
                        "database_size": db_size,
                        "connection_successful": True,
                        "query_result": result,
                    },
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"PostgreSQL sync health check failed: {e}")

            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    def close(self) -> None:
        """Close all client connections."""
        if self._redis_client is not None:
            try:
                self._redis_client.close()
            except Exception as e:
                logger.warning(f"Error closing Redis client: {e}")
            finally:
                self._redis_client = None


***REMOVED*** Global health service instance
_health_service: Optional[HealthService] = None


def get_health_service() -> HealthService:
    """Get the global health service instance.

    Returns:
        HealthService instance
    """
    global _health_service

    if _health_service is None:
        _health_service = HealthService()

    return _health_service


def close_health_service() -> None:
    """Close the global health service instance."""
    global _health_service

    if _health_service is not None:
        _health_service.close()
        _health_service = None

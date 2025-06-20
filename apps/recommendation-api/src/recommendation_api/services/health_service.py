"""Health check service for the Recommendation API.

This service provides comprehensive health checks for all dependencies:
- PostgreSQL database
- Redis cache
- Qdrant vector database
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import asyncpg
import redis
from config.logging import get_logger
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from redis.exceptions import RedisError

from recommendation_api.config import settings

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

    def __init__(self):
        """Initialize the health service."""
        self._redis_client: Optional[redis.Redis] = None
        self._qdrant_client: Optional[QdrantClient] = None

    async def check_all(self) -> Dict[str, HealthCheckResult]:
        """Check health of all services.

        Returns:
            Dictionary mapping service names to health check results
        """
        results = {}

        ***REMOVED*** Run all health checks concurrently
        postgres_task = asyncio.create_task(self.check_postgres())
        redis_task = asyncio.create_task(self.check_redis())
        qdrant_task = asyncio.create_task(self.check_qdrant())

        ***REMOVED*** Wait for all checks to complete
        postgres_result, redis_result, qdrant_result = await asyncio.gather(
            postgres_task, redis_task, qdrant_task, return_exceptions=True
        )

        ***REMOVED*** Handle any exceptions
        if isinstance(postgres_result, Exception):
            postgres_result = HealthCheckResult(
                is_healthy=False, status="error", error=str(postgres_result)
            )

        if isinstance(redis_result, Exception):
            redis_result = HealthCheckResult(
                is_healthy=False, status="error", error=str(redis_result)
            )

        if isinstance(qdrant_result, Exception):
            qdrant_result = HealthCheckResult(
                is_healthy=False, status="error", error=str(qdrant_result)
            )

        results["postgres"] = postgres_result
        results["redis"] = redis_result
        results["qdrant"] = qdrant_result

        return results

    async def check_postgres(self) -> HealthCheckResult:
        """Check PostgreSQL database health.

        Returns:
            Health check result for PostgreSQL
        """
        start_time = time.time()

        try:
            ***REMOVED*** Connect and execute a simple query
            conn = await asyncpg.connect(settings.database_url)
            try:
                result = await conn.execute("SELECT 1")
                version_result = await conn.fetchrow("SELECT version()")
                version = version_result["version"] if version_result else "Unknown"

                response_time = (time.time() - start_time) * 1000

                return HealthCheckResult(
                    is_healthy=True,
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    details={"version": version, "connection_successful": True},
                )
            finally:
                await conn.close()

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"PostgreSQL health check failed: {e}")

            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

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
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
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

    async def check_qdrant(self) -> HealthCheckResult:
        """Check Qdrant vector database health.

        Returns:
            Health check result for Qdrant
        """
        start_time = time.time()

        try:
            ***REMOVED*** Create Qdrant client if not exists
            if self._qdrant_client is None:
                self._qdrant_client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key,
                    timeout=10,
                )

            ***REMOVED*** Get collections to test connectivity
            collections = self._qdrant_client.get_collections()
            response_time = (time.time() - start_time) * 1000

            ***REMOVED*** Check if our collection exists
            collection_exists = any(
                col.name == settings.qdrant_collection_name for col in collections.collections
            )

            collection_info = None
            if collection_exists:
                try:
                    collection_info = self._qdrant_client.get_collection(
                        settings.qdrant_collection_name
                    )
                except Exception as e:
                    logger.warning(f"Could not get collection info: {e}")

            return HealthCheckResult(
                is_healthy=True,
                status="healthy",
                response_time_ms=round(response_time, 2),
                details={
                    "total_collections": len(collections.collections),
                    "collection_exists": collection_exists,
                    "collection_name": settings.qdrant_collection_name,
                    "vectors_count": (collection_info.vectors_count if collection_info else None),
                    "points_count": (collection_info.points_count if collection_info else None),
                },
            )

        except ResponseHandlingException as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Qdrant health check failed: {e}")

            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=f"Qdrant API error: {str(e)}",
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Qdrant health check failed: {e}")

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

        if self._qdrant_client is not None:
            try:
                self._qdrant_client.close()
            except Exception as e:
                logger.warning(f"Error closing Qdrant client: {e}")
            finally:
                self._qdrant_client = None


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


async def close_health_service() -> None:
    """Close the global health service instance."""
    global _health_service

    if _health_service is not None:
        _health_service.close()
        _health_service = None

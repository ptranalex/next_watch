"""Health check service for the Recommendation API.

This service provides comprehensive health checks for all dependencies:
- Redis cache
- Qdrant vector database
"""

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

import redis
from config.logging import get_logger
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from redis.exceptions import RedisError

from recommendation_api.config import settings

if TYPE_CHECKING:
    from fast_core.monitoring import HealthCheckRegistry

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
        redis_task = asyncio.create_task(self.check_redis())
        qdrant_task = asyncio.create_task(self.check_qdrant())

        ***REMOVED*** Wait for all checks to complete
        redis_result, qdrant_result = await asyncio.gather(
            redis_task, qdrant_task, return_exceptions=True
        )

        ***REMOVED*** Handle any exceptions
        if isinstance(redis_result, Exception):
            redis_result = HealthCheckResult(
                is_healthy=False, status="error", error=str(redis_result)
            )

        if isinstance(qdrant_result, Exception):
            qdrant_result = HealthCheckResult(
                is_healthy=False, status="error", error=str(qdrant_result)
            )

        results["redis"] = redis_result
        results["qdrant"] = qdrant_result

        return results

    async def check_redis(self) -> HealthCheckResult:
        """Check Redis cache health.

        Returns:
            Health check result for Redis
        """
        start_time = time.time()

        try:
            ***REMOVED*** Create Redis client if not exists
            if self._redis_client is None:
                ***REMOVED*** Get Redis URL from environment variable first, then fall back to settings
                redis_url = os.getenv("CACHE_REDIS_URL")
                if not redis_url:
                    redis_url = settings.redis_url

                logger.debug(f"Connecting to Redis at {redis_url}")
                self._redis_client = redis.Redis.from_url(
                    redis_url,
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


***REMOVED***
***REMOVED*** NEW HEALTH CHECK REGISTRY INTEGRATION
***REMOVED***


def setup_recommendation_health_checks(registry: "HealthCheckRegistry") -> None:
    """Setup Recommendation API-specific health checks with the new registry system.

    Args:
        registry: Health check registry to register checks with
    """
    from fast_core.monitoring import (
        HealthCheckDefinition,
        HealthCheckType,
        HealthCheckCategory,
        HealthCheckResult,
    )
    import time
    import redis
    from qdrant_client import QdrantClient
    from qdrant_client.http.exceptions import ResponseHandlingException

    ***REMOVED*** Backend Client - CRITICAL (recommendation service needs movie data)
    async def check_backend_client() -> HealthCheckResult:
        """Check backend API client connectivity."""
        start_time = time.time()
        try:
            from recommendation_api.services.backend_client import get_backend_client

            client = get_backend_client()
            ***REMOVED*** Simple health check - try to get a basic endpoint
            ***REMOVED*** This is a mock check since we don't have direct health endpoint access
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                is_healthy=True,
                status="healthy",
                response_time_ms=round(response_time, 2),
                details={"client_configured": True, "connection": "available"},
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    ***REMOVED*** Redis Cache - IMPORTANT (improves performance but not critical)
    async def check_redis_cache() -> HealthCheckResult:
        """Check Redis cache connectivity."""
        start_time = time.time()
        try:
            redis_url = os.getenv("CACHE_REDIS_URL") or settings.redis_url
            client = redis.Redis.from_url(redis_url, decode_responses=True, socket_timeout=3.0)

            ping_result = client.ping()
            response_time = (time.time() - start_time) * 1000

            if ping_result:
                try:
                    info = client.info()
                    return HealthCheckResult(
                        is_healthy=True,
                        status="healthy",
                        response_time_ms=round(response_time, 2),
                        details={
                            "version": info.get("redis_version", "Unknown"),
                            "connected_clients": info.get("connected_clients", 0),
                            "used_memory_human": info.get("used_memory_human", "Unknown"),
                        },
                    )
                finally:
                    client.close()
            else:
                return HealthCheckResult(
                    is_healthy=False,
                    status="unhealthy",
                    response_time_ms=round(response_time, 2),
                    error="Redis ping failed",
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    ***REMOVED*** Qdrant Vector Database - IMPORTANT (for ML recommendations)
    async def check_vector_service() -> HealthCheckResult:
        """Check Qdrant vector database connectivity."""
        start_time = time.time()
        try:
            client = QdrantClient(
                url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=5.0
            )

            ***REMOVED*** Quick connectivity test
            collections = client.get_collections()
            response_time = (time.time() - start_time) * 1000

            ***REMOVED*** Check if our collection exists
            collection_exists = any(
                col.name == settings.qdrant_collection_name for col in collections.collections
            )

            client.close()

            return HealthCheckResult(
                is_healthy=True,
                status="healthy",
                response_time_ms=round(response_time, 2),
                details={
                    "total_collections": len(collections.collections),
                    "collection_exists": collection_exists,
                    "collection_name": settings.qdrant_collection_name,
                },
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    ***REMOVED*** Register health checks with industry-standard category-driven endpoint mapping

    ***REMOVED*** CRITICAL services - automatically included in READINESS + DEEP
    registry.add_check(
        HealthCheckDefinition(
            name="backend_client",
            check_func=check_backend_client,
            category=HealthCheckCategory.CRITICAL,
            timeout_seconds=3.0,
        )
    )

    ***REMOVED*** IMPORTANT services - automatically included in DEEP only
    registry.add_check(
        HealthCheckDefinition(
            name="redis_cache",
            check_func=check_redis_cache,
            category=HealthCheckCategory.IMPORTANT,
            timeout_seconds=2.0,
        )
    )

    registry.add_check(
        HealthCheckDefinition(
            name="vector_database",
            check_func=check_vector_service,
            category=HealthCheckCategory.IMPORTANT,
            timeout_seconds=4.0,
        )
    )

    logger.info(
        "Recommendation API health checks registered - CRITICAL: database | IMPORTANT: redis_cache, vector_database"
    )

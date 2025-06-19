"""Health check service for the BFF.

This service provides health checks for all external dependencies:
- Backend API service
- Recommendation API service
- Auth API service (if configured)
- Redis cache (if accessible)
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from config.logging import get_logger
from httpx import HTTPStatusError, RequestError

from bff_api.config.app import settings
from bff_api.services.cache_service import get_cache_service

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
    """Service for performing health checks on all BFF dependencies."""

    def __init__(self) -> None:
        """Initialize the health service."""
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for health checks.

        Returns:
            Configured HTTP client
        """
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),  ***REMOVED*** 10 second timeout for health checks
                limits=httpx.Limits(max_connections=10),
            )
        return self._http_client

    async def check_all(self) -> Dict[str, HealthCheckResult]:
        """Check health of all external services.

        Returns:
            Dictionary mapping service names to health check results
        """
        ***REMOVED*** Run all health checks concurrently
        backend_task = asyncio.create_task(self.check_backend_api())
        reco_task = asyncio.create_task(self.check_recommendation_api())
        auth_task = asyncio.create_task(self.check_auth_api())
        cache_task = asyncio.create_task(self.check_cache())

        ***REMOVED*** Wait for all checks to complete
        backend_result, reco_result, auth_result, cache_result = await asyncio.gather(
            backend_task, reco_task, auth_task, cache_task, return_exceptions=True
        )

        ***REMOVED*** Handle any exceptions and build results
        results: Dict[str, HealthCheckResult] = {}

        ***REMOVED*** Process backend API result
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

        ***REMOVED*** Process recommendation API result
        if isinstance(reco_result, Exception):
            results["recommendation_api"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(reco_result)
            )
        elif isinstance(reco_result, HealthCheckResult):
            results["recommendation_api"] = reco_result
        else:
            results["recommendation_api"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        ***REMOVED*** Process auth API result
        if isinstance(auth_result, Exception):
            results["auth_api"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(auth_result)
            )
        elif isinstance(auth_result, HealthCheckResult):
            results["auth_api"] = auth_result
        else:
            results["auth_api"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        ***REMOVED*** Process cache result
        if isinstance(cache_result, Exception):
            results["cache"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(cache_result)
            )
        elif isinstance(cache_result, HealthCheckResult):
            results["cache"] = cache_result
        else:
            results["cache"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        return results

    async def check_cache(self) -> HealthCheckResult:
        """Check cache service health.

        Returns:
            Health check result for cache service
        """
        start_time = time.time()

        try:
            cache_service = get_cache_service()
            is_healthy = await cache_service.health_check()
            response_time = (time.time() - start_time) * 1000

            if is_healthy:
                return HealthCheckResult(
                    is_healthy=True,
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    details={
                        "provider": "redis",
                        "key_prefix": cache_service.settings.key_prefix,
                    },
                )
            else:
                return HealthCheckResult(
                    is_healthy=False,
                    status="unhealthy",
                    response_time_ms=round(response_time, 2),
                    error="Cache health check failed",
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Cache health check failed: {e}")
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    async def check_backend_api(self) -> HealthCheckResult:
        """Check Backend API health.

        Returns:
            Health check result for Backend API
        """
        start_time = time.time()

        try:
            client = await self._get_http_client()
            health_url = f"{settings.backend_api_url}/health"

            response = await client.get(health_url)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                ***REMOVED*** Try to parse response for additional details
                try:
                    health_data = response.json()
                    return HealthCheckResult(
                        is_healthy=True,
                        status="healthy",
                        response_time_ms=round(response_time, 2),
                        details={
                            "url": health_url,
                            "status_code": response.status_code,
                            "service_status": health_data.get("status", "unknown"),
                            "backend_checks": health_data.get("checks", {}),
                        },
                    )
                except Exception:
                    ***REMOVED*** JSON parsing failed, but 200 response is still healthy
                    return HealthCheckResult(
                        is_healthy=True,
                        status="healthy",
                        response_time_ms=round(response_time, 2),
                        details={
                            "url": health_url,
                            "status_code": response.status_code,
                            "note": "Health endpoint responded but JSON parsing failed",
                        },
                    )
            else:
                return HealthCheckResult(
                    is_healthy=False,
                    status="unhealthy",
                    response_time_ms=round(response_time, 2),
                    error=f"Backend API returned status {response.status_code}",
                )

        except RequestError as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Backend API health check failed: {e}")
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=f"Connection error: {str(e)}",
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

    async def check_recommendation_api(self) -> HealthCheckResult:
        """Check Recommendation API health.

        Returns:
            Health check result for Recommendation API
        """
        start_time = time.time()

        try:
            client = await self._get_http_client()
            health_url = f"{settings.reco_api_url}/health"

            response = await client.get(health_url)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                try:
                    health_data = response.json()
                    return HealthCheckResult(
                        is_healthy=True,
                        status="healthy",
                        response_time_ms=round(response_time, 2),
                        details={
                            "url": health_url,
                            "status_code": response.status_code,
                            "service_status": health_data.get("status", "unknown"),
                            "reco_checks": health_data.get("checks", {}),
                        },
                    )
                except Exception:
                    return HealthCheckResult(
                        is_healthy=True,
                        status="healthy",
                        response_time_ms=round(response_time, 2),
                        details={
                            "url": health_url,
                            "status_code": response.status_code,
                            "note": "Health endpoint responded but JSON parsing failed",
                        },
                    )
            else:
                return HealthCheckResult(
                    is_healthy=False,
                    status="unhealthy",
                    response_time_ms=round(response_time, 2),
                    error=f"Recommendation API returned status {response.status_code}",
                )

        except RequestError as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Recommendation API health check failed: {e}")
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=f"Connection error: {str(e)}",
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Recommendation API health check failed: {e}")
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    async def check_auth_api(self) -> HealthCheckResult:
        """Check Auth API health.

        Returns:
            Health check result for Auth API
        """
        start_time = time.time()

        try:
            client = await self._get_http_client()
            ***REMOVED*** Try the auth API health endpoint
            health_url = f"{settings.auth_api_url}/health"

            response = await client.get(health_url)
            response_time = (time.time() - start_time) * 1000

            ***REMOVED*** Auth API can return 200 (all healthy) or 503 (service up, dependencies unhealthy)
            if response.status_code in [200, 503]:
                try:
                    health_data = response.json()
                    service_status = health_data.get("status", "unknown")

                    ***REMOVED*** Service is considered "reachable" if it responds with health data
                    ***REMOVED*** Even if some dependencies are unhealthy (503), the auth service itself is up
                    return HealthCheckResult(
                        is_healthy=True,  ***REMOVED*** Service is reachable and responding
                        status="healthy" if response.status_code == 200 else "degraded",
                        response_time_ms=round(response_time, 2),
                        details={
                            "url": health_url,
                            "status_code": response.status_code,
                            "service_status": service_status,
                            "auth_checks": health_data.get("checks", {}),
                            "note": "Service responding" if response.status_code == 503 else None,
                        },
                    )
                except Exception:
                    ***REMOVED*** Even if JSON parsing fails, a 200/503 response means service is up
                    return HealthCheckResult(
                        is_healthy=True,
                        status="healthy" if response.status_code == 200 else "degraded",
                        response_time_ms=round(response_time, 2),
                        details={
                            "url": health_url,
                            "status_code": response.status_code,
                            "note": "Service responding but JSON parsing failed",
                        },
                    )
            else:
                return HealthCheckResult(
                    is_healthy=False,
                    status="unhealthy",
                    response_time_ms=round(response_time, 2),
                    error=f"Auth API returned status {response.status_code}",
                )

        except RequestError as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Auth API health check failed: {e}")
            ***REMOVED*** Auth API is optional for basic BFF functionality
            return HealthCheckResult(
                is_healthy=False,
                status="unavailable",
                response_time_ms=round(response_time, 2),
                error=f"Auth API unavailable: {str(e)}",
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Auth API health check failed: {e}")
            return HealthCheckResult(
                is_healthy=False,
                status="unavailable",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    async def close(self) -> None:
        """Close all client connections."""
        if self._http_client is not None:
            try:
                await self._http_client.aclose()
            except Exception as e:
                logger.warning(f"Error closing HTTP client: {e}")
            finally:
                self._http_client = None


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
        await _health_service.close()
        _health_service = None

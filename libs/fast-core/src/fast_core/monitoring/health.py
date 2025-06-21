"""Health check system for FastAPI applications.

This module provides a health check system for monitoring service dependencies
and reporting their status through a standard health check endpoint.
"""

import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

from config.logging import get_logger
from fastapi import Depends, FastAPI, Response, status

logger = get_logger(__name__)


class HealthCheckResult:
    """Result of a health check."""

    def __init__(
        self,
        is_healthy: bool,
        status: str = "",
        response_time_ms: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        """Initialize health check result.

        Args:
            is_healthy: Whether the check passed
            status: Status string (e.g., "healthy", "unhealthy")
            response_time_ms: Response time in milliseconds
            details: Additional details about the check
            error: Error message if the check failed
        """
        self.is_healthy = is_healthy
        self.status = status or ("healthy" if is_healthy else "unhealthy")
        self.response_time_ms = response_time_ms
        self.details = details or {}
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation of the result
        """
        result: Dict[str, Any] = {
            "status": self.status,
        }

        if self.response_time_ms is not None:
            result["response_time_ms"] = self.response_time_ms

        if self.details:
            result["details"] = self.details

        if self.error:
            result["error"] = self.error

        return result


class HealthCheck:
    """Health check system for monitoring service dependencies."""

    def __init__(self) -> None:
        """Initialize the health check system."""
        self._checks: List[Tuple[str, Callable[[], Awaitable[HealthCheckResult]]]] = []

    def add_check(
        self,
        name: str,
        check_func: Callable[[], Awaitable[HealthCheckResult]],
    ) -> None:
        """Add a health check function.

        Args:
            name: Name of the check
            check_func: Async function that returns health check result
        """
        self._checks.append((name, check_func))
        logger.debug(f"Added health check: {name}")

    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks.

        Returns:
            Health check results
        """
        results = {}
        overall_healthy = True

        for name, check_func in self._checks:
            start_time = time.time()
            try:
                result = await check_func()
                if not result.is_healthy:
                    overall_healthy = False

                results[name] = result.to_dict()
            except Exception as e:
                overall_healthy = False
                results[name] = HealthCheckResult(
                    is_healthy=False,
                    status="error",
                    response_time_ms=round((time.time() - start_time) * 1000, 2),
                    error=str(e),
                ).to_dict()

        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": time.time(),
            "checks": results,
        }


def setup_health_checks(
    app: FastAPI,
    settings: Any,
    path: str = "/health",
    include_details: bool = True,
    require_auth: bool = False,
) -> HealthCheck:
    """Set up health check endpoint.

    Args:
        app: FastAPI application
        settings: Application settings
        path: Health check endpoint path
        include_details: Whether to include detailed check results
        require_auth: Whether to require authentication

    Returns:
        HealthCheck instance
    """
    health_check = HealthCheck()

    ***REMOVED*** Define dependencies
    dependencies = []
    if require_auth:
        try:
            from fast_core.dependencies.auth import get_api_key

            dependencies.append(Depends(get_api_key))
        except ImportError:
            logger.warning(
                "Auth dependency not available, health check will not require authentication"
            )

    @app.get(
        path,
        tags=["Health"],
        summary="Service health check",
        description="Check the health of the service and its dependencies",
        dependencies=dependencies,
        response_model=None,  ***REMOVED*** Use dynamic response
    )
    async def health_endpoint() -> Dict[str, Any]:
        """Health check endpoint.

        Returns:
            Health check results
        """
        results = await health_check.run_checks()
        is_healthy = results["status"] == "healthy"

        ***REMOVED*** Simplify response if details not requested
        if not include_details:
            return {"status": results["status"]}

        return results

    logger.info(f"Health check endpoint registered at: {path}")
    return health_check


***REMOVED*** Common health check functions


async def check_database(db_session: Any) -> HealthCheckResult:
    """Check database connectivity.

    Args:
        db_session: Database session

    Returns:
        Health check result
    """
    start_time = time.time()
    try:
        ***REMOVED*** Execute simple query to check connectivity
        await db_session.execute("SELECT 1")
        response_time = (time.time() - start_time) * 1000

        return HealthCheckResult(
            is_healthy=True,
            status="healthy",
            response_time_ms=round(response_time, 2),
            details={"database": "connected"},
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return HealthCheckResult(
            is_healthy=False,
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            error=str(e),
        )


async def check_redis(redis_client: Any) -> HealthCheckResult:
    """Check Redis connectivity.

    Args:
        redis_client: Redis client

    Returns:
        Health check result
    """
    start_time = time.time()
    try:
        ***REMOVED*** Ping Redis to check connectivity
        ping_result = await redis_client.ping()
        response_time = (time.time() - start_time) * 1000

        if ping_result:
            ***REMOVED*** Get Redis info
            info = await redis_client.info()
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
        else:
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error="Redis ping returned False",
            )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return HealthCheckResult(
            is_healthy=False,
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            error=str(e),
        )

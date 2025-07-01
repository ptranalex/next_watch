"""Enhanced health check system for FastAPI services.

This module provides industry-standard health check endpoints following Kubernetes patterns:
- Liveness probes (/health/live): Basic process health
- Readiness probes (/health/ready): Critical dependencies for traffic routing
- Comprehensive health (/health): All dependencies for monitoring
- Deep diagnostics (/health/deep): Full diagnostic information

Key Features:
- Multi-endpoint architecture
- Health check categorization (critical, important, informational)
- Performance-optimized execution
- Fail-fast readiness logic
- Timeout and error handling
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set
from dataclasses import dataclass

import structlog
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


class HealthCheckType(Enum):
    """Health check endpoint types following Kubernetes patterns."""

    LIVENESS = "liveness"  ***REMOVED*** Basic process health check
    READINESS = "readiness"  ***REMOVED*** Traffic routing decision
    DEEP = "deep"  ***REMOVED*** Full diagnostic information


class HealthCheckCategory(Enum):
    """Health check criticality categories."""

    CRITICAL = "critical"  ***REMOVED*** Must pass for readiness
    IMPORTANT = "important"  ***REMOVED*** Affects functionality but not blocking
    INFORMATIONAL = "info"  ***REMOVED*** Monitoring and metrics only


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""

    is_healthy: bool
    status: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "healthy": self.is_healthy,
            "status": self.status,
        }

        if self.response_time_ms is not None:
            result["response_time_ms"] = self.response_time_ms

        if self.details:
            result["details"] = self.details

        if self.error:
            result["error"] = self.error

        return result


@dataclass
class HealthCheckDefinition:
    """Definition of a health check with metadata."""

    name: str
    check_func: Callable[[], Awaitable[HealthCheckResult]]
    types: Set[HealthCheckType]
    category: HealthCheckCategory
    timeout_seconds: float = 5.0
    cache_ttl_seconds: Optional[int] = None


class HealthCheckRegistry:
    """Registry for managing health checks across different endpoint types."""

    def __init__(self) -> None:
        """Initialize the health check registry."""
        self._checks: Dict[str, HealthCheckDefinition] = {}
        self._cache: Dict[str, tuple[HealthCheckResult, float]] = {}  ***REMOVED*** (result, timestamp)

    def add_check(self, definition: HealthCheckDefinition) -> None:
        """Add a health check to the registry.

        Args:
            definition: Health check definition with metadata
        """
        self._checks[definition.name] = definition
        logger.debug(f"Added health check: {definition.name} ({definition.category.value})")

    def get_checks_by_type(self, check_type: HealthCheckType) -> List[HealthCheckDefinition]:
        """Get all health checks for a specific endpoint type.

        Args:
            check_type: The health check type to filter by

        Returns:
            List of health check definitions for the specified type
        """
        return [check for check in self._checks.values() if check_type in check.types]

    def get_check_category(self, check_name: str) -> Optional[HealthCheckCategory]:
        """Get the category of a specific health check.

        Args:
            check_name: Name of the health check

        Returns:
            Health check category or None if not found
        """
        check = self._checks.get(check_name)
        return check.category if check else None

    async def run_checks_for_type(self, check_type: HealthCheckType) -> Dict[str, Any]:
        """Run all health checks for a specific endpoint type.

        Args:
            check_type: The health check type to execute

        Returns:
            Dictionary with check results and overall status
        """
        checks = self.get_checks_by_type(check_type)

        if not checks:
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "checks": {},
            }

        ***REMOVED*** Run checks concurrently with timeout
        tasks = []
        for check in checks:
            task = asyncio.create_task(self._run_single_check(check), name=check.name)
            tasks.append((check.name, task))

        ***REMOVED*** Wait for all checks with global timeout
        try:
            ***REMOVED*** Gather all results
            results = {}
            overall_healthy = True

            for check_name, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=10.0)  ***REMOVED*** Global timeout
                    results[check_name] = result.to_dict()

                    ***REMOVED*** Only consider CRITICAL and IMPORTANT checks for overall health status
                    ***REMOVED*** INFORMATIONAL checks are included for diagnostics but don't affect health
                    check_category = self.get_check_category(check_name)
                    if check_category in (
                        HealthCheckCategory.CRITICAL,
                        HealthCheckCategory.IMPORTANT,
                    ):
                        if not result.is_healthy:
                            overall_healthy = False

                except asyncio.TimeoutError:
                    logger.warning(f"Health check timeout: {check_name}")
                    results[check_name] = HealthCheckResult(
                        is_healthy=False, status="timeout", error="Health check timed out"
                    ).to_dict()

                    ***REMOVED*** Only affect overall health if this is a critical/important check
                    check_category = self.get_check_category(check_name)
                    if check_category in (
                        HealthCheckCategory.CRITICAL,
                        HealthCheckCategory.IMPORTANT,
                    ):
                        overall_healthy = False

                except Exception as e:
                    logger.error(f"Health check error: {check_name}: {e}")
                    results[check_name] = HealthCheckResult(
                        is_healthy=False, status="error", error=str(e)
                    ).to_dict()

                    ***REMOVED*** Only affect overall health if this is a critical/important check
                    check_category = self.get_check_category(check_name)
                    if check_category in (
                        HealthCheckCategory.CRITICAL,
                        HealthCheckCategory.IMPORTANT,
                    ):
                        overall_healthy = False

            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "checks": results,
            }

        except Exception as e:
            logger.error(f"Health check execution failed: {e}")
            return {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": str(e),
                "checks": {},
            }

    async def _run_single_check(self, check: HealthCheckDefinition) -> HealthCheckResult:
        """Run a single health check with timeout and caching.

        Args:
            check: Health check definition to execute

        Returns:
            Health check result
        """
        ***REMOVED*** Check cache if TTL is set
        if check.cache_ttl_seconds:
            cached = self._get_cached_result(check.name, check.cache_ttl_seconds)
            if cached:
                return cached

        start_time = time.time()

        try:
            ***REMOVED*** Run the check with individual timeout
            result = await asyncio.wait_for(check.check_func(), timeout=check.timeout_seconds)

            ***REMOVED*** Cache result if TTL is set
            if check.cache_ttl_seconds:
                self._cache[check.name] = (result, time.time())

            return result

        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="timeout",
                response_time_ms=round(response_time, 2),
                error=f"Health check timed out after {check.timeout_seconds}s",
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="error",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    def _get_cached_result(self, check_name: str, ttl_seconds: int) -> Optional[HealthCheckResult]:
        """Get cached result if still valid.

        Args:
            check_name: Name of the health check
            ttl_seconds: Time-to-live in seconds

        Returns:
            Cached result if valid, None otherwise
        """
        if check_name not in self._cache:
            return None

        cached_result, timestamp = self._cache[check_name]
        if time.time() - timestamp <= ttl_seconds:
            return cached_result

        ***REMOVED*** Remove expired cache entry
        del self._cache[check_name]
        return None


def setup_kubernetes_health_checks(
    app: FastAPI,
    settings: Any,
    base_path: str = "/health",
    include_deep: bool = True,
    require_auth_deep: bool = False,
) -> HealthCheckRegistry:
    """Setup industry-standard health endpoints following Kubernetes patterns.

    Creates:
    - GET /health/live    (liveness probe - always passes)
    - GET /health/ready   (readiness probe - critical deps only)
    - GET /health         (comprehensive - all deps, backward compat)
    - GET /health/deep    (full diagnostics - optional)

    Args:
        app: FastAPI application
        settings: Application settings
        base_path: Base path for health endpoints
        include_deep: Whether to include deep diagnostics endpoint
        require_auth_deep: Whether deep endpoint requires authentication

    Returns:
        HealthCheckRegistry for adding service-specific checks
    """
    registry = HealthCheckRegistry()
    service_name = getattr(settings, "service_name", "unknown")

    ***REMOVED*** Liveness endpoint - basic process health
    @app.get(f"{base_path}/live", tags=["Health"])
    async def liveness_probe() -> Dict[str, Any]:
        """Liveness probe for Kubernetes/Docker.

        Simple endpoint that always returns 200 if the service is running.
        Used by orchestrators to determine if the container should be restarted.
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": service_name,
        }

    ***REMOVED*** Readiness endpoint - critical dependencies only
    @app.get(f"{base_path}/ready", tags=["Health"])
    async def readiness_probe() -> JSONResponse:
        """Readiness probe for Kubernetes/Docker.

        Checks critical dependencies only to determine if the service
        is ready to handle traffic. Uses fail-fast logic.
        """
        results = await registry.run_checks_for_type(HealthCheckType.READINESS)

        ***REMOVED*** Fail-fast logic: ANY critical failure = not ready
        critical_services = {}
        is_ready = True

        for check_name, result in results["checks"].items():
            check_category = registry.get_check_category(check_name)
            if check_category == HealthCheckCategory.CRITICAL:
                is_healthy = result.get("healthy", False)
                critical_services[check_name] = is_healthy
                if not is_healthy:
                    is_ready = False

        status_code = 200 if is_ready else 503

        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if is_ready else "not_ready",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": service_name,
                "critical_services": critical_services,
            },
        )

    ***REMOVED*** Comprehensive endpoint - all dependencies (backward compatibility)
    @app.get(f"{base_path}", tags=["Health"])
    async def comprehensive_health() -> JSONResponse:
        """Comprehensive health check endpoint.

        Checks all dependencies (CRITICAL + IMPORTANT) for monitoring
        and backward compatibility. Returns detailed check results.
        """
        ***REMOVED*** Get both readiness and additional checks
        readiness_results = await registry.run_checks_for_type(HealthCheckType.READINESS)

        ***REMOVED*** Determine overall health based on all checks
        overall_healthy = readiness_results["status"] == "healthy"
        status_code = 200 if overall_healthy else 503

        ***REMOVED*** Build comprehensive response
        response_data = {
            "status": "healthy" if overall_healthy else "unhealthy",
            "service": service_name,
            "timestamp": readiness_results["timestamp"],
            "checks": readiness_results["checks"],
        }

        ***REMOVED*** Add service configuration info if available
        if hasattr(settings, "environment"):
            response_data["environment"] = settings.environment

        return JSONResponse(status_code=status_code, content=response_data)

    ***REMOVED*** Deep diagnostics endpoint (optional)
    if include_deep:
        ***REMOVED*** Setup dependencies for deep endpoint
        dependencies = []
        if require_auth_deep:
            try:
                from fast_core.dependencies.auth import get_api_key

                dependencies.append(Depends(get_api_key))
            except ImportError:
                logger.warning("Auth dependency not available for deep health endpoint")

        @app.get(f"{base_path}/deep", tags=["Health"], dependencies=dependencies)
        async def deep_health() -> JSONResponse:
            """Deep diagnostic health check endpoint.

            Provides comprehensive diagnostic information including
            all health checks, performance metrics, and configuration details.
            """
            results = await registry.run_checks_for_type(HealthCheckType.DEEP)

            ***REMOVED*** Add extra diagnostic information
            diagnostic_info = {
                "service": service_name,
                "timestamp": results["timestamp"],
                "status": results["status"],
                "checks": results["checks"],
                "diagnostics": {
                    "total_checks": len(results["checks"]),
                    "healthy_checks": sum(
                        1 for check in results["checks"].values() if check.get("healthy", False)
                    ),
                    "check_categories": {
                        "critical": len(
                            [
                                name
                                for name in results["checks"].keys()
                                if registry.get_check_category(name) == HealthCheckCategory.CRITICAL
                            ]
                        ),
                        "important": len(
                            [
                                name
                                for name in results["checks"].keys()
                                if registry.get_check_category(name)
                                == HealthCheckCategory.IMPORTANT
                            ]
                        ),
                        "informational": len(
                            [
                                name
                                for name in results["checks"].keys()
                                if registry.get_check_category(name)
                                == HealthCheckCategory.INFORMATIONAL
                            ]
                        ),
                    },
                },
            }

            ***REMOVED*** Add configuration information if available
            if hasattr(settings, "environment"):
                diagnostic_info["environment"] = settings.environment
            if hasattr(settings, "debug"):
                diagnostic_info["debug_mode"] = settings.debug

            status_code = 200 if results["status"] == "healthy" else 503

            return JSONResponse(status_code=status_code, content=diagnostic_info)

    logger.info(
        f"Health check endpoints registered",
        base_path=base_path,
        endpoints=["live", "ready", "health"] + (["deep"] if include_deep else []),
        service=service_name,
    )

    return registry


***REMOVED*** Utility functions for common health checks


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
        if hasattr(db_session, "execute"):
            ***REMOVED*** SQLAlchemy-style session
            await db_session.execute("SELECT 1")
        elif hasattr(db_session, "ping"):
            ***REMOVED*** Connection pool style
            await db_session.ping()
        else:
            ***REMOVED*** Generic test
            str(db_session)

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
            ***REMOVED*** Get Redis info for additional details
            try:
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
            except Exception:
                ***REMOVED*** Ping succeeded but info failed - still healthy
                return HealthCheckResult(
                    is_healthy=True,
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    details={"ping": "successful"},
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

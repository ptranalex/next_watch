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
import logging
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
    """Health check criticality categories that determine endpoint inclusion."""

    CRITICAL = "critical"  ***REMOVED*** Must pass for readiness - included in READINESS + DEEP
    IMPORTANT = "important"  ***REMOVED*** Affects functionality - included in DEEP only
    INFORMATIONAL = "info"  ***REMOVED*** Monitoring only - included in DEEP only


***REMOVED*** Industry-standard category-to-endpoint mapping
ENDPOINT_CATEGORY_MAPPING = {
    HealthCheckType.READINESS: [
        HealthCheckCategory.CRITICAL,  ***REMOVED*** Only critical services for traffic routing
    ],
    HealthCheckType.DEEP: [
        HealthCheckCategory.CRITICAL,  ***REMOVED*** All categories for comprehensive diagnostics
        HealthCheckCategory.IMPORTANT,
        HealthCheckCategory.INFORMATIONAL,
    ],
}


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
    """Definition of a health check with category-driven endpoint inclusion."""

    name: str
    check_func: Callable[[], Awaitable[HealthCheckResult]]
    category: HealthCheckCategory  ***REMOVED*** Category automatically determines endpoint inclusion
    timeout_seconds: float = 5.0
    cache_ttl_seconds: Optional[int] = None


class HealthCheckRegistry:
    """Registry for health checks with category-driven endpoint mapping."""

    def __init__(self) -> None:
        """Initialize the health check registry."""
        self._checks: Dict[str, HealthCheckDefinition] = {}
        self._cache: Dict[str, tuple[HealthCheckResult, float]] = {}  ***REMOVED*** (result, timestamp)

    def add_check(self, definition: HealthCheckDefinition) -> None:
        """Add a health check to the registry.

        Args:
            definition: Health check definition with category that determines endpoint inclusion
        """
        if definition.name in self._checks:
            logger.warning(f"Overriding existing health check: {definition.name}")

        self._checks[definition.name] = definition
        logger.debug(f"Registered health check: {definition.name} ({definition.category.value})")

    def _update_health_metrics(self, check_name: str, result: HealthCheckResult) -> None:
        """Update health metrics for a completed health check.

        Args:
            check_name: Name of the health check
            result: Health check result
        """
        try:
            ***REMOVED*** Import here to avoid circular dependencies
            from fast_core.monitoring.metrics import get_metrics_registry

            metrics_registry = get_metrics_registry()
            if not metrics_registry:
                return

            ***REMOVED*** Get check definition for category
            check_def = self._checks.get(check_name)
            if not check_def:
                return

            ***REMOVED*** Update individual health check metrics
            metrics_registry.update_health_check_status(
                check_name=check_name,
                check_category=check_def.category.value,
                is_healthy=result.is_healthy,
                duration_seconds=(
                    result.response_time_ms / 1000.0 if result.response_time_ms else None
                ),
            )

        except Exception as e:
            ***REMOVED*** Don't let metrics failures affect health checks
            logger.warning(f"Failed to update health metrics for {check_name}: {e}")

    def _update_overall_health_metrics(self, overall_status: str) -> None:
        """Update overall service health status metrics.

        Args:
            overall_status: Overall health status (healthy, degraded, unhealthy)
        """
        try:
            ***REMOVED*** Import here to avoid circular dependencies
            from fast_core.monitoring.metrics import get_metrics_registry

            metrics_registry = get_metrics_registry()
            if not metrics_registry:
                return

            ***REMOVED*** Update overall service health status
            metrics_registry.update_service_health_status(overall_status)

        except Exception as e:
            ***REMOVED*** Don't let metrics failures affect health checks
            logger.warning(f"Failed to update overall health metrics: {e}")

    def get_checks_by_type(self, check_type: HealthCheckType) -> List[HealthCheckDefinition]:
        """Get all health checks that should run for a specific endpoint type.

        Uses category-driven mapping to determine which checks belong to which endpoints.

        Args:
            check_type: The health check endpoint type

        Returns:
            List of health check definitions for the specified endpoint type
        """
        allowed_categories = ENDPOINT_CATEGORY_MAPPING.get(check_type, [])

        matching_checks = [
            check for check in self._checks.values() if check.category in allowed_categories
        ]

        logger.debug(
            f"Found {len(matching_checks)} checks for {check_type.value}: "
            f"{[check.name for check in matching_checks]}"
        )

        return matching_checks

    def get_check_category(self, check_name: str) -> Optional[HealthCheckCategory]:
        """Get the category of a specific health check.

        Args:
            check_name: Name of the health check

        Returns:
            Category of the health check, or None if not found
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
            critical_healthy = 0
            critical_total = 0
            non_critical_healthy = 0
            non_critical_total = 0

            for check_name, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=10.0)  ***REMOVED*** Global timeout
                    results[check_name] = result.to_dict()

                    ***REMOVED*** Count healthy status by category for degraded detection
                    check_category = self.get_check_category(check_name)
                    if check_category == HealthCheckCategory.CRITICAL:
                        critical_total += 1
                        if result.is_healthy:
                            critical_healthy += 1
                    else:
                        non_critical_total += 1
                        if result.is_healthy:
                            non_critical_healthy += 1

                except asyncio.TimeoutError:
                    logger.warning(f"Health check timeout: {check_name}")
                    results[check_name] = HealthCheckResult(
                        is_healthy=False, status="timeout", error="Health check timed out"
                    ).to_dict()

                    ***REMOVED*** Count timeout by category
                    check_category = self.get_check_category(check_name)
                    if check_category == HealthCheckCategory.CRITICAL:
                        critical_total += 1
                    else:
                        non_critical_total += 1

                except Exception as e:
                    logger.error(f"Health check error: {check_name}: {e}")
                    results[check_name] = HealthCheckResult(
                        is_healthy=False, status="error", error=str(e)
                    ).to_dict()

                    ***REMOVED*** Count error by category
                    check_category = self.get_check_category(check_name)
                    if check_category == HealthCheckCategory.CRITICAL:
                        critical_total += 1
                    else:
                        non_critical_total += 1

            ***REMOVED*** Determine overall status with degraded support
            all_critical_healthy = critical_total == 0 or critical_healthy == critical_total
            all_non_critical_healthy = (
                non_critical_total == 0 or non_critical_healthy == non_critical_total
            )

            if all_critical_healthy and all_non_critical_healthy:
                status = "healthy"  ***REMOVED*** All services healthy
            elif all_critical_healthy:
                status = "degraded"  ***REMOVED*** Critical services up, some non-critical down
            else:
                status = "unhealthy"  ***REMOVED*** Any critical service down

            ***REMOVED*** Update overall health metrics
            self._update_overall_health_metrics(status)

            return {
                "status": status,
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
                ***REMOVED*** Update metrics even for cached results
                self._update_health_metrics(check.name, cached)
                return cached

        start_time = time.time()

        try:
            ***REMOVED*** Run the check with individual timeout
            result = await asyncio.wait_for(check.check_func(), timeout=check.timeout_seconds)

            ***REMOVED*** Cache result if TTL is set
            if check.cache_ttl_seconds:
                self._cache[check.name] = (result, time.time())

            ***REMOVED*** Update health metrics
            self._update_health_metrics(check.name, result)

            return result

        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                is_healthy=False,
                status="timeout",
                response_time_ms=round(response_time, 2),
                error=f"Health check timed out after {check.timeout_seconds}s",
            )

            ***REMOVED*** Update health metrics
            self._update_health_metrics(check.name, result)

            return result
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                is_healthy=False,
                status="error",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

            ***REMOVED*** Update health metrics
            self._update_health_metrics(check.name, result)

            return result

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

        Industry best practice: This endpoint should check ALL services
        for monitoring purposes, unlike readiness which only checks critical ones.
        """
        ***REMOVED*** Run both READINESS and DEEP checks to get comprehensive coverage
        readiness_checks = registry.get_checks_by_type(HealthCheckType.READINESS)
        deep_checks = registry.get_checks_by_type(HealthCheckType.DEEP)

        ***REMOVED*** Combine all unique checks for comprehensive coverage (deduplicate by name)
        all_checks_dict = {}
        for check in readiness_checks + deep_checks:
            all_checks_dict[check.name] = check
        all_checks = list(all_checks_dict.values())

        ***REMOVED*** Execute all checks concurrently
        tasks = []
        for check in all_checks:
            task = asyncio.create_task(registry._run_single_check(check), name=check.name)
            tasks.append((check.name, task))

        ***REMOVED*** Gather results with proper categorization
        results = {}
        critical_healthy = 0
        critical_total = 0
        important_healthy = 0
        important_total = 0
        info_healthy = 0
        info_total = 0

        for check_name, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=10.0)
                results[check_name] = result.to_dict()

                ***REMOVED*** Count by category for comprehensive status determination
                check_category = registry.get_check_category(check_name)
                if check_category == HealthCheckCategory.CRITICAL:
                    critical_total += 1
                    if result.is_healthy:
                        critical_healthy += 1
                elif check_category == HealthCheckCategory.IMPORTANT:
                    important_total += 1
                    if result.is_healthy:
                        important_healthy += 1
                else:  ***REMOVED*** INFORMATIONAL
                    info_total += 1
                    if result.is_healthy:
                        info_healthy += 1

            except (asyncio.TimeoutError, Exception) as e:
                error_msg = "timeout" if isinstance(e, asyncio.TimeoutError) else str(e)
                results[check_name] = HealthCheckResult(
                    is_healthy=False, status="error", error=error_msg
                ).to_dict()

                ***REMOVED*** Count errors by category
                check_category = registry.get_check_category(check_name)
                if check_category == HealthCheckCategory.CRITICAL:
                    critical_total += 1
                elif check_category == HealthCheckCategory.IMPORTANT:
                    important_total += 1
                else:
                    info_total += 1

        ***REMOVED*** Comprehensive status determination (includes all service types)
        all_critical_healthy = critical_total == 0 or critical_healthy == critical_total
        all_important_healthy = important_total == 0 or important_healthy == important_total

        if all_critical_healthy and all_important_healthy:
            registry_status = "healthy"  ***REMOVED*** All critical and important services healthy
        elif all_critical_healthy:
            registry_status = "degraded"  ***REMOVED*** Critical services up, some important down
        else:
            registry_status = "unhealthy"  ***REMOVED*** Any critical service down

        ***REMOVED*** Set HTTP status code based on registry status
        if registry_status == "healthy":
            status_code = 200
        elif registry_status == "degraded":
            status_code = 200  ***REMOVED*** Degraded services can still handle traffic
        else:
            status_code = 503  ***REMOVED*** unhealthy, error, etc.

        ***REMOVED*** Build comprehensive response using registry status
        response_data = {
            "status": registry_status,
            "service": service_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": results,
            "summary": {
                "critical": {"healthy": critical_healthy, "total": critical_total},
                "important": {"healthy": important_healthy, "total": important_total},
                "informational": {"healthy": info_healthy, "total": info_total},
            },
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

    ***REMOVED*** Store registry in app state for meta endpoint access
    app.state.health_registry = registry

    logger.info(
        f"Health check endpoints registered: {base_path} - "
        f"endpoints: {['live', 'ready', 'health'] + (['deep'] if include_deep else [])} - "
        f"service: {service_name}"
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

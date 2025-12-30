"""Meta endpoints system for FastAPI services.

This module provides standardized service metadata endpoints following industry best practices.
Similar to Spring Boot Actuator or .NET Health Checks, it exposes service information
for service discovery, debugging, and operational monitoring.
"""

import datetime
import os
import platform
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter, Request

try:
    from fast_core.routing.versioning import APIVersion

    VERSIONING_AVAILABLE = True
except ImportError:
    VERSIONING_AVAILABLE = False

try:
    from fast_core.monitoring.health import HealthCheckRegistry

    HEALTH_MONITORING_AVAILABLE = True
except ImportError:
    HEALTH_MONITORING_AVAILABLE = False


async def _determine_service_status(
    request: Request, health_check_provider: Callable | None = None
) -> str:
    """Determine dynamic service status based on health registry.

    Args:
        request: FastAPI request object
        health_check_provider: Optional custom health check function

    Returns:
        Service status: "operational", "degraded", "unhealthy", or "unknown"
    """
    try:
        # Primary: Use health registry from app state (respects CRITICAL flags)
        if hasattr(request.app.state, "health_registry") and request.app.state.health_registry:
            return await _get_status_from_registry(request.app.state.health_registry)

        # Fallback: Use custom health check provider
        if health_check_provider:
            return await _get_status_from_provider(health_check_provider, request)

        # No health system available
        return "unknown"

    except Exception as e:
        # Log error but don't fail the meta endpoint
        import logging

        logging.warning(f"Failed to determine service status: {e}")
        return "unknown"


async def _get_status_from_registry(registry: "HealthCheckRegistry") -> str:
    """Get status from health registry with CRITICAL flag support."""
    from fast_core.monitoring.health import HealthCheckCategory, HealthCheckType

    # Get comprehensive health status (CRITICAL + IMPORTANT services)
    # This matches the logic used by the /health endpoint for consistent status
    comprehensive_results = await registry.run_checks_for_type(HealthCheckType.DEEP)
    checks = comprehensive_results.get("checks", {})

    # Count critical vs important health status (aligns with comprehensive health endpoint)
    critical_healthy = 0
    critical_total = 0
    important_healthy = 0
    important_total = 0

    for check_name, check_result in checks.items():
        is_healthy = check_result.get("healthy", False)
        category = registry.get_check_category(check_name)

        if category == HealthCheckCategory.CRITICAL:
            critical_total += 1
            if is_healthy:
                critical_healthy += 1
        elif category == HealthCheckCategory.IMPORTANT:
            important_total += 1
            if is_healthy:
                important_healthy += 1
        # Note: INFORMATIONAL checks don't affect meta endpoint status

    # Status determination logic (matches /health endpoint behavior)
    all_critical_healthy = critical_total == 0 or critical_healthy == critical_total
    all_important_healthy = important_total == 0 or important_healthy == important_total

    if all_critical_healthy and all_important_healthy:
        return "operational"  # All critical and important services healthy
    elif all_critical_healthy:
        return "degraded"  # Critical services up, some important down
    else:
        return "unhealthy"  # Any critical service down


async def _get_status_from_provider(health_check_provider: Callable, request: Request) -> str:
    """Get status from custom health check provider."""
    health_data = await health_check_provider(request)

    if isinstance(health_data, str):
        return health_data

    if isinstance(health_data, dict):
        if "status" in health_data:
            status_value = health_data["status"]
            return str(status_value) if status_value else "unknown"

        # Fallback: simple count-based logic
        checks = health_data.get("checks", {})
        if checks:
            healthy_count = sum(
                1
                for check in checks.values()
                if check.get("healthy", False) or check.get("status") == "healthy"
            )
            total_count = len(checks)

            if healthy_count == total_count:
                return "operational"
            elif healthy_count == 0:
                return "unhealthy"
            else:
                return "degraded"

    return "unknown"


def create_meta_router(
    service_name: str,
    service_description: str,
    version: str = "0.1.0",
    features: list[str] | None = None,
    endpoints: dict[str, str] | None = None,
    debug_info_provider: Callable[[Request], dict[str, Any]] | None = None,
    health_check_provider: Callable[[Request], Awaitable[str | dict[str, Any]]] | None = None,
    is_production: bool = False,
) -> APIRouter:
    """Create standardized meta endpoints router.

    Args:
        service_name: Name of the service
        service_description: Description of the service
        version: Service version
        features: List of service features/capabilities
        endpoints: Dictionary of available endpoints with descriptions
        debug_info_provider: Function that returns debug information
        health_check_provider: Function that returns health status or health data
        is_production: Whether running in production (limits debug info)

    Returns:
        Configured APIRouter with meta endpoints
    """
    router = APIRouter()

    @router.get("/", response_model=dict[str, Any])
    async def service_info(request: Request) -> dict[str, Any]:
        """Service discovery endpoint with basic service information.

        Returns essential information for service registries and discovery mechanisms.
        Following patterns from Kubernetes service discovery and Spring Boot.
        """
        # Get dynamic status
        status = await _determine_service_status(request, health_check_provider)

        meta_info = {
            "name": service_name,
            "description": service_description,
            "version": version,
            "status": status,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "health_endpoints": {
                "liveness": "/health/live",
                "readiness": "/health/ready",
                "comprehensive": "/health",
                "deep": "/health/deep",
            },
            "meta_endpoints": {
                "info": "/info",
                "version": "/version",
                "debug": "/debug" if not is_production else None,
            },
            "api_endpoints": endpoints or {},
            "features": features or [],
            "documentation": "/docs" if not is_production else None,
        }

        # Add status details for non-operational states
        if status != "operational":
            meta_info["status_details"] = {
                "operational": "All systems functioning normally",
                "degraded": "Some non-critical systems experiencing issues",
                "unhealthy": "Critical systems down",
                "unknown": "Unable to determine health status",
            }.get(status, "Status check unavailable")

        # Add versioning information if available
        if VERSIONING_AVAILABLE and endpoints:
            try:
                current_version = APIVersion.from_string(version)
                meta_info["api_versioning"] = {
                    "current": str(current_version),
                    "supported_strategies": ["url_path", "header", "query_param", "accept_header"],
                    "header_name": "API-Version",
                    "url_pattern": f"/v{current_version.major}.{current_version.minor}/*",
                }
            except Exception:
                # If version parsing fails, continue without versioning info
                pass

        return meta_info

    @router.get("/info", response_model=dict[str, Any])
    async def service_metadata() -> dict[str, Any]:
        """Detailed service metadata endpoint.

        Provides comprehensive service information for operational monitoring.
        """
        return {
            "service": {
                "name": service_name,
                "description": service_description,
                "version": version,
                "features": features or [],
                "endpoints": endpoints or {},
            },
            "runtime": {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "process_id": os.getpid(),
                "uptime_seconds": _get_uptime_seconds(),
            },
            "build": {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "environment": "production" if is_production else "development",
            },
        }

    @router.get("/version", response_model=dict[str, str])
    async def service_version() -> dict[str, str]:
        """Simple version endpoint for quick checks."""
        return {
            "service": service_name,
            "version": version,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }

    if not is_production:

        @router.get("/debug", response_model=dict[str, Any])
        async def debug_info(request: Request) -> dict[str, Any]:
            """Development debugging information endpoint.

            Only available in non-production environments for security.
            """
            base_debug = {
                "service": service_name,
                "version": version,
                "environment": "development",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "runtime": {
                    "python_version": platform.python_version(),
                    "platform": platform.platform(),
                    "process_id": os.getpid(),
                    "memory_info": _get_memory_info(),
                    "uptime_seconds": _get_uptime_seconds(),
                },
                "request_info": {
                    "client_host": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                    "headers": dict(request.headers),
                },
            }

            # Add custom debug info if provider is available
            if debug_info_provider:
                try:
                    custom_debug = debug_info_provider(request)
                    if isinstance(custom_debug, dict):
                        base_debug.update(custom_debug)
                except Exception as e:
                    base_debug["debug_provider_error"] = str(e)

            return base_debug

    return router


def _get_uptime_seconds() -> int | None:
    """Get process uptime in seconds.

    Returns None if psutil is not available.
    Install with: pip install fast-core[monitoring]
    """
    try:
        import psutil

        process = psutil.Process(os.getpid())
        return int(process.create_time())
    except ImportError:
        return None


def _get_memory_info() -> dict[str, Any] | None:
    """Get process memory information.

    Returns None if psutil is not available.
    Install with: pip install fast-core[monitoring]
    """
    try:
        import psutil

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return {
            "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
            "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
            "percent": round(process.memory_percent(), 2),
        }
    except ImportError:
        return None


def setup_meta_endpoints(
    app: Any,
    settings: Any,
    service_description: str,
    features: list[str] | None = None,
    endpoints: dict[str, str] | None = None,
    debug_info_provider: Callable[[Request], dict[str, Any]] | None = None,
    health_check_provider: Callable[[Request], Awaitable[str | dict[str, Any]]] | None = None,
) -> None:
    """Setup meta endpoints for a FastAPI application.

    Args:
        app: FastAPI application instance
        settings: Service configuration object
        service_description: Description of the service
        features: List of service features/capabilities
        endpoints: Dictionary of available endpoints with descriptions
        debug_info_provider: Function that returns custom debug information
        health_check_provider: Function that returns health status or health data
    """
    service_name = getattr(settings, "service_name", "unknown-service")
    version = getattr(app, "version", "0.1.0")
    is_production = getattr(settings, "environment", "development") == "production"

    meta_router = create_meta_router(
        service_name=service_name,
        service_description=service_description,
        version=version,
        features=features,
        endpoints=endpoints,
        debug_info_provider=debug_info_provider,
        health_check_provider=health_check_provider,
        is_production=is_production,
    )

    # Include the meta router at root level (no prefix)
    app.include_router(meta_router)


# TEST

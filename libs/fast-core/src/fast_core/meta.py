"""Meta endpoints system for FastAPI services.

This module provides standardized service metadata endpoints following industry best practices.
Similar to Spring Boot Actuator or .NET Health Checks, it exposes service information
for service discovery, debugging, and operational monitoring.
"""

import datetime
import os
import platform
from typing import Any, Dict, List, Optional, Callable
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

try:
    from fast_core.routing.versioning import APIVersion, VersionedRouter

    VERSIONING_AVAILABLE = True
except ImportError:
    VERSIONING_AVAILABLE = False


def create_meta_router(
    service_name: str,
    service_description: str,
    version: str = "0.1.0",
    features: Optional[List[str]] = None,
    endpoints: Optional[Dict[str, str]] = None,
    debug_info_provider: Optional[Callable[[Request], Dict[str, Any]]] = None,
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
        is_production: Whether running in production (limits debug info)

    Returns:
        Configured APIRouter with meta endpoints
    """
    router = APIRouter()

    @router.get("/")
    async def service_info() -> Dict[str, Any]:
        """Service discovery endpoint with basic service information.

        Returns essential information for service registries and discovery mechanisms.
        Following patterns from Kubernetes service discovery and Spring Boot.
        """
        meta_info = {
            "name": service_name,
            "description": service_description,
            "version": version,
            "status": "operational",
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

        ***REMOVED*** Add versioning information if available
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
                ***REMOVED*** If version parsing fails, continue without versioning info
                pass

        return meta_info

    @router.get("/info")
    async def service_metadata() -> Dict[str, Any]:
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

    @router.get("/version")
    async def service_version() -> Dict[str, str]:
        """Simple version endpoint for quick checks."""
        return {
            "service": service_name,
            "version": version,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }

    if not is_production:

        @router.get("/debug")
        async def debug_info(request: Request) -> Dict[str, Any]:
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

            ***REMOVED*** Add custom debug info if provider is available
            if debug_info_provider:
                try:
                    custom_debug = debug_info_provider(request)
                    if isinstance(custom_debug, dict):
                        base_debug.update(custom_debug)
                except Exception as e:
                    base_debug["debug_provider_error"] = str(e)

            return base_debug

    return router


def _get_uptime_seconds() -> Optional[int]:
    """Get process uptime in seconds."""
    try:
        import psutil

        process = psutil.Process(os.getpid())
        return int(process.create_time())
    except ImportError:
        return None


def _get_memory_info() -> Optional[Dict[str, Any]]:
    """Get process memory information."""
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
    features: Optional[List[str]] = None,
    endpoints: Optional[Dict[str, str]] = None,
    debug_info_provider: Optional[Callable[[Request], Dict[str, Any]]] = None,
) -> None:
    """Setup meta endpoints for a FastAPI application.

    Args:
        app: FastAPI application instance
        settings: Service configuration object
        service_description: Description of the service
        features: List of service features/capabilities
        endpoints: Dictionary of available endpoints with descriptions
        debug_info_provider: Function that returns custom debug information
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
        is_production=is_production,
    )

    ***REMOVED*** Include the meta router at root level (no prefix)
    app.include_router(meta_router)

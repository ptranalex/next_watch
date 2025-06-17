"""Meta routes for the Backend API."""

from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint returning API information."""
    return {
        "message": "Welcome to Next Watch Backend API",
        "description": "Backend for Frontend API for serving movie data and user interactions",
        "api_versions": {
            "v1": "Available at /api/v1/",
        },
        "health_checks": {
            "comprehensive": "/health - Full health check with all dependencies",
            "liveness": "/health/live - Simple liveness check",
            "readiness": "/health/ready - Readiness check for critical dependencies",
            "database": "/db-health - Legacy database-only health check",
        },
        "documentation": "/docs",
        "features": [
            "Movie search and browsing",
            "User authentication and profiles",
            "Personalized recommendations",
            "Rating and review system",
            "Watchlist management",
            "Social features and interactions",
        ],
    }


@router.get("/debug")
async def debug_info() -> Dict[str, Any]:
    """Debug endpoint returning server information.

    Returns:
        Debug information including server settings

    Note:
        This endpoint is available in all environments but returns
        limited information in production for security.
    """
    import datetime
    import os

    from fastapi import HTTPException

    from backend_api.config.app import settings

    ***REMOVED*** In production, only return basic info
    if getattr(settings, "environment", "development") == "production":
        return {
            "service": "backend-api",
            "version": "0.1.0",
            "environment": "production",
            "timestamp": datetime.datetime.now().isoformat(),
            "debug": False,
        }

    ***REMOVED*** In development, return more detailed info
    return {
        "service": "backend-api",
        "version": "0.1.0",
        "environment": getattr(settings, "environment", "development"),
        "timestamp": datetime.datetime.now().isoformat(),
        "debug": settings.debug,
        "log_level": settings.log_level,
        "api_port": settings.api_port,
        "cors_origins": settings.cors_origins,
        "performance_metrics_enabled": settings.enable_performance_metrics,
        "database_masked": settings._mask_database_password(settings.database_url),
        "redis_url": settings.redis_url,
        "redis_config": {
            "max_connections": settings.redis_max_connections,
            "socket_timeout": settings.redis_socket_timeout,
            "connect_timeout": settings.redis_socket_connect_timeout,
            "retry_on_timeout": settings.redis_retry_on_timeout,
        },
    }

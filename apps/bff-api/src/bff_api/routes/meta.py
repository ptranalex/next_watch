"""Meta routes for the BFF service.

This module contains endpoints that provide information about the BFF service itself,
including API information, debugging endpoints, and service metadata.
"""

import datetime
from typing import Any, Dict

from config.logging import get_logger
from fastapi import APIRouter

from bff_api.config.app import settings

logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint returning BFF API information."""
    return {
        "message": "Welcome to Next Watch BFF API",
        "description": "Backend for Frontend aggregation layer for Next Watch movie platform",
        "api_versions": {"v1": "Available at /bff/v1/"},
        "authentication": "Available at /bff/v1/auth/",
        "health_checks": {
            "comprehensive": "/health - BFF and external service health check",
            "liveness": "/health/live - Simple liveness check",
            "readiness": "/health/ready - Readiness check for critical dependencies",
        },
        "documentation": "/docs",
        "debug": "/debug - Development debugging information",
        "features": [
            "Movie search and browsing aggregation",
            "User authentication proxy",
            "Personalized recommendations aggregation",
            "Frontend-optimized data formatting",
            "Caching and performance optimization",
            "Request/response transformation",
        ],
    }


@router.get("/debug")
async def debug_info() -> Dict[str, Any]:
    """Development and debugging information endpoint.

    Provides configuration and runtime information for debugging purposes.
    In production, only basic information is returned for security.

    Returns:
        Debug information (limited in production)
    """
    base_info = {
        "service": "bff",
        "version": "0.1.0",
        "environment": settings.environment,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "debug": settings.debug,
    }

    if settings.is_production:
        ***REMOVED*** Limited information in production for security
        return base_info
    else:
        ***REMOVED*** Comprehensive debug information in development
        return {
            **base_info,
            "log_level": settings.log_level,
            "api_port": settings.port,
            "cors_origins": settings.cors_origins,
            "performance_metrics_enabled": settings.enable_performance_metrics,
            "external_services": {
                "backend_api_url": settings.backend_api_url,
                "backend_api_timeout": settings.backend_api_timeout,
                "recommendation_api_url": settings.reco_api_url,
                "auth_api_url": settings.auth_api_url,
            },
            "redis_url": settings.redis_url,
            "cache_ttl_defaults": {
                "default": settings.cache_ttl_default,
                "short": settings.cache_ttl_short,
                "medium": settings.cache_ttl_medium,
                "long": settings.cache_ttl_long,
            },
            "security": {
                "allowed_hosts": settings.allowed_hosts,
                "jwt_configured": bool(settings.jwt_secret),
            },
        }

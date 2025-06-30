"""Meta routes for the Search service.

This module contains endpoints that provide information about the Search service itself,
including API information, debugging endpoints, and service metadata.
"""

import datetime
from typing import Any, Dict

from config.logging import get_logger
from fastapi import APIRouter, Request

from search_api.config.app import settings, SearchAPIConfig


def get_search_config(request: Request) -> SearchAPIConfig:
    """Get the original SearchAPIConfig from app state."""
    return getattr(request.app.state, "search_config", settings)


logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint returning Search API information."""
    return {
        "message": "Welcome to Next Watch Search API",
        "description": "Dedicated search and suggestion service for Next Watch movie platform",
        "api_versions": {"v1": "Available at /api/v1/"},
        "search_endpoints": {
            "search": "/api/v1/search - Movie search with filters",
            "suggestions": "/api/v1/search/suggestions - Basic suggestions",
            "text_suggestions": "/api/v1/search/suggestions/text - Enhanced text suggestions",
            "search_all": "/api/v1/search/all - Search across all entity types",
        },
        "health_checks": {
            "comprehensive": "/health - Search API and external service health check",
            "liveness": "/health/live - Simple liveness check",
            "readiness": "/health/ready - Readiness check for critical dependencies",
        },
        "documentation": "/docs",
        "debug": "/debug - Development debugging information",
        "features": [
            "Movie, actor, and director search",
            "Real-time search suggestions",
            "Redis-backed autocomplete",
            "Search analytics and metrics",
            "Fuzzy matching and typo tolerance",
            "Semantic search capabilities",
            "Advanced filtering and sorting",
        ],
    }


@router.get("/debug")
async def debug_info(request: Request) -> Dict[str, Any]:
    """Development and debugging information endpoint.

    Provides configuration and runtime information for debugging purposes.
    In production, only basic information is returned for security.

    Returns:
        Debug information (limited in production)
    """
    base_info = {
        "service": "search",
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
            "performance_metrics_enabled": get_search_config(request).enable_performance_metrics,
            "external_services": {
                "backend_api_url": settings.backend_api_url,
                "backend_api_timeout": settings.backend_api_timeout,
                "ml_api_url": settings.ml_api_url,
                "ml_api_timeout": settings.ml_api_timeout,
            },
            "redis_config": {
                "url": get_search_config(request).get_redis_url_masked(),
                "suggestion_key_prefix": get_search_config(request).redis_suggestion_key_prefix,
                "entity_key_prefix": get_search_config(request).redis_entity_key_prefix,
                "search_result_prefix": get_search_config(request).redis_search_result_prefix,
            },
            "search_settings": {
                "max_suggestions": get_search_config(request).max_suggestions,
                "search_cache_ttl": get_search_config(request).search_cache_ttl,
                "suggestion_cache_ttl": get_search_config(request).suggestion_cache_ttl,
                "min_query_length": get_search_config(request).min_query_length,
                "max_query_length": get_search_config(request).max_query_length,
                "search_timeout_seconds": get_search_config(request).search_timeout_seconds,
                "suggestion_batch_size": get_search_config(request).suggestion_batch_size,
            },
            "feature_flags": {
                "semantic_search": get_search_config(request).enable_semantic_search,
                "search_analytics": get_search_config(request).enable_search_analytics,
                "fuzzy_matching": get_search_config(request).enable_fuzzy_matching,
                "typo_tolerance": get_search_config(request).enable_typo_tolerance,
                "metrics": True,  ***REMOVED*** Always enabled for production observability
                "cache_metrics": get_search_config(request).cache_enable_metrics,
            },
            "security": {
                "allowed_hosts": get_search_config(request).allowed_hosts,
                "internal_api_key_configured": bool(get_search_config(request).internal_api_key),
            },
        }

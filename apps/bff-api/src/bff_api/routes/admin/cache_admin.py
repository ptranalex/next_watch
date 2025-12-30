"""Admin-only cache statistics and monitoring endpoints.

SECURITY NOTICE: These endpoints expose sensitive operational data and should
NEVER be accessible to public traffic. They are intended for:
- Internal monitoring systems (Prometheus, Grafana)
- Operations teams and administrators
- CI/CD pipelines and health checks
- Internal dashboards and debugging

Access should be restricted via:
- Network policies (internal-only)
- Authentication/authorization
- VPN or admin network access
- Separate admin port/interface
"""

import datetime

from cache import get_global_collector
from config.logging import get_logger
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

from bff_api.config.app import settings
from bff_api.services.cache_service import (
    check_cache_health,
    get_bff_warming_service,
    get_cache,
)
from bff_api.services.smart_warming import get_bff_smart_warming

logger = get_logger(__name__)
router = APIRouter()


async def verify_admin_access(
    x_admin_key: str = Header(None, description="Admin API key for internal access"),
) -> bool:
    """Verify admin access for internal endpoints.

    In production, this should validate:
    - Internal API keys
    - Network source (internal IPs only)
    - Service account tokens
    - Admin user authentication

    Args:
        x_admin_key: Admin API key from request headers

    Returns:
        True if access is authorized

    Raises:
        HTTPException: If access is denied
    """
    # In development, allow access without key for testing
    if settings.environment == "development":
        logger.warning(
            "Admin endpoint accessed without authentication in development mode",
            service="bff",
            component="admin_auth",
        )
        return True

    # In production, require admin key
    expected_admin_key = getattr(settings, "admin_api_key", None)

    if not expected_admin_key:
        logger.error(
            "Admin API key not configured but admin endpoint accessed",
            service="bff",
            component="admin_auth",
        )
        raise HTTPException(status_code=503, detail="Admin endpoints not properly configured")

    if not x_admin_key or x_admin_key != expected_admin_key:
        logger.warning(
            "Unauthorized admin endpoint access attempt",
            provided_key_length=len(x_admin_key) if x_admin_key else 0,
            service="bff",
            component="admin_auth",
        )
        raise HTTPException(status_code=403, detail="Admin access denied - invalid credentials")

    return True


@router.get("/stats")
async def get_cache_statistics(_: bool = Depends(verify_admin_access)) -> JSONResponse:
    """[ADMIN] Get comprehensive cache statistics and performance metrics.

    ⚠️  INTERNAL USE ONLY - Contains sensitive operational data

    Returns:
        Detailed cache statistics including hit rates, response times, and warming info
    """
    try:
        # Get metrics collector
        collector = get_global_collector()

        # Get cache manager
        cache_manager = get_cache()

        # Get warming service
        warming_service = get_bff_warming_service()
        smart_warming = get_bff_smart_warming()

        # Check cache health
        cache_healthy = await check_cache_health()

        # Get overall metrics
        overall_metrics = collector.get_metrics() or {}
        summary = collector.get_summary() or {}

        # Get function-specific metrics for key BFF functions
        function_metrics = {}
        key_functions = [
            "bff_api.routes.v1.movies._get_static_movie_data",
            "bff_api.routes.v1.movies._get_user_movie_interactions",
            "bff_api.routes.v1.movies._get_movies_list_data",
            "_get_static_movie_data",  # Alternative naming
            "_get_movies_list_data",  # Alternative naming
        ]

        for func_name in key_functions:
            func_metrics = collector.get_function_metrics(func_name)
            if func_metrics:
                function_metrics[func_name] = func_metrics

        # Get warming engine stats
        warming_engine = warming_service.get_warming_engine()
        warming_stats = {
            "engine_initialized": warming_engine is not None,
            "registered_functions": (
                list(warming_engine._warming_functions.keys()) if warming_engine else []
            ),
            "available_strategies": (
                [strategy.value for strategy in warming_engine._strategies.keys()]
                if warming_engine
                else []
            ),
        }

        # Background warming service status - REMOVED (using cron jobs instead)
        background_stats = {
            "service_running": False,
            "active_tasks": 0,
            "schedule_config": {},
            "note": "Background warming disabled - using cron jobs for scheduled warming",
        }

        response_data = {
            "status": "healthy" if cache_healthy else "unhealthy",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "cache_health": {
                "healthy": cache_healthy,
                "manager_initialized": cache_manager is not None,
            },
            "metrics": {
                "overall": overall_metrics,
                "summary": summary,
                "by_function": function_metrics,
            },
            "warming": {
                "engine": warming_stats,
                "background_service": background_stats,
                "smart_warming": smart_warming.get_warming_stats(),
            },
            "system_info": {
                "metrics_enabled": collector.enabled if collector else False,
                "cache_type": "Redis",
                "service": "bff-api",
                "environment": settings.environment,
                "admin_access": True,
            },
        }

        logger.info(
            "Admin cache statistics accessed",
            cache_healthy=cache_healthy,
            total_functions=len(function_metrics),
            service="bff",
            endpoint="admin_cache_stats",
        )

        return JSONResponse(status_code=200, content=response_data)

    except Exception as e:
        logger.error(
            "Failed to get admin cache statistics",
            error=str(e),
            service="bff",
            endpoint="admin_cache_stats",
            exc_info=True,
        )

        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve cache statistics: {str(e)}"
        )


@router.get("/metrics/{function_name}")
async def get_function_cache_metrics(
    function_name: str, _: bool = Depends(verify_admin_access)
) -> JSONResponse:
    """[ADMIN] Get detailed cache metrics for a specific function.

    ⚠️  INTERNAL USE ONLY - Contains sensitive performance data

    Args:
        function_name: Name of the cached function to get metrics for

    Returns:
        Detailed metrics for the specified function
    """
    try:
        collector = get_global_collector()

        if not collector or not collector.enabled:
            raise HTTPException(status_code=503, detail="Cache metrics are not enabled")

        function_metrics = collector.get_function_metrics(function_name)

        if not function_metrics:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for function: {function_name}",
            )

        response_data = {
            "function_name": function_name,
            "metrics": function_metrics,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "admin_access": True,
        }

        return JSONResponse(status_code=200, content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get admin function cache metrics",
            function_name=function_name,
            error=str(e),
            service="bff",
            endpoint="admin_function_metrics",
        )

        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve function metrics: {str(e)}"
        )


# REMOVED: Manual warming test endpoint
# See CACHE_WARMING_REFACTOR.md - testing now done via background job CLI


@router.get("/warming/stats")
async def get_warming_statistics(
    _: bool = Depends(verify_admin_access),
) -> JSONResponse:
    """[ADMIN] Get detailed warming statistics and recent activity.

    ⚠️  INTERNAL USE ONLY - Contains operational details

    Returns:
        Comprehensive warming statistics
    """
    try:
        warming_service = get_bff_warming_service()

        # Get warming engine
        warming_engine = warming_service.get_warming_engine()

        # Collect warming statistics
        stats = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "warming_engine": {
                "initialized": warming_engine is not None,
                "registered_functions": (
                    list(warming_engine._warming_functions.keys()) if warming_engine else []
                ),
                "strategies": (
                    [strategy.value for strategy in warming_engine._strategies.keys()]
                    if warming_engine
                    else []
                ),
                "config": (
                    {
                        "max_concurrent_operations": (
                            warming_engine.config.max_concurrent_operations
                            if warming_engine
                            else None
                        ),
                        "max_items_per_strategy": (
                            warming_engine.config.max_items_per_strategy if warming_engine else None
                        ),
                    }
                    if warming_engine
                    else None
                ),
            },
            "background_service": {
                "running": False,
                "active_tasks": 0,
                "task_names": [],
                "schedule": {},
                "note": "Background warming disabled - using cron jobs for scheduled warming",
            },
            "recent_activity": {
                "note": "Recent warming activity tracking would be implemented here"
            },
            "admin_access": True,
        }

        return JSONResponse(status_code=200, content=stats)

    except Exception as e:
        logger.error(
            "Failed to get admin warming statistics",
            error=str(e),
            service="bff",
            endpoint="admin_warming_stats",
        )

        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve warming statistics: {str(e)}"
        )


# REMOVED: Manual warming endpoints moved to background jobs
# See CACHE_WARMING_REFACTOR.md Phase 3 for new background job system
#
# These endpoints have been removed for security and architectural reasons:
# - POST /admin/cache/warming/strategy/{strategy_name}
# - POST /admin/cache/warming/test/{function_name}
#
# Bulk warming now handled by:
# - Background job system (scripts/cache_warming_service.py)
# - Kubernetes CronJobs for scheduled warming
# - Smart reactive warming in cache library


@router.get("/smart-warming/stats")
async def get_smart_warming_statistics(
    _: bool = Depends(verify_admin_access),
) -> JSONResponse:
    """[ADMIN] Get detailed smart warming statistics and performance metrics.

    ⚠️  INTERNAL USE ONLY - Contains sensitive operational data

    Returns:
        Detailed smart warming statistics including event-driven warming metrics
    """
    try:
        smart_warming = get_bff_smart_warming()

        # Get comprehensive smart warming stats
        stats = smart_warming.get_warming_stats()

        # Calculate derived metrics
        total_operations = stats.get("operations_attempted", 0)
        successful_operations = stats.get("operations_successful", 0)
        rate_limited_operations = stats.get("operations_rate_limited", 0)
        failed_operations = stats.get("operations_failed", 0)

        success_rate = (
            (successful_operations / total_operations * 100) if total_operations > 0 else 0.0
        )

        rate_limit_rate = (
            (rate_limited_operations / total_operations * 100) if total_operations > 0 else 0.0
        )

        failure_rate = (failed_operations / total_operations * 100) if total_operations > 0 else 0.0

        response_data = {
            "smart_warming": {
                "enabled": stats.get("enabled", False),
                "operations": {
                    "total_attempted": total_operations,
                    "successful": successful_operations,
                    "rate_limited": rate_limited_operations,
                    "failed": failed_operations,
                    "success_rate_percent": round(success_rate, 2),
                    "rate_limit_rate_percent": round(rate_limit_rate, 2),
                    "failure_rate_percent": round(failure_rate, 2),
                },
                "last_operation": stats.get("last_operation"),
                "rate_limiter": stats.get("rate_limiter", {}),
            },
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "service": "bff-api",
            "environment": settings.environment,
        }

        logger.info(
            "Smart warming statistics accessed",
            total_operations=total_operations,
            success_rate=success_rate,
            enabled=stats.get("enabled", False),
            service="bff",
            endpoint="admin_smart_warming_stats",
        )

        return JSONResponse(status_code=200, content=response_data)

    except Exception as e:
        logger.error(
            "Failed to get smart warming statistics",
            error=str(e),
            service="bff",
            endpoint="admin_smart_warming_stats",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to get smart warming statistics")


# REMOVED: Strategy listing endpoint no longer needed
# Bulk warming strategies now documented in CACHE_WARMING_REFACTOR.md

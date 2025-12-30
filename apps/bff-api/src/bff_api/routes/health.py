"""Health check routes for BFF service."""

import datetime
from typing import Any

from config.logging import get_logger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from bff_api.config.app import settings
from bff_api.dependencies import get_all_services_health
from bff_api.services.cache_service.background_warming_service import (
    get_background_warming_service,
)
from bff_api.services.smart_warming import get_bff_smart_warming

logger = get_logger(__name__)

# Service version - should ideally come from package metadata or environment
SERVICE_VERSION = getattr(settings, "version", "1.0.0")

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str
    environment: str
    backend_api_url: str


@router.get("/health/services")
async def service_clients_health() -> JSONResponse:
    """Service Client Factory health check endpoint.

    Shows the health status of all service clients managed by the
    Service Client Factory system.

    Returns:
        Health status for all registered service clients
    """
    try:
        # Get health status from Service Client Factory
        health_status = await get_all_services_health()

        # Determine overall status
        all_healthy = all(status.get("status") == "healthy" for status in health_status.values())
        overall_status = "healthy" if all_healthy else "degraded"
        status_code = 200 if all_healthy else 503

        if all_healthy:
            logger.debug(
                "Service clients health check",
                status=overall_status,
                service="bff",
                endpoint="service_clients_health",
                services_count=len(health_status),
            )
        else:
            logger.warning(
                "Service clients health is degraded",
                status=overall_status,
                service="bff",
                endpoint="service_clients_health",
                services_count=len(health_status),
            )

        return JSONResponse(
            status_code=status_code,
            content={
                "status": overall_status,
                "service": "bff",
                "version": "0.1.0",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "service_client_factory": {
                    "enabled": True,
                    "services_registered": len(health_status),
                    "services": health_status,
                },
                "summary": {
                    "healthy": sum(
                        1 for s in health_status.values() if s.get("status") == "healthy"
                    ),
                    "unhealthy": sum(
                        1 for s in health_status.values() if s.get("status") == "unhealthy"
                    ),
                    "error": sum(1 for s in health_status.values() if s.get("status") == "error"),
                    "total": len(health_status),
                },
            },
        )

    except Exception as e:
        logger.error(f"Service clients health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "bff",
                "version": "0.1.0",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "error": f"Service Client Factory health check failed: {str(e)}",
                "service_client_factory": {
                    "enabled": True,
                    "error": str(e),
                },
            },
        )


@router.get("/health")
async def health_check(request: Request) -> JSONResponse:
    """Comprehensive health check endpoint with external service monitoring.

    Checks health of all external dependencies:
    - Backend API service
    - Recommendation API service
    - Auth API service

    Returns:
        Health status information with dependency details
    """
    # Get health service from application state
    health_service = getattr(request.app.state, "health_service", None)

    if health_service:
        try:
            # Use comprehensive health service
            health_results = await health_service.check_all()

            # Determine overall health status
            all_critical_healthy = health_results.get("backend_api", {}).is_healthy
            overall_status = "healthy" if all_critical_healthy else "unhealthy"
            status_code = 200 if all_critical_healthy else 503

            # Build detailed response
            checks = {}
            for service_name, result in health_results.items():
                checks[service_name] = {
                    "status": result.status,
                    "healthy": result.is_healthy,
                    "response_time_ms": result.response_time_ms,
                }
                if result.details:
                    checks[service_name]["details"] = result.details
                if result.error:
                    checks[service_name]["error"] = result.error

            if overall_status == "healthy":
                logger.debug(
                    "Health check response",
                    status=overall_status,
                    service="bff",
                    endpoint="health_check",
                )
            else:
                logger.warning(
                    "Health check is unhealthy",
                    status=overall_status,
                    service="bff",
                    endpoint="health_check",
                )

            return JSONResponse(
                status_code=status_code,
                content={
                    "status": overall_status,
                    "service": "bff",
                    "version": "0.1.0",
                    "environment": settings.environment,
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "checks": checks,
                    "external_services": {
                        "backend_api": settings.backend_api_url,
                        "recommendation_api": settings.reco_api_url,
                        "auth_api": settings.auth_api_url,
                    },
                },
            )

        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "service": "bff",
                    "version": "0.1.0",
                    "environment": settings.environment,
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "error": f"Health check failed: {str(e)}",
                    "checks": {
                        "backend_api": {"status": "unknown", "healthy": False},
                        "recommendation_api": {"status": "unknown", "healthy": False},
                        "auth_api": {"status": "unknown", "healthy": False},
                    },
                },
            )
    else:
        # Fallback: basic health check without external service monitoring
        logger.debug(
            "Health check response",
            status="healthy",
            service="bff",
            endpoint="health_check",
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "bff",
                "version": "0.1.0",
                "environment": settings.environment,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "note": "Health service not available - basic health check only",
                "external_services": {
                    "backend_api": settings.backend_api_url,
                    "recommendation_api": settings.reco_api_url,
                    "auth_api": settings.auth_api_url,
                },
            },
        )


@router.get("/health/ready")
async def readiness_check(request: Request) -> JSONResponse:
    """Readiness check for Kubernetes/Docker.

    Checks critical dependencies only (Backend API) to determine if
    the BFF is ready to serve traffic.

    Returns:
        Readiness status (200 if ready, 503 if not ready)
    """
    # Get health service from application state
    health_service = getattr(request.app.state, "health_service", None)

    if health_service:
        try:
            # Check only critical services for readiness
            backend_result = await health_service.check_backend_api()

            is_ready = backend_result.is_healthy
            status_code = 200 if is_ready else 503

            if is_ready:
                logger.debug(
                    "Readiness check response",
                    status=is_ready,
                    service="bff",
                    endpoint="readiness_check",
                )
            else:
                logger.warning(
                    "Readiness check not ready",
                    status=is_ready,
                    service="bff",
                    endpoint="readiness_check",
                )
            return JSONResponse(
                status_code=status_code,
                content={
                    "status": "ready" if is_ready else "not_ready",
                    "service": "bff",
                    "version": "0.1.0",
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "critical_services": {"backend_api": backend_result.is_healthy},
                    "response_time_ms": backend_result.response_time_ms,
                },
            )

        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "service": "bff",
                    "version": "0.1.0",
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "error": f"Readiness check failed: {str(e)}",
                    "critical_services": {"backend_api": False},
                },
            )
    else:
        # Fallback: assume ready if health service not available
        return JSONResponse(
            status_code=200,
            content={
                "status": "ready",
                "service": "bff",
                "version": "0.1.0",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "note": "Health service not available - assuming ready",
                "critical_services": {"backend_api": "unknown"},
            },
        )


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    """Liveness check for Kubernetes/Docker.

    Simple endpoint that always returns 200 if the BFF service is running.
    Used by container orchestrators to determine if the container should be restarted.

    Returns:
        Basic liveness confirmation
    """
    logger.debug(
        "Liveness check response",
        status="alive",
        service="bff",
        endpoint="liveness_check",
    )
    return {
        "status": "alive",
        "service": "bff",
        "version": "0.1.0",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }


# Legacy endpoint for backward compatibility
@router.get("/basic", response_model=HealthResponse)
async def basic_health_check() -> HealthResponse:
    """Basic health check endpoint (legacy).

    Provides basic service information without external dependency checks.
    Maintained for backward compatibility.

    Returns:
        Basic health status information
    """
    logger.debug(
        "Basic health check response",
        status="healthy",
        service="bff",
        endpoint="basic_health_check",
    )
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        version="0.1.0",
        environment=settings.environment,
        backend_api_url=settings.backend_api_url,
    )


@router.get("/health/warming")
async def warming_status() -> JSONResponse:
    """Background warming service status endpoint.

    Provides detailed information about the background warming service including:
    - Service running status
    - Active warming tasks
    - Schedule configuration
    - Task health

    Returns:
        Background warming service status and configuration
    """
    try:
        warming_service = get_background_warming_service()
        status = warming_service.get_status()
        health = await warming_service.health_check()

        logger.info(
            "Warming status check",
            running=status["running"],
            active_tasks=status["active_tasks"],
            service="bff",
            endpoint="warming_status",
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy" if status["running"] else "stopped",
                "service": "background_warming",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "details": {
                    **status,
                    "health": health,
                },
                "schedules": {
                    "morning_warmup": "7:00 AM - Popular content warming",
                    "evening_warmup": "5:00 PM - Metrics-driven warming",
                    "night_optimization": "1:00 AM - Scheduled warming",
                    "continuous_metrics": "Every 10 minutes - Metrics-driven warming",
                },
            },
        )

    except Exception as e:
        logger.error(
            "Warming status check failed",
            error=str(e),
            service="bff",
            endpoint="warming_status",
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "background_warming",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "error": f"Failed to get warming status: {str(e)}",
            },
        )


@router.get("/health/smart-warming")
async def smart_warming_health() -> JSONResponse:
    """Smart warming health check with backend connection monitoring.

    Provides detailed statistics about:
    - Backend connection pool status
    - Circuit breaker state
    - Warming throttling metrics
    - Version-aware warming performance

    Returns:
        Smart warming health status and performance metrics
    """
    try:
        smart_warming = get_bff_smart_warming()
        stats = smart_warming.get_warming_stats()

        # Determine health status based on metrics
        backend_connections = stats.get("backend_connections", {})
        circuit_breaker_open = backend_connections.get("circuit_breaker_open", False)
        success_rate = backend_connections.get("success_rate", 100)
        active_connections = backend_connections.get("active_connections", 0)
        max_connections = backend_connections.get("max_connections", 0)

        # Health status determination
        if circuit_breaker_open:
            status = "degraded"
            health_level = "warning"
        elif success_rate < 95:
            status = "degraded"
            health_level = "warning"
        elif active_connections >= max_connections:
            status = "degraded"
            health_level = "warning"
        else:
            status = "healthy"
            health_level = "ok"

        return JSONResponse(
            status_code=200 if status == "healthy" else 503,
            content={
                "status": status,
                "health_level": health_level,
                "service": "smart_warming",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "metrics": {
                    "backend_connections": {
                        "active": active_connections,
                        "max": max_connections,
                        "utilization_percent": (active_connections / max(1, max_connections)) * 100,
                        "circuit_breaker_open": circuit_breaker_open,
                        "success_rate_percent": success_rate,
                        "avg_response_time_ms": backend_connections.get("avg_response_time_ms", 0),
                        "total_requests": backend_connections.get("total_requests", 0),
                        "failed_requests": backend_connections.get("failed_requests", 0),
                    },
                    "warming_throttling": {
                        "active_throttles": stats.get("warming_throttle_entries", 0),
                        "throttle_window_seconds": stats.get("throttle_window_seconds", 30),
                    },
                    "smart_warming": {
                        key: value
                        for key, value in stats.items()
                        if key
                        not in [
                            "backend_connections",
                            "warming_throttle_entries",
                            "throttle_window_seconds",
                        ]
                    },
                },
                "recommendations": _get_warming_recommendations(stats),
            },
        )

    except Exception as e:
        logger.error("Failed to get smart warming health status", error=str(e), exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "smart_warming",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "error": f"Failed to get smart warming status: {str(e)}",
            },
        )


def _get_warming_recommendations(stats: dict[str, Any]) -> list[dict[str, str]]:
    """Get performance recommendations based on warming statistics."""
    recommendations = []

    backend_stats = stats.get("backend_connections", {})

    # Circuit breaker recommendations
    if backend_stats.get("circuit_breaker_open", False):
        recommendations.append(
            {
                "type": "critical",
                "message": "Backend circuit breaker is open - check backend service health",
                "action": "Investigate backend API responsiveness and consider scaling",
            }
        )

    # Success rate recommendations
    success_rate = backend_stats.get("success_rate", 100)
    if success_rate < 95:
        recommendations.append(
            {
                "type": "warning",
                "message": f"Backend success rate is {success_rate:.1f}% (below 95%)",
                "action": "Monitor backend errors and consider reducing warming concurrency",
            }
        )

    # Response time recommendations
    avg_response_time = backend_stats.get("avg_response_time_ms", 0)
    if avg_response_time > 1000:
        recommendations.append(
            {
                "type": "warning",
                "message": f"Average backend response time is {avg_response_time:.0f}ms",
                "action": "Consider optimizing backend queries or reducing warming frequency",
            }
        )

    # Throttling recommendations
    active_throttles = stats.get("warming_throttle_entries", 0)
    if active_throttles > 100:
        recommendations.append(
            {
                "type": "info",
                "message": f"High number of active throttles: {active_throttles}",
                "action": "Consider adjusting throttle window or warming triggers",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "type": "success",
                "message": "Smart warming is operating within normal parameters",
                "action": "No action required",
            }
        )

    return recommendations

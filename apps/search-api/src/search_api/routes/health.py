"""Health check routes for Search service."""

import datetime
from typing import Dict

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from search_api.config.app import settings, SearchAPIConfig
from search_api.dependencies.clients import get_all_services_health
from config.logging import get_logger


def get_search_config(request: Request) -> SearchAPIConfig:
    """Get the original SearchAPIConfig from app state."""
    return getattr(request.app.state, "search_config", settings)


logger = get_logger(__name__)

***REMOVED*** Service version - should ideally come from package metadata or environment
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
        ***REMOVED*** Get health status from Service Client Factory
        health_status = await get_all_services_health()

        ***REMOVED*** Determine overall status
        all_healthy = all(status.get("status") == "healthy" for status in health_status.values())
        overall_status = "healthy" if all_healthy else "degraded"
        status_code = 200 if all_healthy else 503

        logger.info(
            "Service clients health check",
            status=overall_status,
            service="search",
            endpoint="service_clients_health",
            services_count=len(health_status),
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "status": overall_status,
                "service": "search",
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
                "service": "search",
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
    - Redis for suggestions and caching

    Returns:
        Health status information with dependency details
    """
    ***REMOVED*** Get health service from application state
    health_service = getattr(request.app.state, "health_service", None)

    if health_service:
        try:
            ***REMOVED*** Use comprehensive health service
            health_results = await health_service.check_all()

            ***REMOVED*** Determine overall health status
            all_critical_healthy = health_results.get("backend_api", {}).is_healthy
            redis_healthy = health_results.get("redis", {}).is_healthy
            overall_status = "healthy" if all_critical_healthy and redis_healthy else "unhealthy"
            status_code = 200 if overall_status == "healthy" else 503

            ***REMOVED*** Build detailed response
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

            logger.info(
                "Health check response",
                status=overall_status,
                service="search",
                endpoint="health_check",
            )

            return JSONResponse(
                status_code=status_code,
                content={
                    "status": overall_status,
                    "service": "search",
                    "version": "0.1.0",
                    "environment": settings.environment,
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "checks": checks,
                    "external_services": {
                        "backend_api": settings.backend_api_url,
                        "redis": get_search_config(request).get_redis_url_masked(),
                    },
                    "search_features": {
                        "semantic_search": get_search_config(request).enable_semantic_search,
                        "search_analytics": get_search_config(request).enable_search_analytics,
                        "fuzzy_matching": get_search_config(request).enable_fuzzy_matching,
                        "typo_tolerance": get_search_config(request).enable_typo_tolerance,
                    },
                },
            )

        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "service": "search",
                    "version": "0.1.0",
                    "environment": settings.environment,
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "error": f"Health check failed: {str(e)}",
                    "checks": {
                        "backend_api": {"status": "unknown", "healthy": False},
                        "redis": {"status": "unknown", "healthy": False},
                    },
                },
            )
    else:
        ***REMOVED*** Fallback: basic health check without external service monitoring
        logger.info(
            "Health check response",
            status="healthy",
            service="search",
            endpoint="health_check",
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "search",
                "version": "0.1.0",
                "environment": settings.environment,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "message": "Search API is running",
                "external_services": {
                    "backend_api": settings.backend_api_url,
                    "redis": get_search_config(request).get_redis_url_masked(),
                },
                "search_features": {
                    "semantic_search": get_search_config(request).enable_semantic_search,
                    "search_analytics": get_search_config(request).enable_search_analytics,
                    "fuzzy_matching": get_search_config(request).enable_fuzzy_matching,
                    "typo_tolerance": get_search_config(request).enable_typo_tolerance,
                },
            },
        )


@router.get("/health/ready")
async def readiness_check(request: Request) -> JSONResponse:
    """Readiness probe for Kubernetes deployment.

    Checks if the service is ready to accept traffic.
    """
    try:
        ***REMOVED*** Check critical dependencies
        health_status = await get_all_services_health()

        ***REMOVED*** For search API, we need backend and redis to be healthy
        backend_healthy = health_status.get("backend", {}).get("status") == "healthy"
        redis_healthy = health_status.get("redis", {}).get("status") == "healthy"

        is_ready = backend_healthy and redis_healthy
        status_code = 200 if is_ready else 503

        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if is_ready else "not_ready",
                "service": "search",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "dependencies": {
                    "backend_api": "healthy" if backend_healthy else "unhealthy",
                    "redis": "healthy" if redis_healthy else "unhealthy",
                },
            },
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "search",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "error": str(e),
            },
        )


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness probe for Kubernetes deployment.

    Simple check to verify the service is running.
    """
    return {
        "status": "alive",
        "service": "search",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }


@router.get("/basic", response_model=HealthResponse)
async def basic_health_check() -> HealthResponse:
    """Basic health check endpoint.

    Returns:
        Basic health information
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        version=SERVICE_VERSION,
        environment=settings.environment,
        backend_api_url=settings.backend_api_url,
    )

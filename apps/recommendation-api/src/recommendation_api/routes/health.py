"""Health check routes for the Recommendation API."""

from config.logging import get_logger
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from recommendation_api.config import settings

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check(request: Request) -> JSONResponse:
    """Comprehensive health check endpoint.

    Checks the health of all dependencies:
    - PostgreSQL database
    - Redis cache
    - Qdrant vector database
    """
    health_service = request.app.state.health_service

    try:
        ***REMOVED*** Get health status for all services
        health_results = await health_service.check_all()

        ***REMOVED*** Determine overall health
        all_healthy = all(result.is_healthy for result in health_results.values())
        overall_status = "healthy" if all_healthy else "unhealthy"

        ***REMOVED*** Build response
        response = {
            "status": overall_status,
            "service": "recommendation-api",
            "version": "0.1.0",
            "environment": settings.environment,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {},
        }

        ***REMOVED*** Add individual service checks
        for service_name, result in health_results.items():
            check_data = {
                "status": result.status,
                "healthy": result.is_healthy,
            }

            if result.response_time_ms is not None:
                check_data["response_time_ms"] = result.response_time_ms

            if result.details:
                check_data["details"] = result.details

            if result.error:
                check_data["error"] = result.error

            response["checks"][service_name] = check_data

        ***REMOVED*** Set appropriate HTTP status code
        status_code = 200 if all_healthy else 503

        return JSONResponse(status_code=status_code, content=response)

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "recommendation-api",
                "version": "0.1.0",
                "environment": settings.environment,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": f"Health check failed: {str(e)}",
                "checks": {
                    "postgres": {"status": "unknown", "healthy": False},
                    "redis": {"status": "unknown", "healthy": False},
                    "qdrant": {"status": "unknown", "healthy": False},
                },
            },
        )


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Simple liveness check endpoint.

    Returns basic service status without dependency checks.
    Useful for load balancers and container orchestrators.
    """
    return {
        "status": "alive",
        "service": "recommendation-api",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/health/ready")
async def readiness_check(request: Request) -> JSONResponse:
    """Readiness check endpoint.

    Checks if the service is ready to handle requests by verifying
    that all critical dependencies are available.
    """
    health_service = request.app.state.health_service

    try:
        ***REMOVED*** Check only critical dependencies for readiness
        health_results = await health_service.check_all()

        ***REMOVED*** For readiness, we need database and qdrant to be healthy
        ***REMOVED*** Redis is nice to have but not critical for basic functionality
        critical_services = ["postgres", "qdrant"]
        critical_healthy = all(
            health_results[service].is_healthy
            for service in critical_services
            if service in health_results
        )

        status = "ready" if critical_healthy else "not_ready"
        status_code = 200 if critical_healthy else 503

        return JSONResponse(
            status_code=status_code,
            content={
                "status": status,
                "service": "recommendation-api",
                "version": "0.1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "critical_services": {
                    service: health_results[service].is_healthy
                    for service in critical_services
                    if service in health_results
                },
            },
        )

    except Exception as e:
        logger.error(f"Readiness check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "recommendation-api",
                "version": "0.1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": f"Readiness check failed: {str(e)}",
            },
        )

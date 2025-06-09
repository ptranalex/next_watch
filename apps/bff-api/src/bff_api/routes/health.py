"""Health check routes for BFF service."""

import datetime
import time
from typing import Dict, Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from bff_api.config.app import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str
    environment: str
    backend_api_url: str


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
    ***REMOVED*** Get health service from application state
    health_service = getattr(request.app.state, "health_service", None)

    if health_service:
        try:
            ***REMOVED*** Use comprehensive health service
            health_results = await health_service.check_all()

            ***REMOVED*** Determine overall health status
            all_critical_healthy = health_results.get("backend_api", {}).is_healthy
            overall_status = "healthy" if all_critical_healthy else "unhealthy"
            status_code = 200 if all_critical_healthy else 503

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
        ***REMOVED*** Fallback: basic health check without external service monitoring
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
    ***REMOVED*** Get health service from application state
    health_service = getattr(request.app.state, "health_service", None)

    if health_service:
        try:
            ***REMOVED*** Check only critical services for readiness
            backend_result = await health_service.check_backend_api()

            is_ready = backend_result.is_healthy
            status_code = 200 if is_ready else 503

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
        ***REMOVED*** Fallback: assume ready if health service not available
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
async def liveness_check() -> Dict[str, str]:
    """Liveness check for Kubernetes/Docker.

    Simple endpoint that always returns 200 if the BFF service is running.
    Used by container orchestrators to determine if the container should be restarted.

    Returns:
        Basic liveness confirmation
    """
    return {
        "status": "alive",
        "service": "bff",
        "version": "0.1.0",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }


***REMOVED*** Legacy endpoint for backward compatibility
@router.get("/basic", response_model=HealthResponse)
async def basic_health_check() -> HealthResponse:
    """Basic health check endpoint (legacy).

    Provides basic service information without external dependency checks.
    Maintained for backward compatibility.

    Returns:
        Basic health status information
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        version="0.1.0",
        environment=settings.environment,
        backend_api_url=settings.backend_api_url,
    )

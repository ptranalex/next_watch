"""Health check routes for the Auth API."""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session

from auth_api.config.app import settings
from auth_api.db.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check(request: Request) -> JSONResponse:
    """Comprehensive health check endpoint.

    Checks the health of all dependencies:
    - PostgreSQL database (via movie_storage)
    """
    ***REMOVED*** Check if health service is available
    if not hasattr(request.app.state, "health_service") or request.app.state.health_service is None:
        ***REMOVED*** Fallback to basic checks if health service is not available
        return await health_check_fallback()

    health_service = request.app.state.health_service

    try:
        ***REMOVED*** Get health status for all services
        health_results = await health_service.check_all()

        ***REMOVED*** Determine overall health
        all_healthy = all(result.is_healthy for result in health_results.values())
        overall_status = "healthy" if all_healthy else "unhealthy"

        ***REMOVED*** Build response
        response: Dict[str, Any] = {
            "status": overall_status,
            "service": "auth-api",
            "version": "0.1.0",
            "environment": getattr(settings, "environment", "development"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {},
        }

        ***REMOVED*** Add individual service checks
        for service_name, result in health_results.items():
            check_data: Dict[str, Any] = {
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
                "service": "auth-api",
                "version": "0.1.0",
                "environment": getattr(settings, "environment", "development"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": f"Health check failed: {str(e)}",
                "checks": {
                    "postgres": {"status": "unknown", "healthy": False},
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
        "service": "auth-api",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/health/ready")
async def readiness_check(request: Request) -> JSONResponse:
    """Readiness check endpoint.

    Checks if the service is ready to handle requests by verifying
    that all critical dependencies are available.
    """
    ***REMOVED*** Check if health service is available
    if not hasattr(request.app.state, "health_service") or request.app.state.health_service is None:
        ***REMOVED*** Fallback to basic readiness check
        return await readiness_check_fallback()

    health_service = request.app.state.health_service

    try:
        ***REMOVED*** Check only critical dependencies for readiness
        health_results = await health_service.check_all()

        ***REMOVED*** For readiness, we need database to be healthy
        critical_services = ["postgres"]
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
                "service": "auth-api",
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
                "service": "auth-api",
                "version": "0.1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": f"Readiness check failed: {str(e)}",
            },
        )


@router.get("/db-health")
async def db_health_check(db: Session = Depends(get_db)) -> JSONResponse:
    """Legacy database health check endpoint.

    This endpoint is maintained for backward compatibility.
    Use /health for comprehensive health checks.

    Args:
        db: Database session dependency

    Returns:
        Database health status and connection information
    """
    try:
        from sqlmodel import text
        import traceback

        ***REMOVED*** Try a simple query
        result = db.execute(text("SELECT 1")).scalar()

        ***REMOVED*** Return success if query worked
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "result": result,
                "db_type": str(type(db)),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"Database health check failed: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error": str(e),
                "trace": stack_trace,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )


***REMOVED*** Fallback health check functions
async def health_check_fallback() -> JSONResponse:
    """Fallback health check when health service is not available."""
    logger.warning("Health service not available, using fallback health check")

    try:
        ***REMOVED*** Basic database check using sync method
        from auth_api.services.health_service import HealthService

        health_service = HealthService()

        ***REMOVED*** Use sync postgres check
        postgres_result = health_service.check_postgres_sync()

        ***REMOVED*** Simple response
        all_healthy = postgres_result.is_healthy
        overall_status = "healthy" if all_healthy else "unhealthy"

        response = {
            "status": overall_status,
            "service": "auth-api",
            "version": "0.1.0",
            "environment": getattr(settings, "environment", "development"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {
                "postgres": {
                    "status": postgres_result.status,
                    "healthy": postgres_result.is_healthy,
                    "response_time_ms": postgres_result.response_time_ms,
                    "details": postgres_result.details,
                    "error": postgres_result.error,
                }
            },
            "note": "Fallback health check - health service not initialized",
        }

        status_code = 200 if all_healthy else 503
        return JSONResponse(status_code=status_code, content=response)

    except Exception as e:
        logger.error(f"Fallback health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "auth-api",
                "version": "0.1.0",
                "environment": getattr(settings, "environment", "development"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": f"Health check failed: {str(e)}",
                "note": "Fallback health check failed",
            },
        )


async def readiness_check_fallback() -> JSONResponse:
    """Fallback readiness check when health service is not available."""
    logger.warning("Health service not available, using fallback readiness check")

    try:
        ***REMOVED*** Basic database check
        from auth_api.services.health_service import HealthService

        health_service = HealthService()

        ***REMOVED*** Use sync postgres check
        postgres_result = health_service.check_postgres_sync()

        status = "ready" if postgres_result.is_healthy else "not_ready"
        status_code = 200 if postgres_result.is_healthy else 503

        return JSONResponse(
            status_code=status_code,
            content={
                "status": status,
                "service": "auth-api",
                "version": "0.1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "critical_services": {
                    "postgres": postgres_result.is_healthy,
                },
                "note": "Fallback readiness check - health service not initialized",
            },
        )

    except Exception as e:
        logger.error(f"Fallback readiness check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "auth-api",
                "version": "0.1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": f"Readiness check failed: {str(e)}",
                "note": "Fallback readiness check failed",
            },
        )

"""Main FastAPI application for the Recommendation API service."""

import os
import logging
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncGenerator

***REMOVED*** Load environment variables
try:
    from dotenv import load_dotenv

    ***REMOVED*** Only load .env files if we're not in production
    if os.getenv("ENVIRONMENT") != "production":
        ***REMOVED*** Try multiple locations to find .env files (prioritize current directory)
        possible_paths = [
            Path.cwd() / ".env",
            Path.cwd() / ".env.local",
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[3] / ".env.local",
        ]

        for path in possible_paths:
            if path.exists():
                load_dotenv(dotenv_path=path, override=True)
                break
except ImportError:
    pass  ***REMOVED*** Continue without dotenv if not installed

***REMOVED*** Import configuration after environment variables are loaded
from recommendation_api.config import settings

***REMOVED*** Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from recommendation_api.routes import api_v1_router
from recommendation_api.services.health_service import get_health_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    ***REMOVED*** Startup
    logger.info(f"Starting Recommendation API service with config: {settings}")

    ***REMOVED*** Initialize health service and store in app state
    logger.info("Initializing health service")
    app.state.health_service = get_health_service()

    ***REMOVED*** Initialize any other required services/clients here
    ***REMOVED*** For example: database connections, ML model loading, etc.

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Recommendation API service")

    ***REMOVED*** Cleanup health service
    if hasattr(app.state, "health_service") and app.state.health_service:
        logger.info("Closing health service")
        app.state.health_service.close()

    ***REMOVED*** Cleanup any other resources here


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Create FastAPI app
    app = FastAPI(
        title="Recommendation API",
        description="AI-powered movie recommendation service for Next Watch platform",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    ***REMOVED*** Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  ***REMOVED*** In production, restrict this to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.is_production:
        logger.info(f"Adding TrustedHostMiddleware with allowed_hosts: {settings.allowed_hosts}")
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )

    ***REMOVED*** Include API v1 routes
    app.include_router(api_v1_router, prefix="/reco", tags=["reco-v1"])

    ***REMOVED*** Add root endpoint
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """Root endpoint returning API information."""
        return {
            "message": "Welcome to Next Watch Recommendation API",
            "api_versions": {
                "v1": "Available at /v1/recommendations/",
            },
            "health_checks": {
                "comprehensive": "/health - Full health check with all dependencies",
                "liveness": "/health/live - Simple liveness check",
                "readiness": "/health/ready - Readiness check for critical dependencies",
            },
            "documentation": "/docs",
        }

    ***REMOVED*** Add comprehensive health check endpoint
    @app.get("/health", tags=["health"])
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

    ***REMOVED*** Add simple liveness check endpoint
    @app.get("/health/live", tags=["health"])
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

    ***REMOVED*** Add readiness check endpoint
    @app.get("/health/ready", tags=["health"])
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

    ***REMOVED*** Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


***REMOVED*** Create default app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    ***REMOVED*** Use settings for all server parameters, including proxy headers
    uvicorn.run(
        "recommendation_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        proxy_headers=settings.proxy_headers,
        forwarded_allow_ips=settings.forwarded_allow_ips,
    )

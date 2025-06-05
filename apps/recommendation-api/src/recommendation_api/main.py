"""Main FastAPI application for the Recommendation API service."""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from recommendation_api.routes import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    ***REMOVED*** Startup
    logger.info(f"Starting Recommendation API service with config: {settings}")

    ***REMOVED*** Initialize any required services/clients here
    ***REMOVED*** For example: database connections, ML model loading, etc.

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Recommendation API service")
    ***REMOVED*** Cleanup any resources here


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
    async def root():
        """Root endpoint returning API information."""
        return {
            "message": "Welcome to Next Watch Recommendation API",
            "api_versions": {
                "v1": "Available at /v1/recommendations/",
            },
            "health": "Available at /health/",
            "documentation": "/docs",
        }

    ***REMOVED*** Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "recommendation-api",
            "version": "0.1.0",
            "environment": settings.environment,
            "checks": {
                "database": "pending",  ***REMOVED*** Will be implemented
                "qdrant": "pending",    ***REMOVED*** Will be implemented
                "embedding_model": "pending",  ***REMOVED*** Will be implemented
            }
        }

    ***REMOVED*** Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    return app


***REMOVED*** Create default app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "recommendation_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    ) 
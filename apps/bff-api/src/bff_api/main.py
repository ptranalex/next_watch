"""Main FastAPI application for BFF service."""

import os
import logging
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
from bff_api.config.app import settings
from bff_api.config.logging import configure_logging, get_logger

***REMOVED*** Configure logging early
configure_logging(
    log_level=getattr(settings, "log_level", "INFO"),
    log_dir=(
        Path(getattr(settings, "log_dir", "./logs")) if hasattr(settings, "log_dir") else None
    ),
    verbose=settings.debug,
    quiet=False,
)

***REMOVED*** Get logger for this module
logger = get_logger(__name__)

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

***REMOVED*** Import versioned API router
from bff_api.routes.api_v1 import api_v1_router
from bff_api.routes.v1 import health
from bff_api.middlewares.logging import LoggingMiddleware
from bff_api.middlewares.auth import AuthMiddleware
from bff_api.services.backend_client import BackendClient
from bff_api.services.auth_client import AuthClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    ***REMOVED*** Startup
    logger.info(f"Starting BFF service with config: {settings}")

    ***REMOVED*** Initialize backend client
    backend_client = BackendClient(settings)
    app.state.backend_client = backend_client

    ***REMOVED*** Initialize auth client
    auth_client = AuthClient(settings)
    app.state.auth_client = auth_client

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down BFF service")
    if hasattr(app.state, "backend_client"):
        await app.state.backend_client.close()
    if hasattr(app.state, "auth_client"):
        await app.state.auth_client.close()


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Create FastAPI app
    app = FastAPI(
        title="Next Watch BFF",
        description="Backend for Frontend aggregation layer for Next Watch movie platform",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    ***REMOVED*** Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  ***REMOVED*** Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)

    ***REMOVED*** Add routes
    app.include_router(health.router, prefix="/health", tags=["health"])

    ***REMOVED*** Register versioned BFF API (includes auth routes at /bff/v1/auth/*)
    app.include_router(api_v1_router, prefix="/bff", tags=["bff-v1"])

    ***REMOVED*** Add root endpoint
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """Root endpoint returning BFF API information."""
        return {
            "message": "Welcome to Next Watch BFF API",
            "api_versions": {
                "v1": "Available at /bff/v1/",
            },
            "authentication": "Available at /bff/v1/auth/",
            "health": "Available at /health/",
            "documentation": "/docs",
        }

    ***REMOVED*** Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


***REMOVED*** Create default app instance
app = create_app()

if __name__ == "__main__":
    import sys
    from bff_api.cli.main import main

    ***REMOVED*** Forward to the CLI and pass the exit code to sys.exit
    sys.exit(main())

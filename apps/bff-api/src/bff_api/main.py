"""Main FastAPI application for BFF service."""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

***REMOVED*** Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

***REMOVED*** Load environment variables
try:
    from dotenv import load_dotenv

    ***REMOVED*** Only load .env files if we're not in production
    if os.getenv("ENVIRONMENT") != "production":
        ***REMOVED*** Try multiple locations to find the .env.local file
        possible_paths = [
            Path(__file__).resolve().parents[3] / ".env.local",
            Path.cwd() / ".env.local",
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"Loading environment variables from {path}")
                load_dotenv(dotenv_path=path, override=True)
                break
except ImportError:
    pass  ***REMOVED*** Continue without dotenv if not installed

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

***REMOVED*** Import configuration after environment variables are loaded
from bff_api.config.app import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from bff_api.routes import bff_router, health_router
from bff_api.middlewares.logging import LoggingMiddleware
from bff_api.middlewares.auth import AuthMiddleware
from bff_api.services.backend_client import BackendClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    ***REMOVED*** Startup
    logger.info(f"Starting BFF service with config: {settings}")

    ***REMOVED*** Initialize backend client
    backend_client = BackendClient(settings)
    app.state.backend_client = backend_client

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down BFF service")
    if hasattr(app.state, "backend_client"):
        await app.state.backend_client.close()


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
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", settings.host],
        )

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)

    ***REMOVED*** Add routes
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(bff_router, prefix="/bff", tags=["bff"])

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

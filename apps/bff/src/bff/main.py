"""Main FastAPI application for BFF service."""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from bff.config import Config, configure_logging
from bff.routes import bff_router, health_router
from bff.middlewares.logging import LoggingMiddleware
from bff.middlewares.auth import AuthMiddleware
from bff.services.backend_client import BackendClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    ***REMOVED*** Startup
    config = app.state.config
    logger.info(f"Starting BFF service with config: {config}")

    ***REMOVED*** Initialize backend client
    backend_client = BackendClient(config)
    app.state.backend_client = backend_client

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down BFF service")
    if hasattr(app.state, "backend_client"):
        await app.state.backend_client.close()


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        config: Optional configuration instance

    Returns:
        Configured FastAPI application
    """
    if config is None:
        config = Config.get_instance()

    ***REMOVED*** Configure logging
    configure_logging(config)

    ***REMOVED*** Create FastAPI app
    app = FastAPI(
        title="Next Watch BFF",
        description="Backend for Frontend aggregation layer for Next Watch movie platform",
        version="0.1.0",
        debug=config.debug,
        lifespan=lifespan,
    )

    ***REMOVED*** Store config in app state
    app.state.config = config

    ***REMOVED*** Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if config.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", config.host],
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

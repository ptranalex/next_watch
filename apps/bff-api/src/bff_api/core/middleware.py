"""Middleware configuration for the BFF service.

This module configures all middleware for the Next Watch BFF service,
including CORS, authentication, logging, and performance monitoring.
"""

import datetime
import uuid
from typing import Any

from config.logging import get_logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

from bff_api.config.app import settings
from bff_api.middlewares.auth import AuthMiddleware
from bff_api.middlewares.logging import LoggingMiddleware

logger = get_logger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI application."""

    ***REMOVED*** --- Request Context Binding Middleware (MUST come first) ---
    @app.middleware("http")
    async def bind_request_context(request: Request, call_next: Any) -> Any:
        """Bind request_id and basic request info to structlog context."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            clear_contextvars()

    ***REMOVED*** --- CORS ---
    logger.info("Setting up CORS with origins", origins=settings.cors_origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "Authorization", "Content-Type"],
    )

    ***REMOVED*** --- Trusted Hosts ---
    if settings.is_production:
        logger.info(
            "Setting up TrustedHostMiddleware with allowed hosts", hosts=settings.allowed_hosts
        )
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )

    ***REMOVED*** --- Logging Middleware ---
    logger.info("Setting up request logging middleware")
    app.add_middleware(LoggingMiddleware)

    ***REMOVED*** --- Auth Middleware ---
    logger.info("Setting up authentication middleware")
    app.add_middleware(AuthMiddleware)

    ***REMOVED*** --- Performance Monitoring (Optional) ---
    if settings.enable_performance_metrics:
        logger.info("Setting up performance monitoring middleware")

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next: Any) -> Any:
            start_time = datetime.datetime.now()
            response = await call_next(request)
            duration = (datetime.datetime.now() - start_time).total_seconds()
            response.headers["X-Process-Time"] = str(duration)
            response.headers["X-Service"] = "bff"
            return response

    logger.info("All middleware configured successfully")

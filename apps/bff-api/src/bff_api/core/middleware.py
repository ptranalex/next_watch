"""Middleware configuration for the BFF service.

This module configures all middleware for the Next Watch BFF service,
including CORS, authentication, logging, and performance monitoring.
"""

import datetime
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from bff_api.config.app import settings
from bff_api.middlewares.logging import LoggingMiddleware
from bff_api.middlewares.auth import AuthMiddleware

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    ***REMOVED*** CORS Middleware - Critical for BFF as it serves frontend requests
    ***REMOVED*** The BFF is the primary entry point for frontend applications
    logger.info(f"Setting up CORS with origins: {settings.cors_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "Authorization", "Content-Type"],
    )

    ***REMOVED*** Trusted Host Middleware - Security for production
    if settings.is_production:
        logger.info(
            f"Setting up TrustedHostMiddleware with allowed hosts: {settings.allowed_hosts}"
        )
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )

    ***REMOVED*** Logging Middleware - Track all requests for monitoring
    logger.info("Setting up request logging middleware")
    app.add_middleware(LoggingMiddleware)

    ***REMOVED*** Authentication Middleware - Handle JWT tokens and user context
    logger.info("Setting up authentication middleware")
    app.add_middleware(AuthMiddleware)

    ***REMOVED*** Performance Monitoring Middleware - Optional performance tracking
    if settings.enable_performance_metrics:
        logger.info("Setting up performance monitoring middleware")

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next: Any) -> Any:
            """Add performance timing headers to responses.

            Args:
                request: FastAPI request object
                call_next: Next middleware in chain

            Returns:
                Response with timing headers
            """
            start_time = datetime.datetime.now()
            response = await call_next(request)
            process_time = (datetime.datetime.now() - start_time).total_seconds()
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Service"] = "bff"
            return response

    logger.info("All middleware configured successfully")

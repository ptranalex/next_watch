"""Middleware configuration for the Backend API service.

This module contains middleware setup including CORS, error handling,
and performance monitoring for the Next Watch Backend API service.
"""

import datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend_api.config.app import settings
from backend_api.config.logging import get_logger
from backend_api.middlewares import ErrorHandlerMiddleware
from backend_api.middlewares.database_monitoring import DatabaseMonitoringMiddleware

logger = get_logger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    ***REMOVED*** Add CORS middleware
    ***REMOVED*** Note: This is important for the microservice architecture
    ***REMOVED*** The backend-api is called by the BFF, which needs to make cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  ***REMOVED*** Default Next.js port
            "http://localhost:3001",  ***REMOVED*** Your current port
            "http://localhost:3002",  ***REMOVED*** Any other ports you might use
            "http://localhost:8000",  ***REMOVED*** Other common development ports
            "http://127.0.0.1:3000",  ***REMOVED*** Also allow 127.0.0.1
            "http://127.0.0.1:3001",
        ]
        + settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "Authorization", "Content-Type"],
    )

    ***REMOVED*** Add error handling middleware
    app.add_middleware(ErrorHandlerMiddleware)

    ***REMOVED*** Database monitoring middleware if enabled
    if settings.database_monitoring_enabled:
        app.add_middleware(DatabaseMonitoringMiddleware, log_all_requests=settings.debug)
        logger.info("Database monitoring middleware enabled", debug_mode=settings.debug)

    ***REMOVED*** Performance metrics middleware if enabled
    if settings.enable_performance_metrics:
        setup_performance_middleware(app)

    logger.info(
        "Middleware configuration completed",
        monitoring_enabled=settings.database_monitoring_enabled,
        performance_metrics=settings.enable_performance_metrics,
    )


def setup_performance_middleware(app: FastAPI) -> None:
    """Setup performance monitoring middleware.

    Args:
        app: FastAPI application instance
    """

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Any) -> Any:
        """Add performance timing header to responses.

        Args:
            request: FastAPI request object
            call_next: Next middleware in chain

        Returns:
            Response with X-Process-Time header added
        """
        start_time = datetime.datetime.now()
        response = await call_next(request)
        process_time = (datetime.datetime.now() - start_time).total_seconds()
        response.headers["X-Process-Time"] = str(process_time)
        logger.debug(
            "Request processing time", path=str(request.url.path), process_time_seconds=process_time
        )
        return response

    logger.info("Performance monitoring middleware enabled")

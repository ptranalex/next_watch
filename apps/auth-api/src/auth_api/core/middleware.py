"""Middleware configuration for the FastAPI application."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from auth_api.config.app import settings

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Setup middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    ***REMOVED*** Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  ***REMOVED*** Frontend
            "http://localhost:8001",  ***REMOVED*** BFF
            "http://localhost:8002",  ***REMOVED*** Backend API
        ]
        + settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "Authorization", "Content-Type"],
    )

    ***REMOVED*** Add TrustedHost middleware in production
    if settings.is_production:
        logger.info(f"Adding TrustedHostMiddleware with allowed_hosts: {settings.allowed_hosts}")
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )

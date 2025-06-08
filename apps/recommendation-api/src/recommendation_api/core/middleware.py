"""Middleware configuration for the FastAPI application."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from recommendation_api.config import settings

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Setup middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    ***REMOVED*** Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  ***REMOVED*** In production, restrict this to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ***REMOVED*** Add TrustedHost middleware in production
    if settings.is_production:
        logger.info(f"Adding TrustedHostMiddleware with allowed_hosts: {settings.allowed_hosts}")
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )

"""CORS middleware for FastAPI applications.

This module provides CORS (Cross-Origin Resource Sharing) middleware
configuration for FastAPI applications.
"""

from typing import Any, List

from config.logging import get_logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger(__name__)


def setup_cors(app: FastAPI, settings: Any) -> None:
    """Set up CORS middleware for FastAPI application.

    Args:
        app: FastAPI application
        settings: Application settings with CORS configuration
    """
    ***REMOVED*** Get CORS configuration from settings
    cors_config = {}

    if hasattr(settings, "get_cors_config"):
        cors_config = settings.get_cors_config()
    else:
        ***REMOVED*** Fallback to individual attributes
        cors_config = {
            "allow_origins": getattr(settings, "cors_origins", ["*"]),
            "allow_credentials": getattr(settings, "cors_allow_credentials", True),
            "allow_methods": getattr(settings, "cors_allow_methods", ["*"]),
            "allow_headers": getattr(settings, "cors_allow_headers", ["*"]),
        }

    ***REMOVED*** Add CORS middleware
    app.add_middleware(CORSMiddleware, **cors_config)

    logger.info(
        f"CORS middleware configured with origins: {cors_config.get('allow_origins', ['*'])}"
    )


def get_default_cors_config() -> dict:
    """Get default CORS configuration.

    Returns:
        Dictionary with default CORS settings
    """
    return {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-API-Key",
        ],
        "expose_headers": [
            "X-Request-ID",
            "X-Total-Count",
            "X-Page",
            "X-Page-Size",
        ],
    }


def setup_production_cors(
    app: FastAPI,
    allowed_origins: List[str],
    allow_credentials: bool = True,
) -> None:
    """Set up CORS for production environment with restricted origins.

    Args:
        app: FastAPI application
        allowed_origins: List of allowed origins
        allow_credentials: Whether to allow credentials
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-API-Key",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Total-Count",
            "X-Page",
            "X-Page-Size",
        ],
    )

    logger.info(f"Production CORS middleware configured with origins: {allowed_origins}")

"""Middleware components for FastAPI applications.

This module provides middleware components for FastAPI applications,
including CORS, logging, metrics, security, and tracing.
"""

from typing import Any

from fastapi import FastAPI

try:
    from config.logging import get_logger
except ImportError:
    import logging

    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


def setup_middleware(app: FastAPI, settings: Any) -> None:
    """Set up standard middleware stack for FastAPI application.

    Args:
        app: FastAPI application
        settings: Application settings
    """
    ***REMOVED*** Set up CORS middleware
    try:
        from .cors import setup_cors

        setup_cors(app, settings)
    except ImportError:
        logger.warning("CORS middleware not available, skipping")

    ***REMOVED*** Set up security middleware
    try:
        from .security import setup_security

        setup_security(app, settings)
    except ImportError:
        logger.warning("Security middleware not available, skipping")

    ***REMOVED*** Set up logging middleware
    try:
        from .logging import setup_logging

        setup_logging(app, settings)
    except ImportError:
        logger.warning("Logging middleware not available, skipping")

    ***REMOVED*** Set up metrics middleware
    try:
        from .metrics import setup_metrics

        setup_metrics(app, settings)
    except ImportError:
        logger.warning("Metrics middleware not available, skipping")

    ***REMOVED*** Set up tracing middleware
    try:
        from .tracing import setup_tracing

        setup_tracing(app, settings)
    except ImportError:
        logger.warning("Tracing middleware not available, skipping")

    logger.info("Middleware setup complete")

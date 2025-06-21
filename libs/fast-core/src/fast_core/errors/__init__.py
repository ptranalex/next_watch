"""Error handling for FastAPI applications.

This module provides error handling utilities for FastAPI applications,
including exception handlers and standardized error responses.
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

try:
    from config.logging import get_logger
except ImportError:
    import logging

    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions.

    Args:
        request: Request that caused the exception
        exc: HTTP exception

    Returns:
        JSON response with error details
    """
    logger.debug(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation exceptions.

    Args:
        request: Request that caused the exception
        exc: Validation exception

    Returns:
        JSON response with error details
    """
    errors = exc.errors()
    logger.debug(f"Validation error: {errors}")

    ***REMOVED*** Format errors for better readability
    formatted_errors = []
    for error in errors:
        formatted_errors.append(
            {
                "loc": " -> ".join(str(loc) for loc in error["loc"]),
                "msg": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": formatted_errors,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions.

    Args:
        request: Request that caused the exception
        exc: Exception

    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Set up exception handlers for FastAPI application.

    Args:
        app: FastAPI application
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered")

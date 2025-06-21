"""Error handlers for FastAPI applications.

This module provides error handlers for custom exception classes
and other common error scenarios.
"""

from typing import Any, Dict

from config.logging import get_logger
from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import (
    APIException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ConflictException,
    ExternalServiceException,
    RateLimitException,
    ResourceNotFoundException,
    ServiceUnavailableException,
    ValidationException,
)

logger = get_logger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle API exceptions.

    Args:
        request: HTTP request
        exc: API exception

    Returns:
        JSON response with error details
    """
    ***REMOVED*** Base error response
    error_response: Dict[str, Any] = {
        "detail": exc.detail,
    }

    ***REMOVED*** Add error code if available
    if exc.error_code:
        error_response["error_code"] = exc.error_code

    ***REMOVED*** Add context if available
    if exc.context:
        error_response["context"] = exc.context

    ***REMOVED*** Add exception-specific fields
    if isinstance(exc, ValidationException) and exc.field_errors:
        error_response["field_errors"] = exc.field_errors

    elif isinstance(exc, AuthorizationException) and exc.required_permissions:
        error_response["required_permissions"] = exc.required_permissions

    elif isinstance(exc, ResourceNotFoundException):
        if exc.resource_type:
            error_response["resource_type"] = exc.resource_type
        if exc.resource_id:
            error_response["resource_id"] = exc.resource_id

    elif isinstance(exc, ConflictException) and exc.conflicting_resource:
        error_response["conflicting_resource"] = exc.conflicting_resource

    elif isinstance(exc, RateLimitException) and exc.retry_after:
        error_response["retry_after"] = exc.retry_after

    elif isinstance(exc, ServiceUnavailableException) and exc.service_name:
        error_response["service_name"] = exc.service_name

    elif isinstance(exc, ExternalServiceException):
        if exc.service_name:
            error_response["service_name"] = exc.service_name
        if exc.upstream_status:
            error_response["upstream_status"] = exc.upstream_status

    ***REMOVED*** Log the error
    log_data = {
        "error_code": exc.error_code,
        "status_code": exc.status_code,
        "detail": exc.detail,
        "url": str(request.url),
        "method": request.method,
    }

    if exc.status_code >= 500:
        logger.error("API exception", extra=log_data)
    elif exc.status_code >= 400:
        logger.warning("API exception", extra=log_data)
    else:
        logger.info("API exception", extra=log_data)

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """Handle validation exceptions.

    Args:
        request: HTTP request
        exc: Validation exception

    Returns:
        JSON response with validation error details
    """
    return await api_exception_handler(request, exc)


async def authentication_exception_handler(
    request: Request, exc: AuthenticationException
) -> JSONResponse:
    """Handle authentication exceptions.

    Args:
        request: HTTP request
        exc: Authentication exception

    Returns:
        JSON response with authentication error
    """
    return await api_exception_handler(request, exc)


async def authorization_exception_handler(
    request: Request, exc: AuthorizationException
) -> JSONResponse:
    """Handle authorization exceptions.

    Args:
        request: HTTP request
        exc: Authorization exception

    Returns:
        JSON response with authorization error
    """
    return await api_exception_handler(request, exc)


async def not_found_exception_handler(
    request: Request, exc: ResourceNotFoundException
) -> JSONResponse:
    """Handle resource not found exceptions.

    Args:
        request: HTTP request
        exc: Resource not found exception

    Returns:
        JSON response with not found error
    """
    return await api_exception_handler(request, exc)


async def conflict_exception_handler(request: Request, exc: ConflictException) -> JSONResponse:
    """Handle conflict exceptions.

    Args:
        request: HTTP request
        exc: Conflict exception

    Returns:
        JSON response with conflict error
    """
    return await api_exception_handler(request, exc)


async def rate_limit_exception_handler(request: Request, exc: RateLimitException) -> JSONResponse:
    """Handle rate limit exceptions.

    Args:
        request: HTTP request
        exc: Rate limit exception

    Returns:
        JSON response with rate limit error
    """
    return await api_exception_handler(request, exc)


async def service_unavailable_exception_handler(
    request: Request, exc: ServiceUnavailableException
) -> JSONResponse:
    """Handle service unavailable exceptions.

    Args:
        request: HTTP request
        exc: Service unavailable exception

    Returns:
        JSON response with service unavailable error
    """
    return await api_exception_handler(request, exc)


async def business_logic_exception_handler(
    request: Request, exc: BusinessLogicException
) -> JSONResponse:
    """Handle business logic exceptions.

    Args:
        request: HTTP request
        exc: Business logic exception

    Returns:
        JSON response with business logic error
    """
    return await api_exception_handler(request, exc)


async def external_service_exception_handler(
    request: Request, exc: ExternalServiceException
) -> JSONResponse:
    """Handle external service exceptions.

    Args:
        request: HTTP request
        exc: External service exception

    Returns:
        JSON response with external service error
    """
    return await api_exception_handler(request, exc)


def get_exception_handlers() -> Dict[Any, Any]:
    """Get dictionary of exception handlers.

    Returns:
        Dictionary mapping exception classes to handler functions
    """
    return {
        APIException: api_exception_handler,
        ValidationException: validation_exception_handler,
        AuthenticationException: authentication_exception_handler,
        AuthorizationException: authorization_exception_handler,
        ResourceNotFoundException: not_found_exception_handler,
        ConflictException: conflict_exception_handler,
        RateLimitException: rate_limit_exception_handler,
        ServiceUnavailableException: service_unavailable_exception_handler,
        BusinessLogicException: business_logic_exception_handler,
        ExternalServiceException: external_service_exception_handler,
    }

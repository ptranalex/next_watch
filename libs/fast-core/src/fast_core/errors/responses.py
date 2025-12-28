"""Standard error response models and utilities.

This module provides standard error response models and utilities
for consistent error responses across FastAPI applications.
"""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Standard error detail model."""

    detail: str = Field(..., description="Error detail message")
    error_code: str | None = Field(None, description="Application-specific error code")
    context: dict[str, Any] | None = Field(None, description="Additional error context")


class ValidationErrorDetail(ErrorDetail):
    """Validation error detail model."""

    field_errors: dict[str, str] | None = Field(None, description="Field-specific error messages")


class AuthorizationErrorDetail(ErrorDetail):
    """Authorization error detail model."""

    required_permissions: list[str] | None = Field(None, description="List of required permissions")


class ResourceNotFoundErrorDetail(ErrorDetail):
    """Resource not found error detail model."""

    resource_type: str | None = Field(None, description="Type of resource not found")
    resource_id: str | None = Field(None, description="ID of resource not found")


class ConflictErrorDetail(ErrorDetail):
    """Conflict error detail model."""

    conflicting_resource: str | None = Field(
        None, description="Information about conflicting resource"
    )


class RateLimitErrorDetail(ErrorDetail):
    """Rate limit error detail model."""

    retry_after: int | None = Field(None, description="Seconds to wait before retrying")


class ServiceUnavailableErrorDetail(ErrorDetail):
    """Service unavailable error detail model."""

    service_name: str | None = Field(None, description="Name of unavailable service")


class ExternalServiceErrorDetail(ErrorDetail):
    """External service error detail model."""

    service_name: str | None = Field(None, description="Name of external service")
    upstream_status: int | None = Field(None, description="Status code from upstream service")


class PaginationInfo(BaseModel):
    """Pagination information model."""

    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class SuccessResponse(BaseModel):
    """Standard success response model."""

    message: str = Field(..., description="Success message")
    data: Any | None = Field(None, description="Response data")


class PaginatedResponse(BaseModel):
    """Paginated response model."""

    data: list[Any] = Field(..., description="List of items")
    pagination: PaginationInfo = Field(..., description="Pagination information")


def create_error_response(
    detail: str,
    error_code: str | None = None,
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a standard error response.

    Args:
        detail: Error detail message
        error_code: Application-specific error code
        context: Additional error context
        **kwargs: Additional fields to include in response

    Returns:
        Dictionary containing error response
    """
    response: dict[str, Any] = {
        "detail": detail,
    }

    if error_code:
        response["error_code"] = error_code

    if context:
        response["context"] = context

    ***REMOVED*** Add any additional fields
    response.update(kwargs)

    return response


def create_validation_error_response(
    detail: str = "Validation error",
    field_errors: dict[str, str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a validation error response.

    Args:
        detail: Error detail message
        field_errors: Field-specific error messages
        **kwargs: Additional fields to include in response

    Returns:
        Dictionary containing validation error response
    """
    response = create_error_response(
        detail=detail,
        error_code="VALIDATION_ERROR",
        **kwargs,
    )

    if field_errors:
        response["field_errors"] = field_errors

    return response


def create_success_response(
    message: str,
    data: Any | None = None,
) -> dict[str, Any]:
    """Create a standard success response.

    Args:
        message: Success message
        data: Response data

    Returns:
        Dictionary containing success response
    """
    response = {"message": message}

    if data is not None:
        response["data"] = data

    return response


def create_paginated_response(
    data: list[Any],
    page: int,
    page_size: int,
    total_items: int,
) -> dict[str, Any]:
    """Create a paginated response.

    Args:
        data: List of items
        page: Current page number
        page_size: Number of items per page
        total_items: Total number of items

    Returns:
        Dictionary containing paginated response
    """
    total_pages = (total_items + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1

    return {
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        },
    }


***REMOVED*** Standard response models for OpenAPI documentation
STANDARD_RESPONSES = {
    400: {
        "model": ErrorDetail,
        "description": "Bad Request",
    },
    401: {
        "model": ErrorDetail,
        "description": "Unauthorized",
    },
    403: {
        "model": AuthorizationErrorDetail,
        "description": "Forbidden",
    },
    404: {
        "model": ResourceNotFoundErrorDetail,
        "description": "Not Found",
    },
    409: {
        "model": ConflictErrorDetail,
        "description": "Conflict",
    },
    422: {
        "model": ValidationErrorDetail,
        "description": "Validation Error",
    },
    429: {
        "model": RateLimitErrorDetail,
        "description": "Too Many Requests",
    },
    500: {
        "model": ErrorDetail,
        "description": "Internal Server Error",
    },
    502: {
        "model": ExternalServiceErrorDetail,
        "description": "Bad Gateway",
    },
    503: {
        "model": ServiceUnavailableErrorDetail,
        "description": "Service Unavailable",
    },
}

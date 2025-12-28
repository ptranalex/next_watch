"""
Standard error types for application services and queries.

This module defines a set of standard error types that can be raised by services and queries,
providing a consistent error handling approach throughout the application.
"""

from typing import Any

from fastapi import HTTPException, status


class ServiceError(Exception):
    """Base class for all service errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ResourceNotFoundError(ServiceError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: str | None = None,
        resource_id: str | int | None = None,
        details: dict[str, Any] | None = None,
    ):
        resource_details = details or {}
        if resource_type:
            resource_details["resource_type"] = resource_type
        if resource_id:
            resource_details["resource_id"] = resource_id

        super().__init__(message, resource_details)


class ValidationError(ServiceError):
    """Raised when input data fails validation."""

    def __init__(
        self,
        message: str = "Validation error",
        field_errors: dict[str, list[str]] | None = None,
        details: dict[str, Any] | None = None,
    ):
        validation_details = details or {}
        if field_errors:
            validation_details["field_errors"] = field_errors

        super().__init__(message, validation_details)


class ConflictError(ServiceError):
    """Raised when an operation would result in a conflict with existing data."""

    def __init__(
        self,
        message: str = "Operation would result in a conflict",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details)


class PermissionError(ServiceError):
    """Raised when a user doesn't have permission to perform an operation."""

    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        permission_details = details or {}
        if required_permission:
            permission_details["required_permission"] = required_permission

        super().__init__(message, permission_details)


def service_error_to_http_exception(error: ServiceError) -> HTTPException:
    """
    Convert a service error to an appropriate HTTP exception.

    Args:
        error: The service error to convert

    Returns:
        An HTTP exception with the appropriate status code and detail
    """
    if isinstance(error, ResourceNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": error.message, "details": error.details},
        )
    elif isinstance(error, ValidationError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": error.message, "details": error.details},
        )
    elif isinstance(error, ConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": error.message, "details": error.details},
        )
    elif isinstance(error, PermissionError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": error.message, "details": error.details},
        )
    else:
        ***REMOVED*** Default for other service errors
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": error.message, "details": error.details},
        )

"""Custom exception classes for FastAPI applications.

This module provides custom exception classes that can be raised in
FastAPI applications and handled by the error handlers.
"""

from typing import Any

from fastapi import HTTPException


class APIException(HTTPException):
    """Base API exception class.

    All custom API exceptions should inherit from this class.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ):
        """Initialize API exception.

        Args:
            status_code: HTTP status code
            detail: Error detail message
            error_code: Application-specific error code
            context: Additional context information
            headers: HTTP headers to include in response
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.context = context or {}


class ValidationException(APIException):
    """Validation error exception."""

    def __init__(
        self,
        detail: str = "Validation error",
        field_errors: list[dict[str, Any]] | None = None,
        error_code: str = "VALIDATION_ERROR",
        context: dict[str, Any] | None = None,
    ):
        """Initialize validation exception.

        Args:
            detail: Error detail message
            field_errors: List of field-specific validation errors
            error_code: Application-specific error code
            context: Additional context information
        """
        super().__init__(
            status_code=422,
            detail=detail,
            error_code=error_code,
            context=context,
        )
        self.field_errors = field_errors or []


class AuthenticationException(APIException):
    """Authentication error exception."""

    def __init__(
        self,
        detail: str = "Authentication required",
        error_code: str = "AUTHENTICATION_REQUIRED",
        context: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ):
        """Initialize authentication exception.

        Args:
            detail: Error detail message
            error_code: Application-specific error code
            context: Additional context information
            headers: HTTP headers to include in response
        """
        ***REMOVED*** Add WWW-Authenticate header if not provided
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}

        super().__init__(
            status_code=401,
            detail=detail,
            error_code=error_code,
            context=context,
            headers=headers,
        )


class AuthorizationException(APIException):
    """Authorization error exception."""

    def __init__(
        self,
        detail: str = "Insufficient permissions",
        required_permissions: list[str] | None = None,
        error_code: str = "INSUFFICIENT_PERMISSIONS",
        context: dict[str, Any] | None = None,
    ):
        """Initialize authorization exception.

        Args:
            detail: Error detail message
            required_permissions: List of required permissions
            error_code: Application-specific error code
            context: Additional context information
        """
        super().__init__(
            status_code=403,
            detail=detail,
            error_code=error_code,
            context=context,
        )
        self.required_permissions = required_permissions or []


class ResourceNotFoundException(APIException):
    """Resource not found exception."""

    def __init__(
        self,
        detail: str = "Resource not found",
        resource_type: str | None = None,
        resource_id: str | None = None,
        error_code: str = "RESOURCE_NOT_FOUND",
        context: dict[str, Any] | None = None,
    ):
        """Initialize resource not found exception.

        Args:
            detail: Error detail message
            resource_type: Type of resource that was not found
            resource_id: ID of resource that was not found
            error_code: Application-specific error code
            context: Additional context information
        """
        super().__init__(
            status_code=404,
            detail=detail,
            error_code=error_code,
            context=context,
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class ConflictException(APIException):
    """Conflict exception for duplicate resources or state conflicts."""

    def __init__(
        self,
        detail: str = "Resource conflict",
        conflicting_resource: dict[str, Any] | None = None,
        error_code: str = "RESOURCE_CONFLICT",
        context: dict[str, Any] | None = None,
    ):
        """Initialize conflict exception.

        Args:
            detail: Error detail message
            conflicting_resource: Information about the conflicting resource
            error_code: Application-specific error code
            context: Additional context information
        """
        super().__init__(
            status_code=409,
            detail=detail,
            error_code=error_code,
            context=context,
        )
        self.conflicting_resource = conflicting_resource


class RateLimitException(APIException):
    """Rate limit exceeded exception."""

    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: int | None = None,
        error_code: str = "RATE_LIMIT_EXCEEDED",
        context: dict[str, Any] | None = None,
    ):
        """Initialize rate limit exception.

        Args:
            detail: Error detail message
            retry_after: Number of seconds to wait before retrying
            error_code: Application-specific error code
            context: Additional context information
        """
        headers = {}
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)

        super().__init__(
            status_code=429,
            detail=detail,
            error_code=error_code,
            context=context,
            headers=headers,
        )
        self.retry_after = retry_after


class ServiceUnavailableException(APIException):
    """Service unavailable exception."""

    def __init__(
        self,
        detail: str = "Service temporarily unavailable",
        service_name: str | None = None,
        retry_after: int | None = None,
        error_code: str = "SERVICE_UNAVAILABLE",
        context: dict[str, Any] | None = None,
    ):
        """Initialize service unavailable exception.

        Args:
            detail: Error detail message
            service_name: Name of the unavailable service
            retry_after: Number of seconds to wait before retrying
            error_code: Application-specific error code
            context: Additional context information
        """
        headers = {}
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)

        super().__init__(
            status_code=503,
            detail=detail,
            error_code=error_code,
            context=context,
            headers=headers,
        )
        self.service_name = service_name


class BusinessLogicException(APIException):
    """Business logic error exception."""

    def __init__(
        self,
        detail: str,
        error_code: str = "BUSINESS_LOGIC_ERROR",
        context: dict[str, Any] | None = None,
    ):
        """Initialize business logic exception.

        Args:
            detail: Error detail message
            error_code: Application-specific error code
            context: Additional context information
        """
        super().__init__(
            status_code=400,
            detail=detail,
            error_code=error_code,
            context=context,
        )


class ExternalServiceException(APIException):
    """External service error exception."""

    def __init__(
        self,
        detail: str = "External service error",
        service_name: str | None = None,
        upstream_status: int | None = None,
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        context: dict[str, Any] | None = None,
    ):
        """Initialize external service exception.

        Args:
            detail: Error detail message
            service_name: Name of the external service
            upstream_status: HTTP status code from the external service
            error_code: Application-specific error code
            context: Additional context information
        """
        super().__init__(
            status_code=502,
            detail=detail,
            error_code=error_code,
            context=context,
        )
        self.service_name = service_name
        self.upstream_status = upstream_status

"""
Fast Core Error Handling

This module provides a comprehensive error handling system for FastAPI applications.
It includes:
- Standard exception hierarchy
- Service error handling decorators
- HTTP status code mapping
- Error context and metadata support
"""

from .exceptions import (
    # Exception classes (full names)
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
from .handlers import (
    ServiceErrorContext,
    create_error_response,
    critical_service_handler,
    handle_service_error,
    optional_service_handler,
    service_error_handler,
)

# Export all public classes and functions
__all__ = [
    # Exception classes (full names)
    "APIException",
    "AuthenticationException",
    "AuthorizationException",
    "BusinessLogicException",
    "ConflictException",
    "ExternalServiceException",
    "RateLimitException",
    "ResourceNotFoundException",
    "ServiceUnavailableException",
    "ValidationException",
    # Handler functions and utilities
    "handle_service_error",
    "service_error_handler",
    "critical_service_handler",
    "optional_service_handler",
    "ServiceErrorContext",
    "create_error_response",
]

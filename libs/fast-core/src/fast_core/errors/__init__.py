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
    ***REMOVED*** Exception classes (full names)
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
    handle_service_error,
    service_error_handler,
    ServiceErrorContext,
    create_error_response,
)

***REMOVED*** Export all public classes and functions
__all__ = [
    ***REMOVED*** Exception classes (full names)
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
    ***REMOVED*** Handler functions and utilities
    "handle_service_error",
    "service_error_handler",
    "ServiceErrorContext",
    "create_error_response",
]

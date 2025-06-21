"""Fast Core - A core library for FastAPI applications.

This library provides standardized patterns and utilities for building
FastAPI applications with consistent structure and behavior.
"""

__version__ = "0.1.0"

***REMOVED*** Core application factory
from .app import AppOptions, create_app

***REMOVED*** Configuration
from .config import FastAPIConfig, FastAPIConfigMixin

***REMOVED*** Routing components
from .routing.base import BaseRouter

try:
    from .routing.pagination import (
        PaginatedResult,
        PaginationMeta,
        PaginationParams,
        Paginator,
        get_pagination_params,
        paginate_results,
    )
    from .routing.versioning import (
        APIVersion,
        VersionedRouter,
        VersioningStrategy,
        version_dependency,
        version_header_dependency,
    )
except ImportError:
    pass

***REMOVED*** Error handling
try:
    from .errors.exceptions import (
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
    from .errors.responses import (
        STANDARD_RESPONSES,
        AuthorizationErrorDetail,
        ConflictErrorDetail,
        ErrorDetail,
        ExternalServiceErrorDetail,
        PaginatedResponse,
        PaginationInfo,
        RateLimitErrorDetail,
        ResourceNotFoundErrorDetail,
        ServiceUnavailableErrorDetail,
        SuccessResponse,
        ValidationErrorDetail,
        create_error_response,
        create_paginated_response,
        create_success_response,
        create_validation_error_response,
    )
except ImportError:
    pass

***REMOVED*** Health monitoring
try:
    from .monitoring.health import (
        HealthCheck,
        HealthCheckResult,
        check_database,
        check_redis,
        setup_health_checks,
    )
except ImportError:
    pass

***REMOVED*** Security utilities
try:
    from .security.jwt import (
        JWTConfig,
        JWTManager,
        TokenData,
        create_jwt_manager,
        generate_secret_key,
    )
    from .security.rate_limit import (
        MemoryRateLimiter,
        RateLimiter,
        RedisRateLimiter,
        check_rate_limit,
        create_redis_rate_limiter,
        get_client_key,
        rate_limit,
    )
except ImportError:
    pass

***REMOVED*** Dependencies (conditionally imported based on availability)
try:
    from .dependencies import *
except ImportError:
    pass

***REMOVED*** Middleware setup functions
try:
    from .middleware import setup_middleware
    from .middleware.cors import get_default_cors_config, setup_cors, setup_production_cors
    from .middleware.logging import LoggingMiddleware, get_request_logger, setup_logging
    from .middleware.security import (
        RateLimitMiddleware,
        SecurityHeadersMiddleware,
        get_security_headers,
        setup_security,
    )
except ImportError:
    pass

***REMOVED*** Error handlers setup
try:
    from .errors import setup_exception_handlers
    from .errors.handlers import get_exception_handlers
except ImportError:
    pass

***REMOVED*** Main exports for common usage
__all__ = [
    ***REMOVED*** Core
    "create_app",
    "AppOptions",
    "FastAPIConfig",
    "FastAPIConfigMixin",
    ***REMOVED*** Routing
    "BaseRouter",
    "PaginationParams",
    "get_pagination_params",
    "paginate_results",
    ***REMOVED*** Error handling
    "APIException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "ConflictException",
    "create_error_response",
    "create_success_response",
    "STANDARD_RESPONSES",
    ***REMOVED*** Health monitoring
    "HealthCheck",
    "HealthCheckResult",
    "setup_health_checks",
    ***REMOVED*** Security
    "JWTManager",
    "JWTConfig",
    "TokenData",
    "create_jwt_manager",
    "RateLimiter",
    "MemoryRateLimiter",
    "check_rate_limit",
    "rate_limit",
    ***REMOVED*** Middleware
    "setup_middleware",
    "setup_cors",
    "setup_logging",
    "setup_security",
    ***REMOVED*** Error handlers
    "setup_exception_handlers",
]

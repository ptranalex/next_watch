"""
Fast Core Middleware Configuration

This module provides a flexible builder pattern for configuring FastAPI middleware
with granular control over individual middleware settings.

Features:
- CORS configuration with specific origins, methods, and headers
- Security headers with customizable policies
- Rate limiting with per-endpoint rules
- Logging configuration with filtering and formatting options
- Request/response middleware with custom processing
- Builder pattern for easy composition and reuse
"""

from .config import (
    MiddlewareConfig,
    CORSConfig,
    SecurityConfig,
    LoggingConfig,
    RateLimitConfig,
    RequestConfig,
    DEFAULT_METRICS_EXCLUDE_PATHS,
    DEFAULT_LOGGING_EXCLUDE_PATHS,
)
from .setup import setup_middleware

__all__ = [
    ***REMOVED*** Main configuration class
    "MiddlewareConfig",
    ***REMOVED*** Individual config classes
    "CORSConfig",
    "SecurityConfig",
    "LoggingConfig",
    "RateLimitConfig",
    "RequestConfig",
    ***REMOVED*** Constants for common configurations
    "DEFAULT_METRICS_EXCLUDE_PATHS",
    "DEFAULT_LOGGING_EXCLUDE_PATHS",
    ***REMOVED*** Setup function
    "setup_middleware",
]

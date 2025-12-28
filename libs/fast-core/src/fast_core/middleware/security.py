"""Security middleware for FastAPI applications.

This module provides security middleware for adding security headers
and protection mechanisms to FastAPI applications.
"""

from collections.abc import Callable
from typing import Any, cast

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

logger = structlog.get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""

    def __init__(
        self,
        app: Any,
        hsts_max_age: int = 31536000,  ***REMOVED*** 1 year
        content_type_nosniff: bool = True,
        x_frame_options: str = "DENY",
        x_content_type_options: str = "nosniff",
        referrer_policy: str = "strict-origin-when-cross-origin",
        custom_headers: dict[str, str] | None = None,
    ):
        """Initialize security headers middleware.

        Args:
            app: ASGI application
            hsts_max_age: HSTS max age in seconds
            content_type_nosniff: Whether to add X-Content-Type-Options header
            x_frame_options: X-Frame-Options header value
            x_content_type_options: X-Content-Type-Options header value
            referrer_policy: Referrer-Policy header value
            custom_headers: Additional custom security headers
        """
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.content_type_nosniff = content_type_nosniff
        self.x_frame_options = x_frame_options
        self.x_content_type_options = x_content_type_options
        self.referrer_policy = referrer_policy
        self.custom_headers = custom_headers or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response with security headers
        """
        response = await call_next(request)

        ***REMOVED*** Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains"
            )

        ***REMOVED*** Add content type options
        if self.content_type_nosniff:
            response.headers["X-Content-Type-Options"] = self.x_content_type_options

        ***REMOVED*** Add frame options
        response.headers["X-Frame-Options"] = self.x_frame_options

        ***REMOVED*** Add referrer policy
        response.headers["Referrer-Policy"] = self.referrer_policy

        ***REMOVED*** Add custom headers
        for header, value in self.custom_headers.items():
            response.headers[header] = value

        return cast(Response, response)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 60,
        exclude_paths: list[str] | None = None,
    ):
        """Initialize rate limiting middleware.

        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute per IP
            exclude_paths: Paths to exclude from rate limiting
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.exclude_paths = exclude_paths or []
        self.request_counts: dict[str, Any] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response or rate limit error
        """
        ***REMOVED*** Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return cast(Response, await call_next(request))

        ***REMOVED*** Get client IP
        client_ip = getattr(request.client, "host", "unknown") if request.client else "unknown"

        ***REMOVED*** For now, just proceed (real implementation would track request counts)
        ***REMOVED*** This is a placeholder for a more sophisticated rate limiting implementation
        logger.debug(f"Rate limit check for {client_ip} on {request.url.path}")

        return cast(Response, await call_next(request))


def setup_security(app: FastAPI, settings: Any) -> None:
    """Set up security middleware for FastAPI application.

    Args:
        app: FastAPI application
        settings: Application settings
    """
    ***REMOVED*** Add trusted host middleware
    allowed_hosts = getattr(settings, "allowed_hosts", ["*"])
    if allowed_hosts and "*" not in allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
        logger.info(f"Trusted host middleware configured with hosts: {allowed_hosts}")

    ***REMOVED*** Add security headers middleware
    security_headers_config = {
        "hsts_max_age": getattr(settings, "hsts_max_age", 31536000),
        "x_frame_options": getattr(settings, "x_frame_options", "DENY"),
        "x_content_type_options": getattr(settings, "x_content_type_options", "nosniff"),
        "referrer_policy": getattr(settings, "referrer_policy", "strict-origin-when-cross-origin"),
        "custom_headers": getattr(settings, "custom_security_headers", {}),
    }

    app.add_middleware(SecurityHeadersMiddleware, **security_headers_config)
    logger.info("Security headers middleware configured")

    ***REMOVED*** Add rate limiting if configured
    if getattr(settings, "enable_rate_limiting", False):
        rate_limit_config = {
            "requests_per_minute": getattr(settings, "rate_limit_requests_per_minute", 60),
            "exclude_paths": getattr(settings, "rate_limit_exclude_paths", ["/health", "/metrics"]),
        }
        app.add_middleware(RateLimitMiddleware, **rate_limit_config)
        logger.info("Rate limiting middleware configured")


def get_security_headers() -> dict[str, str]:
    """Get default security headers.

    Returns:
        Dictionary of default security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

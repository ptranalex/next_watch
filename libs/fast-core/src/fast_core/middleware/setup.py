"""
Middleware setup functions for Fast Core.

This module provides functions to set up FastAPI middleware based on
the configuration classes defined in the config module.
"""

import time
import uuid
from typing import Any, Callable, Optional, Dict, Deque, Union
from collections import defaultdict, deque
import structlog

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import (
    MiddlewareConfig,
    CORSConfig,
    SecurityConfig,
    LoggingConfig,
    RateLimitConfig,
    RequestConfig,
)

logger = structlog.get_logger(__name__)


def setup_middleware(app: FastAPI, config: MiddlewareConfig) -> None:
    """
    Set up middleware for FastAPI application based on configuration.

    Args:
        app: FastAPI application instance
        config: Middleware configuration
    """
    if not config.has_any_middleware():
        logger.info("No middleware configured, skipping setup")
        return

    ***REMOVED*** Set up middleware in reverse order (last added = first executed)

    ***REMOVED*** 1. Request processing middleware (innermost)
    if config.request_config and config.request_config.enabled:
        _setup_request_middleware(app, config.request_config)

    ***REMOVED*** 2. Rate limiting middleware
    if config.rate_limit_config and config.rate_limit_config.enabled:
        _setup_rate_limiting_middleware(app, config.rate_limit_config)

    ***REMOVED*** 3. Logging middleware
    if config.logging_config and config.logging_config.enabled:
        _setup_logging_middleware(app, config.logging_config)

    ***REMOVED*** 4. Security headers middleware
    if config.security_config and config.security_config.enabled:
        _setup_security_middleware(app, config.security_config)

    ***REMOVED*** 5. CORS middleware (outermost)
    if config.cors_config and config.cors_config.enabled:
        _setup_cors_middleware(app, config.cors_config)

    logger.info("Middleware setup complete")


def _setup_cors_middleware(app: FastAPI, config: CORSConfig) -> None:
    """Set up CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origins,
        allow_credentials=config.credentials,
        allow_methods=config.methods,
        allow_headers=config.headers,
        expose_headers=config.expose_headers,
        max_age=config.max_age,
    )
    logger.debug(f"CORS middleware configured with origins: {config.origins}")


def _setup_security_middleware(app: FastAPI, config: SecurityConfig) -> None:
    """Set up security headers middleware."""

    ***REMOVED*** Add trusted host middleware if configured
    if config.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.trusted_hosts)

    ***REMOVED*** Add security headers middleware
    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
            response: Response = await call_next(request)

            ***REMOVED*** HSTS
            if config.hsts:
                hsts_value = f"max-age={config.hsts_max_age}"
                if config.hsts_include_subdomains:
                    hsts_value += "; includeSubDomains"
                response.headers["Strict-Transport-Security"] = hsts_value

            ***REMOVED*** Frame options
            response.headers["X-Frame-Options"] = config.frame_options

            ***REMOVED*** Content type options
            if config.content_type_options:
                response.headers["X-Content-Type-Options"] = "nosniff"

            ***REMOVED*** XSS protection
            if config.xss_protection:
                response.headers["X-XSS-Protection"] = "1; mode=block"

            ***REMOVED*** CSP
            if config.csp:
                response.headers["Content-Security-Policy"] = config.csp

            ***REMOVED*** Referrer policy
            response.headers["Referrer-Policy"] = config.referrer_policy

            return response

    app.add_middleware(SecurityHeadersMiddleware)
    logger.debug("Security headers middleware configured")


def _setup_logging_middleware(app: FastAPI, config: LoggingConfig) -> None:
    """Set up request/response logging middleware."""

    class LoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
            ***REMOVED*** Skip excluded paths
            if request.url.path in config.exclude_paths:
                skip_response: Response = await call_next(request)
                return skip_response

            ***REMOVED*** Generate request ID for correlation
            request_id = str(uuid.uuid4())
            request.state.request_id = request_id

            start_time = time.time()

            ***REMOVED*** Log request
            log_data: Dict[str, Any] = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            }

            ***REMOVED*** Only include query params if they exist
            if request.query_params:
                log_data["query_params"] = dict(request.query_params)

            ***REMOVED*** Add user agent as separate field (more useful than in headers)
            if config.log_user_agent:
                user_agent = request.headers.get("user-agent")
                if user_agent:
                    log_data["user_agent"] = user_agent

            ***REMOVED*** Include only essential headers to reduce noise
            if config.include_headers:
                headers = dict(request.headers)

                ***REMOVED*** Remove excluded headers
                for header in config.exclude_headers:
                    headers.pop(header, None)

                ***REMOVED*** Remove noisy/redundant headers for cleaner logs
                noisy_headers = [
                    "user-agent",  ***REMOVED*** Already logged separately
                    "accept-encoding",
                    "accept-language",
                    "sec-ch-ua",
                    "sec-ch-ua-mobile",
                    "sec-ch-ua-platform",
                    "sec-fetch-site",
                    "sec-fetch-mode",
                    "sec-fetch-dest",
                    "dnt",
                    "connection",
                    "postman-token",  ***REMOVED*** Test tool specific
                    "cache-control",  ***REMOVED*** Usually not needed in logs
                ]
                for header in noisy_headers:
                    headers.pop(header, None)

                ***REMOVED*** Only include headers if there are any left after filtering
                if headers:
                    log_data["headers"] = headers

            if config.include_request_body:
                try:
                    body = await request.body()
                    if len(body) > 0:  ***REMOVED*** Only log if there's actually a body
                        if len(body) <= config.max_body_size:
                            log_data["request_body"] = body.decode("utf-8")
                        else:
                            log_data["request_body"] = f"<body too large: {len(body)} bytes>"
                except Exception:
                    log_data["request_body"] = "<unable to read body>"

            ***REMOVED*** Log request with appropriate level
            if config.level.upper() == "DEBUG":
                logger.debug("Request started", **log_data)
            elif config.level.upper() == "WARNING":
                logger.warning("Request started", **log_data)
            elif config.level.upper() == "ERROR":
                logger.error("Request started", **log_data)
            else:
                logger.info("Request started", **log_data)

            ***REMOVED*** Process request
            response: Response = await call_next(request)

            ***REMOVED*** Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            ***REMOVED*** Log response with timing
            process_time = time.time() - start_time
            response_data: Dict[str, Any] = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "response_size": response.headers.get("content-length"),
            }

            if config.include_response_body:
                ***REMOVED*** Note: This is complex for streaming responses
                ***REMOVED*** For now, we'll just log that we would include it
                response_data["response_body"] = "<response body logging not yet implemented>"

            ***REMOVED*** Log response with appropriate level based on status code
            if response.status_code >= 500:
                logger.error("Request completed", **response_data)
            elif response.status_code >= 400:
                logger.warning("Request completed", **response_data)
            elif config.level.upper() == "DEBUG":
                logger.debug("Request completed", **response_data)
            else:
                logger.info("Request completed", **response_data)

            return response

    app.add_middleware(LoggingMiddleware)
    logger.debug("Logging middleware configured")


def _setup_rate_limiting_middleware(app: FastAPI, config: RateLimitConfig) -> None:
    """Set up rate limiting middleware."""

    ***REMOVED*** Note: This is a basic implementation
    ***REMOVED*** In production, you'd want to use Redis or similar for distributed rate limiting

    ***REMOVED*** Simple in-memory rate limiter
    request_counts: Dict[str, Deque[float]] = defaultdict(deque)

    def parse_limit(limit_str: str) -> tuple[int, int]:
        """Parse limit string like '100/minute' into (requests, seconds)."""
        parts = limit_str.split("/")
        num_requests = int(parts[0])
        period = parts[1]

        period_seconds = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }.get(
            period, 60
        )  ***REMOVED*** Default to minute

        return num_requests, period_seconds

    class RateLimitMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
            ***REMOVED*** Get client identifier
            if config.key_func == "ip":
                key = request.client.host if request.client else "unknown"
            else:
                ***REMOVED*** For now, just use IP. In production, you'd implement user-based limiting
                key = request.client.host if request.client else "unknown"

            ***REMOVED*** Check if IP is exempt
            if key in config.exempt_ips:
                exempt_response: Response = await call_next(request)
                return exempt_response

            ***REMOVED*** Get limit for this endpoint
            limit_str = config.endpoints.get(request.url.path, config.default_limit)
            max_requests, window_seconds = parse_limit(limit_str)

            ***REMOVED*** Clean old requests
            now = time.time()
            requests = request_counts[key]
            while requests and requests[0] < now - window_seconds:
                requests.popleft()

            ***REMOVED*** Check rate limit
            if len(requests) >= max_requests:
                rate_limit_response = JSONResponse(
                    status_code=429, content={"detail": "Rate limit exceeded"}
                )
                if config.headers:
                    rate_limit_response.headers["X-RateLimit-Limit"] = str(max_requests)
                    rate_limit_response.headers["X-RateLimit-Remaining"] = "0"
                    rate_limit_response.headers["X-RateLimit-Reset"] = str(
                        int(now + window_seconds)
                    )
                return rate_limit_response

            ***REMOVED*** Record this request
            requests.append(now)

            ***REMOVED*** Process request
            response: Response = await call_next(request)

            ***REMOVED*** Add rate limit headers
            if config.headers:
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = str(max_requests - len(requests))
                response.headers["X-RateLimit-Reset"] = str(int(now + window_seconds))

            return response

    app.add_middleware(RateLimitMiddleware)
    logger.debug(f"Rate limiting middleware configured with default limit: {config.default_limit}")


def _setup_request_middleware(app: FastAPI, config: RequestConfig) -> None:
    """Set up general request processing middleware."""

    ***REMOVED*** Add gzip compression if enabled
    if config.gzip_compression:
        app.add_middleware(GZipMiddleware, minimum_size=config.gzip_minimum_size)

    class RequestProcessingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
            ***REMOVED*** Add request ID
            request_id = str(uuid.uuid4())
            if config.include_request_id:
                ***REMOVED*** Store request ID for use in other middleware/handlers
                request.state.request_id = request_id

            start_time = time.time()

            ***REMOVED*** Process request
            response: Response = await call_next(request)

            ***REMOVED*** Add headers
            if config.include_request_id:
                response.headers[config.request_id_header] = request_id

            if config.include_process_time:
                process_time = time.time() - start_time
                response.headers[config.process_time_header] = f"{process_time:.4f}"

            return response

    app.add_middleware(RequestProcessingMiddleware)
    logger.debug("Request processing middleware configured")

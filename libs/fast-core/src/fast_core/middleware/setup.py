"""
Middleware setup functions for Fast Core.

This module provides functions to set up FastAPI middleware based on
the configuration classes defined in the config module.
"""

import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Any

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import (
    ContextConfig,
    CORSConfig,
    LoggingConfig,
    MetricsConfig,
    MiddlewareConfig,
    RateLimitConfig,
    RequestConfig,
    SecurityConfig,
)

logger = structlog.get_logger(__name__)


def setup_middleware(app: FastAPI, config: MiddlewareConfig) -> None:
    """Set up middleware stack for FastAPI application.

    Middleware is added in reverse order (last added = outermost).
    Order: CORS -> Security -> Rate Limiting -> Logging -> Metrics -> Request -> Context

    Args:
        app: FastAPI application instance
        config: Middleware configuration
    """
    logger.debug("Setting up middleware stack")

    # Auto-enable context middleware if tracing is enabled in the app settings
    # This ensures all services get distributed tracing without manual configuration
    if not config.context_config:
        settings = getattr(app.state, "settings", None)
        if settings and getattr(settings, "enable_tracing", False):
            service_name = getattr(settings, "service_name", "unknown-service")
            logger.info(f"Auto-enabling context middleware for tracing (service: {service_name})")

            # Create default context config with optimal tracing settings
            from .config import ContextConfig

            config._context = ContextConfig(
                enabled=True,
                service_name=service_name,
                auto_generate_request_id=True,
                extract_user_id=True,
                trace_propagation=True,
                include_w3c_trace_context=True,
                include_b3_headers=True,
                include_jaeger_headers=True,
            )

    # 1. Request processing middleware (innermost)
    if config.request_config and config.request_config.enabled:
        _setup_request_middleware(app, config.request_config)

    # 2. Metrics middleware
    if config.metrics_config and config.metrics_config.enabled:
        _setup_metrics_middleware(app, config.metrics_config)

    # 3. Logging middleware
    if config.logging_config and config.logging_config.enabled:
        _setup_logging_middleware(app, config.logging_config)

    # 4. Rate limiting middleware
    if config.rate_limit_config and config.rate_limit_config.enabled:
        _setup_rate_limiting_middleware(app, config.rate_limit_config)

    # 5. Security headers middleware
    if config.security_config and config.security_config.enabled:
        _setup_security_middleware(app, config.security_config)

    # 6. Context middleware (for tracing and request correlation)
    if config.context_config and config.context_config.enabled:
        _setup_context_middleware(app, config.context_config)

    # 7. CORS middleware (outermost)
    if config.cors_config and config.cors_config.enabled:
        _setup_cors_middleware(app, config.cors_config)

    logger.info("Middleware setup complete")


def _setup_context_middleware(app: FastAPI, config: ContextConfig) -> None:
    """Set up request context middleware."""
    from .context import RequestContextMiddleware

    app.add_middleware(
        RequestContextMiddleware,
        service_name=config.service_name,
        auto_generate_request_id=config.auto_generate_request_id,
        extract_user_id=config.extract_user_id,
        trace_propagation=config.trace_propagation,
        include_w3c_trace_context=config.include_w3c_trace_context,
        include_b3_headers=config.include_b3_headers,
        include_jaeger_headers=config.include_jaeger_headers,
    )
    logger.debug(
        f"Request context middleware configured for service: {config.service_name} "
        f"(trace_propagation={config.trace_propagation}, "
        f"extract_user_id={config.extract_user_id}, "
        f"w3c={config.include_w3c_trace_context}, "
        f"b3={config.include_b3_headers}, "
        f"jaeger={config.include_jaeger_headers})"
    )


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

    # Add trusted host middleware if configured
    if config.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.trusted_hosts)

    # Add security headers middleware
    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
            response: Response = await call_next(request)

            # HSTS
            if config.hsts:
                hsts_value = f"max-age={config.hsts_max_age}"
                if config.hsts_include_subdomains:
                    hsts_value += "; includeSubDomains"
                response.headers["Strict-Transport-Security"] = hsts_value

            # Frame options
            response.headers["X-Frame-Options"] = config.frame_options

            # Content type options
            if config.content_type_options:
                response.headers["X-Content-Type-Options"] = "nosniff"

            # XSS protection
            if config.xss_protection:
                response.headers["X-XSS-Protection"] = "1; mode=block"

            # CSP
            if config.csp:
                response.headers["Content-Security-Policy"] = config.csp

            # Referrer policy
            response.headers["Referrer-Policy"] = config.referrer_policy

            return response

    app.add_middleware(SecurityHeadersMiddleware)
    logger.debug("Security headers middleware configured")


def _setup_logging_middleware(app: FastAPI, config: LoggingConfig) -> None:
    """Set up request/response logging middleware."""
    from .logging import LoggingMiddleware

    app.add_middleware(
        LoggingMiddleware,
        log_requests=True,  # Always log requests
        log_responses=True,  # Always log responses
        include_headers=config.include_headers,
        include_body=config.include_request_body,  # Map include_request_body to include_body
        max_body_size=config.max_body_size,
        exclude_paths=config.exclude_paths,
        level=config.level,  # Pass through the logging level
    )
    logger.debug(
        f"Logging middleware configured: level={config.level}, "
        f"headers={config.include_headers}, body={config.include_request_body}, "
        f"exclude_paths={config.exclude_paths}"
    )


def _setup_rate_limiting_middleware(app: FastAPI, config: RateLimitConfig) -> None:
    """Set up rate limiting middleware."""

    # Note: This is a basic implementation
    # In production, you'd want to use Redis or similar for distributed rate limiting

    # Simple in-memory rate limiter
    request_counts: dict[str, deque[float]] = defaultdict(deque)

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
        }.get(period, 60)  # Default to minute

        return num_requests, period_seconds

    class RateLimitMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
            # Get client identifier
            if config.key_func == "ip":
                key = request.client.host if request.client else "unknown"
            else:
                # For now, just use IP. In production, you'd implement user-based limiting
                key = request.client.host if request.client else "unknown"

            # Check if IP is exempt
            if key in config.exempt_ips:
                exempt_response: Response = await call_next(request)
                return exempt_response

            # Get limit for this endpoint
            limit_str = config.endpoints.get(request.url.path, config.default_limit)
            max_requests, window_seconds = parse_limit(limit_str)

            # Clean old requests
            now = time.time()
            requests = request_counts[key]
            while requests and requests[0] < now - window_seconds:
                requests.popleft()

            # Check rate limit
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

            # Record this request
            requests.append(now)

            # Process request
            response: Response = await call_next(request)

            # Add rate limit headers
            if config.headers:
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = str(max_requests - len(requests))
                response.headers["X-RateLimit-Reset"] = str(int(now + window_seconds))

            return response

    app.add_middleware(RateLimitMiddleware)
    logger.debug(f"Rate limiting middleware configured with default limit: {config.default_limit}")


def _setup_request_middleware(app: FastAPI, config: RequestConfig) -> None:
    """Set up general request processing middleware."""

    # Add gzip compression if enabled
    if config.gzip_compression:
        app.add_middleware(GZipMiddleware, minimum_size=config.gzip_minimum_size)

    class RequestProcessingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
            # Get request ID from context if available, or generate new one
            request_id = getattr(request.state, "request_id", None)
            if not request_id and config.include_request_id:
                request_id = str(uuid.uuid4())
                request.state.request_id = request_id

            start_time = time.time()

            # Process request
            response: Response = await call_next(request)

            # Add headers (only if we have a request ID and it's configured)
            if config.include_request_id and request_id:
                response.headers[config.request_id_header] = request_id

            if config.include_process_time:
                process_time = time.time() - start_time
                response.headers[config.process_time_header] = f"{process_time:.4f}"

            return response

    app.add_middleware(RequestProcessingMiddleware)
    logger.debug("Request processing middleware configured")


def _setup_metrics_middleware(app: FastAPI, config: MetricsConfig) -> None:
    """Set up Prometheus metrics middleware."""
    try:
        from fast_core.monitoring.metrics import (
            PrometheusMiddleware,
            initialize_metrics,
            setup_metrics_endpoint,
        )

        # Get or create metrics registry
        service_name = getattr(app.state, "settings", None)
        if service_name and hasattr(service_name, "service_name"):
            service_name = service_name.service_name
        else:
            service_name = app.title or "unknown-service"

        # Initialize metrics registry
        metrics_registry = initialize_metrics(service_name)

        # Add prometheus middleware
        app.add_middleware(
            PrometheusMiddleware,
            metrics_registry=metrics_registry,
            exclude_paths=set(config.exclude_paths),
            exclude_methods=set(config.exclude_methods),
        )

        # Add metrics endpoint if requested
        if config.include_endpoint:
            setup_metrics_endpoint(app, metrics_registry, config.endpoint_path)

        logger.debug(f"Metrics middleware configured with endpoint: {config.endpoint_path}")

    except ImportError as e:
        logger.warning(f"Prometheus metrics not available (missing dependency): {e}")
    except Exception as e:
        logger.error(f"Failed to setup metrics middleware: {e}", exc_info=True)

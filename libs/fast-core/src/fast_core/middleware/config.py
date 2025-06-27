"""
Middleware configuration classes for Fast Core.

This module provides configuration classes for different types of middleware
using a builder pattern for flexible and granular control.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field


@dataclass
class CORSConfig:
    """Configuration for CORS middleware."""

    enabled: bool = True
    origins: List[str] = field(default_factory=lambda: ["*"])
    methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    headers: List[str] = field(default_factory=lambda: ["*"])
    credentials: bool = False
    expose_headers: List[str] = field(default_factory=list)
    max_age: int = 600


@dataclass
class SecurityConfig:
    """Configuration for security headers middleware."""

    enabled: bool = True
    hsts: bool = True
    hsts_max_age: int = 31536000  ***REMOVED*** 1 year
    hsts_include_subdomains: bool = True
    frame_options: str = "DENY"  ***REMOVED*** DENY, SAMEORIGIN, or ALLOW-FROM
    content_type_options: bool = True
    xss_protection: bool = True
    csp: Optional[str] = None
    referrer_policy: str = "strict-origin-when-cross-origin"
    trusted_hosts: List[str] = field(default_factory=list)


@dataclass
class LoggingConfig:
    """Configuration for request/response logging middleware."""

    enabled: bool = True
    level: str = "INFO"
    include_request_body: bool = False
    include_response_body: bool = False
    max_body_size: int = 1024  ***REMOVED*** bytes
    exclude_paths: List[str] = field(default_factory=lambda: ["/health", "/metrics"])
    include_headers: bool = True
    exclude_headers: List[str] = field(default_factory=lambda: ["authorization", "cookie"])
    log_timing: bool = True
    log_user_agent: bool = True


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting middleware."""

    enabled: bool = True
    default_limit: str = "100/minute"  ***REMOVED*** Format: "requests/period"
    storage_url: Optional[str] = None  ***REMOVED*** Redis URL for distributed rate limiting
    key_func: Optional[str] = "ip"  ***REMOVED*** "ip", "user", or custom function name
    endpoints: Dict[str, str] = field(default_factory=dict)  ***REMOVED*** endpoint -> limit mapping
    exempt_ips: List[str] = field(default_factory=list)
    headers: bool = True  ***REMOVED*** Include rate limit headers in response


@dataclass
class RequestConfig:
    """Configuration for general request/response middleware."""

    enabled: bool = True
    max_request_size: int = 10 * 1024 * 1024  ***REMOVED*** 10MB
    timeout: int = 30  ***REMOVED*** seconds
    include_request_id: bool = True
    request_id_header: str = "X-Request-ID"
    include_process_time: bool = True
    process_time_header: str = "X-Process-Time"
    gzip_compression: bool = True
    gzip_minimum_size: int = 1000  ***REMOVED*** bytes


@dataclass
class MetricsConfig:
    """Configuration for Prometheus metrics middleware."""

    enabled: bool = True
    endpoint_path: str = "/metrics"
    include_endpoint: bool = True  ***REMOVED*** Whether to add the /metrics endpoint
    exclude_paths: List[str] = field(
        default_factory=lambda: ["/metrics", "/health", "/docs", "/openapi.json"]
    )
    exclude_methods: List[str] = field(default_factory=lambda: ["OPTIONS"])
    custom_buckets: Optional[List[float]] = None  ***REMOVED*** Custom histogram buckets
    track_request_size: bool = True
    track_response_size: bool = True


class MiddlewareConfig:
    """
    Builder class for configuring FastAPI middleware with granular control.

    Provides a fluent interface for configuring different types of middleware
    with specific settings for each service's needs.

    Example:
        middleware = MiddlewareConfig()
        middleware.cors(
            origins=["https://app.example.com"],
            credentials=True
        ).security_headers(
            hsts=True,
            csp="default-src 'self'"
        ).rate_limiting(
            default_limit="100/minute",
            endpoints={"/api/auth/login": "5/minute"}
        )

        app = create_app(middleware=middleware)
    """

    def __init__(self) -> None:
        self._cors: Optional[CORSConfig] = None
        self._security: Optional[SecurityConfig] = None
        self._logging: Optional[LoggingConfig] = None
        self._rate_limit: Optional[RateLimitConfig] = None
        self._request: Optional[RequestConfig] = None
        self._metrics: Optional[MetricsConfig] = None

    def cors(
        self,
        origins: Optional[List[str]] = None,
        methods: Optional[List[str]] = None,
        headers: Optional[List[str]] = None,
        credentials: bool = False,
        expose_headers: Optional[List[str]] = None,
        max_age: int = 600,
        enabled: bool = True,
    ) -> "MiddlewareConfig":
        """Configure CORS middleware.

        Args:
            origins: List of allowed origins. Defaults to ["*"]
            methods: List of allowed HTTP methods
            headers: List of allowed headers. Defaults to ["*"]
            credentials: Whether to allow credentials
            expose_headers: List of headers to expose to the client
            max_age: Cache duration for preflight requests
            enabled: Whether to enable CORS middleware

        Returns:
            Self for method chaining
        """
        self._cors = CORSConfig(
            enabled=enabled,
            origins=origins or ["*"],
            methods=methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            headers=headers or ["*"],
            credentials=credentials,
            expose_headers=expose_headers or [],
            max_age=max_age,
        )
        return self

    def security_headers(
        self,
        hsts: bool = True,
        hsts_max_age: int = 31536000,
        hsts_include_subdomains: bool = True,
        frame_options: str = "DENY",
        content_type_options: bool = True,
        xss_protection: bool = True,
        csp: Optional[str] = None,
        referrer_policy: str = "strict-origin-when-cross-origin",
        trusted_hosts: Optional[List[str]] = None,
        enabled: bool = True,
    ) -> "MiddlewareConfig":
        """Configure security headers middleware.

        Args:
            hsts: Enable HTTP Strict Transport Security
            hsts_max_age: HSTS max age in seconds
            hsts_include_subdomains: Include subdomains in HSTS
            frame_options: X-Frame-Options header value
            content_type_options: Enable X-Content-Type-Options: nosniff
            xss_protection: Enable X-XSS-Protection
            csp: Content Security Policy header value
            referrer_policy: Referrer-Policy header value
            trusted_hosts: List of trusted host patterns
            enabled: Whether to enable security headers

        Returns:
            Self for method chaining
        """
        self._security = SecurityConfig(
            enabled=enabled,
            hsts=hsts,
            hsts_max_age=hsts_max_age,
            hsts_include_subdomains=hsts_include_subdomains,
            frame_options=frame_options,
            content_type_options=content_type_options,
            xss_protection=xss_protection,
            csp=csp,
            referrer_policy=referrer_policy,
            trusted_hosts=trusted_hosts or [],
        )
        return self

    def logging(
        self,
        level: str = "INFO",
        include_request_body: bool = False,
        include_response_body: bool = False,
        max_body_size: int = 1024,
        exclude_paths: Optional[List[str]] = None,
        include_headers: bool = True,
        exclude_headers: Optional[List[str]] = None,
        log_timing: bool = True,
        log_user_agent: bool = True,
        enabled: bool = True,
    ) -> "MiddlewareConfig":
        """Configure request/response logging middleware.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            include_request_body: Whether to log request bodies
            include_response_body: Whether to log response bodies
            max_body_size: Maximum body size to log in bytes
            exclude_paths: List of paths to exclude from logging
            include_headers: Whether to log headers
            exclude_headers: List of headers to exclude from logging
            log_timing: Whether to log request timing
            log_user_agent: Whether to log user agent
            enabled: Whether to enable logging middleware

        Returns:
            Self for method chaining
        """
        self._logging = LoggingConfig(
            enabled=enabled,
            level=level,
            include_request_body=include_request_body,
            include_response_body=include_response_body,
            max_body_size=max_body_size,
            exclude_paths=exclude_paths or ["/health", "/metrics"],
            include_headers=include_headers,
            exclude_headers=exclude_headers or ["authorization", "cookie"],
            log_timing=log_timing,
            log_user_agent=log_user_agent,
        )
        return self

    def rate_limiting(
        self,
        default_limit: str = "100/minute",
        storage_url: Optional[str] = None,
        key_func: str = "ip",
        endpoints: Optional[Dict[str, str]] = None,
        exempt_ips: Optional[List[str]] = None,
        headers: bool = True,
        enabled: bool = True,
    ) -> "MiddlewareConfig":
        """Configure rate limiting middleware.

        Args:
            default_limit: Default rate limit (e.g., "100/minute", "1000/hour")
            storage_url: Redis URL for distributed rate limiting
            key_func: Key function for rate limiting ("ip", "user", or custom)
            endpoints: Per-endpoint rate limits {"/path": "limit"}
            exempt_ips: List of IP addresses exempt from rate limiting
            headers: Whether to include rate limit headers in responses
            enabled: Whether to enable rate limiting

        Returns:
            Self for method chaining
        """
        self._rate_limit = RateLimitConfig(
            enabled=enabled,
            default_limit=default_limit,
            storage_url=storage_url,
            key_func=key_func,
            endpoints=endpoints or {},
            exempt_ips=exempt_ips or [],
            headers=headers,
        )
        return self

    def request_processing(
        self,
        max_request_size: int = 10 * 1024 * 1024,
        timeout: int = 30,
        include_request_id: bool = True,
        request_id_header: str = "X-Request-ID",
        include_process_time: bool = True,
        process_time_header: str = "X-Process-Time",
        gzip_compression: bool = True,
        gzip_minimum_size: int = 1000,
        enabled: bool = True,
    ) -> "MiddlewareConfig":
        """Configure general request processing middleware.

        Args:
            max_request_size: Maximum request size in bytes
            timeout: Request timeout in seconds
            include_request_id: Whether to add request ID header
            request_id_header: Header name for request ID
            include_process_time: Whether to add process time header
            process_time_header: Header name for process time
            gzip_compression: Whether to enable gzip compression
            gzip_minimum_size: Minimum response size for compression
            enabled: Whether to enable request processing middleware

        Returns:
            Self for method chaining
        """
        self._request = RequestConfig(
            enabled=enabled,
            max_request_size=max_request_size,
            timeout=timeout,
            include_request_id=include_request_id,
            request_id_header=request_id_header,
            include_process_time=include_process_time,
            process_time_header=process_time_header,
            gzip_compression=gzip_compression,
            gzip_minimum_size=gzip_minimum_size,
        )
        return self

    def metrics(
        self,
        endpoint_path: str = "/metrics",
        include_endpoint: bool = True,
        exclude_paths: Optional[List[str]] = None,
        exclude_methods: Optional[List[str]] = None,
        custom_buckets: Optional[List[float]] = None,
        track_request_size: bool = True,
        track_response_size: bool = True,
        enabled: bool = True,
    ) -> "MiddlewareConfig":
        """Configure Prometheus metrics middleware.

        Args:
            endpoint_path: Path for the metrics endpoint
            include_endpoint: Whether to add the /metrics endpoint to the app
            exclude_paths: List of paths to exclude from metrics collection
            exclude_methods: List of HTTP methods to exclude from metrics
            custom_buckets: Custom histogram buckets for response times
            track_request_size: Whether to track request sizes
            track_response_size: Whether to track response sizes
            enabled: Whether to enable metrics collection

        Returns:
            Self for method chaining
        """
        self._metrics = MetricsConfig(
            enabled=enabled,
            endpoint_path=endpoint_path,
            include_endpoint=include_endpoint,
            exclude_paths=exclude_paths or ["/metrics", "/health", "/docs", "/openapi.json"],
            exclude_methods=exclude_methods or ["OPTIONS"],
            custom_buckets=custom_buckets,
            track_request_size=track_request_size,
            track_response_size=track_response_size,
        )
        return self

    ***REMOVED*** Property accessors for the setup module
    @property
    def cors_config(self) -> Optional[CORSConfig]:
        """Get CORS configuration."""
        return self._cors

    @property
    def security_config(self) -> Optional[SecurityConfig]:
        """Get security configuration."""
        return self._security

    @property
    def logging_config(self) -> Optional[LoggingConfig]:
        """Get logging configuration."""
        return self._logging

    @property
    def rate_limit_config(self) -> Optional[RateLimitConfig]:
        """Get rate limiting configuration."""
        return self._rate_limit

    @property
    def request_config(self) -> Optional[RequestConfig]:
        """Get request processing configuration."""
        return self._request

    @property
    def metrics_config(self) -> Optional[MetricsConfig]:
        """Get metrics configuration."""
        return self._metrics

    def has_any_middleware(self) -> bool:
        """Check if any middleware is configured."""
        return any(
            [
                self._cors,
                self._security,
                self._logging,
                self._rate_limit,
                self._request,
                self._metrics,
            ]
        )


***REMOVED*** Simple test to verify the system works
if __name__ == "__main__":
    print("🧪 Testing Fast Core Middleware Configuration System...")

    ***REMOVED*** Test basic configuration
    config = MiddlewareConfig()
    assert not config.has_any_middleware(), "Empty config should have no middleware"

    ***REMOVED*** Test method chaining
    config.cors(origins=["https://example.com"], credentials=True).security_headers(
        hsts=True, csp="default-src 'self'"
    ).rate_limiting(default_limit="100/minute", endpoints={"/api/auth/login": "5/minute"}).logging(
        level="DEBUG", include_request_body=True
    ).request_processing(
        include_request_id=True, gzip_compression=True
    )

    ***REMOVED*** Verify configuration
    assert config.has_any_middleware(), "Should have middleware configured"
    assert config.cors_config is not None, "CORS should be configured"
    assert config.cors_config.enabled, "CORS should be enabled"
    assert config.cors_config.origins == ["https://example.com"], "CORS origins should match"
    assert config.cors_config.credentials, "CORS credentials should be enabled"

    assert config.security_config is not None, "Security should be configured"
    assert config.security_config.enabled, "Security should be enabled"
    assert config.security_config.hsts, "HSTS should be enabled"
    assert config.security_config.csp == "default-src 'self'", "CSP should match"

    assert config.rate_limit_config is not None, "Rate limiting should be configured"
    assert config.rate_limit_config.enabled, "Rate limiting should be enabled"
    assert config.rate_limit_config.default_limit == "100/minute", "Default limit should match"
    assert (
        config.rate_limit_config.endpoints["/api/auth/login"] == "5/minute"
    ), "Endpoint limit should match"

    assert config.logging_config is not None, "Logging should be configured"
    assert config.logging_config.enabled, "Logging should be enabled"
    assert config.logging_config.level == "DEBUG", "Log level should match"
    assert config.logging_config.include_request_body, "Request body logging should be enabled"

    assert config.request_config is not None, "Request processing should be configured"
    assert config.request_config.enabled, "Request processing should be enabled"
    assert config.request_config.include_request_id, "Request ID should be enabled"
    assert config.request_config.gzip_compression, "Gzip compression should be enabled"

    print("✅ All tests passed!")
    print(f"   CORS enabled: {config.cors_config.enabled}")
    print(f"   CORS origins: {config.cors_config.origins}")
    print(f"   Security enabled: {config.security_config.enabled}")
    print(f"   Rate limiting enabled: {config.rate_limit_config.enabled}")
    print(f"   Logging enabled: {config.logging_config.enabled}")
    print(f"   Request processing enabled: {config.request_config.enabled}")
    print(f"   Has any middleware: {config.has_any_middleware()}")
    print("\n🎉 Fast Core Middleware Builder is working correctly!")

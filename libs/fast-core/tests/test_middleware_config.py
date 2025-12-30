"""
Tests for the Fast Core Middleware Configuration System
"""

from fast_core.middleware import (
    CORSConfig,
    LoggingConfig,
    MiddlewareConfig,
    RateLimitConfig,
    RequestConfig,
    SecurityConfig,
)


class TestMiddlewareConfig:
    """Test the MiddlewareConfig builder class."""

    def test_empty_config(self) -> None:
        """Test creating an empty middleware configuration."""
        config = MiddlewareConfig()
        assert not config.has_any_middleware()
        assert config.cors_config is None
        assert config.security_config is None
        assert config.logging_config is None
        assert config.rate_limit_config is None
        assert config.request_config is None

    def test_cors_configuration(self) -> None:
        """Test CORS middleware configuration."""
        config = MiddlewareConfig()
        config.cors(
            origins=["https://example.com"],
            credentials=True,
            methods=["GET", "POST"],
            headers=["Content-Type"],
            max_age=3600,
        )

        assert config.has_any_middleware()
        assert config.cors_config is not None
        assert config.cors_config.enabled is True
        assert config.cors_config.origins == ["https://example.com"]
        assert config.cors_config.credentials is True
        assert config.cors_config.methods == ["GET", "POST"]
        assert config.cors_config.headers == ["Content-Type"]
        assert config.cors_config.max_age == 3600

    def test_security_headers_configuration(self) -> None:
        """Test security headers middleware configuration."""
        config = MiddlewareConfig()
        config.security_headers(
            hsts=True,
            hsts_max_age=31536000,
            frame_options="SAMEORIGIN",
            csp="default-src 'self'",
            trusted_hosts=["example.com"],
        )

        assert config.has_any_middleware()
        assert config.security_config is not None
        assert config.security_config.enabled is True
        assert config.security_config.hsts is True
        assert config.security_config.hsts_max_age == 31536000
        assert config.security_config.frame_options == "SAMEORIGIN"
        assert config.security_config.csp == "default-src 'self'"
        assert config.security_config.trusted_hosts == ["example.com"]

    def test_logging_configuration(self) -> None:
        """Test logging middleware configuration."""
        config = MiddlewareConfig()
        config.logging(
            level="DEBUG",
            include_request_body=True,
            max_body_size=2048,
            exclude_paths=["/health"],
            exclude_headers=["authorization"],
        )

        assert config.has_any_middleware()
        assert config.logging_config is not None
        assert config.logging_config.enabled is True
        assert config.logging_config.level == "DEBUG"
        assert config.logging_config.include_request_body is True
        assert config.logging_config.max_body_size == 2048
        assert config.logging_config.exclude_paths == ["/health"]
        assert config.logging_config.exclude_headers == ["authorization"]

    def test_rate_limiting_configuration(self) -> None:
        """Test rate limiting middleware configuration."""
        config = MiddlewareConfig()
        config.rate_limiting(
            default_limit="100/minute",
            endpoints={"/api/login": "5/minute"},
            exempt_ips=["127.0.0.1"],
            storage_url="redis://localhost:6379",
        )

        assert config.has_any_middleware()
        assert config.rate_limit_config is not None
        assert config.rate_limit_config.enabled is True
        assert config.rate_limit_config.default_limit == "100/minute"
        assert config.rate_limit_config.endpoints == {"/api/login": "5/minute"}
        assert config.rate_limit_config.exempt_ips == ["127.0.0.1"]
        assert config.rate_limit_config.storage_url == "redis://localhost:6379"

    def test_request_processing_configuration(self) -> None:
        """Test request processing middleware configuration."""
        config = MiddlewareConfig()
        config.request_processing(
            max_request_size=5 * 1024 * 1024,
            timeout=30,
            include_request_id=True,
            request_id_header="X-Custom-Request-ID",
            gzip_compression=True,
        )

        assert config.has_any_middleware()
        assert config.request_config is not None
        assert config.request_config.enabled is True
        assert config.request_config.max_request_size == 5 * 1024 * 1024
        assert config.request_config.timeout == 30
        assert config.request_config.include_request_id is True
        assert config.request_config.request_id_header == "X-Custom-Request-ID"
        assert config.request_config.gzip_compression is True

    def test_method_chaining(self) -> None:
        """Test that middleware configuration methods can be chained."""
        config = MiddlewareConfig()
        result = (
            config.cors(origins=["https://example.com"])
            .security_headers(hsts=True)
            .rate_limiting(default_limit="100/minute")
            .logging(level="INFO")
            .request_processing(include_request_id=True)
        )

        # Method chaining should return the same instance
        assert result is config

        # All middleware should be configured
        assert config.has_any_middleware()
        assert config.cors_config is not None
        assert config.security_config is not None
        assert config.rate_limit_config is not None
        assert config.logging_config is not None
        assert config.request_config is not None

    def test_disabled_middleware(self) -> None:
        """Test that middleware can be explicitly disabled."""
        config = MiddlewareConfig()
        config.cors(enabled=False)
        config.security_headers(enabled=False)

        # Should have config objects but they should be disabled
        assert config.cors_config is not None
        assert config.cors_config.enabled is False
        assert config.security_config is not None
        assert config.security_config.enabled is False

        # has_any_middleware should still return True because configs exist
        assert config.has_any_middleware()


class TestConfigurationClasses:
    """Test individual configuration classes."""

    def test_cors_config_defaults(self) -> None:
        """Test CORSConfig default values."""
        config = CORSConfig()
        assert config.enabled is True
        assert config.origins == ["*"]
        assert config.methods == ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        assert config.headers == ["*"]
        assert config.credentials is False
        assert config.expose_headers == []
        assert config.max_age == 600

    def test_security_config_defaults(self) -> None:
        """Test SecurityConfig default values."""
        config = SecurityConfig()
        assert config.enabled is True
        assert config.hsts is True
        assert config.hsts_max_age == 31536000
        assert config.hsts_include_subdomains is True
        assert config.frame_options == "DENY"
        assert config.content_type_options is True
        assert config.xss_protection is True
        assert config.csp is None
        assert config.referrer_policy == "strict-origin-when-cross-origin"
        assert config.trusted_hosts == []

    def test_logging_config_defaults(self) -> None:
        """Test LoggingConfig default values."""
        config = LoggingConfig()
        assert config.enabled is True
        assert config.level == "INFO"
        assert config.include_request_body is False
        assert config.include_response_body is False
        assert config.max_body_size == 1024
        assert config.exclude_paths == ["/health", "/metrics"]
        assert config.include_headers is True
        assert config.exclude_headers == ["authorization", "cookie"]
        assert config.log_timing is True
        assert config.log_user_agent is True

    def test_rate_limit_config_defaults(self) -> None:
        """Test RateLimitConfig default values."""
        config = RateLimitConfig()
        assert config.enabled is True
        assert config.default_limit == "100/minute"
        assert config.storage_url is None
        assert config.key_func == "ip"
        assert config.endpoints == {}
        assert config.exempt_ips == []
        assert config.headers is True

    def test_request_config_defaults(self) -> None:
        """Test RequestConfig default values."""
        config = RequestConfig()
        assert config.enabled is True
        assert config.max_request_size == 10 * 1024 * 1024
        assert config.timeout == 30
        assert config.include_request_id is True
        assert config.request_id_header == "X-Request-ID"
        assert config.include_process_time is True
        assert config.process_time_header == "X-Process-Time"
        assert config.gzip_compression is True
        assert config.gzip_minimum_size == 1000

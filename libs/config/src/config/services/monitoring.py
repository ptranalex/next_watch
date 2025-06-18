"""Monitoring configuration mixin for observability.

Provides configuration for logging, metrics, tracing, and other observability
features across NextWatch services.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field, validator


class MonitoringConfigMixin:
    """Monitoring and observability configuration mixin.

    This mixin provides monitoring configuration that can be composed
    into service configurations. It includes logging, metrics, tracing,
    and health check settings.

    Environment variables (with service prefix):
    - {SERVICE}_ENABLE_METRICS: Enable Prometheus metrics
    - {SERVICE}_METRICS_PORT: Port for metrics endpoint
    - {SERVICE}_LOG_FORMAT: Log format (json, text)
    - {SERVICE}_LOG_STRUCTURED: Enable structured logging
    - {SERVICE}_ENABLE_TRACING: Enable distributed tracing
    - {SERVICE}_HEALTH_CHECK_INTERVAL: Health check interval
    """

    ***REMOVED*** Metrics configuration
    enable_metrics: bool = Field(
        default=True, description="Enable Prometheus metrics collection"
    )
    metrics_port: Optional[int] = Field(
        default=None,
        description="Port for metrics endpoint (if different from main port)",
    )
    metrics_path: str = Field(
        default="/metrics", description="URL path for metrics endpoint"
    )
    enable_performance_metrics: bool = Field(
        default=False,
        description="Enable detailed performance metrics (may impact performance)",
    )

    ***REMOVED*** Logging configuration
    log_format: str = Field(
        default="json", description="Log format: json, text, or structured"
    )
    log_structured: bool = Field(
        default=True, description="Enable structured logging with fields"
    )
    log_request_details: bool = Field(
        default=True, description="Log HTTP request details"
    )
    log_response_time: bool = Field(default=True, description="Log HTTP response times")
    log_sql_queries: bool = Field(
        default=False, description="Log SQL queries (debug only)"
    )
    log_suppress_noise: bool = Field(
        default=True, description="Suppress noisy log entries (health checks, etc.)"
    )

    ***REMOVED*** Tracing configuration
    enable_tracing: bool = Field(
        default=False, description="Enable distributed tracing"
    )
    tracing_endpoint: Optional[str] = Field(
        default=None, description="Tracing collector endpoint (Jaeger, etc.)"
    )
    tracing_sample_rate: float = Field(
        default=0.1, description="Tracing sample rate (0.0 to 1.0)"
    )

    ***REMOVED*** Health check configuration
    health_check_interval: int = Field(
        default=30, description="Health check interval in seconds"
    )
    health_check_timeout: int = Field(
        default=5, description="Health check timeout in seconds"
    )
    enable_deep_health_checks: bool = Field(
        default=False, description="Enable deep health checks (database, cache, etc.)"
    )

    ***REMOVED*** Error tracking
    enable_error_tracking: bool = Field(
        default=True, description="Enable error tracking and alerting"
    )
    error_tracking_dsn: Optional[str] = Field(
        default=None, description="Error tracking service DSN (Sentry, etc.)"
    )

    @validator("log_format")
    def validate_log_format(cls, v: str) -> str:
        """Validate log format is supported."""
        allowed_formats = ["json", "text", "structured"]
        if v not in allowed_formats:
            raise ValueError(
                f"Unsupported log format: {v}. "
                f"Allowed formats: {', '.join(allowed_formats)}"
            )
        return v

    @validator("metrics_port")
    def validate_metrics_port(cls, v: Optional[int]) -> Optional[int]:
        """Validate metrics port if specified."""
        if v is not None:
            if not (1 <= v <= 65535):
                raise ValueError("Metrics port must be between 1 and 65535")
        return v

    @validator("metrics_path")
    def validate_metrics_path(cls, v: str) -> str:
        """Validate metrics path format."""
        if not v.startswith("/"):
            raise ValueError("Metrics path must start with '/'")
        if " " in v:
            raise ValueError("Metrics path cannot contain spaces")
        return v

    @validator("tracing_sample_rate")
    def validate_tracing_sample_rate(cls, v: float) -> float:
        """Validate tracing sample rate is between 0 and 1."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Tracing sample rate must be between 0.0 and 1.0")
        return v

    @validator("health_check_interval")
    def validate_health_check_interval(cls, v: int) -> int:
        """Validate health check interval."""
        if v < 1:
            raise ValueError("Health check interval must be at least 1 second")
        if v > 3600:  ***REMOVED*** 1 hour
            raise ValueError("Health check interval should not exceed 1 hour")
        return v

    @validator("health_check_timeout")
    def validate_health_check_timeout(cls, v: int) -> int:
        """Validate health check timeout."""
        if v < 1:
            raise ValueError("Health check timeout must be at least 1 second")
        if v > 60:
            raise ValueError("Health check timeout should not exceed 60 seconds")
        return v

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary.

        Returns:
            Dictionary with logging configuration
        """
        return {
            "format": self.log_format,
            "structured": self.log_structured,
            "request_details": self.log_request_details,
            "response_time": self.log_response_time,
            "sql_queries": self.log_sql_queries,
            "suppress_noise": self.log_suppress_noise,
        }

    def get_metrics_config(self) -> Dict[str, Any]:
        """Get metrics configuration dictionary.

        Returns:
            Dictionary with metrics configuration
        """
        config = {
            "enabled": self.enable_metrics,
            "path": self.metrics_path,
            "performance_metrics": self.enable_performance_metrics,
        }

        if self.metrics_port:
            config["port"] = self.metrics_port

        return config

    def get_tracing_config(self) -> Dict[str, Any]:
        """Get tracing configuration dictionary.

        Returns:
            Dictionary with tracing configuration
        """
        config: Dict[str, Any] = {
            "enabled": self.enable_tracing,
            "sample_rate": self.tracing_sample_rate,
        }

        if self.tracing_endpoint:
            config["endpoint"] = self.tracing_endpoint

        return config

    def get_health_check_config(self) -> Dict[str, Any]:
        """Get health check configuration dictionary.

        Returns:
            Dictionary with health check configuration
        """
        return {
            "interval": self.health_check_interval,
            "timeout": self.health_check_timeout,
            "deep_checks": self.enable_deep_health_checks,
        }

    def get_error_tracking_config(self) -> Dict[str, Any]:
        """Get error tracking configuration dictionary.

        Returns:
            Dictionary with error tracking configuration
        """
        config: Dict[str, Any] = {
            "enabled": self.enable_error_tracking,
        }

        if self.error_tracking_dsn:
            config["dsn"] = self.error_tracking_dsn

        return config

    def should_log_sql(self, environment: str) -> bool:
        """Determine if SQL queries should be logged based on environment.

        Args:
            environment: Current environment

        Returns:
            True if SQL queries should be logged
        """
        ***REMOVED*** Only log SQL in development or if explicitly enabled
        return (environment == "development") or self.log_sql_queries

    def get_metrics_labels(self, service_name: str) -> Dict[str, str]:
        """Get default metrics labels for the service.

        Args:
            service_name: Name of the service

        Returns:
            Dictionary with default metrics labels
        """
        return {
            "service": service_name,
            "version": "1.0.0",  ***REMOVED*** Could be injected from service config
        }

    def validate_monitoring_production_settings(self, environment: str) -> List[str]:
        """Validate monitoring configuration for production deployment.

        Args:
            environment: Current environment

        Returns:
            List of validation issues, empty if valid
        """
        issues = []

        if environment == "production":
            ***REMOVED*** Metrics should be enabled in production
            if not self.enable_metrics:
                issues.append("Metrics should be enabled in production")

            ***REMOVED*** Performance metrics may impact performance
            if self.enable_performance_metrics:
                issues.append(
                    "Consider disabling detailed performance metrics in production"
                )

            ***REMOVED*** SQL query logging should be disabled
            if self.log_sql_queries:
                issues.append("SQL query logging should be disabled in production")

            ***REMOVED*** Structured logging recommended for production
            if not self.log_structured:
                issues.append("Structured logging recommended for production")

            ***REMOVED*** Error tracking should be configured
            if self.enable_error_tracking and not self.error_tracking_dsn:
                issues.append("Error tracking DSN should be configured in production")

            ***REMOVED*** Tracing sample rate should be reasonable for production
            if self.enable_tracing and self.tracing_sample_rate > 0.1:
                issues.append("Tracing sample rate should be <= 0.1 in production")

        return issues

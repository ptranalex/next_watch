"""Auth-specific metrics and monitoring.

This module provides custom metrics for the Auth API service,
including authentication operations, JWT token management, user management, and security monitoring.
"""

from typing import Dict, Optional, Any, Callable, TypeVar
from fast_core.monitoring.metrics import MetricsRegistry, get_metrics_registry, track_operation
from config.logging import get_logger

***REMOVED*** Type variable for function decorators
F = TypeVar("F", bound=Callable[..., Any])

logger = get_logger(__name__)


class AuthMetrics:
    """Auth-specific metrics collection."""

    def __init__(self, metrics_registry: Optional[MetricsRegistry] = None):
        """Initialize Auth metrics.

        Args:
            metrics_registry: Metrics registry (uses global if None)
        """
        self.registry = metrics_registry or get_metrics_registry()
        if not self.registry:
            logger.warning("No metrics registry available, metrics will be disabled")
            return

        self._setup_custom_metrics()
        logger.info("Auth metrics initialized")

    def _setup_custom_metrics(self) -> None:
        """Set up Auth-specific custom metrics."""
        if not self.registry:
            return

        ***REMOVED*** Authentication operation metrics
        self.auth_requests = self.registry.create_counter(
            "auth_requests_total",
            "Total authentication requests by type and status",
            ["auth_type", "status", "service"],
        )

        self.auth_duration = self.registry.create_histogram(
            "auth_duration_seconds",
            "Duration of authentication operations",
            ["auth_type", "status", "service"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
        )

        self.auth_failures = self.registry.create_counter(
            "auth_failures_total",
            "Authentication failures by reason",
            ["failure_reason", "auth_type", "service"],
        )

        ***REMOVED*** JWT token metrics
        self.jwt_operations = self.registry.create_counter(
            "auth_jwt_operations_total",
            "JWT token operations",
            ["operation", "token_type", "status", "service"],
        )

        self.jwt_duration = self.registry.create_histogram(
            "auth_jwt_duration_seconds",
            "Duration of JWT operations",
            ["operation", "token_type", "service"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
        )

        self.jwt_validation_results = self.registry.create_counter(
            "auth_jwt_validation_results_total",
            "JWT token validation results",
            ["result", "failure_reason", "service"],
        )

        self.active_tokens = self.registry.create_gauge(
            "auth_active_tokens_total",
            "Number of active tokens by type",
            ["token_type", "service"],
        )

        ***REMOVED*** User management metrics
        self.user_operations = self.registry.create_counter(
            "auth_user_operations_total",
            "User management operations",
            ["operation", "status", "service"],
        )

        self.user_registration_attempts = self.registry.create_counter(
            "auth_user_registration_attempts_total",
            "User registration attempts by status",
            ["status", "failure_reason", "service"],
        )

        self.active_users = self.registry.create_gauge(
            "auth_active_users_total",
            "Number of active users in the system",
            ["service"],
        )

        self.user_login_patterns = self.registry.create_counter(
            "auth_user_login_patterns_total",
            "User login patterns and frequency",
            ["pattern_type", "time_period", "service"],
        )

        ***REMOVED*** Security monitoring metrics
        self.security_events = self.registry.create_counter(
            "auth_security_events_total",
            "Security-related events",
            ["event_type", "severity", "service"],
        )

        self.brute_force_attempts = self.registry.create_counter(
            "auth_brute_force_attempts_total",
            "Potential brute force attack attempts",
            ["source_type", "blocked", "service"],
        )

        self.suspicious_activities = self.registry.create_counter(
            "auth_suspicious_activities_total",
            "Suspicious authentication activities",
            ["activity_type", "risk_level", "service"],
        )

        self.rate_limit_hits = self.registry.create_counter(
            "auth_rate_limit_hits_total",
            "Rate limit violations",
            ["endpoint", "limit_type", "service"],
        )

        ***REMOVED*** Database operation metrics
        self.database_operations = self.registry.create_counter(
            "auth_database_operations_total",
            "Database operations by type and status",
            ["operation", "table", "status", "service"],
        )

        self.database_duration = self.registry.create_histogram(
            "auth_database_duration_seconds",
            "Duration of database operations",
            ["operation", "table", "service"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

        self.database_connection_pool = self.registry.create_gauge(
            "auth_database_connections_active",
            "Active database connections",
            ["service"],
        )

        ***REMOVED*** Session management metrics
        self.session_operations = self.registry.create_counter(
            "auth_session_operations_total",
            "Session management operations",
            ["operation", "status", "service"],
        )

        self.session_duration = self.registry.create_histogram(
            "auth_session_duration_seconds",
            "User session duration",
            ["session_type", "service"],
            buckets=(60, 300, 900, 1800, 3600, 7200, 14400, 28800, 86400),  ***REMOVED*** 1m to 1d
        )

        self.concurrent_sessions = self.registry.create_gauge(
            "auth_concurrent_sessions_total",
            "Number of concurrent user sessions",
            ["service"],
        )

        ***REMOVED*** Password security metrics
        self.password_operations = self.registry.create_counter(
            "auth_password_operations_total",
            "Password-related operations",
            ["operation", "status", "service"],
        )

        self.password_strength_scores = self.registry.create_histogram(
            "auth_password_strength_scores",
            "Password strength scores for new registrations",
            ["strength_category", "service"],
            buckets=(0, 1, 2, 3, 4, 5),  ***REMOVED*** Weak to strong
        )

        ***REMOVED*** API integration metrics
        self.api_client_requests = self.registry.create_counter(
            "auth_api_client_requests_total",
            "Requests from different API clients",
            ["client_type", "endpoint", "status", "service"],
        )

        self.token_refresh_patterns = self.registry.create_counter(
            "auth_token_refresh_patterns_total",
            "Token refresh patterns",
            ["refresh_type", "time_until_expiry", "service"],
        )

        ***REMOVED*** Performance metrics
        self.response_size = self.registry.create_histogram(
            "auth_response_size_bytes",
            "Response size for auth operations",
            ["operation", "service"],
            buckets=(50, 100, 250, 500, 1000, 2500, 5000),
        )

        self.auth_cache_performance = self.registry.create_counter(
            "auth_cache_performance_total",
            "Authentication cache performance",
            ["cache_type", "result", "service"],
        )

    def record_auth_request(self, auth_type: str, status: str, duration: float) -> None:
        """Record an authentication request.

        Args:
            auth_type: Type of authentication (login, register, verify, refresh)
            status: Request status (success, failure, timeout)
            duration: Request duration in seconds
        """
        if not self.registry:
            return

        ***REMOVED*** Record auth request
        request_labels = {
            "auth_type": auth_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.auth_requests.labels(**request_labels).inc()

        ***REMOVED*** Record auth duration
        duration_labels = {
            "auth_type": auth_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.auth_duration.labels(**duration_labels).observe(duration)

    def record_auth_failure(self, failure_reason: str, auth_type: str) -> None:
        """Record an authentication failure.

        Args:
            failure_reason: Reason for failure (invalid_credentials, user_not_found, etc.)
            auth_type: Type of authentication that failed
        """
        if not self.registry:
            return

        labels = {
            "failure_reason": failure_reason,
            "auth_type": auth_type,
            "service": self.registry.service_name,
        }
        self.auth_failures.labels(**labels).inc()

    def record_jwt_operation(
        self, operation: str, token_type: str, status: str, duration: float
    ) -> None:
        """Record a JWT operation.

        Args:
            operation: JWT operation (create, verify, decode, refresh)
            token_type: Type of token (access, refresh)
            status: Operation status (success, failure, expired)
            duration: Operation duration in seconds
        """
        if not self.registry:
            return

        ***REMOVED*** Record JWT operation
        operation_labels = {
            "operation": operation,
            "token_type": token_type,
            "status": status,
            "service": self.registry.service_name,
        }
        self.jwt_operations.labels(**operation_labels).inc()

        ***REMOVED*** Record JWT duration
        duration_labels = {
            "operation": operation,
            "token_type": token_type,
            "service": self.registry.service_name,
        }
        self.jwt_duration.labels(**duration_labels).observe(duration)

    def record_jwt_validation(self, result: str, failure_reason: str = "none") -> None:
        """Record JWT token validation result.

        Args:
            result: Validation result (valid, invalid, expired)
            failure_reason: Reason for failure if invalid
        """
        if not self.registry:
            return

        labels = {
            "result": result,
            "failure_reason": failure_reason,
            "service": self.registry.service_name,
        }
        self.jwt_validation_results.labels(**labels).inc()

    def record_user_operation(self, operation: str, status: str) -> None:
        """Record a user management operation.

        Args:
            operation: User operation (create, read, update, delete, authenticate)
            status: Operation status (success, failure, conflict)
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.user_operations.labels(**labels).inc()

    def record_user_registration(self, status: str, failure_reason: str = "none") -> None:
        """Record a user registration attempt.

        Args:
            status: Registration status (success, failure)
            failure_reason: Reason for failure if applicable
        """
        if not self.registry:
            return

        labels = {
            "status": status,
            "failure_reason": failure_reason,
            "service": self.registry.service_name,
        }
        self.user_registration_attempts.labels(**labels).inc()

    def record_security_event(self, event_type: str, severity: str) -> None:
        """Record a security event.

        Args:
            event_type: Type of security event (login_failure, token_misuse, etc.)
            severity: Event severity (low, medium, high, critical)
        """
        if not self.registry:
            return

        labels = {
            "event_type": event_type,
            "severity": severity,
            "service": self.registry.service_name,
        }
        self.security_events.labels(**labels).inc()

    def record_brute_force_attempt(self, source_type: str, blocked: bool) -> None:
        """Record a potential brute force attempt.

        Args:
            source_type: Source of the attempt (ip, user, session)
            blocked: Whether the attempt was blocked
        """
        if not self.registry:
            return

        labels = {
            "source_type": source_type,
            "blocked": "yes" if blocked else "no",
            "service": self.registry.service_name,
        }
        self.brute_force_attempts.labels(**labels).inc()

    def record_suspicious_activity(self, activity_type: str, risk_level: str) -> None:
        """Record suspicious authentication activity.

        Args:
            activity_type: Type of suspicious activity
            risk_level: Risk level (low, medium, high)
        """
        if not self.registry:
            return

        labels = {
            "activity_type": activity_type,
            "risk_level": risk_level,
            "service": self.registry.service_name,
        }
        self.suspicious_activities.labels(**labels).inc()

    def record_rate_limit_hit(self, endpoint: str, limit_type: str) -> None:
        """Record a rate limit violation.

        Args:
            endpoint: API endpoint that hit the limit
            limit_type: Type of rate limit (per_ip, per_user, global)
        """
        if not self.registry:
            return

        labels = {
            "endpoint": endpoint,
            "limit_type": limit_type,
            "service": self.registry.service_name,
        }
        self.rate_limit_hits.labels(**labels).inc()

    def record_database_operation(
        self, operation: str, table: str, status: str, duration: float
    ) -> None:
        """Record a database operation.

        Args:
            operation: Database operation (select, insert, update, delete)
            table: Database table name
            status: Operation status (success, failure, timeout)
            duration: Operation duration in seconds
        """
        if not self.registry:
            return

        ***REMOVED*** Record database operation
        operation_labels = {
            "operation": operation,
            "table": table,
            "status": status,
            "service": self.registry.service_name,
        }
        self.database_operations.labels(**operation_labels).inc()

        ***REMOVED*** Record database duration
        duration_labels = {
            "operation": operation,
            "table": table,
            "service": self.registry.service_name,
        }
        self.database_duration.labels(**duration_labels).observe(duration)

    def record_session_operation(self, operation: str, status: str) -> None:
        """Record a session management operation.

        Args:
            operation: Session operation (create, validate, destroy)
            status: Operation status (success, failure)
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.session_operations.labels(**labels).inc()

    def record_password_operation(self, operation: str, status: str) -> None:
        """Record a password-related operation.

        Args:
            operation: Password operation (hash, verify, change, reset)
            status: Operation status (success, failure)
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "status": status,
            "service": self.registry.service_name,
        }
        self.password_operations.labels(**labels).inc()

    def record_password_strength(self, strength_category: str) -> None:
        """Record password strength for new registrations.

        Args:
            strength_category: Password strength category (weak, fair, good, strong)
        """
        if not self.registry:
            return

        labels = {
            "strength_category": strength_category,
            "service": self.registry.service_name,
        }
        self.password_strength_scores.labels(**labels).observe(1)

    def record_api_client_request(self, client_type: str, endpoint: str, status: str) -> None:
        """Record a request from an API client.

        Args:
            client_type: Type of API client (bff, web, mobile, admin)
            endpoint: API endpoint accessed
            status: Request status (success, failure)
        """
        if not self.registry:
            return

        labels = {
            "client_type": client_type,
            "endpoint": endpoint,
            "status": status,
            "service": self.registry.service_name,
        }
        self.api_client_requests.labels(**labels).inc()

    def record_token_refresh_pattern(self, refresh_type: str, time_until_expiry: str) -> None:
        """Record token refresh patterns.

        Args:
            refresh_type: Type of refresh (automatic, manual, expired)
            time_until_expiry: Time remaining until expiry (soon, medium, early)
        """
        if not self.registry:
            return

        labels = {
            "refresh_type": refresh_type,
            "time_until_expiry": time_until_expiry,
            "service": self.registry.service_name,
        }
        self.token_refresh_patterns.labels(**labels).inc()

    def record_response_size(self, operation: str, size_bytes: int) -> None:
        """Record response size for auth operations.

        Args:
            operation: Auth operation type
            size_bytes: Response size in bytes
        """
        if not self.registry:
            return

        labels = {
            "operation": operation,
            "service": self.registry.service_name,
        }
        self.response_size.labels(**labels).observe(size_bytes)

    def record_cache_performance(self, cache_type: str, result: str) -> None:
        """Record authentication cache performance.

        Args:
            cache_type: Type of cache (user, token, session)
            result: Cache result (hit, miss, error)
        """
        if not self.registry:
            return

        labels = {
            "cache_type": cache_type,
            "result": result,
            "service": self.registry.service_name,
        }
        self.auth_cache_performance.labels(**labels).inc()

    def update_active_tokens(self, token_type: str, count: int) -> None:
        """Update active token count.

        Args:
            token_type: Type of token (access, refresh)
            count: Number of active tokens
        """
        if not self.registry:
            return

        labels = {
            "token_type": token_type,
            "service": self.registry.service_name,
        }
        self.active_tokens.labels(**labels).set(count)

    def update_active_users(self, count: int) -> None:
        """Update active user count.

        Args:
            count: Number of active users
        """
        if not self.registry:
            return

        labels = {"service": self.registry.service_name}
        self.active_users.labels(**labels).set(count)

    def update_concurrent_sessions(self, count: int) -> None:
        """Update concurrent session count.

        Args:
            count: Number of concurrent sessions
        """
        if not self.registry:
            return

        labels = {"service": self.registry.service_name}
        self.concurrent_sessions.labels(**labels).set(count)

    def update_database_connection_pool(self, active_connections: int) -> None:
        """Update database connection pool metric.

        Args:
            active_connections: Number of active database connections
        """
        if not self.registry:
            return

        labels = {"service": self.registry.service_name}
        self.database_connection_pool.labels(**labels).set(active_connections)


***REMOVED*** Global Auth metrics instance
_auth_metrics: Optional[AuthMetrics] = None


def get_auth_metrics() -> Optional[AuthMetrics]:
    """Get the global Auth metrics instance."""
    return _auth_metrics


def initialize_auth_metrics() -> Optional[AuthMetrics]:
    """Initialize global Auth metrics instance.

    Returns:
        AuthMetrics instance if successful, None if metrics registry unavailable
    """
    global _auth_metrics
    _auth_metrics = AuthMetrics()
    ***REMOVED*** Return None if the metrics instance couldn't initialize properly
    if _auth_metrics and not _auth_metrics.registry:
        _auth_metrics = None
    return _auth_metrics


***REMOVED*** Decorator for tracking Auth operations
def track_auth_operation(
    operation_name: str, labels: Optional[Dict[str, str]] = None
) -> Callable[[F], F]:
    """Decorator to track Auth-specific operations.

    Args:
        operation_name: Name of the operation
        labels: Additional labels for the operation

    Returns:
        Decorator function
    """
    registry = get_metrics_registry()
    if not registry:

        def noop_decorator(func: F) -> F:
            return func

        return noop_decorator

    return track_operation(registry, f"auth_{operation_name}", labels)


***REMOVED*** Example usage decorators for common Auth operations
def track_authentication(func: F) -> F:
    """Track authentication operations."""
    return track_auth_operation("authentication")(func)


def track_user_registration(func: F) -> F:
    """Track user registration operations."""
    return track_auth_operation("user_registration")(func)


def track_token_operation(func: F) -> F:
    """Track JWT token operations."""
    return track_auth_operation("token_operation")(func)


def track_user_management(func: F) -> F:
    """Track user management operations."""
    return track_auth_operation("user_management")(func)


def track_security_operation(func: F) -> F:
    """Track security-related operations."""
    return track_auth_operation("security_operation")(func)

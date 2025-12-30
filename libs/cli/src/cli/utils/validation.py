"""Input validation utilities for CLI applications.

Provides common validation functions for CLI arguments and options,
based on patterns from production NextWatch services.
"""

import re
from urllib.parse import urlparse


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def validate_url(url: str, allowed_schemes: list[str] | None = None) -> str:
    """Validate URL format and scheme.

    Args:
        url: URL to validate
        allowed_schemes: List of allowed schemes (default: http, https)

    Returns:
        Validated URL string

    Raises:
        ValidationError: If URL is invalid

    Example:
        >>> validate_url("https://api.example.com:8080/v1")
        'https://api.example.com:8080/v1'
        >>> validate_url("ftp://example.com")  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValidationError: Invalid URL scheme...
    """
    if not url:
        raise ValidationError("URL cannot be empty")

    if allowed_schemes is None:
        allowed_schemes = ["http", "https"]

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}")

    if not parsed.scheme:
        raise ValidationError("URL must include a scheme (http:// or https://)")

    if parsed.scheme not in allowed_schemes:
        raise ValidationError(
            f"Invalid URL scheme '{parsed.scheme}'. Allowed: {', '.join(allowed_schemes)}"
        )

    if not parsed.netloc:
        raise ValidationError("URL must include a hostname")

    return url


def validate_port(port: int | str, allow_zero: bool = False) -> int:
    """Validate port number.

    Args:
        port: Port number to validate
        allow_zero: Whether to allow port 0

    Returns:
        Validated port number

    Raises:
        ValidationError: If port is invalid

    Example:
        >>> validate_port(8080)
        8080
        >>> validate_port("443")
        443
        >>> validate_port(70000)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValidationError: Port must be between...
    """
    try:
        port_int = int(port)
    except (ValueError, TypeError):
        raise ValidationError(f"Port must be a number, got: {port}")

    min_port = 0 if allow_zero else 1
    max_port = 65535

    if port_int < min_port or port_int > max_port:
        raise ValidationError(f"Port must be between {min_port} and {max_port}, got: {port_int}")

    return port_int


def validate_timeout(
    timeout: int | float | str, min_value: float = 0.1, max_value: float = 300.0
) -> float:
    """Validate timeout value.

    Args:
        timeout: Timeout value to validate
        min_value: Minimum allowed timeout
        max_value: Maximum allowed timeout

    Returns:
        Validated timeout value

    Raises:
        ValidationError: If timeout is invalid

    Example:
        >>> validate_timeout(30.5)
        30.5
        >>> validate_timeout("10")
        10.0
        >>> validate_timeout(-1)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValidationError: Timeout must be between...
    """
    try:
        timeout_float = float(timeout)
    except (ValueError, TypeError):
        raise ValidationError(f"Timeout must be a number, got: {timeout}")

    if timeout_float < min_value or timeout_float > max_value:
        raise ValidationError(
            f"Timeout must be between {min_value} and {max_value} seconds, got: {timeout_float}"
        )

    return timeout_float


def validate_pattern(pattern: str, pattern_type: str = "glob") -> str:
    """Validate pattern format.

    Args:
        pattern: Pattern string to validate
        pattern_type: Type of pattern (glob, regex)

    Returns:
        Validated pattern string

    Raises:
        ValidationError: If pattern is invalid

    Example:
        >>> validate_pattern("movie:*")
        'movie:*'
        >>> validate_pattern("user:[0-9]+", "regex")
        'user:[0-9]+'
    """
    if not pattern:
        raise ValidationError("Pattern cannot be empty")

    if pattern_type == "regex":
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern: {e}")
    elif pattern_type == "glob":
        # Basic glob validation - ensure no path traversal
        if ".." in pattern or "/" in pattern or "\\" in pattern:
            raise ValidationError("Glob pattern cannot contain path separators or '..'")
    else:
        raise ValidationError(f"Unknown pattern type: {pattern_type}")

    return pattern


def validate_log_level(level: str) -> str:
    """Validate log level.

    Args:
        level: Log level to validate

    Returns:
        Validated log level string (uppercase)

    Raises:
        ValidationError: If log level is invalid

    Example:
        >>> validate_log_level("info")
        'INFO'
        >>> validate_log_level("invalid")  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValidationError: Invalid log level...
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    level_upper = level.upper()

    if level_upper not in valid_levels:
        raise ValidationError(
            f"Invalid log level '{level}'. Valid levels: {', '.join(valid_levels)}"
        )

    return level_upper


def validate_file_size(size: int | str, max_size: int = 100 * 1024 * 1024) -> int:
    """Validate file size.

    Args:
        size: File size to validate (bytes)
        max_size: Maximum allowed size in bytes

    Returns:
        Validated file size

    Raises:
        ValidationError: If file size is invalid

    Example:
        >>> validate_file_size(1024)
        1024
        >>> validate_file_size("2048")
        2048
    """
    try:
        size_int = int(size)
    except (ValueError, TypeError):
        raise ValidationError(f"File size must be a number, got: {size}")

    if size_int < 0:
        raise ValidationError("File size cannot be negative")

    if size_int > max_size:
        raise ValidationError(f"File size too large: {size_int} bytes (max: {max_size} bytes)")

    return size_int

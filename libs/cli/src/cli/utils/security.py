"""Security utilities for CLI applications.

Provides utilities for masking sensitive information in CLI output,
based on patterns from production NextWatch services.
"""

from typing import Any
from urllib.parse import urlparse

***REMOVED*** Patterns for detecting sensitive field names
SENSITIVE_FIELD_PATTERNS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "key",
    "token",
    "auth",
    "credential",
    "private",
    "api_key",
    "jwt",
    "session",
    "cookie",
}


def mask_sensitive_value(value: str | None, show_length: int = 4, mask_char: str = "*") -> str:
    """Mask sensitive configuration values.

    Args:
        value: Value to mask
        show_length: Number of characters to show at the end
        mask_char: Character to use for masking

    Returns:
        Masked value string

    Example:
        >>> mask_sensitive_value("super_secret_password_123")
        '****_123'
        >>> mask_sensitive_value(None)
        '[red]Not Set[/red]'
        >>> mask_sensitive_value("")
        '[red]Empty[/red]'
    """
    if not value:
        return "[red]Not Set[/red]" if value is None else "[red]Empty[/red]"

    if len(value) <= show_length:
        return mask_char * len(value)

    masked_part = mask_char * 4
    visible_part = value[-show_length:]
    return f"{masked_part}{visible_part}"


def mask_url(url: str, mask_password: bool = True, mask_username: bool = False) -> str:
    """Mask sensitive parts of URLs.

    Args:
        url: URL to mask
        mask_password: Whether to mask the password
        mask_username: Whether to mask the username

    Returns:
        URL with sensitive parts masked

    Example:
        >>> mask_url("redis://user:pass@localhost:6379/0")
        'redis://user:****@localhost:6379/0'
        >>> mask_url("https://api:secret@example.com/v1", mask_username=True)
        'https://****:****@example.com/v1'
    """
    if not url:
        return url

    try:
        parsed = urlparse(url)
    except Exception:
        ***REMOVED*** If URL parsing fails, just return the original
        return url

    ***REMOVED*** No auth info to mask
    if not parsed.username and not parsed.password:
        return url

    ***REMOVED*** Build the masked auth part
    auth_parts = []

    if parsed.username:
        if mask_username:
            auth_parts.append("****")
        else:
            auth_parts.append(parsed.username)

    if parsed.password:
        if mask_password:
            auth_parts.append("****")
        else:
            auth_parts.append(parsed.password)

    ***REMOVED*** Reconstruct the URL
    auth_string = ":".join(auth_parts) if auth_parts else ""

    ***REMOVED*** Build the netloc
    if auth_string:
        netloc = f"{auth_string}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
    else:
        netloc = parsed.netloc

    ***REMOVED*** Reconstruct the full URL
    result = f"{parsed.scheme}://{netloc}"
    if parsed.path:
        result += parsed.path
    if parsed.params:
        result += f";{parsed.params}"
    if parsed.query:
        result += f"?{parsed.query}"
    if parsed.fragment:
        result += f"***REMOVED***{parsed.fragment}"

    return result


def is_sensitive_field(field_name: str, additional_patterns: set[str] | None = None) -> bool:
    """Check if a field name indicates sensitive data.

    Args:
        field_name: Field name to check
        additional_patterns: Additional patterns to check

    Returns:
        True if field is likely sensitive

    Example:
        >>> is_sensitive_field("jwt_secret")
        True
        >>> is_sensitive_field("database_password")
        True
        >>> is_sensitive_field("username")
        False
        >>> is_sensitive_field("custom_key", {"custom"})
        True
    """
    field_lower = field_name.lower()

    ***REMOVED*** Check against default patterns
    patterns = SENSITIVE_FIELD_PATTERNS
    if additional_patterns:
        patterns = patterns.union(additional_patterns)

    ***REMOVED*** Check if any pattern is in the field name
    for pattern in patterns:
        if pattern in field_lower:
            return True

    return False


def mask_dict_values(
    data: dict[str, Any],
    sensitive_fields: list[str] | None = None,
    mask_all_sensitive: bool = True,
    additional_patterns: set[str] | None = None,
) -> dict[str, Any]:
    """Mask sensitive values in a dictionary.

    Args:
        data: Dictionary to mask
        sensitive_fields: Specific fields to mask
        mask_all_sensitive: Whether to auto-detect and mask sensitive fields
        additional_patterns: Additional patterns for sensitive field detection

    Returns:
        Dictionary with sensitive values masked

    Example:
        >>> data = {"username": "user", "password": "secret", "port": 8080}
        >>> mask_dict_values(data)
        {'username': 'user', 'password': '****', 'port': 8080}
    """
    result = data.copy()

    for key, value in result.items():
        should_mask = False

        ***REMOVED*** Check if explicitly specified as sensitive
        if sensitive_fields and key in sensitive_fields:
            should_mask = True

        ***REMOVED*** Check if auto-detection is enabled and field appears sensitive
        elif mask_all_sensitive and is_sensitive_field(key, additional_patterns):
            should_mask = True

        if should_mask and isinstance(value, str):
            result[key] = mask_sensitive_value(value)

    return result


def sanitize_log_data(data: dict[str, Any], mask_urls: bool = True) -> dict[str, Any]:
    """Sanitize data for logging by masking sensitive information.

    Args:
        data: Data to sanitize
        mask_urls: Whether to mask URLs

    Returns:
        Sanitized data safe for logging

    Example:
        >>> log_data = {
        ...     "api_key": "secret123",
        ...     "redis_url": "redis://user:pass@localhost:6379/0",
        ...     "message": "Operation completed"
        ... }
        >>> sanitize_log_data(log_data)
        {'api_key': '****123', 'redis_url': 'redis://user:****@localhost:6379/0', 'message': 'Operation completed'}
    """
    result = mask_dict_values(data)

    if mask_urls:
        for key, value in result.items():
            if isinstance(value, str) and ("://" in value or key.lower().endswith("_url")):
                result[key] = mask_url(value)

    return result


def mask_command_args(args: list[str], sensitive_flags: set[str] | None = None) -> list[str]:
    """Mask sensitive command line arguments.

    Args:
        args: Command line arguments
        sensitive_flags: Set of flag names that are sensitive

    Returns:
        Command line arguments with sensitive values masked

    Example:
        >>> args = ["--api-key", "secret123", "--host", "localhost"]
        >>> mask_command_args(args, {"--api-key"})
        ['--api-key', '****', '--host', 'localhost']
    """
    if not sensitive_flags:
        sensitive_flags = {
            "--password",
            "--passwd",
            "--secret",
            "--key",
            "--token",
            "--api-key",
            "--jwt",
            "--credential",
            "--auth",
        }

    result = []
    mask_next = False

    for arg in args:
        if mask_next:
            result.append("****")
            mask_next = False
        elif arg in sensitive_flags:
            result.append(arg)
            mask_next = True
        elif "=" in arg:
            ***REMOVED*** Handle --key=value format
            flag, value = arg.split("=", 1)
            if flag in sensitive_flags:
                result.append(f"{flag}=****")
            else:
                result.append(arg)
        else:
            result.append(arg)

    return result

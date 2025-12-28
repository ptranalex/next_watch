"""Secret masking utilities for configuration display.

Provides smart masking of sensitive configuration values including passwords,
tokens, API keys, and URLs with credentials, following security best practices.
"""

import re
from typing import Any
from urllib.parse import urlparse, urlunparse


def mask_sensitive_value(
    value: Any,
    field_name: str = "",
    secret_fields: list[str] | None = None,
    show_secrets: bool = False,
) -> str:
    """Mask sensitive configuration values for safe display.

    Args:
        value: The configuration value to potentially mask
        field_name: Name of the configuration field
        secret_fields: List of field names considered sensitive
        show_secrets: Whether to show unmasked values (development only)

    Returns:
        Masked or original string representation of the value

    Example:
        >>> mask_sensitive_value("super_secret_key", "jwt_secret", ["jwt_secret"])
        "***MASKED***"
        >>> mask_sensitive_value("super_secret_key", "jwt_secret", ["jwt_secret"], show_secrets=True)
        "super_secret_key"
    """
    if show_secrets:
        return str(value)

    ***REMOVED*** Default list of sensitive field patterns
    default_secret_patterns = [
        "secret",
        "password",
        "token",
        "key",
        "credential",
        "auth",
        "jwt",
        "api_key",
        "private",
        "cert",
        "ssl",
    ]

    ***REMOVED*** Combine provided secret fields with defaults
    all_secret_fields = (secret_fields or []) + default_secret_patterns

    ***REMOVED*** Check if field name matches any sensitive patterns
    field_lower = field_name.lower()
    is_sensitive = any(pattern in field_lower for pattern in all_secret_fields)

    if not is_sensitive:
        ***REMOVED*** Check for URL with credentials
        if isinstance(value, str) and _has_url_credentials(value):
            return mask_url_credentials(value)
        return str(value)

    ***REMOVED*** Mask sensitive values
    if value is None:
        return "None"
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, int | float):
        return str(value)
    elif isinstance(value, str):
        if len(value) == 0:
            return '""'
        elif len(value) <= 4:
            return "***"
        else:
            ***REMOVED*** Show first and last character with masking in between
            return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"
    else:
        return "***MASKED***"


def mask_url_credentials(url: str) -> str:
    """Mask credentials in database URLs and connection strings.

    Args:
        url: URL that may contain credentials

    Returns:
        URL with credentials masked

    Example:
        >>> mask_url_credentials("postgresql://user:password@localhost:5432/db")
        "postgresql://user:***@localhost:5432/db"
        >>> mask_url_credentials("redis://user:secret123@cache:6379/0")
        "redis://user:***@cache:6379/0"
    """
    if not isinstance(url, str) or not url:
        return str(url)

    try:
        parsed = urlparse(url)

        ***REMOVED*** If no credentials, return as-is
        if not parsed.username and not parsed.password:
            return url

        ***REMOVED*** Create new netloc with masked password
        if parsed.username and parsed.password:
            masked_netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                masked_netloc += f":{parsed.port}"
        elif parsed.username:
            masked_netloc = f"{parsed.username}@{parsed.hostname}"
            if parsed.port:
                masked_netloc += f":{parsed.port}"
        else:
            ***REMOVED*** Just password (unusual but handle it)
            masked_netloc = f":***@{parsed.hostname}"
            if parsed.port:
                masked_netloc += f":{parsed.port}"

        ***REMOVED*** Reconstruct URL with masked credentials
        masked_url = urlunparse(
            (
                parsed.scheme,
                masked_netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

        return masked_url

    except Exception:
        ***REMOVED*** If URL parsing fails, apply basic masking
        return _basic_url_mask(url)


def _has_url_credentials(value: str) -> bool:
    """Check if a string appears to be a URL with credentials.

    Args:
        value: String to check

    Returns:
        True if appears to be URL with credentials
    """
    ***REMOVED*** Ensure we have a string
    if not isinstance(value, str):
        return False  ***REMOVED*** type: ignore[unreachable]

    ***REMOVED*** Look for common patterns: scheme://user:pass@host
    url_with_creds_pattern = r"^[a-zA-Z][a-zA-Z0-9+.-]*://[^:/@]+:[^@/]+@"
    match = re.match(url_with_creds_pattern, value)
    return match is not None


def _basic_url_mask(url: str) -> str:
    """Apply basic regex-based masking to URLs.

    Args:
        url: URL string to mask

    Returns:
        URL with basic credential masking
    """
    ***REMOVED*** Pattern to match user:password@ in URLs
    pattern = r"://([^:/@]+):([^@/]+)@"

    def replace_creds(match: re.Match[str]) -> str:
        username = match.group(1)
        ***REMOVED*** password = match.group(2)  ***REMOVED*** Not used, will be masked
        return f"://{username}:***@"

    return re.sub(pattern, replace_creds, url)


***REMOVED*** Common secret field patterns for different services
AUTH_SECRET_FIELDS = [
    "jwt_secret",
    "jwt_algorithm",
    "password_hash_rounds",
    "session_secret",
    "auth_secret",
    "private_key",
]

DATABASE_SECRET_FIELDS = [
    "database_url",
    "database_password",
    "db_password",
    "postgres_password",
    "mysql_password",
    "redis_password",
]

API_SECRET_FIELDS = [
    "api_key",
    "api_secret",
    "client_secret",
    "access_token",
    "refresh_token",
    "bearer_token",
    "service_key",
]

***REMOVED*** Combined list of common secret fields
COMMON_SECRET_FIELDS = AUTH_SECRET_FIELDS + DATABASE_SECRET_FIELDS + API_SECRET_FIELDS

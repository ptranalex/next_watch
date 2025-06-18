"""Secret masking utilities for secure configuration display."""

import re
from typing import Any, Dict, List, Union, Optional


***REMOVED*** Common patterns for sensitive field names
SENSITIVE_FIELD_PATTERNS = [
    "secret",
    "password",
    "token",
    "key",
    "credential",
    "database_url",
    "redis_url",
    "jwt_secret",
    "api_key",
    "auth",
    "private",
]


def mask_sensitive_value(
    value: Any,
    field_name: str = "",
    mask_char: str = "*",
    show_length: int = 3,
    sensitive_patterns: Optional[List[str]] = None,
) -> str:
    """Mask sensitive values for display.

    Args:
        value: The value to potentially mask
        field_name: Name of the field (used for pattern matching)
        mask_char: Character to use for masking
        show_length: Number of characters to show at start/end
        sensitive_patterns: Additional patterns to check for

    Returns:
        Masked string representation of the value
    """
    if value is None:
        return "None"

    value_str = str(value)
    field_lower = field_name.lower()

    ***REMOVED*** Combine default patterns with any additional ones
    patterns = SENSITIVE_FIELD_PATTERNS + (sensitive_patterns or [])

    ***REMOVED*** Check if field name contains sensitive patterns
    is_sensitive = any(pattern in field_lower for pattern in patterns)

    if not is_sensitive:
        return value_str

    ***REMOVED*** Handle very short values
    if len(value_str) <= show_length * 2:
        return mask_char * len(value_str)

    ***REMOVED*** Show first and last few characters
    if len(value_str) > show_length * 2:
        masked_middle_length = len(value_str) - (show_length * 2)
        return (
            value_str[:show_length]
            + mask_char * min(masked_middle_length, 10)
            + value_str[-show_length:]
        )

    return mask_char * len(value_str)


def mask_url_credentials(url: str, mask_char: str = "*") -> str:
    """Mask credentials in URLs.

    Args:
        url: URL that may contain credentials
        mask_char: Character to use for masking

    Returns:
        URL with credentials masked

    Example:
        >>> mask_url_credentials("postgresql://user:pass@localhost/db")
        'postgresql://user:***@localhost/db'
    """
    ***REMOVED*** Pattern to match URLs with credentials
    pattern = r"([a-zA-Z][a-zA-Z0-9+.-]*://)([^:/@]+):([^@]+)@"

    def mask_password(match: re.Match[str]) -> str:
        protocol = match.group(1)
        username = match.group(2)
        password = match.group(3)
        ***REMOVED*** Mask the password but keep username
        masked_password = mask_char * min(len(password), 8)
        return f"{protocol}{username}:{masked_password}@"

    return re.sub(pattern, mask_password, url)


def mask_config_for_display(
    config: Any, sensitive_patterns: Optional[List[str]] = None, mask_char: str = "*"
) -> Dict[str, Any]:
    """Mask sensitive configuration values for display.

    Args:
        config: Configuration object or dictionary
        sensitive_patterns: Additional sensitive field patterns
        mask_char: Character to use for masking

    Returns:
        Dictionary with sensitive values masked
    """
    ***REMOVED*** Convert config to dictionary if it's not already
    if hasattr(config, "dict"):
        ***REMOVED*** Pydantic model
        config_dict = config.dict()
    elif hasattr(config, "__dict__"):
        ***REMOVED*** Regular object
        config_dict = config.__dict__
    elif isinstance(config, dict):
        ***REMOVED*** Already a dictionary
        config_dict = config
    else:
        ***REMOVED*** Try to extract attributes
        config_dict = {
            attr: getattr(config, attr)
            for attr in dir(config)
            if not attr.startswith("_") and not callable(getattr(config, attr, None))
        }

    masked_dict: Dict[str, Any] = {}

    for key, value in config_dict.items():
        ***REMOVED*** Skip private attributes
        if key.startswith("_"):
            continue

        ***REMOVED*** Handle nested dictionaries recursively
        if isinstance(value, dict):
            masked_dict[key] = mask_config_for_display(
                value, sensitive_patterns, mask_char
            )
        ***REMOVED*** Handle URLs specially
        elif "url" in key.lower() and isinstance(value, str):
            masked_dict[key] = mask_url_credentials(value, mask_char)
        ***REMOVED*** Handle other sensitive values
        else:
            masked_dict[key] = mask_sensitive_value(
                value, key, mask_char, sensitive_patterns=sensitive_patterns
            )

    return masked_dict


def is_sensitive_field(
    field_name: str, additional_patterns: Optional[List[str]] = None
) -> bool:
    """Check if a field name indicates sensitive data.

    Args:
        field_name: Name of the field to check
        additional_patterns: Additional patterns to check for

    Returns:
        True if field appears to contain sensitive data
    """
    patterns = SENSITIVE_FIELD_PATTERNS + (additional_patterns or [])
    field_lower = field_name.lower()
    return any(pattern in field_lower for pattern in patterns)

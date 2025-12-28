"""Type-safe environment variable parsing utilities.

Provides functions to parse environment variables with proper type conversion
and validation, following patterns established in the existing codebase.
"""

import os
from typing import overload


@overload
def get_env_var(key: str, default: str, required: bool = False) -> str: ...


@overload
def get_env_var(key: str, default: None = None, required: bool = False) -> str | None: ...


def get_env_var(key: str, default: str | None = None, required: bool = False) -> str | None:
    """Get an environment variable with optional validation.

    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If required variable is not found

    Example:
        >>> get_env_var("DATABASE_URL", required=True)
        'postgresql://localhost/mydb'
        >>> get_env_var("OPTIONAL_VAR", default="fallback")
        'fallback'
    """
    value = os.getenv(key, default)

    if required and not value:
        raise ValueError(
            f"Required environment variable '{key}' is not set. "
            f"Please set it in your environment or .env file."
        )

    return value


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get a boolean environment variable.

    Treats the following values as True (case-insensitive):
    - "true", "1", "yes", "on", "enabled"

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Boolean value

    Example:
        >>> os.environ["DEBUG"] = "true"
        >>> get_env_bool("DEBUG")
        True
        >>> get_env_bool("MISSING_VAR", default=False)
        False
    """
    value = os.getenv(key, "").lower()
    if not value:
        return default

    return value in ("true", "1", "yes", "on", "enabled")


@overload
def get_env_int(key: str, default: int) -> int: ...


@overload
def get_env_int(key: str, default: None = None) -> int | None: ...


def get_env_int(key: str, default: int | None = None) -> int | None:
    """Get an integer environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found or invalid

    Returns:
        Integer value or default

    Example:
        >>> os.environ["MAX_CONNECTIONS"] = "20"
        >>> get_env_int("MAX_CONNECTIONS")
        20
        >>> get_env_int("MISSING_VAR", default=10)
        10
    """
    value = os.getenv(key)
    if not value:
        return default

    try:
        return int(value)
    except ValueError:
        if default is not None:
            return default
        raise ValueError(f"Environment variable '{key}' has invalid integer value: '{value}'")


def get_env_float(key: str, default: float | None = None) -> float | None:
    """Get a float environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found or invalid

    Returns:
        Float value or default

    Example:
        >>> os.environ["THRESHOLD"] = "0.5"
        >>> get_env_float("THRESHOLD")
        0.5
    """
    value = os.getenv(key)
    if not value:
        return default

    try:
        return float(value)
    except ValueError:
        if default is not None:
            return default
        raise ValueError(f"Environment variable '{key}' has invalid float value: '{value}'")


def get_env_list(key: str, default: list[str] | None = None, separator: str = ",") -> list[str]:
    """Get a list environment variable by splitting on separator.

    Args:
        key: Environment variable name
        default: Default value if not found
        separator: Character to split on

    Returns:
        List of string values

    Example:
        >>> os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1,example.com"
        >>> get_env_list("ALLOWED_HOSTS")
        ['localhost', '127.0.0.1', 'example.com']
    """
    value = os.getenv(key)
    if not value:
        return default or []

    ***REMOVED*** Split and strip whitespace from each item
    return [item.strip() for item in value.split(separator) if item.strip()]

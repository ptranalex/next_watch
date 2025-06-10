"""Environment variable loading and configuration.

This module centralizes the logic for loading environment variables from .env files
using python-dotenv. It follows a hierarchical loading pattern where local overrides
take precedence over default values.
"""

import os
from pathlib import Path
from typing import Optional, overload


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """Find the project root directory by looking for common project markers.

    Args:
        start_path: Starting path for search (defaults to this file's location)

    Returns:
        Path to the project root directory

    Raises:
        FileNotFoundError: If project root cannot be determined
    """
    if start_path is None:
        start_path = Path(__file__).parent

    current = start_path.resolve()

    ***REMOVED*** Look for common project root markers
    markers = [".env", "pyproject.toml", "setup.py", ".git"]

    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent

    ***REMOVED*** Fallback: assume project root is 4 levels up from this file
    ***REMOVED*** (src/bff_api/config/env.py -> project_root)
    fallback_root = Path(__file__).parent.parent.parent.parent
    if fallback_root.exists():
        return fallback_root

    raise FileNotFoundError("Could not determine project root directory")


def load_environment_variables(project_root: Optional[Path] = None) -> bool:
    """Load environment variables from .env files in hierarchical order.

    Loading order (later files override earlier ones):
    1. .env (default values)
    2. .env.local (local overrides, typically git-ignored)

    Args:
        project_root: Project root directory (auto-detected if None)

    Returns:
        True if dotenv is available and files were processed, False otherwise

    Example:
        >>> load_environment_variables()
        True
        >>> os.getenv("BACKEND_API_URL")  ***REMOVED*** Now available if set in .env files
        'http://localhost:8000'
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("python-dotenv not installed. Using system environment variables only.")
        return False

    if project_root is None:
        try:
            project_root = find_project_root()
        except FileNotFoundError:
            print("Warning: Could not find project root. Skipping .env file loading.")
            return False

    ***REMOVED*** Define .env file paths in loading order
    env_files = [
        project_root / ".env",  ***REMOVED*** Default values
        project_root / ".env.local",  ***REMOVED*** Local overrides (git-ignored)
    ]

    files_loaded = []

    ***REMOVED*** Load .env files in order
    for env_file in env_files:
        if env_file.exists():
            ***REMOVED*** For .env.local, override existing values
            override = env_file.name == ".env.local"
            load_dotenv(dotenv_path=env_file, override=override)
            files_loaded.append(env_file.name)

    if files_loaded:
        print(f"Loaded environment variables from: {', '.join(files_loaded)}")
    else:
        print("No .env files found. Using system environment variables only.")

    return True


@overload
def get_env_var(key: str, default: str, required: bool = False) -> str: ...


@overload
def get_env_var(key: str, default: None = None, required: bool = False) -> Optional[str]: ...


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
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
        >>> get_env_var("BACKEND_API_URL", required=True)
        'http://localhost:8000'
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
def get_env_int(key: str, default: None = None) -> Optional[int]: ...


def get_env_int(key: str, default: Optional[int] = None) -> Optional[int]:
    """Get an integer environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found or invalid

    Returns:
        Integer value or default

    Example:
        >>> os.environ["PORT"] = "8001"
        >>> get_env_int("PORT")
        8001
        >>> get_env_int("MISSING_VAR", default=8000)
        8000
    """
    value = os.getenv(key)
    if not value:
        return default

    try:
        return int(value)
    except ValueError:
        print(f"Warning: Invalid integer value for {key}: '{value}'. Using default: {default}")
        return default


***REMOVED*** Auto-load environment variables when module is imported
***REMOVED*** This ensures .env files are loaded early in the application lifecycle
_env_loaded = load_environment_variables()

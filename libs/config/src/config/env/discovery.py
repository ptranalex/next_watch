"""Project root discovery utilities.

Provides utilities to automatically discover the project root directory
by looking for common project markers.
"""

from pathlib import Path


def find_project_root(start_path: Path | None = None) -> Path:
    """Find the project root directory by looking for common project markers.

    Args:
        start_path: Starting path for search (defaults to this file's location)

    Returns:
        Path to the project root directory

    Raises:
        FileNotFoundError: If project root cannot be determined

    Example:
        >>> root = find_project_root()
        >>> print(root)
        /path/to/nextwatch
    """
    if start_path is None:
        start_path = Path(__file__).parent

    current = start_path.resolve()

    ***REMOVED*** Look for common project root markers
    markers = [
        ".env",
        "pyproject.toml",
        "setup.py",
        ".git",
        "README.md",
        "package.json",  ***REMOVED*** For monorepos with JS components
        "Cargo.toml",  ***REMOVED*** For Rust components
    ]

    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent

    ***REMOVED*** If we reach the root without finding markers, try a common fallback
    ***REMOVED*** for NextWatch monorepo structure
    fallback_patterns = [
        "nextwatch",
        "next_watch",
        "libs",
        "apps",
    ]

    current = start_path.resolve()
    while current != current.parent:
        if any(pattern in current.name.lower() for pattern in fallback_patterns):
            ***REMOVED*** Look for typical monorepo structure
            if any((current / subdir).exists() for subdir in ["libs", "apps", "packages"]):
                return current
        current = current.parent

    raise FileNotFoundError(
        f"Could not determine project root directory starting from {start_path}. "
        f"Please ensure you have one of these markers in your project root: {markers}"
    )

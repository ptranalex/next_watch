"""
Utility functions and constants for the suggestion engine.
"""

from typing import Any

***REMOVED*** TMDB image base URLs for different sizes
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

***REMOVED*** Default entity types to search
DEFAULT_ENTITY_TYPES = ["movie", "actor", "director"]


def format_suggestions(raw_suggestions: list[str]) -> list[dict[str, Any]]:
    """
    Format raw suggestion strings into structured suggestion objects.

    This is useful if you want to add metadata to each suggestion.
    If your Redis already stores formatted suggestions, you can skip this.

    Args:
        raw_suggestions: List of raw suggestion strings from Redis

    Returns:
        List of structured suggestion objects
    """
    return [{"text": suggestion, "score": 1.0} for suggestion in raw_suggestions]


def normalize_query(query: str) -> str:
    """
    Normalize a search query for consistent processing.

    Args:
        query: Raw search query

    Returns:
        Normalized query string
    """
    return query.lower().strip()


def build_image_url(image_path: str | None) -> str | None:
    """
    Build a complete image URL from a relative path.

    Args:
        image_path: Relative image path or None

    Returns:
        Complete image URL or None
    """
    if not image_path:
        return None

    if str(image_path).startswith("http"):
        return str(image_path)

    return f"{TMDB_IMAGE_BASE_URL}{image_path}"

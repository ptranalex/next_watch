"""Database operations for the Recommendation API service.

NOTE: Movie-related database operations have been moved to API-based approach.
All movie operations are now handled via MovieDataAdapter and Backend API.

This module is kept for potential future vector database operations
and compatibility purposes.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Movie operations are now handled via MovieDataAdapter and Backend API
# See services/movie_adapter.py for the new API-based approach


def get_movie_by_id(session: Any, movie_id: int, *_: Any, **__: Any) -> dict[str, Any] | None:
    """Backward-compatible stub for legacy debug tooling."""
    raise NotImplementedError(
        "Database operations are not available; use MovieDataAdapter / Backend API."
    )


def get_movies_by_ids(
    session: Any, movie_ids: list[int], *_: Any, **__: Any
) -> list[dict[str, Any]]:
    """Backward-compatible stub for legacy debug tooling."""
    raise NotImplementedError(
        "Database operations are not available; use MovieDataAdapter / Backend API."
    )

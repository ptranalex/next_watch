"""Database connection utilities for the Recommendation API service.

NOTE: Movie-related database connections have been moved to API-based approach.
All movie operations are now handled via MovieDataAdapter and Backend API.

This module is kept for potential future vector database connections
and compatibility purposes.
"""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)

# Movie database connections are now handled via MovieDataAdapter and Backend API
# See services/movie_adapter.py for the new API-based approach


@contextmanager
def get_db_context() -> Iterator[Any]:
    """Backward-compatible DB context manager.

    The Recommendation API migrated to an API-based architecture and no longer
    maintains a direct movie database connection. This exists for legacy debug tooling.
    """
    raise NotImplementedError(
        "Database operations are not available; use MovieDataAdapter / Backend API."
    )
    yield  # pragma: no cover

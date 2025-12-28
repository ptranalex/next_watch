"""
Query implementations for genre-related operations.
"""

from typing import Any

from config.logging import get_logger
from sqlalchemy.sql import text

from backend_api.queries.common import DBSession

logger = get_logger(__name__)


def get_genre_by_name(db_session: DBSession, genre_name: str) -> dict[str, Any] | None:
    """
    Get a genre by its name (case-insensitive match).

    Args:
        db_session: SQLAlchemy database session
        genre_name: Genre name to look up

    Returns:
        Genre details dictionary or None if not found
    """
    query = """
    SELECT g.*
    FROM genre g
    WHERE LOWER(g.name) = LOWER(:genre_name)
    """

    result = db_session.execute(text(query), {"genre_name": genre_name})
    genre = result.first()

    if not genre:
        return None

    ***REMOVED*** Convert to dictionary
    return dict(genre._mapping)

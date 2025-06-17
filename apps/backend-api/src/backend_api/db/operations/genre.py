"""Genre storage operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from backend_api.config.logging import get_logger
from backend_api.models import Genre

logger = get_logger(__name__)


def create_genre(session: Session, name: str, tmdb_id: Optional[int] = None) -> Genre:
    """Create a genre record.

    Args:
        session: Database session
        name: Genre name
        tmdb_id: TMDB genre ID (optional)

    Returns:
        Created Genre instance
    """
    genre = Genre(name=name, tmdb_id=tmdb_id)
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


def get_genre_by_id(session: Session, genre_id: int) -> Optional[Genre]:
    """Get a genre by its ID.

    Args:
        session: Database session
        genre_id: Genre ID

    Returns:
        Genre instance or None if not found
    """
    return session.get(Genre, genre_id)


def get_genre_by_tmdb_id(session: Session, tmdb_id: int) -> Optional[Genre]:
    """Get a genre by its TMDB ID.

    Args:
        session: Database session
        tmdb_id: TMDB genre ID

    Returns:
        Genre instance or None if not found
    """
    statement = select(Genre).where(Genre.tmdb_id == tmdb_id)
    result = session.exec(statement).first()
    return result


def get_genre_by_name(session: Session, name: str) -> Optional[Genre]:
    """Get a genre by its name.

    Args:
        session: Database session
        name: Genre name

    Returns:
        Genre instance or None if not found
    """
    statement = select(Genre).where(Genre.name == name)
    result = session.exec(statement).first()
    return result


def get_genres(session: Session, skip: int = 0, limit: int = 100) -> List[Genre]:
    """Get all genres with pagination.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Genre instances
    """
    statement = select(Genre).offset(skip).limit(limit)
    genres = session.exec(statement).all()
    return list(genres)


def update_genre(session: Session, genre_id: int, name: str) -> Optional[Genre]:
    """Update a genre record.

    Args:
        session: Database session
        genre_id: ID of the genre to update
        name: New genre name

    Returns:
        Updated Genre instance or None if not found
    """
    genre = get_genre_by_id(session, genre_id)

    if not genre:
        return None

    genre.name = name
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


def delete_genre(session: Session, genre_id: int) -> bool:
    """Delete a genre record.

    Args:
        session: Database session
        genre_id: ID of the genre to delete

    Returns:
        True if deleted, False if not found
    """
    genre = get_genre_by_id(session, genre_id)

    if not genre:
        return False

    session.delete(genre)
    session.commit()
    return True

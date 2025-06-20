"""Trailer storage operations."""

import logging
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from movie_storage.config.logging import with_logging
from movie_storage.models.trailer import Trailer

logger = logging.getLogger(__name__)


@with_logging(log_level="INFO")
def create_trailer(session: Session, trailer_data: Dict[str, Any]) -> Trailer:
    """Create a trailer record.

    Args:
        session: Database session
        trailer_data: Trailer data dictionary

    Returns:
        Created Trailer instance
    """
    trailer = Trailer(**trailer_data)
    session.add(trailer)
    session.commit()
    session.refresh(trailer)
    logger.debug(f"Created trailer: {trailer.name} for movie ID {trailer.movie_id}")
    return trailer


def get_trailers_for_movie(session: Session, movie_id: int) -> List[Trailer]:
    """Get all trailers for a movie.

    Args:
        session: Database session
        movie_id: Movie ID

    Returns:
        List of Trailer instances
    """
    statement = select(Trailer).where(Trailer.movie_id == movie_id)
    return list(session.exec(statement).all())


@with_logging(log_level="INFO")
def delete_trailers_for_movie(session: Session, movie_id: int) -> int:
    """Delete all trailers for a movie.

    Args:
        session: Database session
        movie_id: Movie ID

    Returns:
        Number of trailers deleted
    """
    trailers = get_trailers_for_movie(session, movie_id)
    for trailer in trailers:
        session.delete(trailer)
    session.commit()
    logger.debug(f"Deleted {len(trailers)} trailers for movie ID {movie_id}")
    return len(trailers)

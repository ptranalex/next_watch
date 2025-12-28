"""Trailer queries."""

from sqlmodel import Session, select

from backend_api.models import Trailer


def get_trailers_for_movie(session: Session, movie_id: int) -> list[Trailer]:
    """Get all trailers for a movie.

    Args:
        session: Database session
        movie_id: Movie ID

    Returns:
        List of trailers
    """
    statement = select(Trailer).where(Trailer.movie_id == movie_id)
    return list(session.exec(statement).all())

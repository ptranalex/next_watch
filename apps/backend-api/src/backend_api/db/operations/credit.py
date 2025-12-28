"""Credit storage operations."""

from typing import Any

from config.logging import get_logger
from sqlmodel import Session, select

from backend_api.models import Credit

logger = get_logger(__name__)


def create_credit(session: Session, credit_data: dict[str, Any]) -> Credit:
    """Create a credit record for a cast or crew member.

    Args:
        session: Database session
        credit_data: Credit data dictionary

    Returns:
        Created Credit instance
    """
    credit = Credit(**credit_data)
    session.add(credit)
    session.commit()
    session.refresh(credit)
    return credit


def get_credit_by_id(session: Session, credit_id: int) -> Credit | None:
    """Get a credit by its ID.

    Args:
        session: Database session
        credit_id: Credit ID

    Returns:
        Credit instance or None if not found
    """
    return session.get(Credit, credit_id)


def get_credits_by_movie_id(session: Session, movie_id: int) -> list[Credit]:
    """Get all credits for a specific movie.

    Args:
        session: Database session
        movie_id: Movie ID

    Returns:
        List of Credit instances
    """
    statement = select(Credit).where(Credit.movie_id == movie_id)
    credits = session.exec(statement).all()
    return list(credits)


def get_credits_by_person_id(session: Session, tmdb_person_id: int) -> list[Credit]:
    """Get all credits for a specific person.

    Args:
        session: Database session
        tmdb_person_id: TMDB person ID

    Returns:
        List of Credit instances
    """
    statement = select(Credit).where(Credit.tmdb_person_id == tmdb_person_id)
    credits = session.exec(statement).all()
    return list(credits)


def get_credits(
    session: Session, skip: int = 0, limit: int = 100, department: str | None = None
) -> list[Credit]:
    """Get all credits with optional filtering.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        department: Optional department to filter by (e.g., "Acting", "Directing")

    Returns:
        List of Credit instances
    """
    query = select(Credit)

    if department:
        query = query.where(Credit.department == department)

    query = query.offset(skip).limit(limit)
    credits = session.exec(query).all()
    return list(credits)


def update_credit(session: Session, credit_id: int, credit_data: dict[str, Any]) -> Credit | None:
    """Update a credit record.

    Args:
        session: Database session
        credit_id: ID of the credit to update
        credit_data: Updated credit data

    Returns:
        Updated Credit instance or None if not found
    """
    credit = get_credit_by_id(session, credit_id)

    if not credit:
        return None

    for key, value in credit_data.items():
        if hasattr(credit, key):
            setattr(credit, key, value)

    session.add(credit)
    session.commit()
    session.refresh(credit)
    return credit


def delete_credit(session: Session, credit_id: int) -> bool:
    """Delete a credit record.

    Args:
        session: Database session
        credit_id: ID of the credit to delete

    Returns:
        True if deleted, False if not found
    """
    credit = get_credit_by_id(session, credit_id)

    if not credit:
        return False

    session.delete(credit)
    session.commit()
    return True


def delete_credits_for_movie(session: Session, movie_id: int) -> int:
    """Delete all credits for a specific movie.

    Args:
        session: Database session
        movie_id: ID of the movie

    Returns:
        Number of credits deleted
    """
    credits = get_credits_by_movie_id(session, movie_id)
    count = len(credits)

    for credit in credits:
        session.delete(credit)

    session.commit()
    logger.debug(f"Deleted {count} credits for movie ID {movie_id}")
    return count


def create_credits_from_tmdb_data(
    session: Session, movie_id: int, credits_data: dict[str, Any]
) -> list[Credit]:
    """Create credit records from TMDB credits data.

    This function processes the "credits" section of TMDB API response
    and creates corresponding Credit records in the database.

    Args:
        session: Database session
        movie_id: ID of the movie
        credits_data: TMDB credits data dictionary

    Returns:
        List of created Credit instances
    """
    created_credits = []

    ***REMOVED*** Process cast data
    cast_data = credits_data.get("cast", [])
    for cast_member in cast_data:
        if not cast_member.get("id"):
            continue

        credit_data = {
            "movie_id": movie_id,
            "tmdb_person_id": cast_member.get("id"),
            "name": cast_member.get("name", "Unknown"),
            "original_name": cast_member.get("original_name"),
            "character": cast_member.get("character"),
            "department": cast_member.get("known_for_department", "Acting"),
            "cast_id": cast_member.get("cast_id"),
            "order": cast_member.get("order"),
            "gender": cast_member.get("gender"),
            "profile_path": cast_member.get("profile_path"),
            "popularity": cast_member.get("popularity"),
            "credit_id": cast_member.get("credit_id"),
            "adult": cast_member.get("adult", False),
        }

        credit = Credit(**credit_data)
        session.add(credit)
        created_credits.append(credit)

    ***REMOVED*** Process crew data
    crew_data = credits_data.get("crew", [])
    for crew_member in crew_data:
        if not crew_member.get("id"):
            continue

        credit_data = {
            "movie_id": movie_id,
            "tmdb_person_id": crew_member.get("id"),
            "name": crew_member.get("name", "Unknown"),
            "original_name": crew_member.get("original_name"),
            "department": crew_member.get("department"),
            "job": crew_member.get("job"),
            "gender": crew_member.get("gender"),
            "profile_path": crew_member.get("profile_path"),
            "popularity": crew_member.get("popularity"),
            "credit_id": crew_member.get("credit_id"),
            "adult": crew_member.get("adult", False),
        }

        credit = Credit(**credit_data)
        session.add(credit)
        created_credits.append(credit)

    session.commit()
    logger.debug(f"Added {len(created_credits)} credits to movie ID {movie_id}")
    return created_credits

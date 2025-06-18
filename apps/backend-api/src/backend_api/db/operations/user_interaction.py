"""
Operations for user movie interactions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlmodel import Session, and_, delete, select, update

from config.logging import get_logger
from backend_api.models import Movie, User, UserMovieInteraction

logger = get_logger(__name__)


def create_user_movie_interaction(
    db: Session,
    user_id: int,
    movie_id: int,
    watched: bool = False,
    liked: bool = False,
    in_watchlist: bool = False,
) -> UserMovieInteraction:
    """
    Create a new user movie interaction.

    Args:
        db: Database session
        user_id: User ID
        movie_id: Movie ID
        watched: Whether the user has watched the movie
        liked: Whether the user has liked the movie
        in_watchlist: Whether the movie is in the user's watchlist

    Returns:
        The created user movie interaction
    """
    ***REMOVED*** Check if user and movie exist
    user = db.get(User, user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    movie = db.get(Movie, movie_id)
    if not movie:
        raise ValueError(f"Movie with ID {movie_id} not found")

    ***REMOVED*** Check if interaction already exists
    stmt = select(UserMovieInteraction).where(
        and_(
            UserMovieInteraction.user_id == user_id,
            UserMovieInteraction.movie_id == movie_id,
        )
    )
    existing = db.exec(stmt).first()

    if existing:
        ***REMOVED*** Update existing interaction
        existing.watched = watched
        existing.liked = liked
        existing.in_watchlist = in_watchlist
        existing.updated_at = datetime.utcnow()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    ***REMOVED*** Create new interaction
    interaction = UserMovieInteraction(
        user_id=user_id,
        movie_id=movie_id,
        watched=watched,
        liked=liked,
        in_watchlist=in_watchlist,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def get_user_movie_interaction(
    db: Session, user_id: int, movie_id: int
) -> Optional[UserMovieInteraction]:
    """
    Get a user movie interaction by user ID and movie ID.

    Args:
        db: Database session
        user_id: User ID
        movie_id: Movie ID

    Returns:
        The user movie interaction if found, None otherwise
    """
    stmt = select(UserMovieInteraction).where(
        and_(
            UserMovieInteraction.user_id == user_id,
            UserMovieInteraction.movie_id == movie_id,
        )
    )
    return db.exec(stmt).first()


def get_user_movie_interactions(
    db: Session,
    user_id: int,
    watched: Optional[bool] = None,
    liked: Optional[bool] = None,
    in_watchlist: Optional[bool] = None,
) -> List[UserMovieInteraction]:
    """
    Get user movie interactions by user ID with optional filters.

    Args:
        db: Database session
        user_id: User ID
        watched: Filter by watched status
        liked: Filter by liked status
        in_watchlist: Filter by in_watchlist status

    Returns:
        List of user movie interactions
    """
    query = select(UserMovieInteraction).where(UserMovieInteraction.user_id == user_id)

    if watched is not None:
        query = query.where(UserMovieInteraction.watched == watched)
    if liked is not None:
        query = query.where(UserMovieInteraction.liked == liked)
    if in_watchlist is not None:
        query = query.where(UserMovieInteraction.in_watchlist == in_watchlist)

    return list(db.exec(query).all())


def get_user_watchlist(db: Session, user_id: int) -> List[UserMovieInteraction]:
    """
    Get a user's watchlist.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of user movie interactions in the user's watchlist
    """
    return list(get_user_movie_interactions(db, user_id, in_watchlist=True))


def get_user_watched_movies(db: Session, user_id: int) -> List[UserMovieInteraction]:
    """
    Get movies that a user has watched.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of user movie interactions for watched movies
    """
    return list(get_user_movie_interactions(db, user_id, watched=True))


def get_user_liked_movies(db: Session, user_id: int) -> List[UserMovieInteraction]:
    """
    Get movies that a user has liked.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of user movie interactions for liked movies
    """
    return list(get_user_movie_interactions(db, user_id, liked=True))


def update_user_movie_interaction(
    db: Session,
    user_id: int,
    movie_id: int,
    watched: Optional[bool] = None,
    liked: Optional[bool] = None,
    in_watchlist: Optional[bool] = None,
) -> Optional[UserMovieInteraction]:
    """
    Update a user movie interaction.

    Args:
        db: Database session
        user_id: User ID
        movie_id: Movie ID
        watched: New watched status
        liked: New liked status
        in_watchlist: New in_watchlist status

    Returns:
        The updated user movie interaction if found, None otherwise
    """
    interaction = get_user_movie_interaction(db, user_id, movie_id)
    if not interaction:
        ***REMOVED*** Create interaction if it doesn't exist
        data = {
            "watched": watched if watched is not None else False,
            "liked": liked if liked is not None else False,
            "in_watchlist": in_watchlist if in_watchlist is not None else False,
        }
        return create_user_movie_interaction(db, user_id, movie_id, **data)

    ***REMOVED*** Update only the provided fields
    if watched is not None:
        interaction.watched = watched
    if liked is not None:
        interaction.liked = liked
    if in_watchlist is not None:
        interaction.in_watchlist = in_watchlist

    interaction.updated_at = datetime.utcnow()
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def delete_user_movie_interaction(db: Session, user_id: int, movie_id: int) -> bool:
    """
    Delete a user movie interaction.

    Args:
        db: Database session
        user_id: User ID
        movie_id: Movie ID

    Returns:
        True if the interaction was deleted, False otherwise
    """
    interaction = get_user_movie_interaction(db, user_id, movie_id)
    if not interaction:
        return False

    db.delete(interaction)
    db.commit()
    return True


def toggle_user_movie_interaction_flag(
    db: Session, user_id: int, movie_id: int, flag: str
) -> UserMovieInteraction:
    """
    Toggle a specific flag (watched, liked, in_watchlist) for a user movie interaction.

    Args:
        db: Database session
        user_id: User ID
        movie_id: Movie ID
        flag: The flag to toggle ('watched', 'liked', or 'in_watchlist')

    Returns:
        The updated user movie interaction

    Raises:
        ValueError: If the flag is invalid
    """
    if flag not in ["watched", "liked", "in_watchlist"]:
        raise ValueError(f"Invalid flag: {flag}")

    interaction = get_user_movie_interaction(db, user_id, movie_id)

    ***REMOVED*** If interaction doesn't exist, create it with the flag set to True
    if not interaction:
        kwargs = {flag: True}
        return create_user_movie_interaction(db, user_id, movie_id, **kwargs)

    ***REMOVED*** Toggle the flag
    setattr(interaction, flag, not getattr(interaction, flag))
    interaction.updated_at = datetime.utcnow()

    ***REMOVED*** If all flags are False, delete the interaction
    if not (interaction.watched or interaction.liked or interaction.in_watchlist):
        db.delete(interaction)
        db.commit()

        ***REMOVED*** Return a dummy representation with all flags false, but with a valid structure
        return UserMovieInteraction(
            user_id=user_id,
            movie_id=movie_id,
            watched=False,
            liked=False,
            in_watchlist=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction

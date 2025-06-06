"""
User movie interaction queries for optimized read operations.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from movie_storage.db.operations import (
    get_movie_by_id,
    get_user_liked_movies,
    get_user_movie_interaction,
    get_user_watched_movies,
    get_user_watchlist,
)
from movie_storage.models import Movie, UserMovieInteraction
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from backend_api.errors import ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class UserMovieDetail(BaseModel):
    """Detailed information about a movie with user interaction status."""

    interaction_id: Optional[int] = None
    movie_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    watched: bool = False
    liked: bool = False
    in_watchlist: bool = False
    imdb_rating: Optional[float] = None


class UserInteractionQuery:
    """
    Query operations for user movie interactions.

    This class handles optimized read operations for user movie interactions,
    following CQRS principles by separating read operations from write operations.
    """

    def get_user_interaction(
        self, db: Session, user_id: int, movie_id: int
    ) -> Optional[UserMovieInteraction]:
        """
        Get a user's interaction with a specific movie.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            User movie interaction or None if no interaction exists

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Validate movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        ***REMOVED*** Get existing interaction
        return get_user_movie_interaction(db, user_id, movie_id)

    def get_user_watchlist(
        self, db: Session, user_id: int, limit: int = 50, offset: int = 0
    ) -> Tuple[List[UserMovieInteraction], int]:
        """
        Get a user's watchlist with pagination.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Tuple of (list of interactions, total count)

        Raises:
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Get user interactions
        interactions = get_user_watchlist(db, user_id)
        total = len(interactions)

        ***REMOVED*** Apply pagination
        paginated = interactions[offset : offset + limit]

        return paginated, total

    def get_user_watched_movies(
        self, db: Session, user_id: int, limit: int = 50, offset: int = 0
    ) -> Tuple[List[UserMovieInteraction], int]:
        """
        Get movies a user has watched with pagination.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Tuple of (list of interactions, total count)

        Raises:
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Get user interactions
        interactions = get_user_watched_movies(db, user_id)
        total = len(interactions)

        ***REMOVED*** Apply pagination
        paginated = interactions[offset : offset + limit]

        return paginated, total

    def get_user_liked_movies(
        self, db: Session, user_id: int, limit: int = 50, offset: int = 0
    ) -> Tuple[List[UserMovieInteraction], int]:
        """
        Get movies a user has liked with pagination.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Tuple of (list of interactions, total count)

        Raises:
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Get user interactions
        interactions = get_user_liked_movies(db, user_id)
        total = len(interactions)

        ***REMOVED*** Apply pagination
        paginated = interactions[offset : offset + limit]

        return paginated, total

    def get_user_interactions_with_movies(
        self,
        db: Session,
        user_id: int,
        interactions: List[UserMovieInteraction],
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get user interactions with movie details.

        Args:
            db: Database session
            user_id: User ID
            interactions: List of user movie interactions
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Tuple of (list of dictionaries containing interaction and movie details, total count)

        Raises:
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Apply pagination
        total = len(interactions)
        paginated_interactions = interactions[offset : offset + limit]

        ***REMOVED*** Create result with movie details
        result = []
        for interaction in paginated_interactions:
            movie = get_movie_by_id(db, interaction.movie_id)
            if movie:
                result.append({"interaction": interaction, "movie": movie})

        return result, total

    def get_user_movie_details(
        self, db: Session, user_id: int, category: str, limit: int = 20, offset: int = 0
    ) -> Tuple[List[UserMovieDetail], int]:
        """
        Get detailed movie information with user interaction status.

        This is an optimized query for UI display that retrieves movie details
        alongside interaction status in a single, efficiently joined query.

        Args:
            db: Database session
            user_id: User ID
            category: Category of movies to retrieve ('watchlist', 'watched', or 'liked')
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Tuple of (list of user movie details, total count)

        Raises:
            ValidationError: If user_id is invalid or category is unknown
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        if category not in ["watchlist", "watched", "liked"]:
            raise ValidationError(
                message="Invalid category",
                field_errors={"category": ["Must be one of: watchlist, watched, liked"]},
            )

        ***REMOVED*** Construct query based on category
        query = (
            select(UserMovieInteraction, Movie)
            .where(UserMovieInteraction.user_id == user_id)
            .join(Movie)
            .where(UserMovieInteraction.movie_id == Movie.id)
        )

        ***REMOVED*** Apply category filter
        if category == "watchlist":
            query = query.where(UserMovieInteraction.in_watchlist == True)
        elif category == "watched":
            query = query.where(UserMovieInteraction.watched == True)
        elif category == "liked":
            query = query.where(UserMovieInteraction.liked == True)

        ***REMOVED*** Get total count with a separate count query
        count_query = select(func.count()).select_from(query.subquery())
        total_count = db.scalar(count_query)
        total = int(total_count) if total_count is not None else 0

        ***REMOVED*** Apply pagination
        query = query.offset(offset).limit(limit)

        ***REMOVED*** Execute query
        results = db.exec(query).all()

        ***REMOVED*** Transform results into response objects
        details = []
        for interaction, movie in results:
            ***REMOVED*** Ensure movie_id is not None before creating UserMovieDetail
            if movie.id is not None:
                details.append(
                    UserMovieDetail(
                        interaction_id=interaction.id,
                        movie_id=movie.id,
                        title=movie.title,
                        poster_url=movie.poster_url,
                        release_date=(
                            movie.release_date.isoformat() if movie.release_date else None
                        ),
                        watched=interaction.watched,
                        liked=interaction.liked,
                        in_watchlist=interaction.in_watchlist,
                        imdb_rating=movie.imdb_rating,
                    )
                )

        return details, total

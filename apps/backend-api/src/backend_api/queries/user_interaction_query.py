"""
User movie interaction queries for optimized read operations.
"""

from typing import Any

from config.logging import get_logger
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from backend_api.db.operations import (
    get_movie_by_id,
    get_user_liked_movies,
    get_user_movie_interaction,
    get_user_watched_movies,
    get_user_watchlist,
)
from backend_api.errors import ResourceNotFoundError, ValidationError
from backend_api.models import Movie, UserMovieInteraction

logger = get_logger(__name__)


class UserMovieDetail(BaseModel):
    """Detailed information about a movie with user interaction status."""

    interaction_id: int | None = None
    movie_id: int
    title: str
    poster_url: str | None = None
    release_date: str | None = None
    watched: bool = False
    liked: bool = False
    in_watchlist: bool = False
    imdb_rating: float | None = None


class UserInteractionQuery:
    """
    Query operations for user movie interactions.

    This class handles optimized read operations for user movie interactions,
    following CQRS principles by separating read operations from write operations.
    """

    def get_user_interaction(
        self, db: Session, user_id: int, movie_id: int
    ) -> UserMovieInteraction | None:
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

    def get_user_interactions_batch(
        self, db: Session, user_id: int, movie_ids: list[int]
    ) -> dict[int, UserMovieInteraction | None]:
        """
        Get a user's interactions with multiple movies in a single query.

        This is an optimized batch operation that retrieves multiple user-movie
        interactions in one database query instead of N individual queries.

        Args:
            db: Database session
            user_id: User ID
            movie_ids: List of movie IDs to get interactions for

        Returns:
            Dictionary mapping movie_id to UserMovieInteraction (or None if no interaction)

        Raises:
            ValidationError: If user_id is invalid or movie_ids is empty
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        if not movie_ids:
            raise ValidationError(
                message="Movie IDs list cannot be empty",
                field_errors={"movie_ids": ["Must contain at least one movie ID"]},
            )

        ***REMOVED*** Remove duplicates and ensure all are positive integers
        unique_movie_ids = list(set(movie_id for movie_id in movie_ids if movie_id > 0))

        if not unique_movie_ids:
            raise ValidationError(
                message="No valid movie IDs provided",
                field_errors={"movie_ids": ["Must contain at least one positive movie ID"]},
            )

            ***REMOVED*** Use a single optimized batch query
        from sqlmodel import col, select

        ***REMOVED*** Execute single batch query to get all interactions at once
        query = (
            select(UserMovieInteraction)
            .where(UserMovieInteraction.user_id == user_id)
            .where(col(UserMovieInteraction.movie_id).in_(unique_movie_ids))
        )

        interactions = db.exec(query).all()

        ***REMOVED*** Build result dictionary
        result: dict[int, UserMovieInteraction | None] = {}

        ***REMOVED*** Initialize all movie IDs to None
        for movie_id in unique_movie_ids:
            result[movie_id] = None

        ***REMOVED*** Fill in the interactions we found
        for interaction in interactions:
            result[interaction.movie_id] = interaction

        return result

    def get_user_watchlist(
        self, db: Session, user_id: int, limit: int = 50, offset: int = 0
    ) -> tuple[list[UserMovieInteraction], int]:
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
    ) -> tuple[list[UserMovieInteraction], int]:
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
    ) -> tuple[list[UserMovieInteraction], int]:
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
        interactions: list[UserMovieInteraction],
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
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
    ) -> tuple[list[UserMovieDetail], int]:
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
            query = query.where(UserMovieInteraction.in_watchlist)
        elif category == "watched":
            query = query.where(UserMovieInteraction.watched)
        elif category == "liked":
            query = query.where(UserMovieInteraction.liked)

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

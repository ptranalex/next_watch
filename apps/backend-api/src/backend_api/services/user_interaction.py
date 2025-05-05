"""
User movie interaction service module.

This service handles business logic related to how users interact with movies,
including tracking movies as watched, liked, and in watchlists.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session

from movie_storage.models import UserMovieInteraction, User, Movie
from movie_storage.db.operations import (
    get_movie_by_id,
    get_user_movie_interaction,
    create_user_movie_interaction,
    update_user_movie_interaction,
    delete_user_movie_interaction,
    toggle_user_movie_interaction_flag,
)
from backend_api.errors import ResourceNotFoundError, ValidationError, ServiceError

logger = logging.getLogger(__name__)


class UserInteractionService:
    """
    Service for handling user interactions with movies.

    This service encapsulates business logic for tracking user movie interactions
    such as watched status, likes, and watchlist management.

    Following CQRS principles, this service handles commands (state changes)
    while leaving queries (data retrieval) to a separate query class.
    """

    ***REMOVED*** Command methods (write operations)

    def toggle_watchlist(
        self, db: Session, user_id: int, movie_id: int
    ) -> UserMovieInteraction:
        """
        Toggle a movie in a user's watchlist.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Updated user movie interaction

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

        logger.info(f"Toggling watchlist for user {user_id} and movie {movie_id}")
        return toggle_user_movie_interaction_flag(db, user_id, movie_id, "in_watchlist")

    def toggle_watched(
        self, db: Session, user_id: int, movie_id: int
    ) -> UserMovieInteraction:
        """
        Toggle a movie as watched by a user.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Updated user movie interaction

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

        logger.info(f"Toggling watched status for user {user_id} and movie {movie_id}")
        return toggle_user_movie_interaction_flag(db, user_id, movie_id, "watched")

    def toggle_liked(
        self, db: Session, user_id: int, movie_id: int
    ) -> UserMovieInteraction:
        """
        Toggle a movie as liked by a user.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Updated user movie interaction

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

        logger.info(f"Toggling liked status for user {user_id} and movie {movie_id}")
        return toggle_user_movie_interaction_flag(db, user_id, movie_id, "liked")

    def delete_interaction(self, db: Session, user_id: int, movie_id: int) -> bool:
        """
        Delete a user's interaction with a movie.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            True if interaction was deleted, False if no interaction existed

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

        logger.info(f"Deleting interaction for user {user_id} and movie {movie_id}")
        return delete_user_movie_interaction(db, user_id, movie_id)

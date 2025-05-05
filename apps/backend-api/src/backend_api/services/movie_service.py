"""
Movie service module for retrieving and manipulating movie data.

This service follows the CQRS pattern, with this service handling state-changing
operations, while read operations are in a separate query class.
"""

import logging
from typing import Optional, List, Dict, Any
from sqlmodel import Session

from backend_api.errors import ResourceNotFoundError, ValidationError
from movie_storage.db.operations import (
    get_movie_by_id,
    get_credits_by_movie_id,
)

logger = logging.getLogger(__name__)


class MovieService:
    """
    Service for handling state-changing operations on movies.

    Following CQRS principles, this service handles commands (state changes)
    while query operations are handled by separate query classes.
    """

    def get_movie_details(self, db: Session, movie_id: int) -> Dict[str, Any]:
        """
        Get detailed information for a specific movie.

        Args:
            db: Database session
            movie_id: Movie ID

        Returns:
            Movie details as a dictionary

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If movie_id is invalid
        """
        ***REMOVED*** Validate inputs
        if movie_id <= 0:
            raise ValidationError(
                message="Invalid movie ID",
                field_errors={"movie_id": ["Must be positive"]},
            )

        ***REMOVED*** Get movie
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        ***REMOVED*** If it's already a dictionary, return it
        if isinstance(movie, dict):
            return movie

        ***REMOVED*** For SQLModel objects, use their built-in conversion method
        try:
            ***REMOVED*** Use SQLModel's non-deprecated conversion method
            if hasattr(movie, "model_dump"):
                return movie.model_dump()

            ***REMOVED*** For other objects, return a basic dict with its ID
            return {"id": movie_id}
        except Exception:
            logger.warning(f"Failed to convert movie {movie_id} to dictionary")
            return {"id": movie_id}

    def get_movie_cast(self, db: Session, movie_id: int) -> List[Dict[str, Any]]:
        """
        Get cast information for a specific movie.

        Args:
            db: Database session
            movie_id: Movie ID

        Returns:
            List of cast members

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If movie_id is invalid
        """
        ***REMOVED*** Validate inputs
        if movie_id <= 0:
            raise ValidationError(
                message="Invalid movie ID",
                field_errors={"movie_id": ["Must be positive"]},
            )

        ***REMOVED*** Get movie
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        ***REMOVED*** Get all credits for the movie
        credits = get_credits_by_movie_id(db, movie_id)

        ***REMOVED*** Filter for cast members only
        cast_members = []
        for credit in credits:
            ***REMOVED*** Filter for cast members (actors)
            if credit.department == "Acting" or credit.cast_id is not None:
                cast_member = {
                    "id": credit.id,
                    "actor_id": credit.tmdb_person_id,
                    "name": credit.name,
                    "character": credit.character,
                    "profile_path": credit.profile_path,
                    "order": credit.order,
                }
                cast_members.append(cast_member)

        ***REMOVED*** Sort cast by order if available
        cast_members.sort(key=lambda x: x.get("order", 999) or 999)

        return cast_members

"""
Movie service module for retrieving and manipulating movie data.

This service follows the CQRS pattern, with this service handling state-changing
operations, while read operations are in a separate query class.
"""

import logging
from typing import Any, Dict, List, Optional, TypedDict, cast

from movie_storage.db.operations import (
    get_credits_by_movie_id,
    get_movie_by_id,
)
from sqlmodel import Session

***REMOVED*** Use absolute import to avoid mypy errors
import backend_api.errors
from backend_api.errors import ResourceNotFoundError, ValidationError

***REMOVED*** Use relative imports instead
from .. import errors
from ..errors import ResourceNotFoundError, ValidationError

***REMOVED*** Use relative imports for better type checking
from .. import errors
from ..errors import ResourceNotFoundError, ValidationError

***REMOVED*** Use relative imports
from .. import errors
from ..errors import ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class CastMember(TypedDict):
    """Type definition for cast member data."""

    id: int
    name: str
    character: Optional[str]  ***REMOVED*** Character can be None
    profile_path: Optional[str]
    order: Optional[int]
    popularity: Optional[float]


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

    def get_movie_cast(
        self, db: Session, movie_id: int, popularity_threshold: float = 3.0
    ) -> List[CastMember]:
        """
        Get cast information for a specific movie.

        Args:
            db: Database session
            movie_id: Movie ID
            popularity_threshold: Minimum popularity score to include (default 3.0)
                                  Will always return at least 3 cast members regardless

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
        cast_members: List[CastMember] = []
        for credit in credits:
            ***REMOVED*** Filter for cast members (actors)
            if credit.department == "Acting":
                cast_member: CastMember = {
                    "id": credit.tmdb_person_id,
                    "name": credit.name,
                    "character": credit.character,
                    "profile_path": credit.profile_path,
                    "order": credit.order,
                    "popularity": credit.popularity,
                }
                cast_members.append(cast_member)

        ***REMOVED*** Sort cast by order, properly handling 0 values
        cast_members.sort(key=lambda x: float("inf") if x["order"] is None else x["order"])

        ***REMOVED*** Apply popularity filtering while ensuring at least 3 cast members are returned
        if popularity_threshold > 0:
            ***REMOVED*** First, sort by popularity (descending) to get the most popular cast members
            by_popularity = sorted(
                cast_members, key=lambda x: float(x["popularity"] or 0), reverse=True
            )

            ***REMOVED*** Filter by popularity threshold
            filtered_cast = [
                m for m in by_popularity if float(m["popularity"] or 0) >= popularity_threshold
            ]

            ***REMOVED*** Ensure we have at least 3 cast members (or all if there are fewer than 3)
            min_members = min(3, len(by_popularity))

            ***REMOVED*** If we don't have enough members after filtering, add more from the popularity-sorted list
            if len(filtered_cast) < min_members:
                ***REMOVED*** Get the most popular cast members we don't already have
                additional_members = [m for m in by_popularity if m not in filtered_cast]

                ***REMOVED*** Add enough to meet the minimum
                filtered_cast.extend(additional_members[: min_members - len(filtered_cast)])

            ***REMOVED*** Sort the filtered cast by order again
            filtered_cast.sort(key=lambda x: float("inf") if x["order"] is None else x["order"])

            return filtered_cast

        return cast_members

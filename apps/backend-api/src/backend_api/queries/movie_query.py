"""
Movie query module for optimized read operations.

This module provides query operations for movies following the CQRS pattern,
separating read operations from write operations.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlmodel import Session

from backend_api.errors import ResourceNotFoundError, ValidationError
from backend_api.queries.movie_details import (
    get_movie_details_by_id,
    get_movie_details_by_tmdb_id,
    get_movie_genres,
    get_movies_by_ids_bulk,
)
from backend_api.queries.movie_listings import get_movies_with_filters, search_movies_by_title

***REMOVED*** Import query functions directly to avoid circular imports
from backend_api.queries.top_movies import get_top_rated_movies
from backend_api.queries.trailer import get_trailers_for_movie

logger = logging.getLogger(__name__)


class MovieQuery:
    """
    Query operations for movies.

    This class handles optimized read operations for movies,
    following CQRS principles by separating read operations from write operations.
    """

    def get_movies_with_filters(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        genre_id: Optional[int] = None,
        actor_tmdb_id: Optional[int] = None,
        sort_by: str = "title",
        sort_desc: bool = False,
        imdb_rating: Optional[float] = None,
        rotten_tomatoes_rating: Optional[int] = None,
        metacritic_rating: Optional[int] = None,
        year: Optional[int] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get movies with various filtering options.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            genre_id: Filter by genre ID
            actor_tmdb_id: Filter by actor TMDB ID
            sort_by: Field to sort by
            sort_desc: Sort in descending order
            imdb_rating: Minimum IMDb rating
            rotten_tomatoes_rating: Minimum Rotten Tomatoes rating
            metacritic_rating: Minimum Metacritic rating
            year: Filter by release year
            start_year: Filter by start year (inclusive)
            end_year: Filter by end year (inclusive)

        Returns:
            Tuple of (movie list, total count)

        Raises:
            ValidationError: If parameters are invalid
        """
        ***REMOVED*** Validate inputs
        if skip < 0:
            raise ValidationError(
                message="Invalid skip value",
                field_errors={"skip": ["Must be non-negative"]},
            )
        if limit <= 0 or limit > 100:
            raise ValidationError(
                message="Invalid limit value",
                field_errors={"limit": ["Must be between 1 and 100"]},
            )

        valid_sort_fields = [
            "title",
            "release_date",
            "imdb_rating",
            "rotten_tomatoes_rating",
            "metacritic_rating",
        ]
        if sort_by not in valid_sort_fields:
            raise ValidationError(
                message="Invalid sort field",
                field_errors={"sort_by": [f"Must be one of: {', '.join(valid_sort_fields)}"]},
            )

        ***REMOVED*** Get movies
        return get_movies_with_filters(
            db,
            skip=skip,
            limit=limit,
            genre_id=genre_id,
            actor_tmdb_id=actor_tmdb_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
            imdb_rating=imdb_rating,
            rotten_tomatoes_rating=rotten_tomatoes_rating,
            metacritic_rating=metacritic_rating,
            year=year,
            start_year=start_year,
            end_year=end_year,
        )

    def get_movie_details(self, db: Session, movie_id: int) -> Dict[str, Any]:
        """
        Get detailed information for a specific movie.

        Args:
            db: Database session
            movie_id: Movie ID

        Returns:
            Movie details

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
        movie = get_movie_details_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        return movie

    def get_movie_by_tmdb_id(self, db: Session, tmdb_id: int) -> Dict[str, Any]:
        """
        Get movie by TMDB ID.

        Args:
            db: Database session
            tmdb_id: TMDB ID

        Returns:
            Movie details

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If tmdb_id is invalid
        """
        ***REMOVED*** Validate inputs
        if tmdb_id <= 0:
            raise ValidationError(
                message="Invalid TMDB ID",
                field_errors={"tmdb_id": ["Must be positive"]},
            )

        ***REMOVED*** Get movie
        movie = get_movie_details_by_tmdb_id(db, tmdb_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with TMDB ID {tmdb_id} not found",
                resource_type="Movie",
                resource_id=tmdb_id,
            )

        return movie

    def get_movie_genres(self, db: Session, movie_id: int) -> List[Dict[str, Any]]:
        """
        Get genres for a specific movie.

        Args:
            db: Database session
            movie_id: Movie ID

        Returns:
            List of genres

        Raises:
            ValidationError: If movie_id is invalid
        """
        ***REMOVED*** Validate inputs
        if movie_id <= 0:
            raise ValidationError(
                message="Invalid movie ID",
                field_errors={"movie_id": ["Must be positive"]},
            )

        ***REMOVED*** Get genres
        return get_movie_genres(db, movie_id)

    def get_movies_by_ids(self, db: Session, movie_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Get multiple movies by their IDs.

        Args:
            db: Database session
            movie_ids: List of movie IDs to fetch

        Returns:
            List of movie details for the provided IDs

        Raises:
            ValidationError: If movie_ids list is invalid
        """
        ***REMOVED*** Validate inputs
        if not movie_ids:
            return []

        if not all(isinstance(movie_id, int) and movie_id > 0 for movie_id in movie_ids):
            raise ValidationError(
                message="Invalid movie IDs",
                field_errors={"movie_ids": ["All movie IDs must be positive integers"]},
            )

        if len(movie_ids) > 1000:  ***REMOVED*** Reasonable limit
            raise ValidationError(
                message="Too many movie IDs",
                field_errors={"movie_ids": ["Maximum 1000 movie IDs allowed"]},
            )

        ***REMOVED*** Use the existing movie_details module to get movies by IDs
        return get_movies_by_ids_bulk(db, movie_ids)

    def get_movie_trailers(self, db: Session, movie_id: int) -> List[Dict[str, Any]]:
        """
        Get trailers for a specific movie.

        Args:
            db: Database session
            movie_id: Movie ID

        Returns:
            List of trailers

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

        ***REMOVED*** Verify movie exists
        movie = get_movie_details_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        ***REMOVED*** Get trailers
        trailers = get_trailers_for_movie(db, movie_id)
        ***REMOVED*** Convert to dict if necessary
        return [trailer if isinstance(trailer, dict) else trailer.dict() for trailer in trailers]

    def get_top_rated_movies(
        self,
        db: Session,
        limit: int = 10,
        skip: int = 0,
        year: Optional[int] = None,
        genre_id: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get top rated movies for the current year.

        Args:
            db: Database session
            limit: Maximum number of records to return
            skip: Number of records to skip
            year: Filter by release year
            genre_id: Filter by genre ID

        Returns:
            Tuple of (movie list, total count)

        Raises:
            ValidationError: If parameters are invalid
        """
        ***REMOVED*** Validate inputs
        if skip < 0:
            raise ValidationError(
                message="Invalid skip value",
                field_errors={"skip": ["Must be non-negative"]},
            )
        if limit <= 0 or limit > 50:
            raise ValidationError(
                message="Invalid limit value",
                field_errors={"limit": ["Must be between 1 and 50"]},
            )

        ***REMOVED*** Get top movies by calculating page from skip
        page = (skip // limit) + 1 if limit > 0 else 1

        ***REMOVED*** Get top movies
        return get_top_rated_movies(
            db_session=db,
            limit=limit,
            page=page,
            year=year,
            genre_id=genre_id,
        )

    def search_movies_by_title(
        self,
        db: Session,
        title_search: str,
        skip: int = 0,
        limit: int = 20,
        genre_id: Optional[int] = None,
        actor_tmdb_id: Optional[int] = None,
        sort_by: str = "title",
        sort_desc: bool = False,
        imdb_rating: Optional[float] = None,
        rotten_tomatoes_rating: Optional[int] = None,
        metacritic_rating: Optional[int] = None,
        year: Optional[int] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search for movies by title with additional filtering options.

        Args:
            db: Database session
            title_search: Title search string (case-insensitive partial match)
            skip: Number of records to skip
            limit: Maximum number of records to return
            genre_id: Optional genre ID to filter by
            actor_tmdb_id: Optional actor TMDB ID to filter by
            sort_by: Field to sort by
            sort_desc: Whether to sort in descending order
            imdb_rating: Minimum IMDb rating to filter by
            rotten_tomatoes_rating: Minimum Rotten Tomatoes rating to filter by
            metacritic_rating: Minimum Metacritic rating to filter by
            year: Release year to filter by
            start_year: Start release year to filter by (inclusive)
            end_year: End release year to filter by (inclusive)

        Returns:
            Tuple of (movie list, total count)

        Raises:
            ValidationError: If parameters are invalid
        """
        ***REMOVED*** Validate inputs
        if not title_search or not title_search.strip():
            raise ValidationError(
                message="Invalid search query",
                field_errors={"title_search": ["Search query cannot be empty"]},
            )

        if skip < 0:
            raise ValidationError(
                message="Invalid skip value",
                field_errors={"skip": ["Must be non-negative"]},
            )
        if limit <= 0 or limit > 100:
            raise ValidationError(
                message="Invalid limit value",
                field_errors={"limit": ["Must be between 1 and 100"]},
            )

        valid_sort_fields = [
            "title",
            "release_date",
            "imdb_rating",
            "rotten_tomatoes_rating",
            "metacritic_rating",
        ]
        if sort_by not in valid_sort_fields:
            raise ValidationError(
                message="Invalid sort field",
                field_errors={"sort_by": [f"Must be one of: {', '.join(valid_sort_fields)}"]},
            )

        ***REMOVED*** Use the search function from movie_listings
        return search_movies_by_title(
            db_session=db,
            title_search=title_search.strip(),
            skip=skip,
            limit=limit,
            genre_id=genre_id,
            actor_tmdb_id=actor_tmdb_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
            imdb_rating=imdb_rating,
            rotten_tomatoes_rating=rotten_tomatoes_rating,
            metacritic_rating=metacritic_rating,
            year=year,
            start_year=start_year,
            end_year=end_year,
        )

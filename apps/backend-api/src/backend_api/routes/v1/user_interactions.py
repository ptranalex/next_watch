"""
User interaction routes for managing user movie relationships.

These routes handle user interactions with movies such as:
- Watchlist management
- Watched movies tracking
- Movie likes/dislikes
- Import functionality for external services

Authentication is handled by the BFF layer, which passes user context
via X-User-ID header after validating JWT tokens.
"""

import csv
import io
from typing import Annotated, Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile, status
from pydantic import BaseModel
from sqlmodel import Session

***REMOVED*** Import fast-core dependencies and utilities
from fast_core.dependencies import get_request_id
from fast_core.responses import ResponseBuilder

from config.logging import get_logger
from backend_api.db.database import get_db
from backend_api.dependencies import get_user_id_from_header
from backend_api.errors import (
    ResourceNotFoundError,
    ValidationError,
    service_error_to_http_exception,
)
from backend_api.models.user_interaction import UserMovieInteraction
from backend_api.queries import UserInteractionQuery
from backend_api.schemas import (
    MovieSummary,
    UserMovieDetail,
    UserMovieInteractionResponse,
    UserMovieInteractionWithMovie,
)
from backend_api.services.user_interaction import UserInteractionService

logger = get_logger(__name__)

***REMOVED*** Create router
router = APIRouter(prefix="/user/movies", tags=["user-movies"])


***REMOVED*** Get dependencies
def get_user_interaction_service() -> UserInteractionService:
    """Get user interaction service."""
    return UserInteractionService()


def get_user_interaction_query() -> UserInteractionQuery:
    """Get user interaction query."""
    return UserInteractionQuery()


***REMOVED*** Get user interaction with a specific movie (no auth - BFF handles authentication)
@router.get(
    "/{movie_id}/interaction",
    response_model=Union[UserMovieInteractionResponse, Dict[str, Any]],
    summary="Get user interaction with a specific movie",
)
async def get_movie_interaction(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
) -> Union[UserMovieInteraction, Dict[str, Any]]:
    """
    Get user's interaction with a specific movie.

    Note: Authentication is handled by the BFF layer. This endpoint trusts
    that the BFF has already verified the user_id via X-User-ID header.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query

    Returns:
        User's interaction with the movie, or an empty dict if no interaction exists
    """
    try:
        result = interaction_query.get_user_interaction(db, user_id, movie_id)
        return result if result else {}
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user watchlist
@router.get(
    "/watchlist",
    response_model=List[UserMovieInteractionResponse],
    summary="Get user's watchlist",
)
async def get_user_watchlist_endpoint(
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[UserMovieInteraction]:
    """
    Get the current user's watchlist.

    Args:
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies in the user's watchlist
    """
    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_watchlist(db, user_id, limit, offset)
        return interactions
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user watched movies
@router.get(
    "/watched",
    response_model=List[UserMovieInteractionResponse],
    summary="Get user's watched movies",
)
async def get_user_watched_movies_endpoint(
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[UserMovieInteraction]:
    """
    Get the current user's watched movies.

    Args:
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies the user has watched
    """
    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_watched_movies(db, user_id, limit, offset)
        return interactions
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user liked movies
@router.get(
    "/liked",
    response_model=List[UserMovieInteractionResponse],
    summary="Get user's liked movies",
)
async def get_user_liked_movies_endpoint(
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[UserMovieInteraction]:
    """
    Get the current user's liked movies.

    Args:
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies the user has liked
    """
    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_liked_movies(db, user_id, limit, offset)
        return interactions
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Toggle movie in watchlist
@router.post(
    "/{movie_id}/watchlist",
    response_model=UserMovieInteractionResponse,
    summary="Toggle movie in watchlist",
    deprecated=True,
)
async def toggle_watchlist(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Toggle a movie in the user's watchlist (DEPRECATED).

    This endpoint is deprecated. Use PUT /user/movies/{movie_id}/watchlist or
    DELETE /user/movies/{movie_id}/watchlist instead for explicit operations.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.toggle_watchlist(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Toggle movie as watched
@router.post(
    "/{movie_id}/watched",
    response_model=UserMovieInteractionResponse,
    summary="Toggle movie as watched",
    deprecated=True,
)
async def toggle_watched(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Toggle a movie as watched/unwatched (DEPRECATED).

    This endpoint is deprecated. Use PUT /user/movies/{movie_id}/watched or
    DELETE /user/movies/{movie_id}/watched instead for explicit operations.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.toggle_watched(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Toggle movie as liked
@router.post(
    "/{movie_id}/liked",
    response_model=UserMovieInteractionResponse,
    summary="Toggle movie as liked",
    deprecated=True,
)
async def toggle_liked(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Toggle a movie as liked/unliked (DEPRECATED).

    This endpoint is deprecated. Use PUT /user/movies/{movie_id}/liked or
    DELETE /user/movies/{movie_id}/liked instead for explicit operations.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.toggle_liked(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Delete movie interaction
@router.delete(
    "/{movie_id}/interaction",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a movie interaction",
)
async def delete_movie_interaction(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> None:
    """
    Delete all interactions a user has with a movie.

    This removes the movie from watchlist, watched, and liked lists.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service
    """
    try:
        interaction_service.delete_interaction(db, user_id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user movie details with optimized queries
@router.get(
    "/{category}",
    response_model=List[UserMovieDetail],
    summary="Get user's movies with optimized details",
)
async def get_user_movie_details(
    category: Annotated[
        str, Path(title="Category", description="One of: watchlist, watched, liked")
    ],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    sort_by: Annotated[str, Query()] = "title",
    sort_desc: Annotated[bool, Query()] = False,
    imdb_rating: Annotated[Optional[float], Query(ge=0, le=10)] = None,
    rotten_tomatoes_rating: Annotated[Optional[float], Query(ge=0, le=100)] = None,
    metacritic_rating: Annotated[Optional[float], Query(ge=0, le=100)] = None,
    year: Annotated[Optional[int], Query(ge=1900, le=2030)] = None,
) -> List[Any]:
    """
    Get user's movies with detailed information and filtering options.

    This endpoint provides optimized queries to get user's movies with
    complete movie details including ratings, cast, and metadata.

    Args:
        category: Category of movies (watchlist, watched, liked)
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query
        page: Page number (1-based)
        limit: Items per page
        sort_by: Field to sort by (title, year, imdb_rating, etc.)
        sort_desc: Sort in descending order
        imdb_rating: Filter by minimum IMDb rating
        rotten_tomatoes_rating: Filter by minimum Rotten Tomatoes rating
        metacritic_rating: Filter by minimum Metacritic rating
        year: Filter by release year

    Returns:
        List of user movie details with full movie information
    """
    ***REMOVED*** Validate category
    valid_categories = ["watchlist", "watched", "liked"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}",
        )

    ***REMOVED*** Calculate offset from page
    offset = (page - 1) * limit

    ***REMOVED*** Build filters
    filters = {}
    if imdb_rating is not None:
        filters["imdb_rating"] = imdb_rating
    if rotten_tomatoes_rating is not None:
        filters["rotten_tomatoes_rating"] = rotten_tomatoes_rating
    if metacritic_rating is not None:
        filters["metacritic_rating"] = metacritic_rating
    if year is not None:
        filters["year"] = year

    try:
        ***REMOVED*** Get user movie details based on category using available methods
        result, total = interaction_query.get_user_movie_details(
            db, user_id, category, limit, offset
        )
        return result
    except ValidationError as e:
        raise service_error_to_http_exception(e)


class NetflixImportResult(BaseModel):
    """Result of a Netflix history import operation."""

    total_entries: int
    matched_movies: int
    already_marked_watched: int
    newly_marked_watched: int
    unmatched_titles: List[str]


@router.post(
    "/import/netflix",
    response_model=NetflixImportResult,
    summary="Import Netflix watch history",
)
async def import_netflix_history(
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
    file: UploadFile = File(...),
) -> NetflixImportResult:
    """
    Import Netflix watch history from a CSV file.

    Args:
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service
        file: Netflix history CSV file

    Returns:
        Import result with statistics

    Raises:
        HTTPException: If file format is invalid or import fails
    """
    ***REMOVED*** Validate file type
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file",
        )

    try:
        ***REMOVED*** Read CSV content
        content = await file.read()
        csv_content = content.decode("utf-8")

        ***REMOVED*** Process CSV using service
        result = interaction_service.import_netflix_history(db, user_id, csv_content)

        return NetflixImportResult(
            total_entries=result["total_entries"],
            matched_movies=result["matched_movies"],
            already_marked_watched=result["already_marked_watched"],
            newly_marked_watched=result["newly_marked_watched"],
            unmatched_titles=result["unmatched_titles"],
        )

    except Exception as e:
        logger.error(f"Netflix import failed for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process Netflix history file",
        )


***REMOVED*** Explicit CRUD operations for better API design


@router.put(
    "/{movie_id}/watched",
    response_model=UserMovieInteractionResponse,
    summary="Mark movie as watched",
)
async def set_movie_watched(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Mark a movie as watched.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.set_watched(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.delete(
    "/{movie_id}/watched",
    response_model=UserMovieInteractionResponse,
    summary="Unmark movie as watched",
)
async def unset_movie_watched(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Unmark a movie as watched.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.unset_watched(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.put(
    "/{movie_id}/liked",
    response_model=UserMovieInteractionResponse,
    summary="Like a movie",
)
async def set_movie_liked(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Like a movie.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.set_liked(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.delete(
    "/{movie_id}/liked",
    response_model=UserMovieInteractionResponse,
    summary="Unlike a movie",
)
async def unset_movie_liked(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Unlike a movie.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.unset_liked(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.put(
    "/{movie_id}/watchlist",
    response_model=UserMovieInteractionResponse,
    summary="Add movie to watchlist",
)
async def set_movie_watchlist(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Add a movie to the user's watchlist.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.set_watchlist(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.delete(
    "/{movie_id}/watchlist",
    response_model=UserMovieInteractionResponse,
    summary="Remove movie from watchlist",
)
async def unset_movie_watchlist(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Remove a movie from the user's watchlist.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user movie interaction
    """
    try:
        result = interaction_service.unset_watchlist(db, user_id, movie_id)
        return result
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)

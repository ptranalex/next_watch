"""
User movie interactions API routes.

These routes handle user interactions with movies, like marking movies as watched,
adding them to watchlists, or liking them.
"""

import logging
from datetime import datetime
from typing import Annotated, Dict, List, Optional, Union, Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from movie_storage.db.operations import get_movie_by_id
from movie_storage.models.movie import Movie
from movie_storage.models.user import User
from movie_storage.models.user_interaction import UserMovieInteraction
from pydantic import BaseModel
from sqlmodel import Field, Session

from backend_api.db import get_db
from backend_api.dependencies import get_user_id_from_header
from backend_api.errors import (
    ResourceNotFoundError,
    ValidationError,
    service_error_to_http_exception,
)
from backend_api.queries import UserInteractionQuery
from .auth import get_current_user
from backend_api.schemas import (
    MovieSummary,
    UserMovieDetail,
    UserMovieInteractionResponse,
    UserMovieInteractionWithMovie,
)
from backend_api.services.user_interaction import UserInteractionService

logger = logging.getLogger(__name__)

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
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[UserMovieInteraction]:
    """
    Get the current user's watchlist.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies in the user's watchlist
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_watchlist(db, current_user.id, limit, offset)
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
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[UserMovieInteraction]:
    """
    Get the current user's watched movies.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies the user has watched
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_watched_movies(
            db, current_user.id, limit, offset
        )
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
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[UserMovieInteraction]:
    """
    Get the current user's liked movies.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies the user has liked
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_liked_movies(
            db, current_user.id, limit, offset
        )
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
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Toggle a movie in the user's watchlist.

    If the movie is not in the watchlist, it will be added.
    If the movie is already in the watchlist, it will be removed.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction

    Raises:
        HTTPException: If the movie doesn't exist

    Deprecated:
        Use PUT /{movie_id}/watchlist to add to watchlist or
        DELETE /{movie_id}/watchlist to remove from watchlist instead.
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Toggle watchlist status
    try:
        return interaction_service.toggle_watchlist(db, current_user.id, movie_id)
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
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Toggle a movie as watched.

    If the movie is not marked as watched, it will be marked as watched.
    If the movie is already marked as watched, it will be unmarked.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction

    Raises:
        HTTPException: If the movie doesn't exist

    Deprecated:
        Use PUT /{movie_id}/watched to mark as watched or
        DELETE /{movie_id}/watched to unmark as watched instead.
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Toggle watched status
    try:
        return interaction_service.toggle_watched(db, current_user.id, movie_id)
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
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Toggle a movie as liked.

    If the movie is not liked, it will be marked as liked.
    If the movie is already liked, it will be unmarked.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction

    Raises:
        HTTPException: If the movie doesn't exist

    Deprecated:
        Use PUT /{movie_id}/liked to mark as liked or
        DELETE /{movie_id}/liked to unlike instead.
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Toggle liked status
    try:
        return interaction_service.toggle_liked(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Delete a movie interaction completely
@router.delete(
    "/{movie_id}/interaction",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a movie interaction",
)
async def delete_movie_interaction(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> None:
    """
    Delete a user's interaction with a movie completely.

    This removes all interaction flags (watched, liked, in_watchlist).

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        No content

    Raises:
        HTTPException: If the movie doesn't exist or has no interaction
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Delete interaction
    try:
        success = interaction_service.delete_interaction(db, current_user.id, movie_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No interaction found for this movie",
            )
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** New optimized endpoint for movie details by category
@router.get(
    "/{category}",
    response_model=List[UserMovieDetail],
    summary="Get user's movies with optimized details",
)
async def get_user_movie_details(
    category: Annotated[
        str, Path(title="Category", description="One of: watchlist, watched, liked")
    ],
    current_user: Annotated[User, Depends(get_current_user)],
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
    Get the current user's movie details for a specific category with filtering and sorting.

    This endpoint uses an optimized database query and supports filtering by ratings,
    year, and sorting by various criteria.

    Args:
        category: Category of movies to retrieve (watchlist, watched, liked)
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        page: Page number for pagination
        limit: Maximum number of items to return
        sort_by: Field to sort by (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)
        sort_desc: Whether to sort in descending order
        imdb_rating: Filter by minimum IMDb rating
        rotten_tomatoes_rating: Filter by minimum Rotten Tomatoes rating
        metacritic_rating: Filter by minimum Metacritic rating
        year: Filter by release year

    Returns:
        List of movie details with interaction status including imdb_rating
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Convert page to offset
    offset = (page - 1) * limit

    try:
        ***REMOVED*** Get movie details with optimized query (currently only supports basic pagination)
        ***REMOVED*** TODO: Extend get_user_movie_details to support filtering and sorting
        movie_details, total = interaction_query.get_user_movie_details(
            db, current_user.id, category, limit, offset
        )

        ***REMOVED*** For now, apply filtering and sorting in Python (not optimal, but functional)
        ***REMOVED*** This should be moved to the database query for better performance
        if movie_details:
            ***REMOVED*** Apply filters
            if imdb_rating is not None:
                movie_details = [
                    m for m in movie_details if m.imdb_rating and m.imdb_rating >= imdb_rating
                ]
            if rotten_tomatoes_rating is not None:
                movie_details = [
                    m
                    for m in movie_details
                    if hasattr(m, "rotten_tomatoes_rating")
                    and getattr(m, "rotten_tomatoes_rating")
                    and getattr(m, "rotten_tomatoes_rating") >= rotten_tomatoes_rating
                ]
            if metacritic_rating is not None:
                movie_details = [
                    m
                    for m in movie_details
                    if hasattr(m, "metacritic_rating")
                    and getattr(m, "metacritic_rating")
                    and getattr(m, "metacritic_rating") >= metacritic_rating
                ]
            if year is not None:
                movie_details = [
                    m
                    for m in movie_details
                    if m.release_date and m.release_date.startswith(str(year))
                ]

            ***REMOVED*** Apply sorting
            reverse = sort_desc
            if sort_by == "title":
                movie_details.sort(key=lambda x: x.title.lower(), reverse=reverse)
            elif sort_by == "release_date":
                movie_details.sort(key=lambda x: x.release_date or "1900-01-01", reverse=reverse)
            elif sort_by == "imdb_rating":
                movie_details.sort(key=lambda x: x.imdb_rating or 0, reverse=reverse)
            elif sort_by in ["rotten_tomatoes_rating", "metacritic_rating"]:
                movie_details.sort(key=lambda x: getattr(x, sort_by, 0) or 0, reverse=reverse)

        return movie_details
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** New schema for Netflix import results
class NetflixImportResult(BaseModel):
    """Result of a Netflix history import operation."""

    total_entries: int
    matched_movies: int
    already_marked_watched: int
    newly_marked_watched: int
    unmatched_titles: List[str]


***REMOVED*** Import Netflix watch history
@router.post(
    "/import/netflix",
    response_model=NetflixImportResult,
    summary="Import Netflix watch history",
)
async def import_netflix_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
    file: UploadFile = File(...),
) -> NetflixImportResult:
    """
    Import Netflix watch history from a CSV file.

    Parses the Netflix CSV export format, matches movie titles to the database,
    and marks matching movies as watched by the current user.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service
        file: CSV file containing Netflix watch history

    Returns:
        Summary of import results including matches and unmatched titles

    Raises:
        HTTPException: For invalid files or processing errors
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Validate file
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a CSV file",
        )

    ***REMOVED*** Read file content
    try:
        contents = await file.read()
        csv_text = contents.decode("utf-8")

        ***REMOVED*** Process CSV using service
        try:
            result = interaction_service.import_netflix_history(db, current_user.id, csv_text)

            ***REMOVED*** Convert to response model
            return NetflixImportResult(
                total_entries=result["total_entries"],
                matched_movies=result["matched_movies"],
                already_marked_watched=result["already_marked_watched"],
                newly_marked_watched=result["newly_marked_watched"],
                unmatched_titles=result["unmatched_titles"],
            )
        except ValidationError as e:
            ***REMOVED*** Convert validation errors to HTTP exceptions
            raise service_error_to_http_exception(e)
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid UTF-8 encoded CSV file",
        )
    except Exception as e:
        logger.error(f"Error processing Netflix CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )


***REMOVED*** ============================================================================
***REMOVED*** New RESTful endpoints for user interactions
***REMOVED*** ============================================================================


***REMOVED*** PUT endpoint to set watched status
@router.put(
    "/{movie_id}/watched",
    response_model=UserMovieInteractionResponse,
    summary="Mark movie as watched",
)
async def set_movie_watched(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Mark a movie as watched.

    If the movie is already marked as watched, this operation is idempotent and
    will not change the state.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Use new set_watched method for cleaner implementation
        return interaction_service.set_watched(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** DELETE endpoint to unset watched status
@router.delete(
    "/{movie_id}/watched",
    response_model=UserMovieInteractionResponse,
    summary="Unmark movie as watched",
)
async def unset_movie_watched(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Unmark a movie as watched.

    If the movie is not marked as watched, this operation is idempotent and
    will not change the state.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Use new unset_watched method for cleaner implementation
        return interaction_service.unset_watched(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** PUT endpoint to set liked status
@router.put(
    "/{movie_id}/liked",
    response_model=UserMovieInteractionResponse,
    summary="Like a movie",
)
async def set_movie_liked(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Like a movie.

    If the movie is already liked, this operation is idempotent and
    will not change the state.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Use new set_liked method for cleaner implementation
        return interaction_service.set_liked(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** DELETE endpoint to unset liked status
@router.delete(
    "/{movie_id}/liked",
    response_model=UserMovieInteractionResponse,
    summary="Unlike a movie",
)
async def unset_movie_liked(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Unlike a movie.

    If the movie is not liked, this operation is idempotent and
    will not change the state.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Use new unset_liked method for cleaner implementation
        return interaction_service.unset_liked(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** PUT endpoint to add to watchlist
@router.put(
    "/{movie_id}/watchlist",
    response_model=UserMovieInteractionResponse,
    summary="Add movie to watchlist",
)
async def set_movie_watchlist(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Add a movie to watchlist.

    If the movie is already in the watchlist, this operation is idempotent and
    will not change the state.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Use new set_watchlist method for cleaner implementation
        return interaction_service.set_watchlist(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** DELETE endpoint to remove from watchlist
@router.delete(
    "/{movie_id}/watchlist",
    response_model=UserMovieInteractionResponse,
    summary="Remove movie from watchlist",
)
async def unset_movie_watchlist(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> UserMovieInteraction:
    """
    Remove a movie from watchlist.

    If the movie is not in the watchlist, this operation is idempotent and
    will not change the state.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Use new unset_watchlist method for cleaner implementation
        return interaction_service.unset_watchlist(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)

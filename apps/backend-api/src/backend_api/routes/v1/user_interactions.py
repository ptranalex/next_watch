"""
User movie interactions API routes.

These routes handle user interactions with movies, like marking movies as watched,
adding them to watchlists, or liking them.
"""

from typing import Annotated, List, Optional
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
    UploadFile,
    File,
)
from sqlmodel import Session, Field
import logging

from backend_api.db.database import get_db
from backend_api.routes.v1.auth import get_current_user
from backend_api.schemas.user_interaction_schema import (
    UserMovieInteractionResponse,
    UserMovieInteractionWithMovie,
    MovieSummary,
    UserMovieDetail,
)
from backend_api.services.user_interaction import UserInteractionService
from backend_api.queries.user_interaction_query import UserInteractionQuery
from backend_api.errors import (
    ResourceNotFoundError,
    ValidationError,
    service_error_to_http_exception,
)
from movie_storage.models.user import User
from movie_storage.models.movie import Movie
from movie_storage.models.user_interaction import UserMovieInteraction
from movie_storage.db.operations import get_movie_by_id
from pydantic import BaseModel

logger = logging.getLogger(__name__)

***REMOVED*** Create router
router = APIRouter(prefix="/user/movies", tags=["user-movies"])


***REMOVED*** Get dependencies
def get_user_interaction_service():
    """Get user interaction service."""
    return UserInteractionService()


def get_user_interaction_query():
    """Get user interaction query."""
    return UserInteractionQuery()


***REMOVED*** Get user interaction with a specific movie
@router.get(
    "/{movie_id}/interaction",
    response_model=Optional[UserMovieInteractionResponse],
    summary="Get user interaction with a specific movie",
)
async def get_movie_interaction(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
):
    """
    Get the current user's interaction with a specific movie.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query

    Returns:
        User's interaction with the movie, or None if no interaction exists
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Get user interaction
    try:
        return interaction_query.get_user_interaction(db, current_user.id, movie_id)
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
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
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
        interactions, _ = interaction_query.get_user_watchlist(
            db, current_user.id, limit, offset
        )
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
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
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
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
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
)
async def toggle_watchlist(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
):
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
)
async def toggle_watched(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
):
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
)
async def toggle_liked(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
):
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
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
):
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
    "/movies/{category}",
    response_model=List[UserMovieDetail],
    summary="Get user's movies with optimized details",
)
async def get_user_movie_details(
    category: Annotated[
        str, Path(title="Category", description="One of: watchlist, watched, liked")
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    Get the current user's movie details for a specific category using an optimized query.

    This endpoint uses a more efficient database query than the separate endpoints
    by retrieving movie data and interaction status in a single operation.

    Args:
        category: Category of movies to retrieve (watchlist, watched, liked)
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movie details with interaction status including imdb_rating
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Get movie details with optimized query
        movie_details, _ = interaction_query.get_user_movie_details(
            db, current_user.id, category, limit, offset
        )
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
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
    file: UploadFile = File(...),
):
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
            result = interaction_service.import_netflix_history(
                db, current_user.id, csv_text
            )

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
